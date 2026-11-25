"""
Neural network alternatives for C1 and C2, added after the Week 10 supervision meeting.

C1: an LSTM reads the last 28 days at the port (congestion index and class, traffic, disruptions)
together with what is known about tomorrow (vessel schedule, calendar, warning). An MLP on the
same tabular features as XGBoost is a second, non-sequential neural network. Both use the same
chronological split and the same test days as C1, so the results can be compared directly.

C2: customs records are separate consignments, not a time series, so only an MLP is tried.
"""

from typing import Dict, Tuple

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import precision_recall_fscore_support
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch import nn

from . import c1_congestion as c1

SEQ_LEN = 28
SEQ_COLS = ["congestion_index", "roro_units", "scheduled_arrivals", "disruption", "is_holiday",
            "cls_Low", "cls_Medium", "cls_High"]
NEXT_COLS = ["is_dublin", "scheduled_arrivals", "arrivals_vs_28d", "is_holiday", "disruption_warning",
             "month_sin", "month_cos"] + [f"dow_{k}" for k in range(7)]


# ------------------------------------------------------------------ data for the LSTM
def sequence_data(port_days: pd.DataFrame, feat: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    For every row of the C1 feature table, the previous SEQ_LEN days at that port (sequence)
    and the facts known about the target day (next-day vector). Nothing from the target day
    itself is used except the vessel schedule, calendar and warning, as for XGBoost.
    """
    pdays = port_days.sort_values(["port", "date"]).copy()
    for c in c1.CLASSES:
        pdays[f"cls_{c}"] = (pdays["congestion_class"] == c).astype(float)
    pdays["disruption"] = pdays["disruption"].astype(float)
    pdays["is_holiday"] = pdays["is_holiday"].astype(float)
    pos = {}
    hist = {}
    for port, d in pdays.groupby("port"):
        d = d.reset_index(drop=True)
        hist[port] = d[SEQ_COLS].to_numpy(dtype=np.float32)
        pos.update({(port, t): i for i, t in enumerate(d["date"])})

    f = feat.copy()
    f["month_sin"] = np.sin(2 * np.pi * f["month"] / 12)
    f["month_cos"] = np.cos(2 * np.pi * f["month"] / 12)
    for k in range(7):
        f[f"dow_{k}"] = (f["dow"] == k).astype(float)
    seqs = np.empty((len(f), SEQ_LEN, len(SEQ_COLS)), dtype=np.float32)
    for r, (port, t) in enumerate(zip(f["port"], f["date"])):
        i = pos[(port, t)]
        if i < SEQ_LEN:
            raise ValueError("not enough history for the sequence")
        seqs[r] = hist[port][i - SEQ_LEN:i]
    return seqs, f[NEXT_COLS].to_numpy(dtype=np.float32)


class Scaler:
    """Standardise with training statistics only."""

    def fit(self, seq: np.ndarray, nxt: np.ndarray) -> "Scaler":
        self.sm, self.ss = seq.reshape(-1, seq.shape[2]).mean(0), seq.reshape(-1, seq.shape[2]).std(0) + 1e-6
        self.nm, self.ns = nxt.mean(0), nxt.std(0) + 1e-6
        return self

    def __call__(self, seq: np.ndarray, nxt: np.ndarray):
        return (seq - self.sm) / self.ss, (nxt - self.nm) / self.ns


class LSTMClassifier(nn.Module):
    def __init__(self, n_seq: int, n_next: int, hidden: int = 32):
        super().__init__()
        self.lstm = nn.LSTM(n_seq, hidden, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hidden + n_next, 64), nn.ReLU(), nn.Dropout(0.2), nn.Linear(64, 3))

    def forward(self, seq, nxt):
        _, (h, _) = self.lstm(seq)
        return self.head(torch.cat([h[-1], nxt], dim=1))


def _train(seq, nxt, y, epochs: int, seed: int, valid=None):
    """Train with Adam; if valid data is given, return the epoch with the lowest validation loss."""
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    model = LSTMClassifier(seq.shape[2], nxt.shape[1])
    opt = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.CrossEntropyLoss()
    S, N, Y = torch.tensor(seq), torch.tensor(nxt), torch.tensor(y, dtype=torch.long)
    best = (np.inf, 0)
    for ep in range(1, epochs + 1):
        model.train()
        idx = rng.permutation(len(Y))
        for b in range(0, len(idx), 64):
            j = idx[b:b + 64]
            opt.zero_grad()
            loss_fn(model(S[j], N[j]), Y[j]).backward()
            opt.step()
        if valid is not None:
            model.eval()
            with torch.no_grad():
                vl = loss_fn(model(torch.tensor(valid[0]), torch.tensor(valid[1])),
                             torch.tensor(valid[2], dtype=torch.long)).item()
            if vl < best[0]:
                best = (vl, ep)
    return model, best[1]


def _proba(model, seq, nxt) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        return torch.softmax(model(torch.tensor(seq), torch.tensor(nxt)), dim=1).numpy()


def lstm_test(port_days: pd.DataFrame, sets: Dict[str, pd.DataFrame], seeds=range(5),
              max_epochs: int = 60) -> Tuple[pd.DataFrame, list]:
    """
    Same protocol as XGBoost: choose the number of epochs on the 2024 validation year,
    refit on 2017 to 2024 and test on 2025 to mid-2026. Repeated for several seeds.
    Returns the test metrics per seed and the test probabilities of each seed.
    """
    torch.set_num_threads(1)
    data = {k: sequence_data(port_days, v) for k, v in sets.items()}
    y = {k: v["y"].to_numpy() for k, v in sets.items()}
    rows, probas = [], []
    for s in seeds:
        sc = Scaler().fit(*data["train"])
        tr, va = sc(*data["train"]), sc(*data["valid"])
        _, best_ep = _train(*tr, y["train"], max_epochs, s, valid=(*va, y["valid"]))
        trval_seq = np.concatenate([data["train"][0], data["valid"][0]])
        trval_nxt = np.concatenate([data["train"][1], data["valid"][1]])
        sc = Scaler().fit(trval_seq, trval_nxt)
        model, _ = _train(*sc(trval_seq, trval_nxt), np.concatenate([y["train"], y["valid"]]), best_ep, s)
        p = _proba(model, *sc(*data["test"]))
        probas.append(p)
        rows.append({"seed": s, "epochs": best_ep, **c1.evaluate(y["test"], p)})
    return pd.DataFrame(rows), probas


# ------------------------------------------------------------------ MLPs (tabular)
def mlp_classifier(seed: int = 42):
    return make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(64, 32), alpha=1e-3, max_iter=500,
                                                         early_stopping=True, random_state=seed))


def mlp_regressor(seed: int = 42):
    return make_pipeline(StandardScaler(), MLPRegressor(hidden_layer_sizes=(64, 32), alpha=1e-3, max_iter=500,
                                                        early_stopping=True, random_state=seed))


def mlp_c1_test(sets: Dict[str, pd.DataFrame], seeds=range(5)) -> Tuple[pd.DataFrame, list]:
    trval = pd.concat([sets["train"], sets["valid"]])
    y = sets["test"]["y"].to_numpy()
    rows, probas = [], []
    for s in seeds:
        p = mlp_classifier(s).fit(trval[c1.FEATURES], trval["y"]).predict_proba(sets["test"][c1.FEATURES])
        probas.append(p)
        rows.append({"seed": s, **c1.evaluate(y, p)})
    return pd.DataFrame(rows), probas


# ------------------------------------------------------------------ per-class report
def class_report(name: str, y: np.ndarray, proba: np.ndarray) -> pd.DataFrame:
    """Precision, recall and F1 for each congestion class."""
    pred = proba.argmax(axis=1)
    p, r, f, n = precision_recall_fscore_support(y, pred, labels=range(3), zero_division=0)
    return pd.DataFrame({"model": name, "class": c1.CLASSES, "precision": p.round(3), "recall": r.round(3),
                         "f1": f.round(3), "support": n})

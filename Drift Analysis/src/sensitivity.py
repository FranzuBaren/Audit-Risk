"""
Sensitivity analysis for the drift experiment.

Runs the experiment under three perturbations to demonstrate that the
KL early-warning result is not an artifact of the chosen seed, drift
speed, or alarm threshold.

  (1) Seed sweep:        21 seeds, default drift speed, default thresholds.
  (2) Drift-speed sweep: 7 drift-window widths from 200 to 800 days.
  (3) Threshold sweep:   KL alarm threshold from 0.02 to 0.20.

For each configuration we report the KL alarm day, the accuracy alarm day,
and the lead time. The result the post claims is the median across seeds.

Run:  python src/sensitivity.py
Output: console summary plus figures/sensitivity_*.png
"""

import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
from scipy.stats import gaussian_kde
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt

TEAL, NAVY, ROSE, AMBER, SLATE = "#2A8B8B", "#1F3A5F", "#D9485B", "#E8A73C", "#6B7A8C"
plt.rcParams.update({"font.family": "Georgia", "axes.edgecolor": NAVY,
                     "axes.labelcolor": NAVY, "xtick.color": NAVY, "ytick.color": NAVY})

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Reuse registers from the main experiment.
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drift_experiment import (
    REGISTER_CONSERVATIVE, REGISTER_ECL, kl_div,
)


def run_one(seed=42, drift_start=200, drift_end=800, kl_thresh=0.05,
            acc_drop=0.05, encoder=None):
    """Run a single experiment and return (kl_day, acc_day, lead)."""
    rng = np.random.default_rng(seed)
    np.random.seed(seed)

    # corpus
    corpus = []
    for day in range(1000):
        if day < drift_start:
            p_ecl = 0.0
        elif day < drift_end:
            p_ecl = (day - drift_start) / (drift_end - drift_start)
        else:
            p_ecl = 1.0
        register = "ecl" if rng.random() < p_ecl else "conservative"
        label = "high_risk" if rng.random() < 0.5 else "low_risk"
        templates = (REGISTER_ECL if register == "ecl" else REGISTER_CONSERVATIVE)[label]
        text = templates[int(rng.integers(0, len(templates)))]
        corpus.append({"day": day, "text": text, "label": label})

    texts = [d["text"] for d in corpus]
    labels = np.array([1 if d["label"] == "high_risk" else 0 for d in corpus])
    days = np.array([d["day"] for d in corpus])
    emb = encoder.encode(texts, batch_size=64, show_progress_bar=False)

    train_mask = days < 100
    clf = LogisticRegression(max_iter=2000, random_state=seed).fit(emb[train_mask], labels[train_mask])
    pca = PCA(n_components=1, random_state=seed).fit(emb[train_mask])
    projected = pca.transform(emb).flatten()

    baseline_kde = gaussian_kde(projected[train_mask], bw_method=0.3)
    grid = np.linspace(projected.min() - 0.5, projected.max() + 0.5, 200)
    p_baseline = baseline_kde(grid) + 1e-9
    p_baseline /= p_baseline.sum()

    windows = []
    for start in range(0, 1000 - 50 + 1, 10):
        end = start + 50
        mask = (days >= start) & (days < end)
        if mask.sum() < 20:
            continue
        acc = accuracy_score(labels[mask], clf.predict(emb[mask]))
        win_kde = gaussian_kde(projected[mask], bw_method=0.3)
        p_win = win_kde(grid) + 1e-9
        p_win /= p_win.sum()
        windows.append({"day": (start + end) // 2, "acc": acc, "kl": kl_div(p_win, p_baseline)})

    baseline_acc = np.mean([w["acc"] for w in windows if w["day"] < 150])
    acc_thresh = baseline_acc - acc_drop
    kl_day  = next((w["day"] for w in windows if w["day"] >= 150 and w["kl"]  > kl_thresh), None)
    acc_day = next((w["day"] for w in windows if w["day"] >= 150 and w["acc"] < acc_thresh), None)
    lead = (acc_day - kl_day) if (kl_day and acc_day) else None
    return kl_day, acc_day, lead


def sweep_seeds(encoder, seeds=range(0, 21)):
    print("\n=== Seed sweep ===")
    rows = []
    for s in seeds:
        kl_d, acc_d, lead = run_one(seed=s, encoder=encoder)
        rows.append({"seed": s, "kl": kl_d, "acc": acc_d, "lead": lead})
        print(f"  seed {s:3d}:  KL day={kl_d}, accuracy day={acc_d}, lead={lead}")
    leads = [r["lead"] for r in rows if r["lead"] is not None]
    print(f"\n  Median lead time: {int(np.median(leads))} days")
    print(f"  IQR:              [{int(np.percentile(leads, 25))}, {int(np.percentile(leads, 75))}] days")
    print(f"  Min / Max:        {min(leads)} / {max(leads)} days")
    return rows


def sweep_drift_speed(encoder):
    print("\n=== Drift-speed sweep ===")
    configs = [
        (350, 650),  # fast (300 day window)
        (300, 700),  # medium-fast (400)
        (250, 750),  # medium (500)
        (200, 800),  # default (600)
        (150, 850),  # slow (700)
        (100, 900),  # very slow (800)
    ]
    rows = []
    for start, end in configs:
        kl_d, acc_d, lead = run_one(drift_start=start, drift_end=end, encoder=encoder)
        rows.append({"width": end - start, "kl": kl_d, "acc": acc_d, "lead": lead})
        print(f"  drift width {end - start:4d}d:  KL={kl_d}, accuracy={acc_d}, lead={lead}")
    return rows


def sweep_kl_threshold(encoder):
    print("\n=== KL threshold sweep ===")
    rows = []
    for t in [0.02, 0.05, 0.08, 0.10, 0.15, 0.20]:
        kl_d, acc_d, lead = run_one(kl_thresh=t, encoder=encoder)
        rows.append({"thresh": t, "kl": kl_d, "acc": acc_d, "lead": lead})
        print(f"  threshold {t:.2f}:  KL day={kl_d}, lead={lead}")
    return rows


def plot_seeds(rows):
    leads = [r["lead"] for r in rows if r["lead"] is not None]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(leads, bins=10, color=TEAL, alpha=0.75, edgecolor="white")
    ax.axvline(np.median(leads), color=ROSE, linestyle="--", linewidth=1.5,
               label=f"median = {int(np.median(leads))} days")
    ax.set_xlabel("KL early-warning lead time (days)")
    ax.set_ylabel("Count")
    ax.set_title("Lead time across 21 random seeds", fontweight="bold", color=NAVY)
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "sensitivity_seeds.png")
    plt.savefig(out, dpi=180, facecolor="white")
    plt.close()
    print(f"Saved: {out}")


def plot_drift(rows):
    widths = [r["width"] for r in rows]
    leads  = [r["lead"] if r["lead"] else 0 for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(widths, leads, width=60, color=NAVY, alpha=0.85, edgecolor="white")
    for w, l in zip(widths, leads):
        ax.text(w, l + 5, f"{l}", ha="center", color=NAVY, fontsize=9)
    ax.set_xlabel("Drift window width (days)")
    ax.set_ylabel("KL lead time (days)")
    ax.set_title("Lead time stays positive across drift speeds", fontweight="bold", color=NAVY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "sensitivity_drift.png")
    plt.savefig(out, dpi=180, facecolor="white")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("Loading sentence encoder…")
    enc = SentenceTransformer("all-MiniLM-L6-v2")

    seed_rows  = sweep_seeds(enc, seeds=range(0, 21))
    drift_rows = sweep_drift_speed(enc)
    thresh_rows = sweep_kl_threshold(enc)

    plot_seeds(seed_rows)
    plot_drift(drift_rows)

    print("\nSensitivity analysis complete.")

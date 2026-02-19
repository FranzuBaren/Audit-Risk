"""Publication-quality figures for the adversarial stress-test.

Design system: Lora (titles) + Poppins (body) + DejaVu Sans Mono (data).
Warm paper background (#FAFAF8). Semantic color palette.
"""

from collections import Counter
from typing import Dict, List

import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from scipy import stats

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

FONT_TITLE = "Lora"
FONT_BODY = "Poppins"
FONT_MONO = "DejaVu Sans Mono"

CLR = {
    "people": "#2D8E6F", "system": "#3B6CB5", "process": "#C4852C",
    "vendor": "#C44D56", "neutral": "#9E9E9E", "accent": "#7B4BBF",
    "danger": "#D13B40", "safe": "#2CA06B", "bg": "#FAFAF8",
    "text": "#2D2D2D", "muted": "#888888", "grid": "#E8E8E5", "card": "#FFFFFF",
}
CAT_C = {"person": CLR["people"], "system": CLR["system"],
         "process": CLR["process"], "vendor": CLR["vendor"]}
CAT_M = {"person": "o", "system": "s", "process": "D", "vendor": "^"}

cmap_threat = LinearSegmentedColormap.from_list(
    "threat", ["#FAFAF8", "#E8D5A0", "#D4965A", "#C44D56", "#7B2040", "#3A0E28"], 512)
cmap_heat = LinearSegmentedColormap.from_list(
    "heat", ["#FAFAF8", "#A8C8E8", "#6BA3D6", "#C4852C", "#C44D56", "#7B2040"], 512)


def apply_style():
    """Apply the global matplotlib style."""
    plt.rcParams.update({
        "figure.facecolor": CLR["bg"], "axes.facecolor": CLR["bg"],
        "savefig.facecolor": CLR["bg"],
        "text.color": CLR["text"], "axes.labelcolor": CLR["text"],
        "xtick.color": "#666666", "ytick.color": "#666666",
        "axes.edgecolor": "#CCCCCC", "grid.color": CLR["grid"],
        "grid.alpha": 1.0, "grid.linewidth": 0.4,
        "font.family": "sans-serif",
        "font.sans-serif": [FONT_BODY, "DejaVu Sans"],
        "font.size": 9, "axes.titlesize": 12, "axes.labelsize": 9,
        "figure.dpi": 150,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.linewidth": 0.6, "legend.frameon": False, "legend.fontsize": 8,
    })


def _title(ax, text, x=0.0, y=1.06, fontsize=13):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=fontsize,
            fontfamily=FONT_TITLE, fontweight="bold", color=CLR["text"], va="bottom")


def _subtitle(ax, text, x=0.0, y=1.01, fontsize=8.5):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=fontsize,
            fontfamily=FONT_BODY, color=CLR["muted"], va="bottom", style="italic")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURES
# ══════════════════════════════════════════════════════════════════════════════

def fig1_graph(G, pos, outdir="figures"):
    apply_style()
    fig, ax = plt.subplots(figsize=(11, 9))
    for u, v, d in G.edges(data=True):
        w = d["weight"]
        ax.annotate("", xy=pos[v], xytext=pos[u],
            arrowprops=dict(arrowstyle="-|>", mutation_scale=11,
                color=(*plt.cm.colors.to_rgba(CLR["muted"])[:3], 0.08 + 0.40*w),
                lw=0.3 + 2.2*w, connectionstyle="arc3,rad=0.07"))
    for cat in ["person", "system", "process", "vendor"]:
        cn = [n for n in G.nodes() if G.nodes[n]["category"] == cat]
        lb = {"person": "People", "system": "Systems",
              "process": "Processes", "vendor": "Vendors"}[cat]
        ax.scatter([pos[n][0] for n in cn], [pos[n][1] for n in cn],
                   s=420, c=CAT_C[cat], marker=CAT_M[cat], edgecolors="white",
                   linewidths=1.2, zorder=5, label=lb, alpha=0.88)
    for n, (x, y) in pos.items():
        ax.text(x, y - 0.095, n.replace("_", " "), fontsize=6.5, ha="center",
                va="top", fontfamily=FONT_BODY, color=CLR["text"], fontweight="600")
    leg = ax.legend(fontsize=9, loc="upper left", markerscale=0.9)
    leg.get_frame().set_facecolor(CLR["card"])
    leg.get_frame().set_edgecolor(CLR["grid"])
    _title(ax, "Fig. 1  The Enterprise Dependency Graph")
    _subtitle(ax, "19 nodes \u00b7 33 edges \u00b7 Edge A\u2192B: B depends on A \u00b7 Thickness \u221d coupling")
    ax.axis("off"); fig.tight_layout(pad=1.5)
    fig.savefig(f"{outdir}/fig1_graph.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig2_heatmap(G, results, outdir="figures"):
    apply_style()
    scs = [r["scenario"] for r in results]
    ns = sorted(G.nodes(), key=lambda n: -max(r["scores"][n]["fragility"] for r in results))
    M = np.zeros((len(ns), len(scs)))
    for j, r in enumerate(results):
        for i, n in enumerate(ns):
            M[i, j] = r["scores"][n]["fragility"]
    fig, ax = plt.subplots(figsize=(9, 10))
    im = ax.imshow(M, cmap=cmap_heat, aspect="auto", interpolation="nearest", vmin=0)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                    fontfamily=FONT_MONO, color="white" if v > 0.22 else CLR["text"],
                    fontweight="bold" if v > 0.3 else "normal")
    ax.set_xticks(range(len(scs)))
    ax.set_xticklabels([s.short for s in scs], fontsize=9, fontfamily=FONT_BODY, fontweight="bold")
    ax.set_yticks(range(len(ns))); ax.set_yticklabels(ns, fontsize=8.5, fontfamily=FONT_MONO)
    for i, n in enumerate(ns):
        ax.get_yticklabels()[i].set_color(CAT_C[G.nodes[n]["category"]])
    for i in range(M.shape[0] - 1): ax.axhline(i + 0.5, color=CLR["bg"], lw=0.8)
    for j in range(M.shape[1] - 1): ax.axvline(j + 0.5, color=CLR["bg"], lw=0.8)
    cb = fig.colorbar(im, ax=ax, shrink=0.45, pad=0.015, aspect=25)
    cb.set_label("Fragility score", fontsize=9, fontfamily=FONT_BODY)
    cb.outline.set_linewidth(0.3)
    _title(ax, "Fig. 2  Fragility Heatmap")
    _subtitle(ax, "Nodes \u00d7 scenarios \u00b7 Sorted by max fragility")
    fig.tight_layout(pad=1.5)
    fig.savefig(f"{outdir}/fig2_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig3_ridgeplot(results, outdir="figures"):
    apply_style()
    fig, axes = plt.subplots(len(results), 1, figsize=(10, 8), sharex=True,
                             gridspec_kw={"hspace": -0.45})
    for i, (r, ax) in enumerate(zip(results, axes)):
        s = r["scenario"]; f = r["fracs"] * 100
        ax.set_facecolor("none"); ax.patch.set_alpha(0)
        if f.std() > 0:
            kde = stats.gaussian_kde(f, bw_method=0.25)
            x = np.linspace(0, 75, 500); y = kde(x)
            ax.fill_between(x, y, color=s.color, alpha=0.35, lw=0)
            ax.plot(x, y, color=s.color, lw=1.5, alpha=0.9)
        m = f.mean(); p95 = np.percentile(f, 95)
        ax.axvline(m, color=s.color, lw=1.2, alpha=0.7, ymin=0, ymax=0.6)
        ax.axvline(p95, color=s.color, lw=0.8, ls="--", alpha=0.5, ymin=0, ymax=0.4)
        ax.text(-2, 0, s.short, fontsize=9, fontfamily=FONT_BODY, fontweight="bold",
                color=s.color, ha="right", va="bottom")
        ax.text(m, ax.get_ylim()[1] * 0.55, f"{m:.1f}%", fontsize=7.5, ha="center",
                va="bottom", color=s.color, fontweight="bold", fontfamily=FONT_MONO)
        if p95 > m + 5:
            ax.text(p95 + 0.5, ax.get_ylim()[1] * 0.3, f"P95={p95:.0f}%", fontsize=6.5,
                    va="bottom", color=s.color, alpha=0.7, fontfamily=FONT_MONO)
        ax.set_yticks([]); ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(i == len(results) - 1)
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        ax.set_xlim(-8, 75)
    axes[-1].set_xlabel("Organizational damage (%)", fontsize=10, fontfamily=FONT_BODY)
    axes[-1].spines["bottom"].set_color(CLR["muted"])
    fig.text(0.02, 0.97, "Fig. 3  Damage Distributions", fontsize=13,
             fontfamily=FONT_TITLE, fontweight="bold", color=CLR["text"], va="top")
    fig.text(0.02, 0.935, "10,000 sims/scenario \u00b7 Solid = mean \u00b7 Dashed = P95",
             fontsize=8.5, fontfamily=FONT_BODY, color=CLR["muted"], va="top", style="italic")
    fig.savefig(f"{outdir}/fig3_ridgeplot.png", dpi=300, bbox_inches="tight", facecolor=CLR["bg"])
    plt.close(fig)


def fig4_bottleneck(G, bn_rates, total_major, outdir="figures"):
    apply_style()
    ranked = sorted(bn_rates.items(), key=lambda x: -x[1])[:14]
    nm = [n for n, _ in ranked]; rates = [bn_rates[n] * 100 for n in nm]
    colors = [CAT_C[G.nodes[n]["category"]] for n in nm]
    fig, ax = plt.subplots(figsize=(10, 7))
    for i, (r, c) in enumerate(zip(rates, colors)):
        ax.plot([0, r], [i, i], color=c, lw=1.8, alpha=0.6, solid_capstyle="round")
        ax.scatter(r, i, s=120, color=c, edgecolors="white", linewidths=1.2, zorder=5)
        ax.text(r + 1.5, i, f"{r:.0f}%", fontsize=8.5, fontfamily=FONT_MONO,
                va="center", color=CLR["text"], fontweight="bold" if r >= 90 else "normal")
    ax.axvline(90, color=CLR["danger"], lw=1.0, ls="--", alpha=0.5, zorder=1)
    ax.text(91, -0.8, "90% threshold", fontsize=7.5, color=CLR["danger"],
            fontfamily=FONT_BODY, alpha=0.7)
    ax.set_yticks(range(len(nm))); ax.set_yticklabels(nm, fontsize=9.5, fontfamily=FONT_MONO)
    for i, n in enumerate(nm):
        ax.get_yticklabels()[i].set_color(CAT_C[G.nodes[n]["category"]])
    ax.invert_yaxis(); ax.set_xlim(-1, 108)
    ax.set_xlabel("Bottleneck frequency (% of major failures)", fontsize=10, fontfamily=FONT_BODY)
    ax.grid(axis="x", alpha=0.4, lw=0.3)
    _title(ax, "Fig. 4  Bottleneck Frequency \u2014 The Primary Audit Finding")
    _subtitle(ax, f"Across {total_major:,} major failures (>25% damage) from all stressed scenarios")
    fig.tight_layout(pad=1.5)
    fig.savefig(f"{outdir}/fig4_bottleneck.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig5_adversary(G, budget_results, outdir="figures"):
    apply_style()
    fig = plt.figure(figsize=(14, 5.5))
    gs = gridspec.GridSpec(1, 2, figure=fig, width_ratios=[2, 2.5], wspace=0.3)
    a1 = fig.add_subplot(gs[0]); a2 = fig.add_subplot(gs[1])
    ks = [r["k"] for r in budget_results]; dmgs = [r["damage"] * 100 for r in budget_results]
    a1.fill_between(ks, 0, dmgs, color=CLR["danger"], alpha=0.08)
    a1.plot(ks, dmgs, "o-", color=CLR["danger"], lw=2.5, ms=10, mec="white", mew=2, zorder=5)
    for k, d in zip(ks, dmgs):
        a1.text(k, d + 2.5, f"{d:.0f}%", fontsize=10, color=CLR["text"], fontweight="bold",
                ha="center", fontfamily=FONT_MONO)
    a1.set_xlabel("Attack budget (k nodes)", fontsize=10, fontfamily=FONT_BODY)
    a1.set_ylabel("Expected damage (%)", fontsize=10, fontfamily=FONT_BODY)
    a1.set_xticks(ks); a1.set_ylim(0, max(dmgs) * 1.25); a1.grid(alpha=0.4, lw=0.3)
    _title(a1, "Fig. 5a  Adversary Damage Curve", fontsize=11)
    # Dot matrix
    all_targeted = Counter()
    for r in budget_results:
        for n in r["targets"]: all_targeted[n] += 1
    targeted_nodes = sorted([n for n in G.nodes() if all_targeted.get(n, 0) > 0],
                            key=lambda n: -all_targeted[n])
    other_count = len(G.nodes()) - len(targeted_nodes)
    for ri, r in enumerate(budget_results):
        for ni, n in enumerate(targeted_nodes):
            if n in r["targets"]:
                a2.scatter(r["k"], ni, c=CAT_C[G.nodes[n]["category"]], s=280,
                           edgecolors=CLR["text"], linewidths=0.8, zorder=5, marker="s", alpha=0.85)
            else:
                a2.scatter(r["k"], ni, c=CLR["grid"], s=80, marker="o", alpha=0.3, zorder=2)
    a2.set_yticks(range(len(targeted_nodes)))
    a2.set_yticklabels(targeted_nodes, fontsize=9, fontfamily=FONT_MONO)
    for i, n in enumerate(targeted_nodes):
        a2.get_yticklabels()[i].set_color(CAT_C[G.nodes[n]["category"]])
    a2.set_xticks(ks); a2.set_xlabel("Budget k", fontsize=10, fontfamily=FONT_BODY)
    a2.invert_yaxis(); a2.grid(axis="x", alpha=0.3, lw=0.3)
    a2.text(0.02, -0.08, f"+ {other_count} nodes never targeted", transform=a2.transAxes,
            fontsize=7.5, color=CLR["muted"], fontfamily=FONT_BODY, style="italic")
    _title(a2, "Fig. 5b  Target Selection per Budget", fontsize=11)
    fig.tight_layout(pad=1.5)
    fig.savefig(f"{outdir}/fig5_adversary.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig6_cascade(G, pos, budget_results, outdir="figures"):
    apply_style()
    from .cascade import CascadeEngine
    targets_k5 = budget_results[-1]["targets"]
    best = None
    for s in range(17, 500):
        eng = CascadeEngine(G, seed=s)
        failed = eng.cascade_from(targets_k5, stress=1.5)
        cascade = failed - targets_k5
        if len(cascade) >= 3 and len(failed) / len(G.nodes()) > 0.3:
            if best is None or len(failed) > len(best[0]):
                best = (failed, targets_k5, cascade)
            if len(failed) >= 8: break
    if best is None:
        eng = CascadeEngine(G, 42)
        failed = eng.cascade_from(targets_k5, 1.5)
        best = (failed, targets_k5, failed - targets_k5)
    failed, initial, cascade = best
    COL_I, COL_C, COL_S = "#B5262C", "#D97B2A", "#2D8E6F"
    fig, ax = plt.subplots(figsize=(11, 9))
    for u, v, d in G.edges(data=True):
        fp = u in failed and v in failed
        c = COL_I if fp else "#ddd"; a = 0.6 if fp else 0.10; lw = 2.2 if fp else 0.4
        ax.annotate("", xy=pos[v], xytext=pos[u],
            arrowprops=dict(arrowstyle="-|>", mutation_scale=12,
                color=(*plt.cm.colors.to_rgba(c)[:3], a), lw=lw, connectionstyle="arc3,rad=0.08"))
    for n in G.nodes():
        x, y = pos[n]; col = COL_I if n in initial else (COL_C if n in cascade else COL_S)
        sz = 0.058 if n in failed else 0.040; alpha = 0.92 if n in failed else 0.6
        if n in initial:
            ax.add_patch(plt.Circle((x, y), sz * 1.5, color=COL_I, alpha=0.08, zorder=2))
        ax.add_patch(plt.Circle((x, y), sz, color=col, ec="white", lw=1.3, zorder=5, alpha=alpha))
        ax.text(x, y - sz - 0.028, n.replace("_", " "), fontsize=5.5, ha="center",
                va="top", fontfamily=FONT_BODY, color=CLR["text"], fontweight="600")
    li = [mpatches.Patch(color=COL_I, label=f"Adversary target ({len(initial)})"),
          mpatches.Patch(color=COL_C, label=f"Cascade failure ({len(cascade)})"),
          mpatches.Patch(color=COL_S, label=f"Survived ({len(G.nodes()) - len(failed)})")]
    leg = ax.legend(handles=li, fontsize=8.5, loc="upper left", borderpad=0.8)
    leg.get_frame().set_facecolor(CLR["card"]); leg.get_frame().set_edgecolor(CLR["grid"])
    _title(ax, f"Fig. 6  Cascade Anatomy \u2014 Adversary k={len(initial)}")
    _subtitle(ax, f"{len(initial)} targeted \u2192 {len(failed)} total failed ({len(failed)/len(G.nodes()):.0%} of org)")
    info = f"Targeted: {', '.join(sorted(initial))}\nCascade:  {', '.join(sorted(cascade)) if cascade else '(none)'}"
    ax.text(0.02, 0.02, info, transform=ax.transAxes, fontsize=7, color=CLR["muted"],
            va="bottom", fontfamily=FONT_MONO,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=CLR["card"], edgecolor=CLR["grid"], alpha=0.95, lw=0.5))
    ax.set_xlim(-1.55, 1.55); ax.set_ylim(-1.55, 1.55); ax.set_aspect("equal"); ax.axis("off")
    fig.tight_layout(pad=1.5)
    fig.savefig(f"{outdir}/fig6_cascade.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig7_cofailure(G, pos, results, outdir="figures"):
    apply_style()
    result = results[-1]; cf = result["cofail"]; th = 0.08
    CF = nx.Graph()
    for (a, b), count in cf.items():
        rate = count / result["N"]
        if rate > th: CF.add_edge(a, b, weight=rate)
    for n in G.nodes():
        if n not in CF: CF.add_node(n)
    fig, ax = plt.subplots(figsize=(11, 9))
    mw = max((d["weight"] for _, _, d in CF.edges(data=True)), default=1)
    for u, v, d in CF.edges(data=True):
        w = d["weight"]; nw = w / mw
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color=CLR["danger"], alpha=0.08 + 0.55*nw, lw=0.6 + 7*nw, solid_capstyle="round", zorder=1)
    for u, v, d in G.edges(data=True):
        ax.annotate("", xy=pos[v], xytext=pos[u],
            arrowprops=dict(arrowstyle="-|>", mutation_scale=6, color=(0.75, 0.75, 0.75, 0.06),
                            lw=0.15, connectionstyle="arc3,rad=0.08"))
    for n in G.nodes():
        x, y = pos[n]; cd = sum(1 for _, _, d in CF.edges(n, data=True)); sz = 0.032 + 0.013*cd
        ax.add_patch(plt.Circle((x, y), sz, color=CAT_C[G.nodes[n]["category"]],
                     ec="white", lw=0.8, zorder=5, alpha=0.82))
        ax.text(x, y - sz - 0.025, n.replace("_", " "), fontsize=5.5, ha="center",
                va="top", fontfamily=FONT_BODY, color=CLR["text"], fontweight="600")
    tp = sorted(CF.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)[:5]
    for u, v, d in tp:
        mx, my = (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2
        ax.text(mx, my + 0.055, f"{d['weight']:.0%}", fontsize=8, ha="center", va="bottom",
                color=CLR["danger"], fontweight="bold", fontfamily=FONT_MONO,
                bbox=dict(boxstyle="round,pad=0.15", facecolor=CLR["card"], alpha=0.92,
                          edgecolor=CLR["danger"], lw=0.5))
    _title(ax, "Fig. 7  Co-Failure Network")
    _subtitle(ax, f"Red links = pairs co-failing >{th:.0%} of sims \u00b7 Black Swan scenario")
    info = "Top co-failure pairs:\n" + "\n".join(f"  {u} + {v}: {d['weight']:.1%}" for u, v, d in tp[:5])
    ax.text(0.98, 0.02, info, transform=ax.transAxes, fontsize=7, color=CLR["muted"],
            va="bottom", ha="right", fontfamily=FONT_MONO,
            bbox=dict(boxstyle="round,pad=0.5", facecolor=CLR["card"], edgecolor=CLR["grid"], alpha=0.95, lw=0.5))
    ax.set_xlim(-1.55, 1.55); ax.set_ylim(-1.55, 1.55); ax.set_aspect("equal"); ax.axis("off")
    fig.tight_layout(pad=1.5)
    fig.savefig(f"{outdir}/fig7_cofailure.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig8_dotstrip(G, results, outdir="figures"):
    apply_style()
    stressed_r = [r for r in results if r["scenario"].short != "BASE"]
    top_nodes = sorted(G.nodes(),
                       key=lambda n: -max(r["scores"][n]["fragility"] for r in stressed_r))[:14]
    fig, ax = plt.subplots(figsize=(12, 6))
    for ni, n in enumerate(top_nodes):
        frags = [r["scores"][n]["fragility"] for r in stressed_r]
        ax.plot([min(frags), max(frags)], [ni, ni], color=CLR["muted"], lw=0.8, alpha=0.4, zorder=1)
        for r in stressed_r:
            f = r["scores"][n]["fragility"]
            ax.scatter(f, ni, s=60 + f*400, color=r["scenario"].color, alpha=0.7,
                       edgecolors="white", linewidths=0.6, zorder=5)
        ax.plot(np.mean(frags), ni, "|", color=CLR["text"], ms=12, mew=1.5, zorder=6)
    ax.set_yticks(range(len(top_nodes)))
    ax.set_yticklabels(top_nodes, fontsize=9.5, fontfamily=FONT_MONO)
    for i, n in enumerate(top_nodes):
        ax.get_yticklabels()[i].set_color(CAT_C[G.nodes[n]["category"]])
    ax.invert_yaxis(); ax.set_xlabel("Fragility score", fontsize=10, fontfamily=FONT_BODY)
    ax.grid(axis="x", alpha=0.4, lw=0.3)
    for r in stressed_r:
        ax.plot([], [], "o", color=r["scenario"].color, ms=7, label=r["scenario"].short)
    ax.plot([], [], "|", color=CLR["text"], ms=10, mew=1.5, label="Mean")
    leg = ax.legend(fontsize=7.5, loc="lower right", ncol=3, handletextpad=0.3, columnspacing=1)
    leg.get_frame().set_facecolor(CLR["card"]); leg.get_frame().set_edgecolor(CLR["grid"])
    _title(ax, "Fig. 8  Cross-Scenario Fragility Profile")
    _subtitle(ax, "Each dot = one scenario \u00b7 Size \u221d fragility \u00b7 Vertical bar = mean across scenarios")
    fig.tight_layout(pad=1.5)
    fig.savefig(f"{outdir}/fig8_dotstrip.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig9_threatmap(G, pos, results, threat, bn_rates, adv_freq, budget_results, outdir="figures"):
    apply_style()
    threat_max = max(threat.values())
    bs = results[-1]["scores"]
    fig = plt.figure(figsize=(20, 9))
    gs = gridspec.GridSpec(1, 2, figure=fig, wspace=0.02)
    ax1 = fig.add_subplot(gs[0]); ax2 = fig.add_subplot(gs[1])
    # Left: Day 0
    for u, v, d in G.edges(data=True):
        w = d["weight"]
        ax1.annotate("", xy=pos[v], xytext=pos[u],
            arrowprops=dict(arrowstyle="-|>", mutation_scale=10,
                color=(0.5, 0.5, 0.5, 0.08 + 0.30*w), lw=0.2 + 1.5*w, connectionstyle="arc3,rad=0.07"))
    for cat in ["person", "system", "process", "vendor"]:
        cn = [n for n in G.nodes() if G.nodes[n]["category"] == cat]
        ax1.scatter([pos[n][0] for n in cn], [pos[n][1] for n in cn],
                    s=300, c=CAT_C[cat], marker=CAT_M[cat], edgecolors="white", linewidths=0.8,
                    zorder=5, alpha=0.8)
    for n, (x, y) in pos.items():
        ax1.text(x, y - 0.09, n.replace("_", " "), fontsize=5.5, ha="center", va="top",
                 fontfamily=FONT_BODY, color=CLR["text"], fontweight="500")
    ax1.text(0.5, 1.04, "Day 0 \u2014 The org chart", transform=ax1.transAxes,
             fontsize=14, fontfamily=FONT_TITLE, fontweight="bold", color=CLR["muted"],
             ha="center", va="bottom")
    ax1.text(0.5, -0.01, "Before simulation", transform=ax1.transAxes,
             fontsize=9, ha="center", color=CLR["muted"], fontfamily=FONT_BODY, style="italic")
    ax1.set_xlim(-1.6, 1.6); ax1.set_ylim(-1.6, 1.6); ax1.set_aspect("equal"); ax1.axis("off")
    # Right: After 60k sims
    for u, v, d in G.edges(data=True):
        w = d["weight"]; tu = threat[u]/threat_max; tv = threat[v]/threat_max; te = max(tu, tv)
        if te > 0.35:
            c = cmap_threat(te); a = 0.15 + 0.65*te; lw = 0.6 + 3.5*te
        else:
            c = (0.75, 0.75, 0.75); a = 0.06 + 0.08*w; lw = 0.15 + 0.5*w
        ax2.annotate("", xy=pos[v], xytext=pos[u],
            arrowprops=dict(arrowstyle="-|>", mutation_scale=10,
                color=(*c[:3], a), lw=lw, connectionstyle="arc3,rad=0.07"))
    for n in G.nodes():
        x, y = pos[n]; t = threat[n] / threat_max; color = cmap_threat(t)
        sz = 0.028 + 0.065 * t
        if t > 0.45:
            for gr, ga in [(sz*2.5, 0.04), (sz*1.9, 0.07), (sz*1.45, 0.12)]:
                ax2.add_patch(plt.Circle((x, y), gr, color=color, alpha=ga, zorder=2))
        if bn_rates.get(n, 0) > 0.70:
            ax2.add_patch(plt.Circle((x, y), sz + 0.02, color="none", ec=CLR["danger"],
                          lw=2.5, zorder=4, alpha=0.85))
        if adv_freq.get(n, 0) >= 3:
            ax2.plot(x, y, "*", color="white", ms=sz*200, zorder=6, mec=color, mew=0.6)
        ax2.add_patch(plt.Circle((x, y), sz, color=color, ec="white", lw=1.0, zorder=5))
        ax2.text(x, y - sz - 0.028, n.replace("_", " "), fontsize=5.5, ha="center", va="top",
                 fontfamily=FONT_BODY, color=CLR["text"], fontweight="600")
        if t > 0.30:
            pf = bs[n]["p_fail"]
            ax2.text(x, y + sz + 0.028, f"{pf:.0%}", fontsize=8, ha="center", va="bottom",
                     color=color, fontweight="bold", fontfamily=FONT_MONO)
    ax2.text(0.5, 1.04, "After 60,000 simulations \u2014 The threat map", transform=ax2.transAxes,
             fontsize=14, fontfamily=FONT_TITLE, fontweight="bold", color=CLR["danger"],
             ha="center", va="bottom")
    ax2.text(0.5, -0.01,
             "Size + color = composite threat \u00b7 Ring = bottleneck >70% \u00b7 \u2605 = adversary target",
             transform=ax2.transAxes, fontsize=8, ha="center", color=CLR["muted"],
             fontfamily=FONT_BODY, style="italic")
    ax2.set_xlim(-1.6, 1.6); ax2.set_ylim(-1.6, 1.6); ax2.set_aspect("equal"); ax2.axis("off")
    # Colorbar
    cax = fig.add_axes([0.93, 0.15, 0.01, 0.55])
    sm = ScalarMappable(cmap=cmap_threat, norm=Normalize(0, threat_max)); sm.set_array([])
    cb = fig.colorbar(sm, cax=cax)
    cb.set_label("Composite threat", fontsize=9, fontfamily=FONT_BODY); cb.outline.set_linewidth(0.3)
    # Legend
    legend_els = [
        mpatches.Patch(facecolor="none", edgecolor=CLR["danger"], lw=2.5,
                       label="Bottleneck (>70% of failures)"),
        Line2D([0], [0], marker="*", color="w", markerfacecolor=CLR["accent"],
               markersize=12, label="Adversary primary target", lw=0),
    ]
    ax2.legend(handles=legend_els, loc="lower left", fontsize=8, borderpad=0.8,
               handletextpad=0.5).get_frame().set_facecolor(CLR["card"])
    fig.savefig(f"{outdir}/fig9_threatmap.png", dpi=300, bbox_inches="tight", facecolor=CLR["bg"])
    plt.close(fig)

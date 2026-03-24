"""
Generovanie grafov pre analyzu datasetu.

Vytvara PNG subory do reports/output/figures/.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "reports" / "output" / "figures"

sns.set_theme(style="whitegrid", context="paper", font_scale=1.05)
plt.rcParams["axes.titleweight"] = "bold"


def _ensure_dir():
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def altman_by_industry(ratios, top_n=10):
    """Boxplot Altman Z-skore podla odvetvia."""
    _ensure_dir()
    counts = ratios["Odvetvie"].value_counts()
    top = counts.head(top_n).index
    data = ratios[ratios["Odvetvie"].isin(top)].dropna(subset=["altman_z_own"])
    data = data[data["altman_z_own"].between(-10, 20)]

    order = data.groupby("Odvetvie")["altman_z_own"].median().sort_values().index

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(data=data, y="Odvetvie", x="altman_z_own", order=order, ax=ax,
                color="#4C72B0", fliersize=3)
    ax.axvline(1.81, color="red", linestyle="--", linewidth=1, label="zГіna distresu (Z<1.81)")
    ax.axvline(2.99, color="green", linestyle="--", linewidth=1, label="bezpeДЌnГЎ zГіna (Z>2.99)")
    ax.set_xlabel("Altman Z-skГіre")
    ax.set_ylabel("Odvetvie")
    ax.set_title(f"DistribГєcia Altman Z-skГіre podДѕa odvetvia (top {top_n} odvetvГ­)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    out = FIG_DIR / "01_altman_by_industry.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def industry_region_heatmap(df, top_n_industries=10):
    """Heatmapa poctu firiem podla odvetvia a kraja."""
    _ensure_dir()
    top_ind = df["Odvetvie"].value_counts().head(top_n_industries).index
    sub = df[df["Odvetvie"].isin(top_ind)]
    pivot = pd.crosstab(sub["Odvetvie"], sub["Kraj"])

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", cbar_kws={"label": "poДЌet firiem"}, ax=ax)
    ax.set_title(f"PoДЌet firiem podДѕa odvetvia a kraja (top {top_n_industries} odvetvГ­)")
    ax.set_xlabel("Kraj")
    ax.set_ylabel("Odvetvie")
    fig.tight_layout()
    out = FIG_DIR / "02_industry_region_heatmap.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def top_n_by_revenue(df, n=15):
    """Top N firiem podla celkovych trzeb."""
    _ensure_dir()
    revenue_col = "TrЕѕby (spolu)"
    sub = df[["Nazov", "Odvetvie", revenue_col]].dropna(subset=[revenue_col])
    sub = sub.nlargest(n, revenue_col)
    sub["revenue_mil_skk"] = sub[revenue_col] / 1_000_000

    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.barh(sub["Nazov"], sub["revenue_mil_skk"], color="#55A868")
    ax.set_xlabel("TrЕѕby (mil. SKK, rok 2008)")
    ax.set_ylabel("")
    ax.set_title(f"Top {n} firiem podДѕa celkovГЅch trЕѕieb (2008)")
    ax.invert_yaxis()
    for bar, val, ind in zip(bars, sub["revenue_mil_skk"], sub["Odvetvie"]):
        ax.text(val, bar.get_y() + bar.get_height() / 2,
                f"  {val:,.0f} ({ind})", va="center", fontsize=8)
    fig.tight_layout()
    out = FIG_DIR / "03_top_revenue.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def kar_status_distribution(df):
    """Rozdelenie firiem podla stavu KaR/likvidacie."""
    _ensure_dir()
    s = df["KaR, LikvidГЎcie"].fillna("bez evidencie").value_counts()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(s.index, s.values, color=["#4C72B0", "#C44E52", "#DD8452"][: len(s)])
    ax.set_title("Stav firiem v evidencii konkurzov a likvidГЎciГ­")
    ax.set_ylabel("PoДЌet firiem")
    for i, v in enumerate(s.values):
        ax.text(i, v + 1, str(v), ha="center", fontsize=10)
    fig.tight_layout()
    out = FIG_DIR / "04_kar_status.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def generate_all(df, ratios):
    return [
        altman_by_industry(ratios),
        industry_region_heatmap(df),
        top_n_by_revenue(df),
        kar_status_distribution(df),
    ]

if __name__ == "__main__":
    from src.load import load_clean_dataset
    from src.ratios import compute_ratios
    df = load_clean_dataset()
    ratios = compute_ratios(df)
    for p in generate_all(df, ratios):
        print(f"saved: {p}")

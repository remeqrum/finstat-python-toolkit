"""
Generovanie grafov pre analyzu datasetu.
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
    _ensure_dir()
    counts = ratios["Odvetvie"].value_counts()
    top = counts.head(top_n).index
    data = ratios[ratios["Odvetvie"].isin(top)].dropna(subset=["altman_z_own"])
    data = data[data["altman_z_own"].between(-10, 20)]
    order = data.groupby("Odvetvie")["altman_z_own"].median().sort_values().index
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(data=data, y="Odvetvie", x="altman_z_own", order=order, ax=ax, color="#4C72B0", fliersize=3)
    ax.axvline(1.81, color="red", linestyle="--", linewidth=1, label="zona distresu")
    ax.axvline(2.99, color="green", linestyle="--", linewidth=1, label="bezpecna zona")
    ax.set_xlabel("Altman Z-skore"); ax.set_ylabel("Odvetvie")
    ax.set_title(f"Distribucia Altman Z podla odvetvia (top {top_n})")
    ax.legend(loc="lower right"); fig.tight_layout()
    out = FIG_DIR / "01_altman_by_industry.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    return out

def industry_region_heatmap(df, top_n_industries=10):
    _ensure_dir()
    top_ind = df["Odvetvie"].value_counts().head(top_n_industries).index
    sub = df[df["Odvetvie"].isin(top_ind)]
    pivot = pd.crosstab(sub["Odvetvie"], sub["Kraj"])
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", cbar_kws={"label": "pocet firiem"}, ax=ax)
    ax.set_title("Pocet firiem podla odvetvia a kraja")
    fig.tight_layout()
    out = FIG_DIR / "02_industry_region_heatmap.png"
    fig.savefig(out, dpi=140); plt.close(fig)
    return out

if __name__ == "__main__":
    from src.load import load_clean_dataset
    from src.ratios import compute_ratios
    df = load_clean_dataset()
    ratios = compute_ratios(df)
    print(f"saved: {altman_by_industry(ratios)}")
    print(f"saved: {industry_region_heatmap(df)}")

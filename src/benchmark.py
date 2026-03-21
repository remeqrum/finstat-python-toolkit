"""
Odvetvove a regionalne agregaty pre benchmark analyzu.
"""

import pandas as pd

RATIO_COLS = (
    "liq_cash", "liq_quick", "liq_current",
    "dbt_total", "dbt_equity_ratio", "dbt_debt_equity",
    "prof_roa", "prof_roe", "prof_ros", "prof_ebitda_margin",
    "act_asset_turnover",
    "altman_z_own", "altman_z_finstat",
)


def _aggregate_by(ratios, group_col):
    """Median + kvartily per skupina."""
    cols = [c for c in RATIO_COLS if c in ratios.columns]
    g = ratios.groupby(group_col, dropna=True)

    agg = g[cols].median().add_suffix("_median")
    agg["company_count"] = g.size()
    for c in cols:
        agg[f"{c}_q25"] = g[c].quantile(0.25)
        agg[f"{c}_q75"] = g[c].quantile(0.75)

    return agg.sort_values("company_count", ascending=False)


def industry_aggregates(ratios):
    """Agregaty podla odvetvia."""
    return _aggregate_by(ratios, "Odvetvie")


def region_aggregates(ratios):
    """Agregaty podla kraja."""
    return _aggregate_by(ratios, "Kraj")


def compare_to_industry(ratios, ico):
    """
    Porovna firmu s medianom jej odvetvia.
    Vrati tabulku: firma vs median vs Q25/Q75.
    """
    ico = str(ico).strip()
    company_row = ratios.loc[ratios["Ico"] == ico]
    if company_row.empty:
        raise KeyError(f"Ico {ico!r} not found in ratios DataFrame.")

    company = company_row.iloc[0]
    industry = company["Odvetvie"]

    # vsetky firmy v rovnakom odvetvi okrem danej firmy
    peers = ratios[
        (ratios["Odvetvie"] == industry) & (ratios["Ico"] != ico)
    ]

    rows = []
    for col in RATIO_COLS:
        if col not in ratios.columns:
            continue
        company_val = company[col]
        if pd.isna(company_val):
            continue
        peer_vals = peers[col].dropna()
        if peer_vals.empty:
            continue
        median = peer_vals.median()
        q25 = peer_vals.quantile(0.25)
        q75 = peer_vals.quantile(0.75)
        if company_val < q25:
            position = "pod 1. kvartilom"
        elif company_val > q75:
            position = "nad 3. kvartilom"
        else:
            position = "v medzikvartilovom rozsahu"
        rows.append({
            "ukazovateДѕ":     col,
            "firma":          round(float(company_val), 4),
            "mediГЎn odvetvia": round(float(median), 4),
            "Q25":            round(float(q25), 4),
            "Q75":            round(float(q75), 4),
            "n_peers":        len(peer_vals),
            "pozГ­cia":        position,
        })

    out = pd.DataFrame(rows)
    out.attrs["ico"] = ico
    out.attrs["nazov"] = company["Nazov"]
    out.attrs["odvetvie"] = industry
    return out


if __name__ == "__main__":
    from src.load import load_clean_dataset
    from src.ratios import compute_ratios

    df = load_clean_dataset()
    ratios = compute_ratios(df)

    ind = industry_aggregates(ratios)
    print("=== Top 5 odvetvi ===")
    show = ["company_count", "liq_current_median", "dbt_total_median",
            "prof_roa_median", "altman_z_own_median"]
    print(ind[show].head(5).round(3).to_string())
    print()

    sample_ico = ratios["Ico"].iloc[0]
    cmp = compare_to_industry(ratios, sample_ico)
    print(f"=== Benchmark: {cmp.attrs['nazov']} (Ico {cmp.attrs['ico']}, "
          f"odvetvie: {cmp.attrs['odvetvie']}) ===")
    print(cmp.to_string(index=False))


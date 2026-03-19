"""
Odvetvove agregaty pre benchmark analyzu.
"""
import pandas as pd

RATIO_COLS = (
    "liq_cash", "liq_quick", "liq_current",
    "dbt_total", "dbt_equity_ratio", "dbt_debt_equity",
    "prof_roa", "prof_roe", "prof_ros", "prof_ebitda_margin",
    "act_asset_turnover", "altman_z_own", "altman_z_finstat",
)

def _aggregate_by(ratios, group_col):
    cols = [c for c in RATIO_COLS if c in ratios.columns]
    g = ratios.groupby(group_col, dropna=True)
    agg = g[cols].median().add_suffix("_median")
    agg["company_count"] = g.size()
    for c in cols:
        agg[f"{c}_q25"] = g[c].quantile(0.25)
        agg[f"{c}_q75"] = g[c].quantile(0.75)
    return agg.sort_values("company_count", ascending=False)

def industry_aggregates(ratios):
    return _aggregate_by(ratios, "Odvetvie")

def region_aggregates(ratios):
    return _aggregate_by(ratios, "Kraj")

if __name__ == "__main__":
    from src.load import load_clean_dataset
    from src.ratios import compute_ratios
    df = load_clean_dataset()
    ratios = compute_ratios(df)
    print(industry_aggregates(ratios).head(5).round(3).to_string())

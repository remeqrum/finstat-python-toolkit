"""
Vypocet financnych ukazovatelov z uctovnych zavierok.

Likvidita, zadlzenost, rentabilita, aktivita + Altman Z-skore.
"""

import numpy as np
import pandas as pd

# mapovanie skratenych nazvov na stlpce v datasete
COL = {
    "total_assets":      "Spolu majetok [002+030+061]",
    "current_assets":    "ObeЕѕnГЅ majetok [031+038+046+055]",
    "inventory":         "ZГЎsoby sГєДЌet [032 aЕѕ 037]",
    "short_receivables": "KrГЎtkodobГ© pohДѕadГЎvky sГєДЌet [047 aЕѕ 054]",
    "cash":              "FinanДЌnГ© ГєДЌty sГєДЌet [056 aЕѕ 060]",
    "equity":            "VlastnГ© imanie [068+073+080+084+087]",
    "liabilities":       "ZГЎvГ¤zky [089+094+106+117+118]",
    "short_liabilities": "KrГЎtkodobГ© zГЎvГ¤zky sГєДЌet [107 aЕѕ 116]",
    "bank_loans":        "BankovГ© Гєvery [119+120]",
    "retained":          "VГЅsledok hospodГЎrenia minulГЅch rokov [085+086]",
    "ebit":              "VГЅsledok hospodГЎrenia z hospodГЎrskej ДЌinnosti [11-12-17-18+19-20 -21+22-23+(-24)-(-25)]",
    "ebitda":            "EBITDA",
    "net_income":        "VГЅsledok hospodГЎrenia za ГєДЌtovnГ© obdobie po zdanenГ­ [001-(068+073+080 +084+088+121)]",
    "value_added":       "PridanГЎ hodnota [03+04-08]",
    "revenue_total":     "TrЕѕby (spolu)",
}

ALTMAN_FINSTAT = "KreditnГЅ model: Altmanovo Z-skГіre"
ALTMAN_FINSTAT_LABEL = "KreditnГЅ model: Altmanovo Z-skГіre - indikГЎcia"


def _safe_div(num, den):
    """Bezpecne delenie - nuly nahradi NaN."""
    den = den.replace(0, np.nan)
    return num / den


def _num(df, key):
    return pd.to_numeric(df[COL[key]], errors="coerce")


def compute_ratios(df):
    """Vypocita vsetky financne ukazovatele. Vrati dataframe s jednym riadkom na firmu."""

    total_assets    = _num(df, "total_assets")
    current_assets  = _num(df, "current_assets")
    cash            = _num(df, "cash")
    short_recv      = _num(df, "short_receivables")
    equity          = _num(df, "equity")
    liabilities     = _num(df, "liabilities")
    short_liab      = _num(df, "short_liabilities")
    retained        = _num(df, "retained")
    ebit            = _num(df, "ebit")
    ebitda          = _num(df, "ebitda")
    net_income      = _num(df, "net_income")
    revenue         = _num(df, "revenue_total")

    out = pd.DataFrame({
        "Ico":      df["Ico"].values,
        "Nazov":    df["Nazov"].values,
        "Odvetvie": df["Odvetvie"].values,
        "Kraj":     df["Kraj"].values,
    })

    # likvidita
    out["liq_cash"]    = _safe_div(cash, short_liab)
    out["liq_quick"]   = _safe_div(cash + short_recv, short_liab)
    out["liq_current"] = _safe_div(current_assets, short_liab)

    # zadlzenost
    out["dbt_total"]        = _safe_div(liabilities, total_assets)
    out["dbt_equity_ratio"] = _safe_div(equity, total_assets)
    out["dbt_debt_equity"]  = _safe_div(liabilities, equity)

    # rentabilita
    out["prof_roa"]           = _safe_div(net_income, total_assets)
    out["prof_roe"]           = _safe_div(net_income, equity)
    out["prof_ros"]           = _safe_div(net_income, revenue)
    out["prof_ebitda_margin"] = _safe_div(ebitda, revenue)

    # aktivita
    out["act_asset_turnover"] = _safe_div(revenue, total_assets)

    # Altman Z-skore (povodna formula 1968)
    x1 = _safe_div(current_assets - short_liab, total_assets)
    x2 = _safe_div(retained, total_assets)
    x3 = _safe_div(ebit, total_assets)
    x4 = _safe_div(equity, liabilities)
    x5 = _safe_div(revenue, total_assets)
    out["altman_z_own"]    = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

    # porovnanie s hodnotou z finstatu
    out["altman_z_finstat"] = pd.to_numeric(df[ALTMAN_FINSTAT], errors="coerce")
    out["altman_label"]     = df[ALTMAN_FINSTAT_LABEL].astype("string")

    # firma je v zone distresu ak Z < 1.81
    out["risk_altman"] = out["altman_z_own"] < 1.81

    return out


if __name__ == "__main__":
    from src.load import load_clean_dataset

    df = load_clean_dataset()
    r = compute_ratios(df)

    numeric = r.select_dtypes(include="number")
    summary = numeric.describe().T[["count", "mean", "50%", "min", "max"]].round(3)
    print(summary.to_string())
    print()
    print(f"Companies in distress zone (Altman Z < 1.81): "
          f"{r['risk_altman'].sum()} / {r['altman_z_own'].notna().sum()} "
          f"({r['risk_altman'].mean():.1%})")


"""
Vypocet financnych ukazovatelov.
Likvidita, zadlzenost, rentabilita, aktivita.
"""
import numpy as np
import pandas as pd

COL = {
    "total_assets":      "Spolu majetok [002+030+061]",
    "current_assets":    "ObeЕѕnГЅ majetok [031+038+046+055]",
    "cash":              "FinanДЌnГ© ГєДЌty sГєДЌet [056 aЕѕ 060]",
    "short_receivables": "KrГЎtkodobГ© pohДѕadГЎvky sГєДЌet [047 aЕѕ 054]",
    "equity":            "VlastnГ© imanie [068+073+080+084+087]",
    "liabilities":       "ZГЎvГ¤zky [089+094+106+117+118]",
    "short_liabilities": "KrГЎtkodobГ© zГЎvГ¤zky sГєДЌet [107 aЕѕ 116]",
    "ebitda":            "EBITDA",
    "net_income":        "VГЅsledok hospodГЎrenia za ГєДЌtovnГ© obdobie po zdanenГ­ [001-(068+073+080 +084+088+121)]",
    "revenue_total":     "TrЕѕby (spolu)",
}

def _safe_div(num, den):
    den = den.replace(0, np.nan)
    return num / den

def _num(df, key):
    return pd.to_numeric(df[COL[key]], errors="coerce")

def compute_ratios(df):
    total_assets = _num(df, "total_assets")
    current_assets = _num(df, "current_assets")
    cash = _num(df, "cash")
    short_recv = _num(df, "short_receivables")
    equity = _num(df, "equity")
    liabilities = _num(df, "liabilities")
    short_liab = _num(df, "short_liabilities")
    ebitda = _num(df, "ebitda")
    net_income = _num(df, "net_income")
    revenue = _num(df, "revenue_total")

    out = pd.DataFrame({
        "Ico": df["Ico"].values, "Nazov": df["Nazov"].values,
        "Odvetvie": df["Odvetvie"].values, "Kraj": df["Kraj"].values,
    })
    # likvidita
    out["liq_cash"] = _safe_div(cash, short_liab)
    out["liq_quick"] = _safe_div(cash + short_recv, short_liab)
    out["liq_current"] = _safe_div(current_assets, short_liab)
    # zadlzenost
    out["dbt_total"] = _safe_div(liabilities, total_assets)
    out["dbt_equity_ratio"] = _safe_div(equity, total_assets)
    out["dbt_debt_equity"] = _safe_div(liabilities, equity)
    # rentabilita
    out["prof_roa"] = _safe_div(net_income, total_assets)
    out["prof_roe"] = _safe_div(net_income, equity)
    out["prof_ros"] = _safe_div(net_income, revenue)
    out["prof_ebitda_margin"] = _safe_div(ebitda, revenue)
    # aktivita
    out["act_asset_turnover"] = _safe_div(revenue, total_assets)
    return out

if __name__ == "__main__":
    from src.load import load_clean_dataset
    df = load_clean_dataset()
    r = compute_ratios(df)
    print(r.select_dtypes(include="number").describe().round(3).to_string())

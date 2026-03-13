"""
Vypocet financnych ukazovatelov.
"""
import numpy as np
import pandas as pd

COL = {
    "total_assets":      "Spolu majetok [002+030+061]",
    "current_assets":    "ObeЕѕnГЅ majetok [031+038+046+055]",
    "cash":              "FinanДЌnГ© ГєДЌty sГєДЌet [056 aЕѕ 060]",
    "short_receivables": "KrГЎtkodobГ© pohДѕadГЎvky sГєДЌet [047 aЕѕ 054]",
    "short_liabilities": "KrГЎtkodobГ© zГЎvГ¤zky sГєДЌet [107 aЕѕ 116]",
}

def _safe_div(num, den):
    den = den.replace(0, np.nan)
    return num / den

def _num(df, key):
    return pd.to_numeric(df[COL[key]], errors="coerce")

def compute_ratios(df):
    cash = _num(df, "cash")
    short_recv = _num(df, "short_receivables")
    current_assets = _num(df, "current_assets")
    short_liab = _num(df, "short_liabilities")

    out = pd.DataFrame({
        "Ico": df["Ico"].values,
        "Nazov": df["Nazov"].values,
        "Odvetvie": df["Odvetvie"].values,
        "Kraj": df["Kraj"].values,
    })
    # likvidita
    out["liq_cash"] = _safe_div(cash, short_liab)
    out["liq_quick"] = _safe_div(cash + short_recv, short_liab)
    out["liq_current"] = _safe_div(current_assets, short_liab)
    return out

if __name__ == "__main__":
    from src.load import load_clean_dataset
    df = load_clean_dataset()
    r = compute_ratios(df)
    print(r.describe().round(3).to_string())

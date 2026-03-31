"""
Streamlit dashboard - interaktivny prehlad datasetu.

Spustenie: streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.benchmark import compare_to_industry, industry_aggregates
from src.load import load_clean_dataset
from src.ratios import compute_ratios

st.set_page_config(page_title="Benchmark dashboard SK SMEs", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def _data():
    df = load_clean_dataset()
    ratios = compute_ratios(df)
    return df, ratios


df, ratios = _data()

st.title("Benchmark slovenskГЅch firiem вЂ” automatizovanГЅ dashboard")
st.caption(
    "BakalГЎrska prГЎca, praktickГЎ ДЌasЕҐ В· zdroj: ГєДЌtovnГ© zГЎvierky 2008 (FinStat) В· "
    f"{len(df)} firiem v {df['Odvetvie'].nunique()} odvetviach"
)

# --- Sidebar: filtre ---
with st.sidebar:
    st.header("Filtre")
    industries = sorted(df["Odvetvie"].dropna().unique())
    industry = st.selectbox("Odvetvie", ["(vЕЎetky)"] + industries)
    regions = sorted(df["Kraj"].dropna().unique())
    region = st.selectbox("Kraj", ["(vЕЎetky)"] + regions)

    sub_df = df.copy()
    sub_ratios = ratios.copy()
    if industry != "(vЕЎetky)":
        sub_df = sub_df[sub_df["Odvetvie"] == industry]
        sub_ratios = sub_ratios[sub_ratios["Odvetvie"] == industry]
    if region != "(vЕЎetky)":
        sub_df = sub_df[sub_df["Kraj"] == region]
        sub_ratios = sub_ratios[sub_ratios["Kraj"] == region]

    st.metric("VybranГЅch firiem", len(sub_df))

# --- Taby ---
tab_overview, tab_industry, tab_company = st.tabs(
    ["PrehДѕad", "OdvetvovГ© mediГЎny", "Firma vs odvetvie"]
)

# === Tab 1: Prehlad ===
with tab_overview:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Firmy", len(sub_df))
    c2.metric("MediГЎn ROA", f"{sub_ratios['prof_roa'].median():.2%}"
              if sub_ratios["prof_roa"].notna().any() else "вЂ”")
    c3.metric("MediГЎn Altman Z", f"{sub_ratios['altman_z_own'].median():.2f}"
              if sub_ratios["altman_z_own"].notna().any() else "вЂ”")
    distress_count = int(sub_ratios["risk_altman"].sum())
    c4.metric("V zГіne distresu", distress_count)

    st.subheader("Top firmy podДѕa trЕѕieb")
    revenue_col = "TrЕѕby (spolu)"
    top = (sub_df[["Nazov", "Odvetvie", "Kraj", revenue_col]]
           .dropna(subset=[revenue_col])
           .nlargest(15, revenue_col)
           .reset_index(drop=True))
    top[revenue_col] = (top[revenue_col] / 1_000_000).round(1)
    top = top.rename(columns={revenue_col: "TrЕѕby (mil. SKK)"})
    st.dataframe(top, use_container_width=True)

    st.subheader("DistribГєcia ROA")
    roa = sub_ratios["prof_roa"].dropna()
    roa = roa[roa.between(-1, 1)]
    if not roa.empty:
        fig, ax = plt.subplots(figsize=(9, 3.5))
        sns.histplot(roa, bins=30, kde=True, color="#4C72B0", ax=ax)
        ax.axvline(0, color="black", lw=0.7)
        ax.set_xlabel("ROA"); ax.set_ylabel("PoДЌet firiem")
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Pre vybranГЅ filter nie sГє dostupnГ© Гєdaje o ROA.")

# === Tab 2: Odvetvove mediany ===
with tab_industry:
    st.subheader("MediГЎn ukazovateДѕov podДѕa odvetvia")
    ind = industry_aggregates(ratios)
    show_cols = [
        "company_count",
        "liq_current_median", "dbt_total_median", "prof_roa_median",
        "prof_ebitda_margin_median", "altman_z_own_median",
    ]
    pretty = ind[show_cols].rename(columns={
        "company_count":             "PoДЌet firiem",
        "liq_current_median":        "Likvidita 3. st.",
        "dbt_total_median":          "Celk. zadlЕѕenosЕҐ",
        "prof_roa_median":           "ROA",
        "prof_ebitda_margin_median": "EBITDA marЕѕa",
        "altman_z_own_median":       "Altman Z",
    }).round(3)
    st.dataframe(pretty, use_container_width=True)



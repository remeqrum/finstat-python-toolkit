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

st.title("Benchmark slovenských firiem — automatizovaný dashboard")
st.caption(
    "Bakalárska práca, praktická časť · zdroj: účtovné závierky 2008 (FinStat) · "
    f"{len(df)} firiem v {df['Odvetvie'].nunique()} odvetviach"
)

# --- Sidebar: filtre ---
with st.sidebar:
    st.header("Filtre")
    industries = sorted(df["Odvetvie"].dropna().unique())
    industry = st.selectbox("Odvetvie", ["(všetky)"] + industries)
    regions = sorted(df["Kraj"].dropna().unique())
    region = st.selectbox("Kraj", ["(všetky)"] + regions)

    sub_df = df.copy()
    sub_ratios = ratios.copy()
    if industry != "(všetky)":
        sub_df = sub_df[sub_df["Odvetvie"] == industry]
        sub_ratios = sub_ratios[sub_ratios["Odvetvie"] == industry]
    if region != "(všetky)":
        sub_df = sub_df[sub_df["Kraj"] == region]
        sub_ratios = sub_ratios[sub_ratios["Kraj"] == region]

    st.metric("Vybraných firiem", len(sub_df))

# --- Taby ---
tab_overview, tab_industry, tab_company = st.tabs(
    ["Prehľad", "Odvetvové mediány", "Firma vs odvetvie"]
)

# === Tab 1: Prehlad ===
with tab_overview:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Firmy", len(sub_df))
    c2.metric("Medián ROA", f"{sub_ratios['prof_roa'].median():.2%}"
              if sub_ratios["prof_roa"].notna().any() else "—")
    c3.metric("Medián Altman Z", f"{sub_ratios['altman_z_own'].median():.2f}"
              if sub_ratios["altman_z_own"].notna().any() else "—")
    distress_count = int(sub_ratios["risk_altman"].sum())
    c4.metric("Altman distres", distress_count)
    taffler_count = int(sub_ratios["risk_taffler"].sum())
    c5.metric("Taffler distres", taffler_count)

    st.subheader("Top firmy podľa tržieb")
    revenue_col = "Tržby (spolu)"
    top = (sub_df[["Nazov", "Odvetvie", "Kraj", revenue_col]]
           .dropna(subset=[revenue_col])
           .nlargest(15, revenue_col)
           .reset_index(drop=True))
    top[revenue_col] = (top[revenue_col] / 1_000_000).round(1)
    top = top.rename(columns={revenue_col: "Tržby (mil. SKK)"})
    st.dataframe(top, use_container_width=True)

    st.subheader("Distribúcia ROA")
    roa = sub_ratios["prof_roa"].dropna()
    roa = roa[roa.between(-1, 1)]
    if not roa.empty:
        fig, ax = plt.subplots(figsize=(9, 3.5))
        sns.histplot(roa, bins=30, kde=True, color="#4C72B0", ax=ax)
        ax.axvline(0, color="black", lw=0.7)
        ax.set_xlabel("ROA"); ax.set_ylabel("Počet firiem")
        st.pyplot(fig, clear_figure=True)
    else:
        st.info("Pre vybraný filter nie sú dostupné údaje o ROA.")

# === Tab 2: Odvetvove mediany ===
with tab_industry:
    st.subheader("Medián ukazovateľov podľa odvetvia")
    ind = industry_aggregates(ratios)
    show_cols = [
        "company_count",
        "liq_current_median", "dbt_total_median", "prof_roa_median",
        "prof_ebitda_margin_median", "altman_z_own_median",
    ]
    pretty = ind[show_cols].rename(columns={
        "company_count":             "Počet firiem",
        "liq_current_median":        "Likvidita 3. st.",
        "dbt_total_median":          "Celk. zadlženosť",
        "prof_roa_median":           "ROA",
        "prof_ebitda_margin_median": "EBITDA marža",
        "altman_z_own_median":       "Altman Z",
    }).round(3)
    st.dataframe(pretty, use_container_width=True)

# === Tab 3: Porovnanie firmy ===
with tab_company:
    st.subheader("Porovnanie konkrétnej firmy s odvetvím")

    eligible = sub_df[["Ico", "Nazov", "Odvetvie"]].dropna().sort_values("Nazov")
    if eligible.empty:
        st.info("Vo vybranom filtri nie sú firmy.")
    else:
        labels = eligible["Nazov"] + " (IČO " + eligible["Ico"] + ")"
        choice = st.selectbox("Firma", labels.tolist())
        ico = choice.split("IČO ")[-1].rstrip(")")

        try:
            cmp = compare_to_industry(ratios, ico)
        except KeyError as e:
            st.error(str(e))
        else:
            st.markdown(
                f"**{cmp.attrs['nazov']}** &nbsp;·&nbsp; "
                f"odvetvie: {cmp.attrs['odvetvie']} &nbsp;·&nbsp; IČO {ico}"
            )
            st.dataframe(cmp, use_container_width=True, hide_index=True)

            if not cmp.empty:
                fig, ax = plt.subplots(figsize=(9, 4))
                x = range(len(cmp))
                ax.barh([i - 0.2 for i in x], cmp["firma"], height=0.4, label="firma", color="#4C72B0")
                ax.barh([i + 0.2 for i in x], cmp["medián odvetvia"], height=0.4,
                        label="medián odvetvia", color="#DD8452")
                ax.set_yticks(list(x))
                ax.set_yticklabels(cmp["ukazovateľ"])
                ax.invert_yaxis()
                ax.legend()
                st.pyplot(fig, clear_figure=True)

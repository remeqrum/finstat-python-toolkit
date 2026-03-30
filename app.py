"""
Streamlit dashboard - zakladny prehlad.
Spustenie: streamlit run app.py
"""
import streamlit as st
import pandas as pd
from src.load import load_clean_dataset
from src.ratios import compute_ratios

st.set_page_config(page_title="Benchmark dashboard", layout="wide")

@st.cache_data
def _data():
    df = load_clean_dataset()
    ratios = compute_ratios(df)
    return df, ratios

df, ratios = _data()
st.title("Benchmark slovenskych firiem")
st.caption(f"Zdroj: uctovne zavierky 2008, {len(df)} firiem")

st.subheader("Top firmy podla trzeb")
revenue_col = "Trzby (spolu)"
if revenue_col not in df.columns:
    revenue_col = [c for c in df.columns if "TrЕѕby" in c][0]
top = df[["Nazov", "Odvetvie", revenue_col]].dropna(subset=[revenue_col]).nlargest(15, revenue_col)
st.dataframe(top)

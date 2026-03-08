"""
Modul na nacitanie a cistenie uctovnych zavierok z CSV suborov (finstat.sk).
"""

import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

FULL_FORM_CSV = RAW / "dataset_uctovnych_vykazov_2008.csv"
BRUTTO_CSV = RAW / "dataset_uctovnych_vykazov_aktiva_brutto_2008.csv"

DATE_COLS = (
    "Obdobie od", "Obdobie do",
    "PredchГЎdzajГєce obdobie od", "PredchГЎdzajГєce obdobie do",
    "DГЎtum vzniku", "DГЎtum zГЎniku",
    "DГЎtum zverejnenia ГєДЌtovnej zГЎvierky",
)

EXCEL_PREFIX_COLS = ("DIC", "ICDPH")
EXCEL_PREFIX_RE = re.compile(r'^="(.*)\"$')


def _strip_excel_prefix(value):
    if not isinstance(value, str):
        return value
    match = EXCEL_PREFIX_RE.match(value)
    return match.group(1) if match else value


def _clean_metadata(df):
    df = df.copy()
    for col in EXCEL_PREFIX_COLS:
        if col in df.columns:
            df[col] = df[col].map(_strip_excel_prefix)
    for col in DATE_COLS:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            df[col] = parsed.where(parsed.dt.year > 1900)
    return df


def load_full_form(path=FULL_FORM_CSV):
    df = pd.read_csv(
        path, sep=";", encoding="utf-8", skiprows=[1],
        dtype={"Ico": str}, low_memory=False,
    )
    return _clean_metadata(df)


def load_brutto_form(path=BRUTTO_CSV):
    df = pd.read_csv(
        path, sep=";", encoding="utf-8",
        dtype={"Ico": str}, low_memory=False,
    )
    return _clean_metadata(df)


def merge_datasets(full, brutto):
    """Spoji oba datasety podla ICO."""
    brutto_unique = brutto.drop_duplicates(subset="Ico", keep="first")
    keep_cols = [
        c for c in brutto_unique.columns
        if c == "Ico" or c.startswith(("AktivaBrutto-", "AktivaCorr-"))
    ]
    return full.merge(
        brutto_unique[keep_cols], on="Ico", how="left",
        validate="many_to_one",
    )


if __name__ == "__main__":
    full = load_full_form()
    brutto = load_brutto_form()
    df = merge_datasets(full, brutto)
    print(f"merged shape={df.shape}, unique_ico={df['Ico'].nunique()}")

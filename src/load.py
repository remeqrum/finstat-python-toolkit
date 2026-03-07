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

# stlpce s datumami ktore treba parsovat
DATE_COLS = (
    "Obdobie od", "Obdobie do",
    "PredchГЎdzajГєce obdobie od", "PredchГЎdzajГєce obdobie do",
    "DГЎtum vzniku", "DГЎtum zГЎniku",
    "DГЎtum zverejnenia ГєДЌtovnej zГЎvierky",
)

# excel niekedy exportuje DIC ako ="12345"
EXCEL_PREFIX_COLS = ("DIC", "ICDPH")
EXCEL_PREFIX_RE = re.compile(r'^="(.*)\"$')


def _strip_excel_prefix(value):
    if not isinstance(value, str):
        return value
    match = EXCEL_PREFIX_RE.match(value)
    return match.group(1) if match else value


def _clean_metadata(df):
    """Ocisti metadatove stlpce."""
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
    """Nacita hlavny CSV subor s uctovnymi zavierkami."""
    df = pd.read_csv(
        path, sep=";", encoding="utf-8", skiprows=[1],
        dtype={"Ico": str}, low_memory=False,
    )
    return _clean_metadata(df)


def load_brutto_form(path=BRUTTO_CSV):
    """Nacita CSV s rozclenenym aktiv brutto/korekcia/netto."""
    df = pd.read_csv(
        path, sep=";", encoding="utf-8",
        dtype={"Ico": str}, low_memory=False,
    )
    return _clean_metadata(df)


if __name__ == "__main__":
    df = load_full_form()
    print(f"full: shape={df.shape}")
    # print(df.dtypes)

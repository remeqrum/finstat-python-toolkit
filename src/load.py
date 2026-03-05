"""
Modul na nacitanie CSV suborov z finstat.sk.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

FULL_FORM_CSV = RAW / "dataset_uctovnych_vykazov_2008.csv"
BRUTTO_CSV = RAW / "dataset_uctovnych_vykazov_aktiva_brutto_2008.csv"


def load_full_form(path=FULL_FORM_CSV):
    """Nacita hlavny CSV subor s uctovnymi zavierkami."""
    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8",
        skiprows=[1],
        dtype={"Ico": str},
        low_memory=False,
    )
    return df


def load_brutto_form(path=BRUTTO_CSV):
    """Nacita CSV s rozclenenym aktiv brutto/korekcia/netto."""
    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8",
        dtype={"Ico": str},
        low_memory=False,
    )
    return df


if __name__ == "__main__":
    df = load_full_form()
    print(f"full: shape={df.shape}")
    br = load_brutto_form()
    print(f"brutto: shape={br.shape}")

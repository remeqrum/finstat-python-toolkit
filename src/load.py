"""
Modul na nacitanie CSV suborov z finstat.sk.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

FULL_FORM_CSV = RAW / "dataset_uctovnych_vykazov_2008.csv"


def load_full_form(path=FULL_FORM_CSV):
    """Nacita hlavny CSV subor."""
    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8",
        skiprows=[1],
        dtype={"Ico": str},
        low_memory=False,
    )
    return df


if __name__ == "__main__":
    df = load_full_form()
    print(f"shape={df.shape}")
    print(df.head())

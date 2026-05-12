"""
Modul na nacitanie a cistenie uctovnych zavierok z CSV suborov (finstat.sk).
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

FULL_FORM_CSV = RAW / "dataset_uctovnych_vykazov_2008.csv"
BRUTTO_CSV = RAW / "dataset_uctovnych_vykazov_aktiva_brutto_2008.csv"

# stlpce s datumami ktore treba parsovat
DATE_COLS = (
    "Obdobie od",
    "Obdobie do",
    "Predchádzajúce obdobie od",
    "Predchádzajúce obdobie do",
    "Dátum vzniku",
    "Dátum zániku",
    "Dátum zverejnenia účtovnej závierky",
)

# excel niekedy exportuje DIC ako ="12345" - treba odstranit
EXCEL_PREFIX_COLS = ("DIC", "ICDPH")
EXCEL_PREFIX_RE = re.compile(r'^="(.*)\"$')


def _strip_excel_prefix(value):
    """Odstrani excel prefix ='...' ak existuje."""
    if not isinstance(value, str):
        return value
    match = EXCEL_PREFIX_RE.match(value)
    return match.group(1) if match else value


def _clean_metadata(df):
    """Ocisti metadatove stlpce - excel prefixy a datumy."""
    df = df.copy()

    for col in EXCEL_PREFIX_COLS:
        if col in df.columns:
            df[col] = df[col].map(_strip_excel_prefix)

    # 0001-01-01 su placeholder hodnoty z finstatu, nahradzujeme NaT
    for col in DATE_COLS:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            df[col] = parsed.where(parsed.dt.year > 1900)

    return df


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
    return _clean_metadata(df)


def load_brutto_form(path=BRUTTO_CSV):
    """Nacita CSV s rozclenenym aktiv brutto/korekcia/netto."""
    df = pd.read_csv(
        path,
        sep=";",
        encoding="utf-8",
        dtype={"Ico": str},
        low_memory=False,
    )
    return _clean_metadata(df)


def merge_datasets(full, brutto):
    """Spoji oba datasety podla ICO."""
    # brutto dataset moze mat duplicity pre to iste ICO - ponechavame prvy zaznam
    brutto_unique = brutto.drop_duplicates(subset="Ico", keep="first")
    keep_cols = [
        c for c in brutto_unique.columns
        if c == "Ico" or c.startswith(("AktivaBrutto-", "AktivaCorr-"))
    ]
    return full.merge(
        brutto_unique[keep_cols],
        on="Ico",
        how="left",
        validate="many_to_one",
    )


def load_clean_dataset():
    """Nacita, ocisti a spoji oba datasety. Hlavna funkcia modulu."""
    full = load_full_form()
    brutto = load_brutto_form()
    df = merge_datasets(full, brutto)
    
    # Zakladna validacia dat:
    # Pre vypocet vsetkych financnych ukazovatelov potrebujeme mat Aktiva spolu > 0.
    # Zaporne alebo nulove aktiva su uctovny nezmysel pre nase ucely.
    povodny_pocet = len(df)
    
    col_assets = "Spolu majetok [002+030+061]"
    if col_assets in df.columns:
        valid_assets = pd.to_numeric(df[col_assets], errors="coerce") > 0
        df = df[valid_assets].copy()
        
    odstranene = povodny_pocet - len(df)
    if odstranene > 0:
        print(f"[Validacia] Odstranenych {odstranene} firiem kvoli neplatnym (<=0) aktivam.")
        
    return df


def save_processed(df, name="dataset_clean"):
    """Ulozi dataframe do parquet suboru."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    out = PROCESSED / f"{name}.parquet"
    df.to_parquet(out, index=False)
    return out


if __name__ == "__main__":
    df = load_clean_dataset()
    out = save_processed(df)
    print(
        f"shape={df.shape}  "
        f"unique_ico={df['Ico'].nunique()}  "
        f"odvetvi={df['Odvetvie'].nunique()}  "
        f"-> {out}"
    )


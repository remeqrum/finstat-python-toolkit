# FinStat Python Toolkit

Automatizacia spracovania uctovnych zavierok slovenskych podnikov.

Praktická časť bakalárskej práce - spracovanie dat z portalu finstat.sk, 
vypocet financnych ukazovatelov a generovanie reportov.

## Ako spustit

### Instalacia

```
pip install -r requirements.txt
```

Alebo dvojklik na `install.bat`.

### Spustenie pipeline

```
python -m src.load
python -m src.ratios
python -m src.visualize
```

Alebo `run_pipeline.bat`.

### Dashboard

```
streamlit run app.py
```

Otvori sa na http://localhost:8501.

### Report pre firmu

```
python -m src.report --ico 31321828
```

## Struktura projektu

```
src/
  load.py         - nacitanie a cistenie CSV
  ratios.py       - financne ukazovatele + Altman Z
  benchmark.py    - odvetvove agregaty
  visualize.py    - grafy (PNG)
  report.py       - Excel + HTML reporty
app.py            - Streamlit dashboard
data/raw/         - vstupne CSV subory
reports/output/   - vygenerovane vystupy
```

## Zname problemy

- Dataset je z roku 2008, hodnoty su v SKK (nie EUR)
- Pri zmene roku treba upravit nazvy suborov v `src/load.py`
- Ak streamlit nefunguje, skuste `pip install streamlit` osobitne

## Zdroj dat

finstat.sk - uctovne zavierky 2008

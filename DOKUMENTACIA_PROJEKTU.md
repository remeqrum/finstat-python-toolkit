# Dokumentacia projektu

Praktická časť bakalárskej práce - automatizácia spracovania účtovných závierok.

## Co projekt robi

Pipeline na spracovanie CSV suborov z finstat.sk:
1. Nacita a ocisti data (src/load.py)
2. Vypocita 12 financnych ukazovatelov (src/ratios.py)
3. Porovna firmy s odvetvovym medianom (src/benchmark.py)
4. Vygeneruje grafy (src/visualize.py)
5. Vytvori Excel a HTML reporty (src/report.py)
6. Interaktivny dashboard (app.py)

## Pouzite kniznice

| Kniznica | Na co |
| --- | --- |
| pandas | spracovanie tabulkovych dat |
| numpy | numericke vypocty |
| matplotlib + seaborn | grafy |
| openpyxl | Excel reporty |
| jinja2 | HTML sablony |
| streamlit | webovy dashboard |

## Vstupne data

Dva CSV subory z finstat.sk (rok 2008, 246 firiem):
- `dataset_uctovnych_vykazov_2008.csv` - hlavny subor
- `dataset_uctovnych_vykazov_aktiva_brutto_2008.csv` - aktiva brutto

Hodnoty su v SKK (euro sa zaviedlo az 1.1.2009).

## Spustenie

Pozri README.md

## Vztah ku kapitolam prace

| Cast textu | Subor v projekte |
| --- | --- |
| 4.3.1 ETL modul | src/load.py |
| 4.3.2 Financne ukazovatele | src/ratios.py |
| 4.3.3 Validacia Altman Z | src/ratios.py |
| 4.3.4 Odvetvove agregaty | src/benchmark.py |
| 4.3.5 Vizualizacia | src/visualize.py |
| 4.3.6 Generator reportov | src/report.py |
| 4.3.7 Dashboard | app.py |
| 4.4 Casomierove porovnanie | notebooks/ |

## Obmedzenia

- Manualne casy v tabulke 18 su odhady, nie merania
- Dataset z roku 2008, maly pocet firiem (246)
- Ziadne strojove ucenie, vsetko je deterministicke

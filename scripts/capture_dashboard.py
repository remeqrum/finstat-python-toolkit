"""
Screenshot script pre streamlit dashboard.
Potrebuje beziacu instanciu na localhost:8501.

Pouzitie:
    python scripts/capture_dashboard.py
    python scripts/capture_dashboard.py --company "Mincovna"
    python scripts/capture_dashboard.py --url http://localhost:8502 --output reports/screens
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "reports" / "output" / "figures"
DEFAULT_URL = "http://localhost:8501"


def main():
    parser = argparse.ArgumentParser(description="Zachytenie screenshotov dashboardu.")
    parser.add_argument("--company", default="TESCO",
                        help="Cast nazvu firmy ktoru hladame v dashboarde (default: TESCO)")
    parser.add_argument("--url", default=DEFAULT_URL,
                        help=f"URL streamlit dashboardu (default: {DEFAULT_URL})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT,
                        help="Adresar pre vystupne PNG subory")
    parser.add_argument("--headed", action="store_true",
                        help="Spustit prehliadac v viditelnom okne (pre debug)")
    args = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Chyba: kniznica 'playwright' nie je nainstalovana.")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not args.headed)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()

        page.goto(args.url, wait_until="networkidle", timeout=60000)
        page.wait_for_selector("h1", timeout=30000)
        page.wait_for_timeout(2500)

        # screenshot prehladu
        out_overview = args.output / "streamlit_01_overview.png"
        page.screenshot(path=str(out_overview), full_page=True)
        print(f"Uložené: {out_overview}")

        # tab odvetvove mediany
        page.get_by_role("tab", name="Odvetvové mediány").click()
        page.wait_for_timeout(2000)
        out_industry = args.output / "streamlit_02_industry_medians.png"
        page.screenshot(path=str(out_industry), full_page=True)
        print(f"Uložené: {out_industry}")

        # tab porovnanie firmy - vyberieme zadanu firmu
        page.get_by_role("tab", name="Firma vs odvetvie").click()
        page.wait_for_timeout(2000)
        company_box = page.locator('div[data-baseweb="select"]').last
        company_box.click()
        page.wait_for_timeout(500)
        page.keyboard.type(args.company)
        page.wait_for_timeout(800)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        out_company = args.output / "streamlit_03_company_benchmark.png"
        page.screenshot(path=str(out_company), full_page=True)
        print(f"Uložené: {out_company}")

        browser.close()


if __name__ == "__main__":
    main()

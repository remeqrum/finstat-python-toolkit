"""
Screenshot script pre streamlit dashboard.
Potrebuje beziacu instanciu na localhost:8501.
"""

from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports" / "output" / "figures"
URL = "http://localhost:8501"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000})
        page = context.new_page()

        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_selector("h1", timeout=30000)
        page.wait_for_timeout(2500)

        # screenshot prehladu
        page.screenshot(path=str(OUT / "streamlit_01_overview.png"), full_page=True)
        print(f"saved: {OUT / 'streamlit_01_overview.png'}")

        # tab odvetvove mediany
        page.get_by_role("tab", name="Odvetvové mediány").click()
        page.wait_for_timeout(2000)
        page.screenshot(path=str(OUT / "streamlit_02_industry_medians.png"), full_page=True)
        print(f"saved: {OUT / 'streamlit_02_industry_medians.png'}")

        # tab porovnanie firmy - vyberieme TESCO
        page.get_by_role("tab", name="Firma vs odvetvie").click()
        page.wait_for_timeout(2000)
        company_box = page.locator('div[data-baseweb="select"]').last
        company_box.click()
        page.wait_for_timeout(500)
        page.keyboard.type("TESCO")
        page.wait_for_timeout(800)
        page.keyboard.press("Enter")
        page.wait_for_timeout(3000)
        page.screenshot(path=str(OUT / "streamlit_03_company_benchmark.png"), full_page=True)
        print(f"saved: {OUT / 'streamlit_03_company_benchmark.png'}")

        browser.close()


if __name__ == "__main__":
    main()

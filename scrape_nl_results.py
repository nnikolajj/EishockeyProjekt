"""
Scrapt alle Resultate der National League 2025/26 von Flashscore -> CSV
Spalten: Heimmannschaft, Auswärtsmannschaft, Resultat

Setup (einmalig):
    pip install playwright
    playwright install chromium

Ausführen:
    python scrape_nl_results.py
"""
import csv
from playwright.sync_api import sync_playwright

URL = "https://www.flashscore.com/hockey/switzerland/national-league-2025-2026/results/"
OUT = "nl_2025_26_results.csv"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="en-US")
        page.goto(URL, wait_until="domcontentloaded")

        # Cookie-Banner wegklicken (falls vorhanden)
        try:
            page.click("#onetrust-reject-all-handler", timeout=5000)
        except Exception:
            pass

        page.wait_for_selector("div.event__match", timeout=20000)

        # "Show more matches" so lange klicken, bis nichts mehr nachlädt
        while True:
            btn = page.query_selector("a.event__more")
            if not btn:
                break
            before = len(page.query_selector_all("div.event__match"))
            btn.scroll_into_view_if_needed()
            btn.click()
            try:
                page.wait_for_function(
                    f"document.querySelectorAll('div.event__match').length > {before}",
                    timeout=8000,
                )
            except Exception:
                break

        rows = page.evaluate(
            """() => [...document.querySelectorAll('div.event__match')].map(m => {
                const t = s => (m.querySelector(s)?.textContent || '').trim();
                return [
                    t('.event__homeParticipant'),
                    t('.event__awayParticipant'),
                    t('.event__score--home') + ':' + t('.event__score--away'),
                ];
            })"""
        )
        browser.close()

    rows = [r for r in rows if r[0] and r[1] and r[2] != ":"]

    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Heimmannschaft", "Auswärtsmannschaft", "Resultat"])
        w.writerows(rows)

    print(f"{len(rows)} Spiele -> {OUT}")


if __name__ == "__main__":
    main()
"""
Scrapt alle Resultate der National League 2025/26 von Flashscore -> CSV
Spalten: Heimmannschaft, Auswärtsmannschaft, Heim Score, Auswärts Score
 
Setup (einmalig):
    pip install playwright
    playwright install chromium
 
Ausführen:
    python scrape_nl_results.py
"""
import csv
import re
from playwright.sync_api import sync_playwright
 
URL = "https://www.flashscore.com/hockey/switzerland/national-league-2025-2026/results/"
OUT = "nl_2025_26_results.csv"
 
 
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="en-US")
        page.goto(URL, wait_until="domcontentloaded")
 
        # Cookie-Banner wegklicken (falls vorhanden)
        try:
            page.click("#onetrust-reject-all-handler", timeout=5000)
        except Exception:
            pass
 
        page.wait_for_selector("div.event__match", timeout=20000)
 
        # "Show more matches" so lange klicken, bis nichts mehr nachlädt
        while True:
            btn = page.query_selector("a.event__more")
            if not btn:
                break
            before = len(page.query_selector_all("div.event__match"))
            btn.scroll_into_view_if_needed()
            btn.click()
            try:
                page.wait_for_function(
                    f"document.querySelectorAll('div.event__match').length > {before}",
                    timeout=8000,
                )
            except Exception:
                break
 
        rows = page.evaluate(
            """() => [...document.querySelectorAll('div.event__match')].map(m => {
                const t = s => (m.querySelector(s)?.textContent || '').trim();
                return [
                    t('.event__homeParticipant'),
                    t('.event__awayParticipant'),
                    t('.event__score--home'),
                    t('.event__score--away'),
                ];
            })"""
        )
        browser.close()
 
    def clean(text):
        text = re.sub(r":Advancing to next round", "", text, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", text).strip()
 
    rows = [[clean(h), clean(a), sh, sa] for h, a, sh, sa in rows]
    rows = [r for r in rows if r[0] and r[1] and r[2] != "" and r[3] != ""]
 
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Heimmannschaft", "Auswärtsmannschaft", "Heim Score", "Auswärts Score"])
        w.writerows(rows)
 
    print(f"{len(rows)} Spiele -> {OUT}")
 
 
if __name__ == "__main__":
    main()
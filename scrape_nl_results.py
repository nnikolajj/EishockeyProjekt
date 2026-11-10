import csv
import re
from playwright.sync_api import sync_playwright

URLS = {
    "2025_26": "https://www.flashscore.com/hockey/switzerland/national-league-2025-2026/results/",
    "2024_25": "https://www.flashscore.com/hockey/switzerland/national-league-2024-2025/results/",
    "2023_24": "https://www.flashscore.com/hockey/switzerland/national-league-2023-2024/results/",
    "2022_23": "https://www.flashscore.com/hockey/switzerland/national-league-2022-2023/results/",
    "2021_22": "https://www.flashscore.com/hockey/switzerland/national-league-2021-2022/results/",
    "2020_21": "https://www.flashscore.com/hockey/switzerland/national-league-2020-2021/results/",
    "2019_20": "https://www.flashscore.com/hockey/switzerland/national-league-2019-2020/results/",
}

def clean(text):
    text = re.sub(r":?Advancing to next round: .*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Winner:.*$", "", text)   # "WinterthurWinner: Winterthur" -> "Winterthur"
    return re.sub(r"\s+", " ", text).strip()


def get_data(page, url):
    page.goto(url, wait_until="domcontentloaded")

    try:
        page.click("#onetrust-reject-all-handler", timeout=5000)
    except Exception:
        pass

    page.wait_for_selector("div.event__match", timeout=20000)

    while True:
        btn = page.get_by_role("button", name="Show more matches")
        if btn.count() == 0:
            break
        before = page.locator("div.event__match").count()
        btn.click()
        try:
            page.wait_for_function(
                f"document.querySelectorAll('div.event__match').length > {before}",
                timeout=8000,
            )
        except Exception:
            break

    return page.evaluate(
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


def save_csv(season, rows):
    filename = f"./csv_data/nl_{season}_results.csv"
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Heimmannschaft", "Auswärtsmannschaft", "Heim Score", "Auswärts Score"])
        w.writerows(rows)
    print(f"{season}: {len(rows)} Spiele -> {filename}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="en-US")

        for season, url in URLS.items():
            raw = get_data(page, url)
            rows = [
                [clean(h), clean(a), sh, sa]
                for h, a, sh, sa in raw
                if clean(h) and clean(a) and sh != "" and sa != ""
            ]
            save_csv(season, rows)

        browser.close()


if __name__ == "__main__":
    main()
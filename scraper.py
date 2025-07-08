
import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError

async def get_champion_stats(username: str, tag: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(locale='en-US')
        try:
            # Construct the lolchess.gg URL dynamically
            profile_base_url = f"https://lolchess.gg/profile/na/{username}-{tag}/set14/statistics?staticType=champions"
            await page.goto(profile_base_url, wait_until="domcontentloaded", timeout=120000)

            try:
                # Click the cookie consent button if it exists
                await page.click("button:has-text('AGREE')", timeout=5000)
            except TimeoutError:
                print("Cookie consent button not found, continuing...")
                pass

            # Click the update button
            try:
                await page.click("button:has-text('Update')", timeout=10000)
                print("Clicked update button.")
                await page.wait_for_timeout(2000) # Wait for update to process
            except TimeoutError:
                print("Update button not found or clickable, continuing...")
                pass

            # Take a screenshot before clicking the statistics tab
            await page.screenshot(path="debug_before_statistics_click.png")
            print("Screenshot saved: debug_before_statistics_click.png")

            # Click the main statistics tab (English)
            await page.click("a:has-text('Statistics')", timeout=30000)
            await page.wait_for_timeout(1000)

            # Click the champion statistics sub-tab (English)
            await page.click("a:has-text('Champion Statistics')", timeout=30000)
            await page.wait_for_timeout(1000)

            # Scroll down the page to load all content
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000) # Wait for scroll to take effect

            # Use a more specific selector to find the table (English header)
            table_selector = "table:has(th:text-is('Champion'))"
            await page.wait_for_selector(table_selector, timeout=120000)

            champion_stats = []

            rows = await page.query_selector_all(f"{table_selector} tbody tr")

            for row in rows:
                champion_name_element = await row.query_selector("td.name span.name-text")
                games_played_element = await row.query_selector("td.plays")

                if champion_name_element and games_played_element:
                    champion_name = await champion_name_element.inner_text()
                    games_played_text = await games_played_element.inner_text()
                    games_played = int(games_played_text.strip())

                    champion_stats.append({
                        "champion": champion_name,
                        "games_played": games_played
                    })

            return champion_stats
        finally:
            await browser.close()

async def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python scraper.py <username> <tag>")
        sys.exit(1)
    
    username = sys.argv[1]
    tag = sys.argv[2]

    stats = await get_champion_stats(username, tag)
    if stats:
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print("Could not retrieve champion statistics.")

if __name__ == "__main__":
    asyncio.run(main())

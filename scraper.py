
import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError

async def get_champion_stats(username: str, tag: str, browser):
    context = await browser.new_context(locale='en-US')
    page = await context.new_page()
    try:
        # Construct the lolchess.gg URL dynamically
        profile_base_url = f"https://lolchess.gg/profile/na/{username}-{tag}/set14/statistics?staticType=champions"
        print(f"Navigating to {profile_base_url}...")
        await page.goto(profile_base_url, wait_until="domcontentloaded", timeout=120000)
        print("Page loaded.")

        try:
            # Click the cookie consent button if it exists
           # print("Attempting to click cookie consent button...")
            await page.click("button:has-text('AGREE')", timeout=5000)
           # print("Cookie consent button clicked.")
        except TimeoutError:
          #  print("Cookie consent button not found, continuing...")
            pass

        # Click the update button
        try:
           # print("Attempting to click update button...")
            await page.click(".updateRecord", timeout=10000)
            print(f"Updated {username}.")
            await page.wait_for_timeout(2000) # Wait for update to process
        except TimeoutError:
           # print("Update button not found or clickable, continuing...")
            pass


        # await page.goto(profile_base_url, wait_until="domcontentloaded", timeout=120000)
        # Take a screenshot before clicking the statistics tab
        #await page.screenshot(path="debug_before_statistics_click.png")
        #print("Screenshot saved: debug_before_statistics_click.png")

        # Click the main statistics tab (English)
        #print("Attempting to click Statistics tab...")
        #await page.click("a:has-text('Statistics')", timeout=30000)
        #await page.wait_for_timeout(1000)
       # print("Statistics tab clicked.")

        # Click the champion statistics sub-tab (English)
        #print("Attempting to click Champion Statistics sub-tab...")
        #await page.click("a:has-text('Champion Statistics')", timeout=30000)
       # await page.wait_for_timeout(1000)
        #print("Champion Statistics sub-tab clicked.")

        # Scroll down the page to load all content
        #print("Scrolling down to load all content...")
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(2000) # Wait for scroll to take effect
        #print("Scrolled down.")

        # Use a more specific selector to find the table (English header)
        table_selector = "table:has(th:text-is('Champion'))"
        #print(f"Waiting for table with selector: {table_selector}...")
        await page.wait_for_selector(table_selector, timeout=120000)
        print("Table found.")

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
            await context.close()

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

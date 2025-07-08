
import asyncio
import json
import sys
from playwright.async_api import async_playwright, TimeoutError

async def get_lobby_players(profile_url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(profile_url, wait_until="domcontentloaded", timeout=120000)

            try:
                await page.wait_for_selector("div.PlayerScoutingContainer", timeout=30000)
                live_game_module = await page.query_selector("div.PlayerScoutingContainer")
            except TimeoutError:
                live_game_module = None

            if not live_game_module:
                print("No live game detected for this player.")
                return []

            player_links = []
            await page.wait_for_selector("a.PlayerScoutingPlayer", timeout=30000)
            
            player_cards = await live_game_module.query_selector_all("a.PlayerScoutingPlayer")

            for card in player_cards:
                href = await card.get_attribute("href")
                if href:
                    player_links.append(f"https://www.metatft.com{href}")
            return player_links
        finally:
            await browser.close()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python metatft_scraper.py <profile_url>")
        sys.exit(1)
    
    profile_url = sys.argv[1]
    
    players = await get_lobby_players(profile_url)
    if players:
        print(json.dumps(players, indent=2))
    else:
        print("Could not retrieve lobby players.")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import json
import sys
from collections import defaultdict
from playwright.async_api import async_playwright

# Import functions from other scripts
from metatft_scraper import get_lobby_players
from scraper import get_champion_stats

async def get_player_username_tag_from_url(profile_url: str):
    # URL format: https://www.metatft.com/player/na/USERNAME-TAG
    parts = profile_url.split('/')
    username_tag = parts[-1] # e.g., HULUHASLIVESPORT-NA1
    
    # Split by the last hyphen to separate username and tag
    if '-' in username_tag:
        username_parts = username_tag.rsplit('-', 1)
        username = username_parts[0]
        tag = "#" + username_parts[1]
        return username, tag
    return None, None

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main_orchestrator.py <your_metatft_profile_url>")
        sys.exit(1)
    
    your_metatft_profile_url = sys.argv[1]

    print(f"Getting lobby players from MetaTFT for {your_metatft_profile_url}...")
    lobby_players_metatft_urls = await get_lobby_players(your_metatft_profile_url)

    if not lobby_players_metatft_urls:
        print("No live game detected or could not retrieve lobby players from MetaTFT.")
        sys.exit(0)

    # Get your own username and tag to exclude yourself from the lobby sum
    your_username, your_tag = await get_player_username_tag_from_url(your_metatft_profile_url)
    your_full_id = f"{your_username}{your_tag}" if your_username and your_tag else ""

    total_lobby_champion_plays = defaultdict(int)

    print("Scraping champion data for lobby players from lolchess.gg (excluding yourself)...")
    
    scraping_tasks = []
    player_info_list = [] # To store player_username, player_tag for later use

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for player_metatft_url in lobby_players_metatft_urls:
            player_username, player_tag = await get_player_username_tag_from_url(player_metatft_url)
            
            if not player_username or not player_tag:
                print(f"Skipping invalid player URL: {player_metatft_url}")
                continue

            player_full_id = f"{player_username}{player_tag}"

            if player_full_id.lower() == your_full_id.lower():
                print(f"Skipping self: {player_full_id}")
                continue

            print(f"Adding {player_full_id} to scraping queue...")
            scraping_tasks.append(get_champion_stats(player_username, player_tag.replace('#', ''), browser))
            player_info_list.append({"username": player_username, "tag": player_tag})

        # Run all scraping tasks concurrently
        all_player_champion_stats = await asyncio.gather(*scraping_tasks)
        await browser.close()

    for i, player_champion_stats in enumerate(all_player_champion_stats):
        player_username = player_info_list[i]["username"]
        player_tag = player_info_list[i]["tag"]
        player_full_id = f"{player_username}{player_tag}"

        if player_champion_stats:
            print(f"Processing stats for {player_full_id}...")
            for stat in player_champion_stats:
                total_lobby_champion_plays[stat["champion"]] += stat["games_played"]
        else:
            print(f"Could not retrieve champion statistics for {player_full_id}.")

    print("\nAggregated Champion Plays for Lobby (excluding yourself):\n")
    print("--------------------------------------------------")
    print(f"{"Champion":<20} {"Total Plays":>15}")
    print("--------------------------------------------------")
    for champion, total_plays in sorted(total_lobby_champion_plays.items(), key=lambda item: item[1], reverse=True):
        print(f"{champion:<20} {total_plays:>15}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
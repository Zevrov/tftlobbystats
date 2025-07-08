
import json
from collections import defaultdict

def summarize_champion_stats():
    try:
        with open("champion_stats.json", "r", encoding="utf-8") as f:
            champion_data = json.load(f)

        champion_play_counts = defaultdict(int)
        for entry in champion_data:
            champion_play_counts[entry["champion"]] += entry["games_played"]

        print("\nChampion Play Counts (Last 20 Games):\n")
        print("-------------------------------------")
        print(f"{"Champion":<20} {"Games Played":>15}")
        print("-------------------------------------")
        for champion, count in sorted(champion_play_counts.items(), key=lambda item: item[1], reverse=True):
            print(f"{champion:<20} {count:>15}")
        print("-------------------------------------")

    except FileNotFoundError:
        print("Error: champion_stats.json not found. Please run the scraper first.")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from champion_stats.json.")

if __name__ == "__main__":
    summarize_champion_stats()


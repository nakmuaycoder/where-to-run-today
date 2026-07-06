"""Main entry point for the where-to-run-today scraper.

This script parses command line arguments, loads the configuration,
and initiates the scraping process.
"""

import argparse
from typing import List

from config import read_config
from scraper import Scraper


def run_scrap(config_path: str, mock: bool = False) -> None:
    """Loads configuration and runs the scraper.

    Args:
        config_path: The path to the configuration JSON file.
        mock: If True, uses mock data instead of live scraping for testing.
    """
    config = read_config(path_config=config_path)

    scraper = Scraper(
        department=config.department,
        data_json=config.data_json,
        prefecture_url=config.prefecture_url,
        watchlist=config.watchlist,
        sms_user=config.free_mobile_user,
        sms_pass=config.free_mobile_pass,
    )

    if mock:
        print("--- MOCK MODE ---")
        # Mocking levels: Alpilles and Calanques open, others closed
        scraper.levels = {
            "1": 1,  # Alpilles
            "3": 2,  # Calanques
            "23": 3,  # Sainte-Victoire
        }
        # We still need forest_ids to map IDs to names
        # Use hardcoded IDs in mock mode to avoid network dependency
        scraper.forest_ids = {"1": "Alpilles", "3": "Calanques", "23": "Sainte-Victoire"}
        scraper.results = scraper.process()

        open_forests: List[str] = []
        monitor_all: bool = not scraper.watchlist or "ALL" in [w.upper() for w in scraper.watchlist]

        for forest, level in scraper.results.items():
            if not monitor_all and forest not in scraper.watchlist:
                continue
            status: str = scraper._interpret_level(level)
            print(f"{forest.capitalize()}: {status} (Level {level})")
            if level in [1, 2]:
                open_forests.append(forest)

        if open_forests:
            message: str = "🏃 [MOCK] Forests OPEN: " + ", ".join(open_forests)
            scraper._notify(message)
    else:
        scraper.run()


def main() -> None:
    """Parses arguments and starts the application."""
    parser = argparse.ArgumentParser(description="Scraper for forest fire risk levels.")

    parser.add_argument(
        "--config_path", type=str, default="src/config.json", help="Path to the config.json file."
    )
    parser.add_argument("--mock", action="store_true", help="Run in mock mode for testing.")

    args = parser.parse_args()
    run_scrap(config_path=args.config_path, mock=args.mock)


if __name__ == "__main__":
    main()

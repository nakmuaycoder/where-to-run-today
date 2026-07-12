"""Scraper module for forest fire risk monitoring.

This module contains the Scraper class which handles downloading and parsing
data from prefecture websites to determine if forests are open for activities.
"""

import datetime
import json
import logging
import zoneinfo
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

try:
    from freeMobileSMS.sms import FreeMobileTxtMe
except ImportError:
    FreeMobileTxtMe = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Scraper:
    """A scraper to monitor forest access based on wildfire risk.

    Attributes:
        department: The department code (e.g., '13').
        prefecture_url: The URL of the prefecture's forest risk page.
        data_json_url: The URL where the risk level JSON data is hosted.
        watchlist: A list of forests to monitor.
        sms_user: Free Mobile SMS API user.
        sms_pass: Free Mobile SMS API key.
        forest_ids: A mapping of forest IDs to their names.
        levels: A mapping of forest IDs to their risk levels.
        results: A mapping of forest names to their risk levels.
    """

    def __init__(
        self,
        department: str = "13",
        data_json: Optional[str] = None,
        prefecture_url: Optional[str] = None,
        watchlist: Optional[List[str]] = None,
        sms_user: Optional[str] = None,
        sms_pass: Optional[str] = None,
    ) -> None:
        """Initializes the Scraper with department and connection details.

        Args:
            department: The department code.
            data_json: Optional override for the JSON data URL.
            prefecture_url: Optional override for the prefecture URL.
            watchlist: Optional list of forests to watch.
            sms_user: Optional SMS API user.
            sms_pass: Optional SMS API key.
        """
        self.department: str = department
        self.prefecture_url: str = (
            prefecture_url or f"https://www.risque-prevention-incendie.fr/{department}"
        )
        self.data_json_url: str = (
            data_json
            or f"https://www.risque-prevention-incendie.fr/static/{department}/import_data"
        )
        self.watchlist: List[str] = watchlist or []
        self.sms_user: Optional[str] = sms_user
        self.sms_pass: Optional[str] = sms_pass
        self.forest_ids: Dict[str, str] = {}
        self.levels: Dict[str, int] = {}
        self.results: Dict[str, int] = {}
        self.used_date: str = ""

    def run(self) -> None:
        """Executes the scraping process and sends notifications if necessary."""
        logger.info("Starting scrap...")
        try:
            self.forest_ids = self._get_forest_ids()
            self.levels = self._get_levels()
            self.results = self.process()

            if not self.results:
                logger.warning("No data found for today (might be off-season).")
                return

            logger.info("Scraping successful.")

            open_forests: List[str] = []
            monitor_all: bool = not self.watchlist or "ALL" in [w.upper() for w in self.watchlist]

            for forest, level in self.results.items():
                status: str = self._interpret_level(level)
                is_open: bool = level in [1, 2]

                # Filter by watchlist unless monitor_all is True
                if not monitor_all and forest not in self.watchlist:
                    continue

                print(f"{forest.capitalize()}: {status} (Level {level})")
                if is_open:
                    open_forests.append(forest)

            if open_forests:
                date_label = "today"
                if self.used_date:
                    try:
                        dt = datetime.datetime.strptime(self.used_date, "%Y%m%d")
                        date_label = dt.strftime("%d/%m/%Y")
                    except Exception:
                        date_label = self.used_date
                message: str = self.format_status_message(date_label)
                logger.info(f"Notification: {message}")
                self._notify(message)
            else:
                logger.info("No forest from the watchlist is open.")

        except Exception as e:
            logger.error(f"An error occurred during scraping: {e}")

    def format_status_message(self, date_label: str, is_mock: bool = False) -> str:
        """Formats the status of massifs into a list with plain text symbols.

        Args:
            date_label: The date string to display, or empty.
            is_mock: Whether the scraper is running in mock mode.

        Returns:
            A string with the status of each watched massif.
        """
        monitor_all: bool = not self.watchlist or "ALL" in [w.upper() for w in self.watchlist]
        prefix = "[MOCK] " if is_mock else ""
        date_suffix = f" on {date_label}" if date_label else ""
        header = f"{prefix}Massifs{date_suffix}:"
        lines = [header]

        for forest, level in self.results.items():
            if not monitor_all and forest not in self.watchlist:
                continue
            symbol = "[OK]" if level in [1, 2] else "[KO]"
            lines.append(f"{symbol} {forest.capitalize()}")

        return "\n".join(lines)

    def process(self) -> Dict[str, int]:
        """Maps forest names to their corresponding risk levels.

        Returns:
            A dictionary where keys are forest names and values are level integers.
        """
        if not self.levels or not self.forest_ids:
            return {}

        return {name: self.levels.get(id_, 0) for id_, name in self.forest_ids.items()}

    def _interpret_level(self, level: int) -> str:
        """Translates a numerical risk level into a human-readable status.

        Args:
            level: The numerical level (0-4).

        Returns:
            A string representing the status (OPEN, CLOSED, etc.).
        """
        if level == 0:
            return "No data"
        elif level in [1, 2]:
            return "OPEN"
        elif level in [3, 4]:
            return "CLOSED"
        return f"Unknown ({level})"

    def _download(self, link: str) -> str:
        """Downloads the content of a given URL.

        Args:
            link: The URL to download.

        Returns:
            The raw string content of the response, or an empty string on 404/error.
        """
        try:
            response = requests.get(link, timeout=10)
            if response.status_code == 404:
                return ""
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Download failed for {link}: {e}")
            return ""

    def _get_levels(self) -> Dict[str, int]:
        """Fetches risk levels from the JSON data source.

        Tries tomorrow's date first, then falls back to today's date.

        Returns:
            A dictionary mapping forest IDs to risk levels.
        """
        try:
            tz = zoneinfo.ZoneInfo("Europe/Paris")
        except zoneinfo.ZoneInfoNotFoundError:
            tz = None
        today = datetime.datetime.now(tz)
        dates_to_try = [
            (today + datetime.timedelta(days=1)).strftime("%Y%m%d"),
            today.strftime("%Y%m%d"),
        ]

        data = None
        for date_str in dates_to_try:
            url = f"{self.data_json_url.rstrip('/')}/{date_str}.json"
            logger.info(f"Fetching levels from {url}")
            content = self._download(link=url)
            if content:
                try:
                    data = json.loads(content)
                    self.used_date = date_str
                    break
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to decode JSON levels data for {date_str}: {e}")

        if data is None:
            return {}

        logger.info(f"Successfully retrieved levels data for {self.used_date}")

        parsed_levels = {}
        raw_data = {}
        if isinstance(data, dict):
            if "massifs" in data and isinstance(data["massifs"], dict):
                raw_data = data["massifs"]
            else:
                raw_data = data

        for key, val in raw_data.items():
            try:
                if isinstance(val, list) and len(val) > 0:
                    parsed_levels[key] = int(val[0])
                elif isinstance(val, (int, str)):
                    parsed_levels[key] = int(val)
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse level for key {key}: {val}")

        return parsed_levels

    def _get_forest_ids(self) -> Dict[str, str]:
        """Parses the prefecture website to extract forest names and their IDs.

        Returns:
            A dictionary mapping forest IDs to forest names.
        """
        logger.info(f"Fetching forest IDs from {self.prefecture_url}")
        response: str = self._download(link=self.prefecture_url)
        if not response:
            return {}

        soup = BeautifulSoup(response, "lxml")
        table = soup.find("table", id="tabm")
        if not table:
            table = soup.find("table", class_="table table-condensed table-striped")

        if not table:
            logger.error("Could not find the forest table on the page")
            return {}

        rows = table.find_all("tr")
        forest_ids: Dict[str, str] = {}
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                if forest_id := row.get("id"):
                    forest_name: str = cols[1].text.strip()
                    forest_ids[forest_id] = forest_name

        return forest_ids

    def _notify(self, message: str) -> None:
        """Sends an SMS notification using the Free Mobile API.

        Args:
            message: The message string to send.
        """
        if not self.sms_user or not self.sms_pass:
            logger.info("SMS credentials not provided, skipping notification.")
            return

        if FreeMobileTxtMe:
            try:
                sms_sender = FreeMobileTxtMe(self.sms_user, self.sms_pass)
                sms_sender.send_message(message)
                logger.info("SMS sent successfully.")
            except Exception as e:
                logger.error(f"Failed to send SMS: {e}")
        else:
            logger.warning("freeMobileSMS library not found, cannot send SMS.")

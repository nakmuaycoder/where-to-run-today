from where_to_run_today.scraper import Scraper


def test_scraper_url_construction():
    scraper = Scraper(department="83")
    assert "83" in scraper.prefecture_url
    assert "83" in scraper.data_json_url


def test_interpret_level():
    scraper = Scraper()
    assert scraper._interpret_level(1) == "OPEN"
    assert scraper._interpret_level(3) == "CLOSED"
    assert scraper._interpret_level(0) == "No data"
    assert scraper._interpret_level(9) == "Unknown (9)"


def test_process_mapping():
    scraper = Scraper()
    scraper.forest_ids = {"1": "Alpilles", "2": "Arbois"}
    scraper.levels = {"1": 1, "2": 3}
    results = scraper.process()
    assert results["Alpilles"] == 1
    assert results["Arbois"] == 3


def test_format_status_message():
    # Test case-insensitivity in watchlist filtering
    scraper = Scraper(watchlist=["alpilles", "ARBOIS", "sainte-victoire"])
    scraper.results = {"Alpilles": 1, "Arbois": 3, "Sainte-Victoire": 1, "Calanques": 2}

    # 1. Test formatting with date_label and watchlist filtering
    msg = scraper.format_status_message(date_label="12/07/2026")
    expected = "Massifs on 12/07/2026:\n[OK] Alpilles\n[KO] Arbois\n[OK] Sainte-Victoire"
    assert msg == expected

    # 2. Test formatting with mock mode
    scraper_mock = Scraper()  # No watchlist, defaults to monitor all
    scraper_mock.results = {"Alpilles": 1, "Arbois": 3, "Sainte-Victoire": 1}
    msg_mock = scraper_mock.format_status_message(date_label="", is_mock=True)
    expected_mock = "[MOCK] Massifs:\n[OK] Alpilles\n[KO] Arbois\n[OK] Sainte-Victoire"
    assert msg_mock == expected_mock

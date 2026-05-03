from scraper import Scraper


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

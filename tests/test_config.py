import json

from config import Config, read_config


def test_config_model():
    config = Config(department="13", watchlist=["ALL"])
    assert config.department == "13"
    assert config.watchlist == ["ALL"]
    assert config.prefecture_url is None


def test_read_config(tmp_path):
    d = tmp_path / "config"
    d.mkdir()
    p = d / "test_config.json"
    content = {"department": "83", "watchlist": ["Sainte-Baume"], "free_mobile_user": "user123"}
    p.write_text(json.dumps(content))

    config = read_config(str(p))
    assert config.department == "83"
    assert config.free_mobile_user == "user123"
    assert "Sainte-Baume" in config.watchlist

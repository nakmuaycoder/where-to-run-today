"""Configuration module for the where-to-run-today project.

This module defines the Config data structure and a function to load
configuration from a JSON file using Pydantic.
"""

import json
import pathlib
from typing import List, Optional

from pydantic import BaseModel


class Config(BaseModel):
    """Pydantic model representing the application configuration.

    Attributes:
        department: The department code (e.g., '13').
        prefecture_url: Optional override for the prefecture website URL.
        data_json: Optional override for the risk data JSON URL.
        free_mobile_user: User ID for Free Mobile SMS API.
        free_mobile_pass: API Key for Free Mobile SMS API.
        watchlist: List of forest names to monitor, or ['ALL'] for all forests.
    """

    department: str = "13"
    prefecture_url: Optional[str] = None
    data_json: Optional[str] = None
    free_mobile_user: Optional[str] = None
    free_mobile_pass: Optional[str] = None
    watchlist: List[str] = []


def read_config(path_config: str) -> Config:
    """Reads and parses a JSON configuration file.

    Args:
        path_config: The path to the JSON configuration file.

    Returns:
        A Config object populated with the data from the JSON file.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    path_object = pathlib.Path(path_config)
    with path_object.open("r") as f:
        config_dict = json.load(f)
    return Config(**config_dict)

"""File loaders."""

from pathlib import Path
from typing import Callable, Dict, Union

import yaml  # type: ignore
import json

from merge_logs.types import FileBaseFormat


def get_loaders() -> Dict[str, Callable[[Union[str, Path]], FileBaseFormat]]:
    return {
        "yaml": load_yaml,
        "json_lastrow": load_json_lastrow,
        "json_rows": load_json_rows,
    }


def load_yaml(path: Union[str, Path]) -> FileBaseFormat:
    """Load a simple yaml file."""
    with open(path) as f:
        return yaml.safe_load(f)


def load_json_lastrow(path: Union[str, Path]) -> FileBaseFormat:
    """Load the last row of file as a json."""
    # Find row
    last_line = ""
    with open(path) as f:
        for last_line in f:
            pass

    # Read
    return json.loads(last_line)


def load_json_rows(path: Union[str, Path]) -> FileBaseFormat:
    """Load rows of a txt file as jsons."""
    jsons = {}
    with open(path) as f:
        for i, line in enumerate(f):
            jsons[i] = json.loads(line)
    return jsons

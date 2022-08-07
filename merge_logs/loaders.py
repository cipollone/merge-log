"""File loaders."""

from pathlib import Path
from typing import Callable, Dict, Union

import yaml  # type: ignore

from merge_logs.types import FileBaseFormat


def get_loaders() -> Dict[str, Callable[[Union[str, Path]], FileBaseFormat]]:
    return {
        "yaml": load_yaml,
        "json_lastrow": load_json_lastrow,
    }


def load_yaml(path: Union[str, Path]) -> FileBaseFormat:
    """Load a simple yaml file."""
    with open(path) as f:
        return yaml.safe_load(f)


# TODO: fill
def load_json_lastrow(path: Union[str, Path]) -> FileBaseFormat:
    pass

"""Main module."""

import argparse
import csv
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple, cast

import numpy as np
import yaml  # type: ignore


def merge_format0(in_paths: Sequence[str], out_path: str):
    """Merge all inputs according to format0; see program help."""

    # Load
    data = []
    for in_path in in_paths:
        with open(in_path) as f:
            data.append(yaml.safe_load(f))

    # Format
    FileFormat = Dict[Any, List[float]]
    data = cast(List[FileFormat], data)

    # Check keys
    keys = set(data[0].keys())
    for i, file_data in enumerate(data):
        assert set(file_data.keys()) == keys, (
            f"Keys difference between files {0} and {i}"
        )

    # Combine
    combined: FileFormat = {}
    for key in keys:
        combined[key] = []
        for file_data in data:
            combined[key].extend(file_data[key])

    # Collect statistics
    stats: Dict[Any, Tuple[float, float]] = {}
    for key in keys:
        stats[key] = (np.mean(combined[key]), np.std(combined[key]))

    # Write all
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(stats)


def main():
    """Entry point."""
    # Arguments
    parser = argparse.ArgumentParser(description="Merge multiple log files")
    parser.add_argument(
        "--format",
        type=int,
        help=(
            "Select the format of the log file. "
            "Format 0: the input files are yaml files containing a "
            "dictionaries, where each key points to a list of values. "
            "Lists of the different files will be collapsed into a single statistic. "
            "All keys should match."
        ),
    )
    parser.add_argument("--out", type=str, required=True, help="Output csv file")
    parser.add_argument(
        "in_paths",
        type=str,
        nargs="+",
        help="A sequence of input files",
    )

    # Parse
    args = parser.parse_args()

    # Check if out path exists
    if Path(args.out).exists():
        ans = input(f"Should I overwrite existing {args.out}? (Y/n) ")
        if ans not in ("y", "Y", ""):
            quit()

    # Do
    if args.format == 0:
        merge_format0(in_paths=args.in_paths, out_path=args.out)
    else:
        raise ValueError(f"Format {args.format} not supported")


if __name__ == "__main__":
    main()

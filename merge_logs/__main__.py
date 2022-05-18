"""Main module."""

import argparse
import csv
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np
import yaml  # type: ignore

Stats = Dict[Any, List[float]]
FileFormat0 = Dict[Any, List[float]]
FileFormat1 = Dict[int, List[float]]
FileFormat2 = Dict[int, List[List[float]]]


def merge_format0(data: List[FileFormat0]) -> Stats:
    """Merge all inputs according to format0; see program help."""
    # Check keys
    keys = set(data[0].keys())
    for i, file_data in enumerate(data):
        assert set(file_data.keys()) == keys, (
            f"Keys difference between files {0} and {i}"
        )

    # Combine
    combined: FileFormat0 = {}
    for key in keys:
        combined[key] = []
        for file_data in data:
            combined[key].extend(file_data[key])

    # Collect statistics
    stats: Stats = {}
    for key in keys:
        stats[key] = [np.mean(combined[key]), np.std(combined[key])]

    return stats


def merge_format1(data: List[FileFormat1]) -> Stats:
    """Merge all inputs according to format1; see program help."""
    # Check keys
    all_keys = [sorted(data_i.keys()) for data_i in data]
    for i, keys in enumerate(all_keys):
        assert len(keys) == len(all_keys[0]), (
            f"Numer of keys differ between files {0} and {i}"
        )

    # Combine
    combined: FileFormat1 = {}
    for key in all_keys[0]:
        combined[key] = []
        for file_data, file_keys in zip(data, all_keys):
            other_key = min(file_keys, key=lambda k: abs(key - k))
            combined[key].extend(file_data[other_key])

    # Collect statistics
    stats: Stats = {}
    for key in all_keys[0]:
        stats[key] = [np.mean(combined[key]), np.std(combined[key])]

    return stats


def merge_format2(data: List[FileFormat2]) -> Stats:
    """Merge all inputs according to format2; see program help."""
    # Check keys
    all_keys = [sorted(data_i.keys()) for data_i in data]
    for i, keys in enumerate(all_keys):
        assert len(keys) == len(all_keys[0]), (
            f"Numer of keys differ between files {0} and {i}"
        )
    # Check number of stats
    n_stats = len(data[0][all_keys[0][0]][0])
    for file_data in data:
        for key in file_data:
            for samples in file_data[key]:
                assert len(samples) == n_stats, (
                    f"Not all timesteps contain {n_stats} statistics"
                )

    # Combine
    combined: FileFormat2 = {}
    for key in all_keys[0]:
        combined[key] = [[] for _ in range(n_stats)]
        for file_data, file_keys in zip(data, all_keys):
            other_key = min(file_keys, key=lambda k: abs(key - k))
            for samples in file_data[other_key]:
                for stat_i, stat in enumerate(samples):
                    combined[key][stat_i].append(stat)

    # Collect statistics
    stats: Stats = {}
    for key in all_keys[0]:
        stats[key] = []
        for stat_i in range(n_stats):
            stats[key].extend(
                [np.mean(combined[key][stat_i]), np.std(combined[key][stat_i])]
            )

    return stats


def merge_formats(format_id: int, in_paths: Sequence[str], out_path: str):
    """Merge according to a format."""
    # Load
    data = []
    for in_path in in_paths:
        with open(in_path) as f:
            data.append(yaml.safe_load(f))

    # Select
    formats = [
        merge_format0,
        merge_format1,
        merge_format2,
    ]
    if format_id not in range(len(formats)):
        raise ValueError(f"Format {format_id} not supported")
    merge_format = formats[format_id]

    # Do
    stats = merge_format(data)  # type: ignore

    # Write all
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        for stat in sorted(stats):
            writer.writerow([stat, *stats[stat]])


def main():
    """Entry point."""
    # Arguments
    parser = argparse.ArgumentParser(description="Merge multiple log files")
    parser.add_argument(
        "--format",
        type=int,
        required=True,
        help=(
            "Select the format of the log file. "
            "Format 0: the input files are yaml files containing a "
            "dictionaries, where each key points to a list of values. "
            "Lists of the different files will be collapsed into a single statistic. "
            "All keys should match. "
            "Format 1: like format 0 but keys are ints, and they don't need to match "
            "exactly; the closest entry will be selected."
            "Format 2: similar to 0, but multiple stats are combined at the same time "
            "in different columns"
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
    merge_formats(args.format, in_paths=args.in_paths, out_path=args.out)


if __name__ == "__main__":
    main()

"""Main module."""

import argparse
import csv
from pathlib import Path
from typing import List, Optional, Sequence, cast

from merge_logs.formats import (MergerType, merge_format0, merge_format1,
                                merge_format2, merge_format3)
from merge_logs.loaders import get_loaders


def merge_formats(
    format_id: int,
    nested: Optional[Sequence[str]],
    loader: str,
    in_paths: Sequence[str],
    out_path: str,
):
    """Merge according to a format; see program help."""
    # Load
    loader_fn = get_loaders()[loader]
    data = [
        loader_fn(in_path)
        for in_path in in_paths
    ]

    # Select
    formats = cast(List[MergerType], [
        merge_format0,
        merge_format1,
        merge_format2,
        merge_format3,
    ])
    if format_id not in range(len(formats)):
        raise ValueError(f"Format {format_id} not supported")
    merge_format = formats[format_id]

    # Do
    stats = merge_format(data, nested)

    # Write all
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONNUMERIC)
        for stat in sorted(stats):
            writer.writerow([stat, *stats[stat]])


def main():
    """Entry point."""
    # Arguments
    parser = argparse.ArgumentParser(
        description="Merge multiple log files and save timeseries "
        "mean and standard deviation"
    )
    parser.add_argument(
        "--format",
        type=int,
        required=True,
        help=(
            "Select the format of the input log file. \n"
            "Format 0: the input files should contain dictionaries, "
            "where each key points to a list of values. "
            "Lists of the different files will be collapsed into "
            "a single statistic. All keys should match. \n"
            "Format 1: like format 0 but keys are ints, "
            "and they don't need to match exactly; "
            "the closest entry will be selected."
            "Format 2: similar to 0, but multiple stats are combined "
            "at the same time in different columns.\n"
        ),
    )
    # TODO: doc format 3
    parser.add_argument(
        "--nested",
        type=str,
        nargs="+",
        help="Sequence of nested keys to be traversed in input files, if any"
    )
    parser.add_argument(
        "--loader",
        required=True,
        choices=get_loaders().keys(),
        help="How to load input file. 'json-lastrow' interprets "
        "the last row of the file as the json to be loaded."
    )
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Output csv file",
    )
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
    merge_formats(
        args.format,
        nested=args.nested,
        loader=args.loader,
        in_paths=args.in_paths,
        out_path=args.out,
    )


if __name__ == "__main__":
    main()

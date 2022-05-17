
import argparse
from pathlib import Path
from typing import Sequence


def merge_all(in_paths: Sequence[str], out_path: str):
    pass


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
    parser.add_argument("--out", type=str, required=True, help="Output file")
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
    merge_all(in_paths=args.in_paths, out_path=args.out)


if __name__ == "__main__":
    main()

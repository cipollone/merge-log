"""Format parsers."""

from typing import Callable, List, Optional, Sequence

import numpy as np

from merge_logs.types import (FileBaseFormat, FileFormat0, FileFormat1,
                              FileFormat2, FileFormat3, Stats, TimeStats)

MergerType = Callable[[List[FileBaseFormat], Optional[Sequence[str]]], Stats]


def merge_format0(
    data: List[FileFormat0],
    nested_feature: Optional[Sequence[str]] = None,
) -> Stats:
    """Merge all inputs according to format0; see program help."""
    # Check
    assert nested_feature is None, "Format0 can only merge top-level features."

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


def merge_format1(
    data: List[FileFormat1],
    nested_feature: Optional[Sequence[str]] = None,
) -> TimeStats:
    """Merge all inputs according to format1; see program help."""
    # Check
    assert nested_feature is None, "Format1 can only merge top-level features."

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


def merge_format2(
    data: List[FileFormat2],
    nested_feature: Optional[Sequence[str]] = None,
) -> TimeStats:
    """Merge all inputs according to format2; see program help."""
    # Check
    assert nested_feature is None, "Format2 can only merge top-level features."

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


def merge_format3(
    data: List[FileFormat3],
    nested_feature: Optional[Sequence[str]] = None,
) -> TimeStats:
    """Merge all inputs according to format3; see program help."""
    # TODO
    pass

"""Format parsers."""

from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from merge_logs.types import (FileBaseFormat, FileFormat0, FileFormat1,
                              FileFormat2, FileFormat3, Stats, TimeStats)

CsvHeader = Sequence[str]
MergerType = Callable[
    [List[FileBaseFormat], Optional[Sequence[str]]],
    Tuple[Stats, Optional[CsvHeader]]
]


def merge_format0(
    data: List[FileFormat0],
    features: Optional[Sequence[str]] = None,
) -> Tuple[Stats, Optional[CsvHeader]]:
    """Merge all inputs according to format0; see program help."""
    # Check
    assert features is None, "Can't select features"

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

    return stats, None


def merge_format1(
    data: List[FileFormat1],
    features: Optional[Sequence[str]] = None,
) -> Tuple[TimeStats, Optional[CsvHeader]]:
    """Merge all inputs according to format1; see program help."""
    # Check
    assert features is None, "Can't select features"

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
    stats: TimeStats = {}
    for key in all_keys[0]:
        stats[key] = [np.mean(combined[key]), np.std(combined[key])]

    return stats, None


def merge_format2(
    data: List[FileFormat2],
    features: Optional[Sequence[str]] = None,
) -> Tuple[TimeStats, Optional[CsvHeader]]:
    """Merge all inputs according to format2; see program help."""
    # Check
    assert features is None, "Can't select features"

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
    stats: TimeStats = {}
    for key in all_keys[0]:
        stats[key] = []
        for stat_i in range(n_stats):
            stats[key].extend(
                [np.mean(combined[key][stat_i]), np.std(combined[key][stat_i])]
            )

    return stats, None


def merge_format3(
    data: List[FileFormat3],
    features: Sequence[str],
) -> Tuple[TimeStats, Optional[CsvHeader]]:
    """Merge all inputs according to format3; see program help."""
    # Get feature names
    features_names = [
        nested_feat.split(",")[-1] for nested_feat in features
    ]

    # Check equal number of steps
    n_steps = len(data[0])
    assert all((len(file_stats) == n_steps for file_stats in data)), (
        f"Not all files contain {n_steps} statistics"
    )

    # Collect all
    all_stats: Dict[str, List[List[float]]] = {}
    for name, feature in zip(features_names, features):
        feat_stats = []
        for step in range(n_steps):
            feat_step_stats = [
                get_nested(file_stats[step], feature)
                for file_stats in data
            ]
            feat_stats.append(feat_step_stats)
        all_stats[name] = feat_stats

    # Compute statistics
    stats: TimeStats = {}
    for i in range(n_steps):
        stats[i] = []
        for name in features_names:
            feat_step_stats = all_stats[name][i]
            stats[i].append(np.mean(feat_step_stats))
            stats[i].append(np.std(feat_step_stats))

    return stats, features_names


def get_nested(data, nested_feature: str):
    """Return nested key.

    :param nested_feature: a string where each nested key is separated by ,
    """
    return _get_nested(data, nested_feature=nested_feature.split(","))


def _get_nested(data, nested_feature: Optional[Sequence[str]]):
    """Return nested key."""
    if nested_feature is None or len(nested_feature) == 0:
        return data
    return _get_nested(data[nested_feature[0]], nested_feature[1:])

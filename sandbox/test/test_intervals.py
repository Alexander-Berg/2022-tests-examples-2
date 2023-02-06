import pytest
from sandbox.projects.yabs.release.binary_search import intervals


class TestGetBestPatrition(object):
    @pytest.mark.parametrize(("candidates", "expected_partition"), [
        (
            [
                [intervals.Interval(1, 2, intervals.NO_DIFF), ],
            ],
            [intervals.Interval(1, 2, intervals.NO_DIFF), ]
        ),
        (
            [
                [intervals.Interval(1, 3, intervals.NO_DIFF), ],
                [intervals.Interval(1, 2, intervals.NO_DIFF), intervals.Interval(2, 3, intervals.DIFF_DATA), ],
            ],
            [intervals.Interval(1, 3, intervals.NO_DIFF), ],
        ),
        pytest.param(
            [
                [intervals.Interval(1, 3, intervals.NO_CMP_TASK), ],
                [intervals.Interval(1, 2, intervals.DIFF_DATA), intervals.Interval(2, 3, intervals.DIFF_DATA), ],
            ],
            [intervals.Interval(1, 2, intervals.DIFF_DATA), intervals.Interval(2, 3, intervals.DIFF_DATA), ]
        ),
        (
            [
                [intervals.Interval(1, 3, intervals.DIFF_DATA), ],
                [intervals.Interval(1, 2, intervals.NO_DIFF), intervals.Interval(2, 3, intervals.DIFF_DATA), ],
            ],
            [intervals.Interval(1, 2, intervals.NO_DIFF), intervals.Interval(2, 3, intervals.DIFF_DATA), ]
        ),
        (
            [
                [
                    intervals.Interval(6583307, 6583333, intervals.NO_DIFF),
                    intervals.Interval(6583333, 6583369, intervals.DIFF_DATA),
                    intervals.Interval(6583369, 6583375, intervals.NO_DIFF),
                    intervals.Interval(6583375, 6583384, intervals.DIFF_DATA),
                    intervals.Interval(6583384, 6583402, intervals.FIXED),
                    intervals.Interval(6583402, 6583652, intervals.NO_DIFF)
                ],
                [
                    intervals.Interval(6583307, 6583369, intervals.DIFF_DATA),
                    intervals.Interval(6583369, 6583375, intervals.NO_DIFF),
                    intervals.Interval(6583375, 6583384, intervals.DIFF_DATA),
                    intervals.Interval(6583384, 6583402, intervals.FIXED),
                    intervals.Interval(6583402, 6583652, intervals.NO_DIFF)
                ],
                [
                    intervals.Interval(6583307, 6583384, intervals.BROKEN),
                    intervals.Interval(6583384, 6583402, intervals.FIXED),
                    intervals.Interval(6583402, 6583652, intervals.NO_DIFF)
                ],
                [
                    intervals.Interval(6583307, 6583375, intervals.NO_CMP_TASK),
                    intervals.Interval(6583375, 6583384, intervals.DIFF_DATA),
                    intervals.Interval(6583384, 6583402, intervals.FIXED),
                    intervals.Interval(6583402, 6583652, intervals.NO_DIFF)
                ],
                [
                    intervals.Interval(6583307, 6583402, intervals.NO_CMP_TASK),
                    intervals.Interval(6583402, 6583652, intervals.NO_DIFF)
                ]
            ],
            [
                intervals.Interval(6583307, 6583333, intervals.NO_DIFF),
                intervals.Interval(6583333, 6583369, intervals.DIFF_DATA),
                intervals.Interval(6583369, 6583375, intervals.NO_DIFF),
                intervals.Interval(6583375, 6583384, intervals.DIFF_DATA),
                intervals.Interval(6583384, 6583402, intervals.FIXED),
                intervals.Interval(6583402, 6583652, intervals.NO_DIFF)
            ],
        ),
    ])
    def test_get_best_partition(self, candidates, expected_partition):
        assert intervals.get_best_partition(candidates) == expected_partition


class TestPartitionInterval(object):
    @pytest.mark.parametrize(("interval_map", "interval", "expected_splitted_interval"), [
        (
            {},
            (1, 1),
            []
        ),
        (
            {
                (1, 2): {"diff_type": intervals.NO_DIFF},
            },
            (1, 2),
            [
                intervals.Interval(1, 2, intervals.NO_DIFF),
            ]
        ),
        (
            {
                (1, 2): {"diff_type": intervals.NO_DIFF},
            },
            (1, 1),
            []
        ),
        (
            {
                (1, 3): {"diff_type": intervals.DIFF_DATA},
                (1, 2): {"diff_type": intervals.DIFF_DATA},
                (2, 3): {"diff_type": intervals.NO_DIFF},
            },
            (1, 3),
            [
                intervals.Interval(1, 2, intervals.DIFF_DATA),
                intervals.Interval(2, 3, intervals.NO_DIFF),
            ]
        ),
        (
            {
                (1, 3): {"diff_type": intervals.NO_DIFF},
                (1, 2): {"diff_type": intervals.DIFF_DATA},
                (2, 3): {"diff_type": intervals.NO_DIFF},
            },
            (1, 3),
            [
                intervals.Interval(1, 3, intervals.NO_DIFF),
            ]
        ),
        (
            {
                (1, 3): {"diff_type": intervals.NO_DIFF},
                (1, 2): {"diff_type": intervals.DIFF_DATA},
                (2, 3): {"diff_type": intervals.NO_DIFF},
            },
            (1, 3),
            [
                intervals.Interval(1, 3, intervals.NO_DIFF),
            ]
        ),
        (
            {
                (1, 2): {"diff_type": intervals.NO_DIFF},
                (2, 3): {"diff_type": intervals.DIFF_DATA},
                (3, 4): {"diff_type": intervals.NO_DIFF},
            },
            (1, 4),
            [
                intervals.Interval(1, 2, intervals.NO_DIFF),
                intervals.Interval(2, 3, intervals.DIFF_DATA),
                intervals.Interval(3, 4, intervals.NO_DIFF),
            ]
        ),
        (
            {
                (1, 5): {"diff_type": intervals.DIFF_DATA},
                (1, 3): {"diff_type": intervals.NO_DIFF},
                (3, 5): {"diff_type": intervals.DIFF_DATA},
                (4, 5): {"diff_type": intervals.DIFF_DATA},
                (3, 4): {"diff_type": intervals.NO_DIFF},
            },
            (1, 5),
            [
                intervals.Interval(1, 3, intervals.NO_DIFF),
                intervals.Interval(3, 4, intervals.NO_DIFF),
                intervals.Interval(4, 5, intervals.DIFF_DATA),
            ]
        ),
    ])
    def test_partition_interval_full_coverage(self, interval_map, interval, expected_splitted_interval):
        seq = intervals.Partitioner(interval_map).partition_interval(interval)
        assert seq == expected_splitted_interval

    @pytest.mark.parametrize(("interval_map", "interval", "expected_splitted_interval"), [
        (
            {
                (1, 3): {"diff_type": intervals.DIFF_DATA},
                (1, 2): {"diff_type": intervals.DIFF_DATA},
            },
            (1, 3),
            [
                intervals.Interval(1, 2, intervals.DIFF_DATA),
                intervals.Interval(2, 3, intervals.NO_CMP_TASK),
            ]
        ),
        (
            {
                (1, 3): {"diff_type": intervals.DIFF_DATA},
                (2, 3): {"diff_type": intervals.DIFF_DATA},
            },
            (1, 3),
            [
                intervals.Interval(1, 2, intervals.NO_CMP_TASK),
                intervals.Interval(2, 3, intervals.DIFF_DATA),
            ]
        ),
        (
            {
                (1, 3): {"diff_type": intervals.DIFF_DATA},
                (1, 2): {"diff_type": intervals.NO_DIFF},
                (2, 3): {"diff_type": intervals.DIFF_DATA},
            },
            (0, 3),
            [
                intervals.Interval(0, 1, intervals.NO_CMP_TASK),
                intervals.Interval(1, 2, intervals.NO_DIFF),
                intervals.Interval(2, 3, intervals.DIFF_DATA),
            ]
        ),
        (
            {
                (1, 3): {"diff_type": intervals.DIFF_DATA},
                (1, 2): {"diff_type": intervals.NO_DIFF},
                (2, 3): {"diff_type": intervals.DIFF_DATA},
            },
            (1, 4),
            [
                intervals.Interval(1, 2, intervals.NO_DIFF),
                intervals.Interval(2, 3, intervals.DIFF_DATA),
                intervals.Interval(3, 4, intervals.NO_CMP_TASK),
            ]
        ),
        (
            {
                (1, 4): {"diff_type": intervals.DIFF_DATA},
                (2, 3): {"diff_type": intervals.DIFF_DATA},
            },
            (1, 4),
            [
                intervals.Interval(1, 2, intervals.NO_CMP_TASK),
                intervals.Interval(2, 3, intervals.DIFF_DATA),
                intervals.Interval(3, 4, intervals.NO_CMP_TASK),
            ]
        ),
    ])
    def test_partition_interval_no_coverage(self, interval_map, interval, expected_splitted_interval):
        seq = intervals.Partitioner(interval_map).partition_interval(interval)
        assert seq == expected_splitted_interval

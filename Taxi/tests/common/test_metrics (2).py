import numpy as np

from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.common.metrics.recall_hits import RecallHits
from projects.common.metrics.classification import (
    count_recalls_for_fixed_precisions,
    count_precisions_for_fixed_recalls,
)


class TestRecallHits:
    def prepare_job(self, recall_hits):
        job = clusters.MockCluster().job()
        input_table = job.table('').label('input')
        output_table = recall_hits(input_table)
        output_table.label('output').put('output')
        return job

    def test_simple(self):
        recall_hits = RecallHits(ne_hit_extractor='position')
        job = self.prepare_job(recall_hits)

        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(position=0),
                        Record(position=1),
                        Record(position=2),
                        Record(position=2),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        assert output == [
            Record(
                cum_hits=1,
                cum_recall=0.25,
                hits=1,
                position=0,
                recall=0.25,
                total=4,
            ),
            Record(
                cum_hits=2,
                cum_recall=0.5,
                hits=1,
                position=1,
                recall=0.25,
                total=4,
            ),
            Record(
                cum_hits=4,
                cum_recall=1.0,
                hits=2,
                position=2,
                recall=0.5,
                total=4,
            ),
        ]

    def test_zero_recall(self):
        recall_hits = RecallHits(ne_hit_extractor='position')
        job = self.prepare_job(recall_hits)

        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [Record(position=None), Record(position=None)],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        assert output == [
            Record(
                cum_hits=0,
                cum_recall=0.0,
                hits=0,
                position=0,
                recall=0.0,
                total=2,
            ),
        ]

    def test_weight(self):
        recall_hits = RecallHits(
            ne_hit_extractor='position', ne_weight_extractor='weight',
        )
        job = self.prepare_job(recall_hits)

        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(position=0, weight=1),
                        Record(position=1, weight=1),
                        Record(position=2, weight=3),
                        Record(position=2, weight=3),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        assert output == [
            Record(
                cum_hits=1,
                cum_recall=0.125,
                hits=1,
                position=0,
                recall=0.125,
                total=8,
            ),
            Record(
                cum_hits=2,
                cum_recall=0.25,
                hits=1,
                position=1,
                recall=0.125,
                total=8,
            ),
            Record(
                cum_hits=8,
                cum_recall=1.0,
                hits=6,
                position=2,
                recall=0.75,
                total=8,
            ),
        ]

    def test_groupby(self):
        recall_hits = RecallHits(
            ne_hit_extractor='position', groupby=['groupby'],
        )
        job = self.prepare_job(recall_hits)

        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(position=0, groupby=1),
                        Record(position=1, groupby=1),
                        Record(position=2, groupby=2),
                        Record(position=2, groupby=2),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        assert output == [
            Record(
                cum_hits=1,
                cum_recall=0.5,
                groupby=1,
                hits=1,
                position=0,
                recall=0.5,
                total=2,
            ),
            Record(
                cum_hits=0,
                cum_recall=0.0,
                groupby=2,
                hits=0,
                position=0,
                recall=0.0,
                total=2,
            ),
            Record(
                cum_hits=2,
                cum_recall=1.0,
                groupby=1,
                hits=1,
                position=1,
                recall=0.5,
                total=2,
            ),
            Record(
                cum_hits=0,
                cum_recall=0.0,
                groupby=2,
                hits=0,
                position=1,
                recall=0.0,
                total=2,
            ),
            Record(
                cum_hits=2,
                cum_recall=1.0,
                groupby=2,
                hits=2,
                position=2,
                recall=1.0,
                total=2,
            ),
        ]

    def test_max_position(self):
        recall_hits = RecallHits(ne_hit_extractor='position', max_position=1)
        job = self.prepare_job(recall_hits)

        output = []
        job.local_run(
            sources={
                'input': StreamSource(
                    [
                        Record(position=0),
                        Record(position=1),
                        Record(position=2),
                        Record(position=2),
                    ],
                ),
            },
            sinks={'output': ListSink(output)},
        )
        assert output == [
            Record(
                cum_hits=1,
                cum_recall=0.25,
                hits=1,
                position=0,
                recall=0.25,
                total=4,
            ),
            Record(
                cum_hits=2,
                cum_recall=0.5,
                hits=1,
                position=1,
                recall=0.25,
                total=4,
            ),
        ]


class TestClassificationMetrics:
    def test_count_recalls_for_fixed_precisions(self):
        thrs, recalls = count_recalls_for_fixed_precisions(
            np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0]]),
            np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0]]),
            0.9,
            False,
            3,
        )
        assert np.all(np.equal(thrs, np.array([1, 1, 1])))
        assert np.all(np.equal(recalls, np.array([1, 1, 1])))

        thrs, recalls = count_recalls_for_fixed_precisions(
            np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0]]),
            np.array([[1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1]]),
            0.9,
            False,
            3,
        )
        assert np.all(np.equal(thrs, np.array([1, 1, 1])))
        assert np.all(np.equal(recalls, np.array([0, 0, 0])))

    def test_count_precisions_for_fixed_recalls(self):
        thrs, precisions = count_precisions_for_fixed_recalls(
            np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0]]),
            np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0]]),
            0.9,
            False,
            3,
        )
        assert np.all(np.equal(thrs, np.array([0, 0, 0])))
        assert np.all(np.equal(precisions, np.array([0, 0, 0])))

        thrs, precisions = count_precisions_for_fixed_recalls(
            np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0], [1, 0, 0]]),
            np.array([[1, 0, 0], [1, 0, 0], [0, 0, 1], [0, 0, 1]]),
            0.9,
            False,
            3,
        )
        assert np.all(np.equal(thrs, np.array([0, 0, 0])))
        assert np.all(np.equal(precisions, np.array([0, 0, 0])))

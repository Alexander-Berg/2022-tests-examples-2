import json

from nile.api.v1 import clusters, Record
from nile.api.v1 import aggregators as na, extractors as ne
from nile.api.v1.local import StreamSource, ListSink

from taxi.ml.nirvana.common.learning.impl.single_pred.pipeline import NilePipeline
from taxi.ml.nirvana.common.learning import data_splitters


class FeaturesExtractor:
    def __call__(self, request):
        return [1, 2, 3, request['column']]


class TargetExtractor:
    def __call__(self, request, record):
        return record.target


class WeightExtractor:
    def __call__(self, request, target, record):
        return 0.5


class Handler:
    def __init__(self, features_extractor):
        self.features_extractor = features_extractor

    def __call__(self, request):
        return sum(self.features_extractor(request))


class Measures:
    def __call__(self, response, record):
        return {
            '0': response > record.target,
            '1': response > record.target + 1,
            '2': response > record.target + 2,
        }


class Metrics:
    def __call__(self, measures_table):
        return (
            measures_table.project(
                measure_0=ne.custom(lambda measures: measures['0']),
                measure_1=ne.custom(lambda measures: measures['1']),
                measure_2=ne.custom(lambda measures: measures['2']),
            ).aggregate(
                metric_0=na.sum('measure_0'),
                metric_1=na.sum('measure_1'),
                metric_2=na.sum('measure_2'),
            )
        )


class Factory:
    def create_data_splitter(self) -> data_splitters.Base:
        return data_splitters.Const('all')

    def create_request_parser(self):
        return json.loads

    def create_features_extractor(self) -> FeaturesExtractor:
        return FeaturesExtractor()

    def create_target_extractor(self) -> TargetExtractor:
        return TargetExtractor()

    def create_weight_extractor(self) -> WeightExtractor:
        return WeightExtractor()

    def create_handler(self) -> Handler:
        return Handler(self.create_features_extractor())

    def get_handler_files(self):
        return dict()

    def create_response_parser(self):
        return json.loads

    def create_response_dumper(self):
        return json.dumps

    def create_measures(self) -> Measures:
        return Measures()


def test_flow():
    job = clusters.MockCluster().job()

    factory = Factory()

    nile_pipeline = NilePipeline(
        job=job,
        factory=factory,
        data_splits_params={'intensity': 'data', 'output_keys': ['all']},
        dataset_splits_params={'key_field': 'request_id'},
        metrics_load=(
            'common.test_learning_single_pred_flow.Metrics'
        ),
    )

    data_table = job.table('').label('input')
    data_splits = nile_pipeline.create_data_splits(data_table)
    dataset_splits = nile_pipeline.create_dataset_splits(data_splits)
    responses_splits = nile_pipeline.create_responses_splits(data_splits)
    metrics_splits = nile_pipeline.create_metrics_splits(responses_splits)
    assert len(metrics_splits) == 1
    data_splits['all'].put('').label('data')
    dataset_splits['all'].put('').label('dataset')
    responses_splits['all'].put('').label('responses')
    metrics_splits['all'].put('').label('metrics')

    data_output = []
    dataset_output = []
    responses_output = []
    metrics_output = []
    job.local_run(
        sources={
            'input': StreamSource(
                [
                    Record(
                        request_id=1,
                        request=json.dumps(dict(column=2)),
                        target=7,
                    ),
                    Record(
                        request_id=2,
                        request=json.dumps(dict(column=2)),
                        target=6,
                    ),
                    Record(
                        request_id=3,
                        request=json.dumps(dict(column=3)),
                        target=7,
                    ),
                    Record(
                        request_id=4,
                        request=json.dumps(dict(column=3)),
                        target=5,
                    ),
                ],
            ),
        },
        sinks={
            'data': ListSink(data_output),
            'dataset': ListSink(dataset_output),
            'responses': ListSink(responses_output),
            'metrics': ListSink(metrics_output),
        },
    )

    assert data_output == [
        Record(request='{"column": 2}', request_id=1, target=7),
        Record(request='{"column": 2}', request_id=2, target=6),
        Record(request='{"column": 3}', request_id=3, target=7),
        Record(request='{"column": 3}', request_id=4, target=5),
    ]
    assert dataset_output == [
        Record(features=[1, 2, 3, 2], key=1, target=7, weight=0.5),
        Record(features=[1, 2, 3, 2], key=2, target=6, weight=0.5),
        Record(features=[1, 2, 3, 3], key=3, target=7, weight=0.5),
        Record(features=[1, 2, 3, 3], key=4, target=5, weight=0.5),
    ]
    assert responses_output == [
        Record(request='{"column": 2}', request_id=1, response='8', target=7),
        Record(request='{"column": 2}', request_id=2, response='8', target=6),
        Record(request='{"column": 3}', request_id=3, response='9', target=7),
        Record(request='{"column": 3}', request_id=4, response='9', target=5),
    ]
    assert metrics_output == [Record(metric_0=4, metric_1=3, metric_2=1)]

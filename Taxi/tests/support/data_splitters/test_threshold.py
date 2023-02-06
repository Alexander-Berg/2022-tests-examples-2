from ciso8601 import parse_datetime_as_naive

from nile.api.v1 import Record

from projects.common.nile import test_utils
from projects.common.learning.factories import import_object

from projects.support.data_splitters.threshold import DataSplitter


def iter_records(data):
    for elem in data:
        params = {k: test_utils.to_bytes(v) for k, v in elem.items()}
        yield Record(**params)


def test_threshold(load_json):
    threshold = DataSplitter(
        field='creation_dttm',
        threshold=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        comparator=import_object(
            'projects.support.data_splitters.comparators.str_dttm_comparator',
        ),
        le_label='train',
        geq_label='test',
    )
    assert (
        threshold(Record(**{'creation_dttm': '2020-02-02T00:00:00Z'}))
        == 'test'
    )

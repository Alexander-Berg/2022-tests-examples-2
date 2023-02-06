import pytest

from taxi.core import async
from taxi_maintenance.stuff import yt_pbl_garbage_collector


class DummyYtClient(object):
    def __init__(self):
        self.map_reduce_log = []

    def run_map_reduce(self, *args, **kwargs):
        self.map_reduce_log.append(
            (kwargs['source_table'], kwargs['reduce_by'], kwargs['sort_by'])
        )

    def read_table(self, table):
        return iter([])

    def delete_rows(self, table, rows):
        pass

    def create_temp_table(self, *args, **kwargs):
        pass

    def remove(self, *args, **kwargs):
        pass


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_do_stuff(patch):
    yt_client = DummyYtClient()

    @patch('taxi.external.yt_wrapper.get_yt_mapreduce_clients')
    @async.inline_callbacks
    def get_yt_mapreduce_clients(*args, **kwargs):
        yield
        async.return_value([yt_client])

    yield yt_pbl_garbage_collector.do_stuff()

    expected_mr_log = [
        (
            'replica/external/pbl/indexes/clid',
            [
                'alias_id', 'payment_type', 'trust_payment_id',
                'trust_refund_id'
            ],
            [
                'alias_id', 'payment_type', 'trust_payment_id',
                'trust_refund_id', 'csv_updated'
            ],
        ),
        (
            'replica/external/pbl/indexes/db',
            [
                'alias_id', 'payment_type', 'trust_payment_id',
                'trust_refund_id'
            ],
            [
                'alias_id', 'payment_type', 'trust_payment_id',
                'trust_refund_id', 'csv_updated'
            ],
        ),
    ]

    assert sorted(yt_client.map_reduce_log) == expected_mr_log


@pytest.mark.parametrize('rows,expected', [
    ([], []),
    ([{'id': 'foo', 'csv_updated': 1}], []),
    (
        [{'id': 'foo', 'csv_updated': 1}, {'id': 'bar', 'csv_updated': 2}],
        [{'id': 'foo', 'csv_updated': 1}],
    ),
    (
        [{'id': 'foo', 'csv_updated': None}, {'id': 'bar', 'csv_updated': 2}],
        [],
    ),
])
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_exclude_last_reducer(rows, expected, key=None):
    result = list(yt_pbl_garbage_collector._exclude_last_reducer(key, rows))
    assert result == expected

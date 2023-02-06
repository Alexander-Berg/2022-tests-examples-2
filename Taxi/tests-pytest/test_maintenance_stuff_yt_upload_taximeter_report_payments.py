import datetime
import functools
import json

import freezegun
import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import replication
from taxi.util import dates
from taxi.internal.taximeter_reports_map_reduce import orders_payments
from taxi.internal.yt_replication import external_uploads
from taxi_maintenance.stuff import (
    yt_upload_taximeter_report_payments as yt_upload
)

NOW = datetime.datetime(2018, 4, 21, 10)
NOW_TS = dates.timestamp_us(NOW)

TARGETS_INFO = {
    'driver_workshifts': {
        'table_path': 'replica/mongo/struct/driver_workshifts'
    },
    'commission_transactions_struct': {
        'table_path': 'replica/mongo/struct/commission_transactions'
    },
    'childchair_rent_transactions': {
        'table_path': 'replica/mongo/struct/childchair_rent_transactions'
    },
    'taximeter_orders': {
        'table_path': 'replica/postgres/taximeter_orders'
    },
}


@pytest.fixture(autouse=True)
def replication_mock(monkeypatch):
    @async.inline_callbacks
    def get_yt_target_info(target_name, **kwargs):
        yield
        async.return_value(TARGETS_INFO[target_name])

    monkeypatch.setattr(
        replication, 'get_yt_target_info', get_yt_target_info
    )


class _DummyYTClient(object):
    tmp_template = '{}.tmp'

    def __init__(self, data):
        self.data = data

    def exists(self, path):
        table, attr = self._get(path)
        if attr is not None:
            return attr in self.data[table]
        else:
            return table in self.data

    def create(self, _type, path, *args, **kwargs):
        if _type == 'table':
            table, _ = self._get(path)
            self.data[table] = {}

    def remove(self, path, *args, **kwargs):
        assert path.startswith('reports_intermediate_result')
        assert path.endswith('tmp')
        assert '/' not in path
        self.data.pop(path)

    def get(self, path):
        table, attr = self._get(path)
        return self.data[table][attr]

    def set(self, path, value):
        table, attr = self._get(path)
        self.data[table][attr] = value

    def create_temp_table(self, prefix, *args, **kwargs):
        path = self.tmp_template.format(prefix)
        self.data[path] = {}
        return path

    def run_map(self, *args, **kwargs):
        pass

    def run_map_reduce(self, *args, **kwargs):
        pass

    def run_reduce(self, *args, **kwargs):
        pass

    def run_sort(self, *args, **kwargs):
        pass

    def copy(self, _from, to, *args, **kwargs):
        self.data[to.split('/')[-1]] = self.data[_from]

    def run_merge(self, *args, **kwargs):
        pass

    def TablePath(self, *args, **kwargs):
        return

    def insert_rows(self, *args, **kwargs):
        pass

    def read_table(self, *args, **kwargs):
        return ()

    @staticmethod
    def _get(path):
        splitted = path.split('/@')
        splitted[0] = splitted[0].split('/')[-1]
        if len(splitted) == 1:
            return splitted[0], None
        return splitted


@pytest.mark.config(
    YT_REPLICATION_RUNTIME_CLUSTERS=['seneca-sas', 'seneca-man', 'seneca-vla']
)
@pytest.inline_callbacks
def test_do_stuff(patch, monkeypatch):
    monkeypatch.setattr(settings, 'YT_CLUSTER_GROUPS', {
        'runtime': ['seneca-sas', 'seneca-man', 'seneca-vla'],
        'map_reduce': ['hahn', 'arnold'],
    })
    dummy_yt_client = _DummyYTClient({
        'taximeter_report_order_payments': {
            # 2018-04-21 8:00
            'map_reduce_start_timestamp': 1524297600,
        },
        'report_order_payments': {
            'last_updated': 1524304800,
        },
    })

    @patch('taxi.external.yt_wrapper.get_client')
    def get_client(*args, **kwargs):
        return dummy_yt_client

    @patch('taxi.external.yt_wrapper.get_appropriate_bundle')
    def get_appropriate_bundle(*args, **kwargs):
        return ''

    @patch('taxi.internal.yt_tools.dyntables_kit.mount_and_wait')
    def mount_and_wait(yt_client, path):
        pass

    monkeypatch.setattr(external_uploads, 'upload_with_transfer_manager',
                        external_uploads.upload_with_insert_rows)
    expected_yt_data = {
        'taximeter_report_order_payments': {
            'map_reduce_start_timestamp': 1524297600,
        },
        'taximeter_report_park_balances': {
            'map_reduce_start_timestamp': NOW_TS,
        },
        'report_order_payments': {'last_updated': 1524297600},
        'report_park_balances': {'last_updated': NOW_TS},
    }

    with freezegun.freeze_time(NOW, ignore=['']):
        yield yt_upload.do_stuff()

    assert dummy_yt_client.data == expected_yt_data

    with freezegun.freeze_time(
                NOW + datetime.timedelta(minutes=60), ignore=['']):
        yield yt_upload.do_stuff()

    assert dummy_yt_client.data == expected_yt_data


@pytest.mark.parametrize('rows_path,is_map_operation', [
    ('orders_rows_to_map.json', True),
    ('rows_to_reduce.json', False),
])
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_map_reduce(load, rows_path, is_map_operation):
    map_reduce_handler = yield orders_payments._get_map_reduce_handler(
        NOW - datetime.timedelta(hours=3)
    )
    if is_map_operation:
        yt_operation = map_reduce_handler.get_mapper()
    else:  # reduce part
        yt_operation = functools.partial(
            map_reduce_handler.get_reducer(), None
        )

    all_rows = json.loads(load(rows_path))
    for test_num, rows in enumerate(all_rows):
        result = []
        processed = yt_operation(rows['input'])
        result.extend(processed)
        assert result == rows['expected'], (
            '%s: test num %d failed' % (rows_path, test_num)
        )

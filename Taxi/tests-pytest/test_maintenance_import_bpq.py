import datetime

import pytest

from taxi import config
from taxi.core import db
from taxi_maintenance.stuff import import_bpq


@pytest.mark.now('2018-06-20 10:30:00+0300')
@pytest.mark.config(BPQ_ENABLE=True)
@pytest.inline_callbacks
def test_import_bpq(patch, monkeypatch):

    # we always need fresh config
    monkeypatch.setattr(config.BPQ_MOST_RECENT_LOADED_TS,
                        'get', config.BPQ_MOST_RECENT_LOADED_TS.get_fresh)

    class MockYtClient(object):
        def __init__(self):
            self._data = None
            self._expected_from = None

        def set_data(self, data, expected_from):
            self._data = data
            self._expected_from = expected_from

        def read_table(self, path):
            assert path is self
            assert self._data is not None
            return iter(self._data)

        def TablePath(self, path, columns=None, lower_key=None):
            assert (path ==
                    '//home/taxi-analytics/efficiency/production/webdrivers')
            assert set(columns) == {'dttm_utc_1_min', 'driver_id'}
            assert lower_key == self._expected_from
            return self

    yt_client = MockYtClient()

    @patch('taxi.external.yt_wrapper.get_client')
    def test_get_cleint(cluster):
        assert cluster == 'hahn'
        return yt_client

    data = [
        {
            'driver_id': '1_a',
            'dttm_utc_1_min': '2018-06-20 07:16:00'
        },
        {
            'driver_id': '1_b',
            'dttm_utc_1_min': '2018-06-20 07:17:00'
        },
        {
            'driver_id': '2_a',
            'dttm_utc_1_min': '2018-06-20 07:18:00'
        },
        {
            'driver_id': '2_c',
            'dttm_utc_1_min': '2018-06-20 07:18:00'
        },
        {
            'driver_id': '3_a',
            'dttm_utc_1_min': '2018-06-20 07:18:40'
        }
    ]
    yt_client.set_data(data, '2018-06-20 07:15:00')

    yield import_bpq.do_stuff()

    expected_bad_positions = sorted([
        {
            '_id': 'pd_id_AAA',
            'updated': datetime.datetime(2018, 6, 20, 7, 18),
        },
        {
            '_id': 'pd_id_BBB',
            'updated': datetime.datetime(2018, 6, 20, 7, 17),
        },
        {
            '_id': 'pd_id_CCC',
            'updated': datetime.datetime(2018, 6, 20, 7, 18),
        }
    ])
    actual_bad_positions = yield db.bad_position_quality.find().run()
    for expected, actual in zip(expected_bad_positions, actual_bad_positions):
        for key in expected:
            assert actual[key] == expected[key]
    actual_most_recent_ts = yield config.BPQ_MOST_RECENT_LOADED_TS.get()
    assert actual_most_recent_ts == '2018-06-20 07:18:40'

    data = [
        {
            'driver_id': '1_a',
            'dttm_utc_1_min': '2018-06-20 07:19:00'
        },
        {
            'driver_id': '1_d',
            'dttm_utc_1_min': '2018-06-20 07:19:00'
        }
    ]
    yt_client.set_data(data, actual_most_recent_ts)

    yield import_bpq.do_stuff()

    expected_bad_positions = sorted([
        {
            '_id': 'pd_id_AAA',
            'updated': datetime.datetime(2018, 6, 20, 7, 19),
        },
        {
            '_id': 'pd_id_BBB',
            'updated': datetime.datetime(2018, 6, 20, 7, 17),
        },
        {
            '_id': 'pd_id_CCC',
            'updated': datetime.datetime(2018, 6, 20, 7, 18),
        },
        {
            '_id': 'pd_id_DDD',
            'updated': datetime.datetime(2018, 6, 20, 7, 19),
        },
    ])
    actual_bad_positions = yield db.bad_position_quality.find().run()
    for expected, actual in zip(expected_bad_positions, actual_bad_positions):
        for key in expected:
            assert actual[key] == expected[key]
    actual_most_recent_ts = yield config.BPQ_MOST_RECENT_LOADED_TS.get()
    assert actual_most_recent_ts == '2018-06-20 07:19:00'

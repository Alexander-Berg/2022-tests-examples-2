# coding: utf8

from __future__ import unicode_literals

import datetime

import pytest

from taxi.external import yt_wrapper
from taxi.internal.yt_tools import dyntables_kit
from taxi_maintenance.stuff import yt_export_sms_report as yt_export


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_functions(monkeypatch, mock):
    stat_dict = yield yt_export._load_sms_history(
        start_dt=datetime.datetime(2018, 1, 1, 0, 0, 0),
        stop_dt=datetime.datetime(2018, 2, 1, 0, 0, 0)
    )
    assert len(stat_dict) == 3

    task_ids = stat_dict.keys()
    assert set(task_ids) == {1107548, 1047454, 1107549}

    sms_senders = {item['login'] for item in stat_dict.itervalues()}
    assert sms_senders == {'piskarev', 'nevladov'}

    def _dummy_mount_and_wait(client, path):
        pass

    class DummyYtClient(object):
        class TablePath():
            def __init__(self, *args, **kwargs):
                pass

        def exists(self, path):
            return True

        def create(*args, **kwargs):
            pass

        @mock
        def delete_rows(path, data):
            pass

        @mock
        def insert_rows(path, data):
            pass

    def _dummy_get_yt_clients(*args, **kwargs):
        return [DummyYtClient()]

    monkeypatch.setattr(
        yt_wrapper,
        'get_yt_mapreduce_clients',
        _dummy_get_yt_clients,
    )

    monkeypatch.setattr(
        dyntables_kit,
        'mount_and_wait',
        _dummy_mount_and_wait,
    )

    yt_export._export_sms_report(stat_dict, None)

    delete_rows_args = DummyYtClient.delete_rows.calls[0]
    assert delete_rows_args['data'] == [
        {'date': '2018-01-31'},
        {'date': '2018-01-01'},
    ]

    insert_rows_args = DummyYtClient.insert_rows.calls[0]
    assert insert_rows_args['data'] == [
        {
            'task_id': 1107548,
            'date': '2018-01-31',
            'time': '21:04:00',
            'text': 'Вы нужны в Домодедово: много заказов, спрос растет!',
            'from': 'piskarev',
            'to': '+79060768500,+79688037171,+79295500505',
            'total': 3,
            'complete': 2,
        },
        {
            'task_id': 1107549,
            'date': '2018-01-31',
            'time': '21:04:00',
            'text': 'Вы нужны во Внукове: много заказов, спрос растет!',
            'from': 'nevladov',
            'to': '+79060768500',
            'total': 1,
            'complete': 0,
        },
        {
            'task_id': 1047454,
            'date': '2018-01-01',
            'time': '19:40:00',
            'text': 'Вы нужны в Шереметьево: много заказов, спрос растет!',
            'from': 'piskarev',
            'to': '+79152847842,+79197611364,+79252627051',
            'total': 3,
            'complete': 3,
        }
    ]

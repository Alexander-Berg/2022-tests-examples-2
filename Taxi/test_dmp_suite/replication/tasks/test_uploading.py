import argparse
import pathlib
import typing as tp
from datetime import datetime
from unittest import mock

import pytest
from mock import patch

import sources_root
from connection import ctl
from dmp_suite.ctl import CTL_LAST_LOAD_DATE, CTL_LAST_SYNC_DATE
from dmp_suite.replication import integration
from dmp_suite.replication.tasks.uploading import (BaseIncrementSource, BaseSnapshotSource,
                                                   FunctionIncrementSource, SingleTargetIncrementTask,
                                                   SingleTargetSnapshotTask)
from dmp_suite.task.execution import run_task
from dmp_suite.yt.dyntable_operation.dynamic_table_loaders import GenericDataIncrement
from test_dmp_suite.replication import test_utils
from test_dmp_suite.task.utils import WrapCtlMock

YAMLS_PATH = pathlib.Path(
    sources_root.SOURCES_ROOT,
    'dmp_suite/test_dmp_suite/replication/replication_yaml/test_source',
)

REPLICATION_DATA = [
    {
        'id': 1,
        'upload_ts': '2020-08-03 14:56:01',
        'data': {
            'id': 1,
            'a': 'b',
            'c': 3,
            'd': False,
            'e': [1, 'f'],
            'some_decimal': {
                '$decimal': '1.23'
            },
            'some_date': {
                '$datetime_date': '2020-10-06'
            },
            'some_datetime': {
                '$datetime': '2020-10-06 04:56:01Z'
            },
            'updated_at': {
                '$datetime': '2020-08-03 14:56:01'
            },
        }
    },
    {
        'id': 2,
        'upload_ts': '2020-08-03 14:56:02',
        'data': {
            'id': 2,
            'a': 'b',
            'c': 3,
            'd': False,
            'e': [1, 'f'],
            'some_decimal': {
                '$decimal': '1.234'
            },
            'some_date': {
                '$datetime_date': '2020-10-06'
            },
            'some_datetime': {
                '$datetime': '2020-10-06 04:56:01'
            },
            'updated_at': {
                '$datetime': '2020-08-03 14:56:02'
            },
        }
    },
    {
        'id': 3,
        'upload_ts': '2020-08-03 14:56:03',
        'data': {
            'id': 3,
            'a': 'b',
            'c': 3,
            'd': False,
            'e': [1, 'f'],
            'some_decimal': {
                '$decimal': '1.2345'
            },
            'some_date': {
                '$datetime_date': '2020-10-06'
            },
            'some_datetime': {
                '$datetime': '2020-10-06 04:56:01+03:00'
            },
            'updated_at': {
                '$datetime': '2020-08-03 14:56:03'
            },
        }
    },
]


def do_nothing(_, __):
    return REPLICATION_DATA


def ctl_mock():
    ctl = WrapCtlMock()
    return patch('connection.ctl.get_ctl', return_value=ctl)


class DummyBaseIncrementSource(BaseIncrementSource):
    def read(self, args, current_ctl_value):
        if not current_ctl_value:
            raise ValueError
        increment = GenericDataIncrement(records=REPLICATION_DATA, last_load_date=datetime(2020, 11, 14))
        yield increment


@mock.patch(
    'dmp_suite.datetime_utils.utcnow',
    mock.MagicMock(return_value=datetime(2020, 11, 15, 0, 0)),
)
def test_single_target_increment_task_ctl():
    rule_path = f'{YAMLS_PATH}/test_uploading.yaml'

    task = SingleTargetIncrementTask(
        name='test_single_target_increment_task_ctl',
        source=DummyBaseIncrementSource(
            description='test_single_target_increment_task_ctl',
        ),
        rule_path=rule_path,
        key_fields=('timestamp',),
    )
    rule = integration.get_rule_by_path(rule_path)

    with mock.patch(
            'connection.replication_api.get_client',
            return_value=test_utils.ApiMock([], REPLICATION_DATA),
    ), \
         mock.patch('dmp_suite.replication.data_uploading.data_uploader.SnapshotUploader._push_chunk',
                    return_value=None), \
         ctl_mock():
        ctl_connect = ctl.get_ctl().replication
        ctl_connect.set_param(rule, CTL_LAST_LOAD_DATE, datetime(2020, 11, 11))
        run_task(task)
        new_ctl = ctl_connect.get_param(rule, CTL_LAST_LOAD_DATE)
        assert new_ctl == datetime(2020, 11, 14)
        assert ctl_connect.get_param(rule, CTL_LAST_SYNC_DATE) == datetime(2020, 11, 15, 0, 0)


class DummyBaseSnapshotSource(BaseSnapshotSource):
    def read(self, args: argparse.Namespace) -> tp.Iterable[tp.Dict]:
        return REPLICATION_DATA


@mock.patch(
    'dmp_suite.datetime_utils.utcnow',
    mock.MagicMock(return_value=datetime(2020, 11, 15, 0, 0)),
)
def test_single_target_snapshot_task_ctl():
    rule_path = f'{YAMLS_PATH}/test_uploading.yaml'
    task = SingleTargetSnapshotTask(
        name='test_single_target_snapshot_task_ctl',
        source=DummyBaseSnapshotSource(
            description='test_single_target_snapshot_task_ctl',
        ),
        rule_path=rule_path,
        key_fields=('timestamp',),
    )
    rule = integration.get_rule_by_path(rule_path)

    with mock.patch(
            'connection.replication_api.get_client',
            return_value=test_utils.ApiMock([], REPLICATION_DATA),
    ), \
         mock.patch('dmp_suite.replication.data_uploading.data_uploader.SnapshotUploader._push_chunk',
                    return_value=None), \
         ctl_mock():
        ctl_connect = ctl.get_ctl().replication
        run_task(task)
        assert ctl_connect.get_param(rule, CTL_LAST_LOAD_DATE) is None
        assert ctl_connect.get_param(rule, CTL_LAST_SYNC_DATE) == datetime(2020, 11, 15, 0, 0)


def test_reader_func_validation():
    rule_path = f'{YAMLS_PATH}/test_uploading.yaml'

    def right_reader_func(_, __):
        yield GenericDataIncrement(records=REPLICATION_DATA, last_load_date=datetime(2020, 11, 14))

    FunctionIncrementSource(
        description='test_single_target_increment_task_ctl',
        reader_func=right_reader_func
    )

    def wrong_reader_func(_, __):
        return GenericDataIncrement(records=REPLICATION_DATA, last_load_date=datetime(2020, 11, 14))

    with pytest.raises(ValueError):
        FunctionIncrementSource(
            description='test_single_target_increment_task_ctl',
            reader_func=wrong_reader_func
        )

import argparse
import contextlib
import datetime as dt
import decimal
import functools
import json
import inspect
import mock
import multiprocessing as mp
import os
import pickle
import pytest

import pytz
import dateutil.tz as tz
from requests import models

import sources_root
import typing as tp
import urllib3.exceptions

from connection import yt as yt_connection
from connection import ctl as ctl_connection
from dmp_suite import yt
from dmp_suite import ctl
from dmp_suite import datetime_utils as dtu
from dmp_suite.replication.api import errors
from dmp_suite.replication.tasks import streaming
from dmp_suite.replication.tasks import uploading
from dmp_suite.task.execution import ExecutionArgs, run_task
from dmp_suite.yt import etl
from dmp_suite.yt import operation
from dmp_suite.yt.dyntable_operation import dynamic_table_loaders

from test_dmp_suite.replication import test_utils
from test_dmp_suite.task import utils as task_test_utils


def ctl_mock():
    ctl = task_test_utils.WrapCtlMock()
    return mock.patch('connection.ctl.get_ctl', return_value=ctl)


DEADLOCK_DETECTION_THRESHOLD = 60.0

YAMLS_PATH = os.path.join(
    sources_root.SOURCES_ROOT,
    'dmp_suite/test_dmp_suite/replication/replication_yaml/test_source',
)


class DummyTable(etl.ETLTable):
    __unique_keys__ = True
    __location_cls__ = yt.NotLayeredYtLocation
    __layout__ = yt.NotLayeredYtLayout('test', 'test')

    id = yt.Int(sort_key=True, sort_position=0)
    a = yt.String()
    c = yt.Int()
    d = yt.Boolean()
    e = yt.Any()
    updated_at = yt.Datetime()


class DummyDynamicTable(DummyTable):
    __dynamic__ = True


def test_create_error():
    def create_response(code, reason, content):
        resp = models.Response()
        resp.reason = reason
        resp.status_code = code
        if isinstance(content, str):
            resp._content = content.encode()
        else:
            resp._content = json.dumps(content).encode()
        return resp

    err = errors.get_error(
        response=create_response(400, 'Bad request', 'Forbidden'),
    )
    assert err.__class__ == errors.ApiError
    assert str(err) == 'Bad request 400: Forbidden'

    err = errors.get_error(
        response=create_response(400, 'Bad request', {'code': 'inactive-target-error', 'k': 'v'}),
    )
    assert err.__class__ == errors.InactiveTargetError
    assert str(err) == 'Bad request 400: {"code": "inactive-target-error", "k": "v"}'

    err = errors.get_error(
        response=create_response(400, 'Bad request', {'code': 'put-data-personal-strict', 'k': 'v'}),
    )
    assert err.__class__ == errors.PutDataPersonalStrictError
    assert str(err) == 'Bad request 400: {"code": "put-data-personal-strict", "k": "v"}'


def test_error_pickling_unpickling():
    resp = models.Response()
    err = errors.ApiError('msg', response=resp)

    pickled = pickle.dumps(err)
    unpickled = pickle.loads(pickled)

    assert unpickled.__class__ == errors.ApiError
    assert str(unpickled) == 'msg'


class TestStreamingInitErrors:
    def test_error_on_task_creation_with_static_destination(self):
        rule_path = f'{YAMLS_PATH}/test_rule_w_ext_destination.yaml'
        with pytest.raises(streaming.TableTypeUnsupportedError):
            streaming.OdsStreamingTask(
                name='name',
                extractors={},
                target_table=DummyTable,
                rule_path=rule_path,
                destination_name='test_rule_w_2_ext_destinations_raw_ext',
            )

    def test_error_on_task_creation_with_wrong_destination(self):
        rule_path = f'{YAMLS_PATH}/test_rule_w_2_ext_destinations.yaml'
        with pytest.raises(streaming.WrongDestinationError):
            streaming.OdsStreamingTask(
                name='name',
                extractors={},
                target_table=DummyDynamicTable,
                rule_path=rule_path,
                destination_name='123',
            )

    def test_error_on_task_creation_with_wrong_destination_type(self):
        rule_path = f'{YAMLS_PATH}/test_rule_w_yt_destination.yaml'
        with pytest.raises(streaming.UnsupportedDestinationTypeError):
            streaming.OdsStreamingTask(
                name='name',
                extractors={},
                target_table=DummyDynamicTable,
                rule_path=rule_path,
                destination_name='test_rule_w_yt_destination_raw',
            )


JSON_REPLICATION_DATA = [
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

JSON_EXPECTED_DATA = [
    {
        'id': 1,
        'a': 'b',
        'c': 3,
        'd': False,
        'e': [1, 'f'],
        'some_decimal': decimal.Decimal('1.23'),
        'some_date': dt.datetime(2020, 10, 6, 0, 0),
        'some_datetime': dt.datetime(2020, 10, 6, 4, 56, 1, 0, pytz.UTC),
        'updated_at': dt.datetime(2020, 8, 3, 14, 56, 1),
    },
    {
        'id': 2,
        'a': 'b',
        'c': 3,
        'd': False,
        'e': [1, 'f'],
        'some_decimal': decimal.Decimal('1.234'),
        'some_date': dt.datetime(2020, 10, 6, 0, 0),
        'some_datetime': dt.datetime(2020, 10, 6, 4, 56, 1, 0),
        'updated_at': dt.datetime(2020, 8, 3, 14, 56, 2),
    },
    {
        'id': 3,
        'a': 'b',
        'c': 3,
        'd': False,
        'e': [1, 'f'],
        'some_decimal': decimal.Decimal('1.2345'),
        'some_date': dt.datetime(2020, 10, 6, 0, 0),
        'some_datetime': dt.datetime(
            2020, 10, 6, 4, 56, 1, 0, tz.tzoffset(None, 10800)
        ),
        'updated_at': dt.datetime(2020, 8, 3, 14, 56, 3),
    },
]


RAW_JSON_REPLICATION_DATA = [
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
                '$a': {
                    'raw_type': 'decimal'
                },
                '$v': '1.23'
            },
            'some_date': {
                '$a': {
                    'raw_type': 'date'
                },
                '$v': '2020-10-06'
            },
            'some_datetime': {
                '$a': {
                    'raw_type': 'datetime'
                },
                '$v': '2020-10-06T04:56:01+00:00'
            },
            'updated_at': {
                '$a': {
                    'raw_type': 'datetime'
                },
                '$v': '2020-08-03T14:56:01'
            },
            'some_bytes': {
                '$a': {
                    'raw_type': 'bytes'
                },
                '$v': 'dGVzdA=='
            },
            'some_time': {
                '$a': {
                    'raw_type': 'time'
                },
                '$v': '16:20'
            },
            'some_timedelta': {
                '$a': {
                    'raw_type': 'timedelta',
                    'raw_attrs': {
                        'seconds': 3600,
                        'microseconds': 100
                    }
                },
                '$v': '3600'
            }
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
                '$a': {
                    'raw_type': 'decimal'
                },
                '$v': '1.234'
            },
            'some_date': {
                '$a': {
                    'raw_type': 'date'
                },
                '$v': '2020-10-06'
            },
            'some_datetime': {
                '$a': {
                    'raw_type': 'datetime'
                },
                '$v': '2020-10-06T04:56:01'
            },
            'updated_at': {
                '$a': {
                    'raw_type': 'datetime'
                },
                '$v': '2020-08-03T14:56:02'
            },
            'some_bytes': {
                '$a': {
                    'raw_type': 'bytes'
                },
                '$v': 'dGVzdA=='
            },
            'some_time': {
                '$a': {
                    'raw_type': 'time'
                },
                '$v': '16:20'
            },
            'some_timedelta': {
                '$a': {
                    'raw_type': 'timedelta',
                    'raw_attrs': {
                        'seconds': 3600,
                        'microseconds': 100
                    }
                },
                '$v': '3600'
            }
        }
    },
    {
        'id': 3,
        'upload_ts': '2020-08-03T14:56:03',
        'data': {
            'id': 3,
            'a': 'b',
            'c': 3,
            'd': False,
            'e': [1, 'f'],
            'some_decimal': {
                '$a': {
                    'raw_type': 'decimal'
                },
                '$v': '1.2345'
            },
            'some_date': {
                '$a': {
                    'raw_type': 'date'
                },
                '$v': '2020-10-06'
            },
            'some_datetime': {
                '$a': {
                    'raw_type': 'datetime'
                },
                '$v': '2020-10-06T04:56:01+03:00'
            },
            'updated_at': {
                '$a': {
                    'raw_type': 'datetime'
                },
                '$v': '2020-08-03T14:56:03'
            },
            'some_bytes': {
                '$a': {
                    'raw_type': 'bytes'
                },
                '$v': 'dGVzdA=='
            },
            'some_time': {
                '$a': {
                    'raw_type': 'time'
                },
                '$v': '16:20'
            },
            'some_timedelta': {
                '$a': {
                    'raw_type': 'timedelta',
                    'raw_attrs': {
                        'seconds': 3620,
                        'microseconds': 100
                    }
                },
                '$v': '3620'
            }
        }
    },
]


RAW_JSON_EXPECTED_DATA = [
    {
        'id': 1,
        'a': 'b',
        'c': 3,
        'd': False,
        'e': [1, 'f'],
        'some_decimal': decimal.Decimal('1.23'),
        'some_date': dt.date(2020, 10, 6),
        'some_datetime': dt.datetime(2020, 10, 6, 4, 56, 1, 0, pytz.UTC),
        'updated_at': dt.datetime(2020, 8, 3, 14, 56, 1),
        'some_bytes': b'test',
        'some_time': dt.time(16, 20),
        'some_timedelta': dt.timedelta(hours=1, microseconds=100),
    },
    {
        'id': 2,
        'a': 'b',
        'c': 3,
        'd': False,
        'e': [1, 'f'],
        'some_decimal': decimal.Decimal('1.234'),
        'some_date': dt.date(2020, 10, 6),
        'some_datetime': dt.datetime(2020, 10, 6, 4, 56, 1, 0),
        'updated_at': dt.datetime(2020, 8, 3, 14, 56, 2),
        'some_bytes': b'test',
        'some_time': dt.time(16, 20),
        'some_timedelta': dt.timedelta(hours=1, microseconds=100),
    },
    {
        'id': 3,
        'a': 'b',
        'c': 3,
        'd': False,
        'e': [1, 'f'],
        'some_decimal': decimal.Decimal('1.2345'),
        'some_date': dt.date(2020, 10, 6),
        'some_datetime': dt.datetime(
            2020, 10, 6, 4, 56, 1, 0, tz.tzoffset(None, 10800)
        ),
        'updated_at': dt.datetime(2020, 8, 3, 14, 56, 3),
        'some_bytes': b'test',
        'some_time': dt.time(16, 20),
        'some_timedelta': dt.timedelta(hours=1, seconds=20, microseconds=100),
    },
]


def _ctl_field_converter(value):
    return dtu.msk2utc(value).replace(tzinfo=None)


def run_test_in_different_process(test):
    @functools.wraps(test)
    def decorator(*args, **kwargs):
        errors_queue = mp.Queue()

        def tst_wrapper(eq):
            try:
                test(*args, **kwargs)
            except Exception as e:
                eq.put(e)
                raise

        process = mp.Process(target=tst_wrapper, args=(errors_queue,))
        process.start()
        process.join(DEADLOCK_DETECTION_THRESHOLD)

        if process.exitcode is None:
            process.kill()
            raise RuntimeError(
                'Probable deadlock detected, further investigation needed',
            )

        if process.exitcode != 0:
            exc = errors_queue.get_nowait()
            raise RuntimeError('Test failed') from exc

        process.close()
    return decorator


class TestStreaming:

    def make_task(self, **kwargs):
        merged_kwargs = dict(
            name='dummy',
            target_table=DummyDynamicTable,
            extractors={},
            rule_path=f'{YAMLS_PATH}/test_rule_w_ext_destination.yaml',
            destination_name='test_rule_w_ext_destinations_raw_ext',
            ctl_field_converter=_ctl_field_converter,
            work_timeout=10,
        )

        merged_kwargs.update(kwargs)
        return streaming.OdsStreamingTask(**merged_kwargs)

    @contextlib.contextmanager
    def _patch_task_and_env(
            self, task, *,
            api_mock,
            # Тут мы просто вызываем list, чтобы "размотать" items
            # и провернуть всю цепочку обработки айтемов, полученных
            # от API репликации:
            upload_data_to_yt=list,
            other_mocks: tp.Optional[tp.List] = None
    ):
        context_managers = []
        with contextlib.ExitStack() as stack:
            context_managers.append(
                mock.patch.object(
                    task,
                    '_get_api_client',
                    test_utils.PicklableMock(return_value=api_mock),
                ),
            )

            context_managers.append(
                mock.patch.object(
                    task,
                    '_upload_data_to_yt',
                    test_utils.PicklableMock(side_effect=upload_data_to_yt),
                ),
            )

            context_managers.append(
                mock.patch.object(
                    task,
                    'run_in_current_process',
                    test_utils.PicklableMock(
                        side_effect=task.run_in_current_process,
                    ),
                ),
            )

            context_managers.append(
                mock.patch.object(
                    task,
                    'run_in_process_pool',
                    test_utils.PicklableMock(
                        side_effect=task.run_in_process_pool,
                    ),
                ),
            )

            context_managers.append(ctl_mock())

            if other_mocks is not None:
                for m in other_mocks:
                    context_managers.append(m)

            for cm in context_managers:
                stack.enter_context(cm)

            yield task

    def test_single_process_load_is_run_for_queue_wo_partitions(self):
        api_mock = test_utils.ApiMock([], JSON_REPLICATION_DATA)

        with self._patch_task_and_env(
                self.make_task(),
                api_mock=api_mock,
        ) as task:
            task._run_task(argparse.Namespace())
            task.run_in_current_process.assert_called_once()
            task.run_in_process_pool.assert_not_called()

    @run_test_in_different_process
    def test_multi_process_load_is_run_for_queue_w_partitions(self):
        partitions = ['1', '2']
        api_mock = test_utils.ApiMock(partitions, JSON_REPLICATION_DATA)

        with self._patch_task_and_env(self.make_task(), api_mock=api_mock) as task:
            task._run_task(argparse.Namespace())
            call_partitions = [
                call[0][1] for call in task.run_in_process_pool.call_args_list
            ]

            assert len(call_partitions) == 1
            assert call_partitions[0] == partitions

    def test_last_sync_date_is_set(self):
        api_mock = test_utils.ApiMock([], JSON_REPLICATION_DATA)
        with self._patch_task_and_env(
                self.make_task(),
                api_mock=api_mock,
        ) as task:
            ctl_obj = ctl_connection.get_ctl().yt
            current_ctl = ctl_obj.get_param(
                DummyDynamicTable, ctl.CTL_LAST_SYNC_DATE,
            )
            assert current_ctl is None
            with mock.patch(
                    'dmp_suite.datetime_utils.utcnow',
                    return_value=dt.datetime(2020, 8, 4, 0, 0),
            ):
                task._run_task(argparse.Namespace())
            new_ctl = ctl_obj.get_param(
                DummyDynamicTable, ctl.CTL_LAST_SYNC_DATE,
            )
            assert new_ctl == dt.datetime(2020, 8, 4, 0, 0)

    def test_extractors_pickling_unpickling(self):
        extractors = {
            'a': 'b',
            'c': lambda doc: doc['f'],
        }
        task = streaming.OdsStreamingTask(
            name='dummy',
            target_table=DummyDynamicTable,
            extractors=extractors,
            rule_path=f'{YAMLS_PATH}/test_rule_w_ext_destination.yaml',
            destination_name='test_rule_w_ext_destinations_raw_ext',
        )
        assert isinstance(task._extractors, bytes)

        unpickled_extractors = task.extractors
        assert set(extractors.keys()) == set(unpickled_extractors.keys())

        for name, original_extractor in extractors.items():
            unpickled_extractor = unpickled_extractors[name]
            if callable(original_extractor):
                assert (
                    inspect.signature(original_extractor)
                    == inspect.signature(unpickled_extractor)
                )
                assert (
                    inspect.getsource(original_extractor)
                    == inspect.getsource(unpickled_extractor)
                )
            else:
                assert unpickled_extractor == original_extractor

    @run_test_in_different_process
    @pytest.mark.parametrize('partitions', [
        ([]),
        (['1', '2']),
    ])
    def test_ctl_is_set(self, partitions):
        api_mock = test_utils.ApiMock(partitions, JSON_REPLICATION_DATA)

        with self._patch_task_and_env(
                self.make_task(),
                api_mock=api_mock,
        ) as task:
            ctl_obj = ctl_connection.get_ctl().yt
            current_ctl = ctl_obj.get_param(
                DummyDynamicTable, ctl.CTL_LAST_LOAD_DATE,
            )
            assert current_ctl is None

            task._run_task(argparse.Namespace())

            if not partitions:
                # we use multiprocessing, so we have different objects there
                api_mock.queue_read.assert_called()

            new_ctl = ctl_obj.get_param(
                DummyDynamicTable, ctl.CTL_LAST_LOAD_DATE,
            )
            assert new_ctl == dt.datetime(2020, 8, 3, 11, 56, 3)

    @run_test_in_different_process
    @pytest.mark.parametrize('partitions', [
        ([]),
        (['1', '2']),
    ])
    def test_ctl_is_not_decreased(self, partitions):
        api_mock = test_utils.ApiMock(partitions, JSON_REPLICATION_DATA)

        with self._patch_task_and_env(
                self.make_task(),
                api_mock=api_mock,
        ) as task:
            ctl_obj = ctl_connection.get_ctl().yt
            original_ctl = dt.datetime(4444, 8, 3, 11, 56, 3)

            ctl_obj.set_param(
                DummyDynamicTable, ctl.CTL_LAST_LOAD_DATE, original_ctl
            )

            current_ctl = ctl_obj.get_param(
                DummyDynamicTable, ctl.CTL_LAST_LOAD_DATE,
            )
            assert current_ctl == original_ctl

            task._run_task(argparse.Namespace())

            if not partitions:
                # we use multiprocessing, so we have different objects there
                api_mock.queue_read.assert_called()

            new_ctl = ctl_obj.get_param(
                DummyDynamicTable, ctl.CTL_LAST_LOAD_DATE,
            )
            assert new_ctl == original_ctl

    @run_test_in_different_process
    @pytest.mark.parametrize('partitions', [
        ([]),
        (['1', '2']),
    ])
    def test_loading_data_without_ctl_field_leads_to_error(self, partitions):
        api_mock = test_utils.ApiMock(partitions, JSON_REPLICATION_DATA)

        with self._patch_task_and_env(
                self.make_task(ctl_data_field='dummy_field'),
                api_mock=api_mock,
        ) as task:

            if partitions:
                with pytest.raises(streaming.PartitionDataUploadError):
                    task._run_task(argparse.Namespace())
            else:
                with pytest.raises(streaming.InvalidDataError):
                    task._run_task(argparse.Namespace())

            if not partitions:
                api_mock.queue_read.assert_called()

    @pytest.mark.parametrize('raw_data, output_format, expected_data, compressed', [
        (JSON_REPLICATION_DATA, 'json', JSON_EXPECTED_DATA, False),
        (RAW_JSON_REPLICATION_DATA, 'raw_json', RAW_JSON_EXPECTED_DATA, False),
        (JSON_REPLICATION_DATA, 'json', JSON_EXPECTED_DATA, True),
        (RAW_JSON_REPLICATION_DATA, 'raw_json', RAW_JSON_EXPECTED_DATA, True),
    ])
    def test_load(self, raw_data, output_format, expected_data, compressed):
        api_mock = test_utils.ApiMock(
            [],
            raw_data,
            output_format=output_format,
            compressed=compressed,
        )

        uploaded = []
        num_updates = 0

        def upload(items):
            nonlocal uploaded, num_updates
            num_updates += 1
            uploaded.extend(list(items))

        with self._patch_task_and_env(
            self.make_task(),
            api_mock=api_mock,
            upload_data_to_yt=upload,
        ) as task:
            task._run_task(argparse.Namespace())
            api_mock.queue_read.assert_called()

            # Так как у таска задан work_timeout = 10
            # а ApiMock всегда отдаёт try_next_read_after = 1,
            # то за 10 секунд должно случиться около 10 обновлений
            assert num_updates == 10
            assert uploaded
            # Так как queue_read вызовется 10 раз, и каждый
            # раз он будет возвращать одни и те же записи, то
            # в uploaded их будет в 10 раз больше.
            # для сравнения возьмём количество записей
            # равное числу записей в одной странице
            # отдаваемой ApiMock:
            page_size = len(raw_data)
            assert uploaded[:page_size] == expected_data

    def test_connection_reset_retries(self):
        api_mock = test_utils.ApiMock(
            [],
            JSON_REPLICATION_DATA,
            # На первый запрос API должно выдать ошибку.
            errors=[urllib3.exceptions.ProtocolError('Connection reset by peer')],
        )

        with self._patch_task_and_env(
                self.make_task(),
                api_mock=api_mock,
        ) as task:
            task._run_task(argparse.Namespace())
            task.run_in_current_process.assert_called_once()
            task.run_in_process_pool.assert_not_called()


class SingleStreamingTestTable(yt.ETLTable):
    __unique_keys__ = True
    __dynamic__ = True
    __location_cls__ = yt.NotLayeredYtLocation
    __layout__ = yt.NotLayeredYtLayout('test', 'test')

    id = yt.Int(sort_key=True, sort_position=0)
    some_string = yt.String()
    some_decimal = yt.String()
    some_date = yt.Date()
    some_datetime = yt.Datetime()
    some_timedelta = yt.String()
    utc_updated_dttm = yt.Datetime()


def _streaming_reader_func(args, current_ctl_value):
    yield dynamic_table_loaders.GenericDataIncrement(
        records=[
            {
                'id': 1,
                'some_string': 'abc',
                'some_decimal': decimal.Decimal('1.23'),
                'some_date': dt.date(2020, 10, 6),
                'some_datetime': dt.datetime(
                    2020, 10, 6, 4, 56, 1, 0, pytz.UTC
                ),
                'some_timedelta': dt.timedelta(hours=1, microseconds=100),
                'msk_updated_dttm': dt.datetime(2021, 4, 27, 15, 1, 3),
            },
            {
                'id': 2,
                'some_string': 'abc',
                'some_decimal': decimal.Decimal('1.23'),
                'some_date': dt.date(2020, 10, 6),
                'some_datetime': dt.datetime(
                    2020, 10, 6, 4, 56, 1, 0, pytz.UTC
                ),
                'some_timedelta': dt.timedelta(hours=1, microseconds=100),
                'msk_updated_dttm': dt.datetime(2021, 4, 27, 15, 1, 4),
            },
        ],
        last_load_date=dt.datetime(2021, 4, 27, 12, 1, 4),
    )


def _streaming_pull_assert(name, rule_path, target_table, destination_name):
    pull_task = streaming.OdsStreamingTask(
        name=name,
        target_table=target_table,
        extractors={
            'utc_updated_dttm': lambda d: dtu.msk2utc(d['msk_updated_dttm']),
        },
        rule_path=rule_path,
        destination_name=destination_name,
        ctl_data_field='msk_updated_dttm',
        ctl_field_converter=lambda v: dtu.msk2utc(v).replace(tzinfo=None),
        work_timeout=10,
    )
    pull_task._run_task(argparse.Namespace())
    table_path = yt.YTMeta(target_table).target_path()

    yt_connection.get_yt_client().freeze_table(table_path, sync=True)
    written_data = list(operation.read_yt_table(table_path))

    for row in written_data:
        del row['etl_updated']

    assert written_data == [
        {
            'id': 1,
            'some_date': '2020-10-06',
            'some_datetime': '2020-10-06 04:56:01',
            'some_decimal': '1.23',
            'some_string': 'abc',
            'some_timedelta': '1:00:00.000100',
            'utc_updated_dttm': '2021-04-27 12:01:03',
        },
        {
            'id': 2,
            'some_date': '2020-10-06',
            'some_datetime': '2020-10-06 04:56:01',
            'some_decimal': '1.23',
            'some_string': 'abc',
            'some_timedelta': '1:00:00.000100',
            'utc_updated_dttm': '2021-04-27 12:01:04',
        },
    ]


@pytest.mark.slow
def test_streaming_push_pull():

    rule_path = os.path.join(
        sources_root.SOURCES_ROOT,
        'replication_rules/replication_rules/dmp_suite/api_test_rule.yaml',
    )

    push_task = uploading.SingleTargetIncrementTask(
        name='integration_test_upload',
        source=uploading.FunctionIncrementSource(
            description='test',
            reader_func=_streaming_reader_func,
        ),
        rule_path=rule_path,
        key_fields=('id',),
    )
    push_task._run_task(argparse.Namespace())

    _streaming_pull_assert(
        name='integration_test_download',
        rule_path=rule_path,
        target_table=SingleStreamingTestTable,
        destination_name='dmp_suite_api_test_rule_ext'
    )


class MultipleStreamingTestTableFirst(SingleStreamingTestTable):
    __layout__ = yt.NotLayeredYtLayout('test', 'test_first')


class MultipleStreamingTestTableSecond(SingleStreamingTestTable):
    __layout__ = yt.NotLayeredYtLayout('test', 'test_second')


@pytest.mark.slow
def test_multiple_streaming_push_pull():
    rules_names = (
        'api_test_first_rule',
        'api_test_second_rule'
    )

    rules_paths = [
        os.path.join(
            sources_root.SOURCES_ROOT,
            f'replication_rules/replication_rules/dmp_suite/{name}.yaml',
        )
        for name in rules_names
    ]

    push_task = uploading.MultiTargetIncrementTask(
        name='integration_test_upload',
        source=uploading.FunctionIncrementSource(
            description='test',
            reader_func=_streaming_reader_func,
        ),
        rules_paths=rules_paths,
        key_fields=('id',),
    )
    push_task._run_task(argparse.Namespace())

    for rule_path, target_table, destination_name in zip(rules_paths, [MultipleStreamingTestTableFirst, MultipleStreamingTestTableSecond], rules_names):
        _streaming_pull_assert(
            name='integration_test_download',
            rule_path=rule_path,
            target_table=target_table,
            destination_name=f'dmp_suite_{destination_name}_ext'
        )


@pytest.mark.parametrize('ignore_raw_ctl', [True, False])
def test_backfill_ignore_raw_ctl(ignore_raw_ctl):
    class OdsTable(yt.ETLTable):
        __dynamic__ = True

    class RawTable(yt.ETLTable):
        pass

    raw_args = ['--ignore-raw-ctl'] if ignore_raw_ctl else []

    task = streaming.OdsStreamingTask(
        name='test_backfill',
        rule_path=f'{YAMLS_PATH}/test_rule_w_ext_destination.yaml',
        target_table=OdsTable,
        destination_name='test_rule_w_ext_destinations_raw_ext',
        backfill_source_table=RawTable,
        extractors={},
    )
    raw_ctl_wait = mock.MagicMock()
    with mock.patch('dmp_suite.replication.tasks.initialization.wait_for_flush_table'), \
        mock.patch('dmp_suite.replication.tasks.initialization._InitializationTask._run'), \
        mock.patch('dmp_suite.replication.tasks.initialization.StreamingInitializationTask._wait_for_equalize_raw_ctl_to_ods', raw_ctl_wait):
        run_task(
            task_def=task,
            raw_args=raw_args,
            execution_args=ExecutionArgs(
                as_backfill=True,
                accident_used=False,
                lock_used=False,
            ),
            retry_times=1,
            retry_sleep=0,
        )
        if ignore_raw_ctl:
            raw_ctl_wait.assert_not_called()
        else:
            raw_ctl_wait.assert_called_once()

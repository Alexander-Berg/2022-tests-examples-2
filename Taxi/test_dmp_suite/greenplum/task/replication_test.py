import contextlib
import typing as tp
from datetime import datetime

import pytest
from mock import MagicMock, patch

from connection import ctl as ctl_connection
from connection import greenplum as gp_connection
from connection import yt as yt_connection
from dmp_suite import ctl, datetime_utils as dtu
from dmp_suite import greenplum as gp
from dmp_suite import yt as yt_suite
from dmp_suite.greenplum.task import replication
from dmp_suite.greenplum.task import transformations
from dmp_suite.replication.meta.dmp_integration.table import ReplicationTable
from dmp_suite.task.cli import StartEndDate
from dmp_suite.task.execution import run_task
from dmp_suite.yt.dyntable_operation import dynamic_table_loaders
from test_dmp_suite.greenplum.task import slow_replication_test_tables as tables
from test_dmp_suite.greenplum.utils import GreenplumTestTable, external_gp_layout
from test_dmp_suite.replication.test_dmp_integration import ReplicationTargetProxyTest
from test_dmp_suite.task.utils import WrapCtlMock


def _group_and_maximize_by_id(docs: tp.List[dict], maximize_field: str) -> tp.List[dict]:
    # Group by id and maximize value of maximize_field
    res = {}
    for doc in docs:
        id = doc['id']
        if id not in res or res[id][maximize_field] < doc[maximize_field]:
            res[id] = doc
    return list(res.values())


class GPTargetTable(GreenplumTestTable):
    __layout__ = external_gp_layout()

    a_utc_created_dttm = gp.Datetime(key=True)
    id = gp.Int(key=True)
    value = gp.String()


def ctl_mock():
    ctl = WrapCtlMock()
    return patch('connection.ctl.get_ctl', return_value=ctl)


@patch(
    'dmp_suite.datetime_utils.utcnow',
    MagicMock(return_value=datetime(2020, 11, 14, 0, 0)),
)
@patch(
    'dmp_suite.yt.partitions_utils.period_from_table_partitions',
    MagicMock(return_value=dtu.Period(
        start=datetime(2020, 1, 1, 0, 0),
        end=datetime(2020, 12, 31, 23, 59, 59),
    ))
)
def test_replication_increment_task_ctl():
    with ctl_mock(), patch(
            'dmp_suite.greenplum.task.replication._ReplicationIncrementTask._do_actual_work_without_processor',
            return_value=iter([datetime(year=2020, day=11, month=11)])
    ):
        task = replication._ReplicationIncrementTask(
            name='test_replication_increment_task_ctl',
            source=(
                transformations.OdsFromHistoryTableTaskSource(
                    tables.YTSourceTable
                )
            ),
            target=GPTargetTable,
            ctl_field='a_utc_created_dttm',
            raise_on_empty_source=False,
        )

        ctl_obj = ctl_connection.get_ctl().gp
        current_ctl = ctl_obj.get_param(
            GPTargetTable, ctl.CTL_LAST_SYNC_DATE,
        )
        assert current_ctl is None
        current_ctl = ctl_obj.get_param(
            GPTargetTable, ctl.CTL_LAST_LOAD_DATE,
        )
        assert current_ctl is None
        run_task(task)
        new_ctl = ctl_obj.get_param(
            GPTargetTable, ctl.CTL_LAST_SYNC_DATE,
        )
        assert new_ctl == datetime(2020, 11, 14, 0, 0)
        new_ctl = ctl_obj.get_param(
            GPTargetTable, ctl.CTL_LAST_LOAD_DATE,
        )
        assert new_ctl == datetime(2020, 11, 11, 0, 0)


def test_load_with_empty_ctl():
    with ctl_mock(), \
            patch(
                'dmp_suite.greenplum.task.replication'
                '._ReplicationIncrementTask.do_actual_work',
                return_value=iter([datetime(year=2020, day=11, month=11)]),
            ) as patched_actual_work, \
            patch(
                'dmp_suite.yt.partitions_utils.period_from_table_partitions',
                return_value=dtu.Period(
                    start=datetime(2020, 1, 1, 0, 0),
                    end=datetime(2020, 3, 31, 23, 59, 59),
                )
            ), \
            patch(
                'dmp_suite.datetime_utils.utcnow',
                return_value=datetime(2020, 4, 1, 0, 1),
            ):
        task = replication._ReplicationIncrementTask(
            name='test_replication_increment_task_ctl',
            source=(
                transformations.OdsFromHistoryTableTaskSource(
                    tables.YTSourceTable
                )
            ),
            target=GPTargetTable,
            ctl_field='a_utc_created_dttm',
            raise_on_empty_source=False,
        )

        ctl_obj = ctl_connection.get_ctl().gp
        current_ctl = ctl_obj.get_param(
            GPTargetTable, ctl.CTL_LAST_LOAD_DATE,
        )
        assert current_ctl is None
        run_task(task)
        actual_periods = [
            call[0][0].period for call in patched_actual_work.call_args_list
        ]
        expected_periods = [
            dtu.Period(
                start=datetime(2019, 12, 31, 23, 30),
                end=datetime(2019, 12, 31, 23, 59, 59, 999999),
            ),
            dtu.Period(
                start=datetime(2020, 1, 1, 0, 0),
                end=datetime(2020, 1, 31, 23, 59, 59, 999999),
            ),
            dtu.Period(
                start=datetime(2020, 2, 1, 0, 0),
                end=datetime(2020, 2, 29, 23, 59, 59, 999999),
            ),
            dtu.Period(
                start=datetime(2020, 3, 1, 0, 0),
                end=datetime(2020, 3, 31, 23, 59, 59, 999999),
            ),
            dtu.Period(
                start=datetime(2020, 4, 1, 0, 0),
                end=datetime(2020, 4, 1, 0, 1),
            ),
        ]
        assert actual_periods == expected_periods, (
                'Task called with unexpected periods'
        )


def test_load_with_empty_ctl_and_start_offset():
    with ctl_mock(), \
            patch(
                'dmp_suite.greenplum.task.replication'
                '._ReplicationIncrementTask.do_actual_work',
                return_value=iter([datetime(year=2020, day=11, month=11)]),
            ) as patched_actual_work, \
            patch(
                'dmp_suite.yt.partitions_utils.period_from_table_partitions',
                return_value=dtu.Period(
                    start=datetime(2020, 1, 1, 0, 0),
                    end=datetime(2020, 3, 31, 23, 59, 59),
                )
            ), \
            patch(
                'dmp_suite.datetime_utils.utcnow',
                return_value=datetime(2020, 4, 1, 0, 1),
            ):
        task = replication._ReplicationIncrementTask(
            name='test_replication_increment_task_ctl',
            source=(
                transformations.OdsFromHistoryTableTaskSource(
                    tables.YTSourceTable
                )
            ),
            target=GPTargetTable,
            ctl_field='a_utc_created_dttm',
            raise_on_empty_source=False,
            start_offset=dtu.timedelta(minutes=0)
        )

        ctl_obj = ctl_connection.get_ctl().gp
        current_ctl = ctl_obj.get_param(
            GPTargetTable, ctl.CTL_LAST_LOAD_DATE,
        )
        assert current_ctl is None
        run_task(task)
        actual_periods = [
            call[0][0].period for call in patched_actual_work.call_args_list
        ]
        expected_periods = [
            dtu.Period(
                start=datetime(2020, 1, 1, 0, 0),
                end=datetime(2020, 1, 31, 23, 59, 59, 999999),
            ),
            dtu.Period(
                start=datetime(2020, 2, 1, 0, 0),
                end=datetime(2020, 2, 29, 23, 59, 59, 999999),
            ),
            dtu.Period(
                start=datetime(2020, 3, 1, 0, 0),
                end=datetime(2020, 3, 31, 23, 59, 59, 999999),
            ),
            dtu.Period(
                start=datetime(2020, 4, 1, 0, 0),
                end=datetime(2020, 4, 1, 0, 1),
            ),
        ]
        assert actual_periods == expected_periods, (
                'Task called with unexpected periods'
        )


class ReplicationShardTable(ReplicationTable):
    __replication_target__ = ReplicationTargetProxyTest(
        'test_source/test_raw_history_ctl_usage.yaml',
        'test_raw_history_ctl_usage_destination',
    )


@contextlib.contextmanager
def _patch_task(source_ctl_value, new_ctl_value):
    utcnow_patch = patch(
        'dmp_suite.datetime_utils.utcnow',
        MagicMock(return_value=datetime(2020, 11, 14, 0, 0)),
    )
    period_patch = patch(
        'dmp_suite.yt.partitions_utils.period_from_table_partitions',
        MagicMock(return_value=dtu.Period(
            start=datetime(2020, 1, 1, 0, 0),
            end=datetime(2020, 12, 31, 23, 59, 59),
        ))
    )
    source_ctl_patch = patch(  # В RawHistory ctl данных, БОЛЬШЕ, чем было обработано таском
        'dmp_suite.greenplum.task.replication._ReplicationIncrementTask.source_entity_ctl_value',
        new_callable=MagicMock(return_value=source_ctl_value),
    )

    work_patch = patch(
        'dmp_suite.greenplum.task.replication._ReplicationIncrementTask._do_actual_work_without_processor',
        return_value=iter([new_ctl_value])
    )

    with utcnow_patch, period_patch, source_ctl_patch, work_patch:
        yield


# выбираем минимальный из ctl
@pytest.mark.parametrize('source_ctl_value, new_ctl_value, expected_ctl_value', [
    # В RawHistory значение ctl МЕНЬШЕ, чем было обработано данных таском
    (
            datetime(year=2020, month=11, day=10),
            datetime(year=2020, month=11, day=11),
            datetime(year=2020, month=11, day=10)
    ),
    # В RawHistory значение ctl БОЛЬШЕ, чем было обработано данных таском
    (
            datetime(year=2020, month=11, day=12),
            datetime(year=2020, month=11, day=11),
            datetime(year=2020, month=11, day=11)
    ),
    # для RawHistory нет ctl
    (
            None,
            None,
            None
    ),
    # ничего не загрузили из RawHistory
    (
            datetime(year=2020, month=11, day=10),
            None,
            datetime(year=2020, month=11, day=9)
    ),

])
def test_replication_increment_task_raw_history_ctl_usage(source_ctl_value, new_ctl_value, expected_ctl_value):
    task = replication._ReplicationIncrementTask(
        name='test_replication_increment_task_ctl',
        source=(
            transformations.OdsFromHistoryTableTaskSource(
                ReplicationShardTable
            )
        ),
        target=GPTargetTable,
        ctl_field='a_utc_created_dttm',
        raise_on_empty_source=False,
    )

    init_ctl_value = None
    if source_ctl_value:
        init_ctl_value = datetime(year=2020, month=11, day=9)

    with ctl_mock(), _patch_task(source_ctl_value, new_ctl_value):
        gp_ctl = ctl_connection.get_ctl().gp
        # начальное значение ctl
        gp_ctl.set_param(
            entity=GPTargetTable,
            parameter=ctl.CTL_LAST_LOAD_DATE,
            value=init_ctl_value
        )

        run_task(task)

        last_load_date = gp_ctl.get_param(
            entity=GPTargetTable,
            parameter=ctl.CTL_LAST_LOAD_DATE,
        )
        assert last_load_date == expected_ctl_value


class GPWrongIndexTargetTable(GreenplumTestTable):
    __layout__ = external_gp_layout()

    a_utc_created_dttm = gp.Datetime()
    id = gp.Int(key=True)
    value = gp.String()
    value_2 = gp.String()


def test_replication_stg_task_validate():
    with pytest.raises(ValueError):
        replication.stg_from_raw_history_task(
            name='stg_from_raw_history_task',
            source=tables.YTSourceTable,
            target=GPWrongIndexTargetTable,
            ctl_field='a_utc_created_dttm',
        )

    replication.stg_from_raw_history_task(
        name='stg_from_raw_history_task',
        source=tables.YTSourceTable,
        target=GPTargetTable,
        ctl_field='a_utc_created_dttm',
    )


def test_replication_task_validate():
    class MockSource:
        @property
        def yt_table(self):
            return tables.YTSourceTable

    source = tp.cast(replication.ReplicationIncrementSourceType, MockSource())

    with pytest.raises(ValueError):
        replication._ReplicationIncrementTask(
            name='stg_from_raw_history_task',
            source=source,
            target=GPWrongIndexTargetTable,
            ctl_field='value',
            raise_on_empty_source=True,
        )

    replication._ReplicationIncrementTask(
        name='stg_from_raw_history_task',
        source=source,
        target=GPTargetTable,
        ctl_field='a_utc_created_dttm',
        raise_on_empty_source=True,
    )


def _sk(d: dict):
    return list(d.items())


@pytest.mark.slow('gp')
class TestGpLoad:
    docs = [
        {
            'a_utc_created_dttm': datetime(2020, 2, 20, 1, 1, 5),
            'id': 1,
            'value': 'a',
        },
        {
            'a_utc_created_dttm': datetime(2020, 2, 20, 1, 1, 3),
            'id': 1,
            'value': 'b',
        },
        {
            'a_utc_created_dttm': datetime(2020, 2, 20, 1, 1, 1),
            'id': 2,
            'value': 'a',
        },
        {
            'a_utc_created_dttm': datetime(2020, 2, 21, 1, 1, 1),
            'id': 3,
            'value': 'a',
        },
        {
            'a_utc_created_dttm': datetime(2020, 2, 21, 1, 2, 1),
            'id': 3,
            'value': 'b',
        },
        {
            'a_utc_created_dttm': datetime(2020, 4, 20, 1, 1, 1),
            'id': 4,
            'value': 'a',
        },
        {
            'a_utc_created_dttm': datetime(2020, 4, 20, 1, 1, 1),
            'id': 5,
            'value': 'a',
        },
    ]

    docs_raw_format = [
        {
            'a_utc_created_dttm': d['a_utc_created_dttm'],
            'id': d['id'],
            'doc': d
        } for d in docs
    ]

    @pytest.fixture(scope='class', autouse=True)
    def setup_and_teardown(self, request, slow_test_settings):
        cls = request.cls
        with slow_test_settings():
            dynamic_table_loaders.upload(
                data=cls.docs_raw_format,
                yt_table_or_meta=tables.YTSourceTable,
                extractors={},
            )
        yield

    @pytest.fixture(scope='class')
    def setup_mr(self, request, slow_test_settings):
        with slow_test_settings():
            source_meta = yt_suite.YTMeta(tables.YTSourceTable)
            ytc = yt_connection.create_yt_client()
            ytc.freeze_table(
                source_meta.with_partition('2020-02').target_path(), sync=True,
            )
            ytc.freeze_table(
                source_meta.with_partition('2020-04').target_path(), sync=True,
            )
        yield

    @staticmethod
    def _get_gp_data(table):
        with gp_connection.connection.transaction():
            gp_data = [
                dict(r) for r in gp_connection.connection.select_all(table)
            ]
        return gp_data

    def test_select_data(self):
        task = replication.stg_from_raw_history_task(
            name='test',
            source=tables.YTSourceTable,
            target=tables.GpStgTargetTable,
            ctl_field='a_utc_created_dttm',
            use_source_entity_ctl=False,
            mr_use_threshold=1000,
        )

        expected_data = [
            {
                'a_utc_created_dttm': '2020-02-20 01:01:03',
                'id': 1,
                'doc': {
                    'a_utc_created_dttm': '2020-02-20 01:01:03.000000',
                    'id': 1,
                    'value': 'b'
                },
            },
            {
                'a_utc_created_dttm': '2020-02-20 01:01:05',
                'id': 1,
                'doc': {
                    'a_utc_created_dttm': '2020-02-20 01:01:05.000000',
                    'id': 1,
                    'value': 'a'
                },
            },
            {
                'a_utc_created_dttm': '2020-02-20 01:01:01',
                'id': 2,
                'doc': {
                    'a_utc_created_dttm': '2020-02-20 01:01:01.000000',
                    'id': 2,
                    'value': 'a'
                },
            },
            {
                'a_utc_created_dttm': '2020-02-21 01:01:01',
                'doc': {
                    'a_utc_created_dttm': '2020-02-21 01:01:01.000000',
                    'id': 3,
                    'value': 'a'
                },
                'id': 3
            },
            {
                'a_utc_created_dttm': '2020-02-21 01:02:01',
                'id': 3,
                'doc': {
                    'a_utc_created_dttm': '2020-02-21 01:02:01.000000',
                    'id': 3,
                    'value': 'b'
                },
            },
            {
                'a_utc_created_dttm': '2020-04-20 01:01:01',
                'id': 4,
                'doc': {
                    'a_utc_created_dttm': '2020-04-20 01:01:01.000000',
                    'id': 4,
                    'value': 'a'
                },
            },
            {
                'a_utc_created_dttm': '2020-04-20 01:01:01',
                'id': 5,
                'doc': {
                    'a_utc_created_dttm': '2020-04-20 01:01:01.000000',
                    'id': 5,
                    'value': 'a'
                },
            },
        ]

        actual_data = task.source.select_data()  # type: ignore
        assert sorted(actual_data, key=_sk) == sorted(expected_data, key=_sk)  # Fixed!

    @pytest.mark.parametrize(
        'period,expected_count',
        [
            pytest.param(None, len(docs)),
            pytest.param(
                dtu.Period(
                    datetime(2020, 2, 21, 1, 1, 1),
                    datetime(2021, 2, 20, 1, 3, 1)
                ),
                4,
            ),
            pytest.param(
                dtu.Period(
                    datetime(2020, 2, 22, 3, 1, 5),
                    datetime(2020, 3, 20, 1, 3, 1)
                ),
                0,
            ),
            pytest.param(
                dtu.Period(
                    datetime(2020, 2, 20, 1, 1, 1),
                    datetime(2020, 2, 20, 1, 1, 1)
                ),
                1,
            ),
        ],
    )
    def test_count_rows(self, period: tp.Optional[dtu.Period], expected_count: int):
        task = replication.stg_from_raw_history_task(
            name='test',
            source=tables.YTSourceTable,
            target=tables.GpStgTargetTable,
            ctl_field='a_utc_created_dttm',
            use_source_entity_ctl=False,
            mr_use_threshold=1000,
        )

        actual_count = task.source.get_rows_count_to_load(period)  # type: ignore
        assert actual_count == expected_count

    def test_gp_stg_loading_in_mem(self):
        task = replication.stg_from_raw_history_task(
            name='test',
            source=tables.YTSourceTable,
            target=tables.GpStgTargetTable,
            ctl_field='a_utc_created_dttm',
            use_source_entity_ctl=False,
            mr_use_threshold=1000,
        )

        with patch.object(
                task.source,
                '_serialize_tsv_mapreduce',
        ) as patched_task_source:
            run_task(task)
            patched_task_source.assert_not_called()

        gp_data = self._get_gp_data(tables.GpStgTargetTable)

        assert sorted(gp_data, key=_sk) == sorted(self.docs, key=_sk)

    def test_gp_ods_uploading_in_mem(self):
        task = replication.ods_from_raw_history_task(
            name='test',
            source=tables.YTSourceTable,
            target=tables.GpOdsTargetTable,
            ctl_field='a_utc_created_dttm',
            use_source_entity_ctl=False,
            mr_use_threshold=1000,
        )

        with patch.object(
                task.source,
                '_serialize_tsv_mapreduce',
        ) as patched_task_source:
            run_task(task)
            patched_task_source.assert_not_called()

        actual_gp_data = self._get_gp_data(tables.GpOdsTargetTable)
        expected_data = _group_and_maximize_by_id(self.docs, maximize_field='a_utc_created_dttm')

        assert sorted(actual_gp_data, key=_sk) == sorted(expected_data, key=_sk)

    def test_gp_stg_loading_mr(self, setup_mr):
        task = replication.stg_from_raw_history_task(
            name='test',
            source=tables.YTSourceTable,
            target=tables.GpStgTargetTable,
            ctl_field='a_utc_created_dttm',
            use_source_entity_ctl=False,
        ).arguments(
            period=StartEndDate(default=dtu.Period('2020-01-01', '2020-04-30'))
        )

        with patch.object(
            task.source,
            '_serialize_tsv_in_memory',
        ) as patched_task_source:
            run_task(task)
            patched_task_source.assert_not_called()

        gp_data = self._get_gp_data(tables.GpStgTargetTable)

        assert sorted(gp_data, key=_sk) == sorted(self.docs, key=_sk)

    def test_gp_ods_uploading_mr(self, setup_mr):
        task = replication.ods_from_raw_history_task(
            name='test',
            source=tables.YTSourceTable,
            target=tables.GpOdsTargetTable,
            ctl_field='a_utc_created_dttm',
            use_source_entity_ctl=False,
        ).arguments(
            period=StartEndDate(default=dtu.Period('2020-01-01', '2020-04-30'))
        )

        with patch.object(
            task.source,
            '_serialize_tsv_in_memory',
        ) as patched_task_source:
            run_task(task)
            patched_task_source.assert_not_called()

        actual_gp_data = self._get_gp_data(tables.GpOdsTargetTable)
        expected_data = _group_and_maximize_by_id(self.docs, maximize_field='a_utc_created_dttm')

        assert sorted(actual_gp_data, key=_sk) == sorted(expected_data, key=_sk)

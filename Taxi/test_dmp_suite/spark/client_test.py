import copy
import os
import tempfile
from multiprocessing import Process

import mock
import pytest
from pyspark import Row
from pyspark.sql.functions import col

from dmp_suite.common_utils import deep_update_dict
from dmp_suite.spark.base_udf import DatetimeUDF
from dmp_suite.spark.client import (
    create_spark_session,
    _get_log_properties_path,
    _spark_session_args,
    patch_spark_session_args,
    _make_session_args,
)
from dmp_suite.yt import YTTable, Date
from dmp_suite.yt import operation as yt, YTMeta, etl
from init_py_env import settings, service
from test_dmp_suite.spark.utils import get_develop_jar_path
from test_dmp_suite.yt import utils


class TestTable(YTTable):
    msk = Date()


test_table = utils.fixture_random_yt_table(TestTable)


def run_helper(table, local_jar_path):
    with settings.patch(spark={'local_jar_path': local_jar_path}):
        meta = YTMeta(table)
        etl.init_target_table(meta)
        yt.write_yt_table(meta.target_path(), [dict(msk='2020-02-03 03:00:00')])
        session = create_spark_session(
            num_executors=1,
            cores_per_executor=1
        )
        with session as spark:
            result = spark.read.yt(meta.target_path()) \
                .withColumn('utc', DatetimeUDF.msk_to_utc(col('msk'))) \
                .collect()
        if not [Row(msk='2020-02-03 03:00:00',
                    utc='2020-02-03 00:00:00')] == result:
            raise RuntimeError('invalid data')


def assert_local_jar_path(table, local_jar_path, expected=True):
    # https://st.yandex-team.ru/SPYT-54 может быть только 1 сессия на процесс
    # так как тестируем конфиги jar, то нужно создать новую spark_session
    # в тестах на расчеты это не требуется, нужно использовать локальный spark
    # создаем под каждый spark_session свой под процесс
    proc = Process(target=run_helper, args=(table, local_jar_path))
    proc.start()
    proc.join()
    success = not proc.exitcode
    assert success == expected


@pytest.mark.slow
def test_develop_jar(test_table):
    assert_local_jar_path(test_table, None)


@pytest.mark.slow
def test_local_jar(test_table):
    local_jar_path = get_develop_jar_path(service)
    assert_local_jar_path(test_table, os.path.dirname(local_jar_path))


@pytest.mark.slow
def test_local_jar_empty(test_table):
    with tempfile.TemporaryDirectory() as tmpdir:
        assert_local_jar_path(test_table, tmpdir, False)


base_settings = dict(
dmp_profile=dict(
  DEFAULT=dict(
    num_executors=4,
    executor_memory_per_core='4G',
    dynamic_allocation=False,
    spark_conf_args={'spark.sql.autoBroadcastJoinThreshold': -1}
  ),
  TINY=dict(num_executors=1),
  SMALL=dict(
      num_executors=5,
      spark_conf_args={'spark.sql.broadcastTimeout': "1800"}
  ),
),
discovery_path='test_path'
)

expected_log4j_opt = '-Dlog4j.configuration={}'.format(_get_log_properties_path())
expected_spark_conf_args = {
    'spark.sql.autoBroadcastJoinThreshold': -1,
    'spark.jars': 'test_jar_path',
    'spark.driver.extraClassPath': 'test_jar_path',
    'spark.driver.extraJavaOptions': expected_log4j_opt
}
base_expected = dict(
    num_executors=4,
    executor_memory_per_core='4G',
    dynamic_allocation=False,
    spark_conf_args=expected_spark_conf_args
)

expected_spark_conf_args_broadcast = copy.copy(expected_spark_conf_args)
expected_spark_conf_args_broadcast['spark.sql.broadcastTimeout'] = '1800'


@pytest.mark.parametrize('args, expected', [
    # дефолтный профиль конфигов
    (
        dict(),
        dict(base_expected)
    ),
    # кастомный профиль TINY
    (
        dict(dmp_profile='TINY'),
        dict(base_expected, num_executors=1)
    ),
    # кастомный профиль SMALL
    (
        dict(dmp_profile='SMALL'),
        dict(
            base_expected,
            num_executors=5,
            spark_conf_args=expected_spark_conf_args_broadcast
        )
    ),
    # дефолтные конфиги + аргументы
    (
        dict(
            num_executors=50,
            spark_conf_args={'spark.sql.broadcastTimeout': "1800"}
        ),
        dict(
            base_expected,
            num_executors=50,
            spark_conf_args=expected_spark_conf_args_broadcast
        )
    ),
    # кастомный профиль + аргументы
    (
        dict(
            dmp_profile='SMALL',
            num_executors=50,
            spark_conf_args={
                'spark.sql.broadcastTimeout': "3600",
                'spark.jars': 'tmp_jar',
            }
        ),
        dict(
            base_expected,
            num_executors=50,
            spark_conf_args={
                'spark.sql.autoBroadcastJoinThreshold': -1,
                'spark.sql.broadcastTimeout': "3600",
                'spark.jars': 'tmp_jar',
                'spark.driver.extraClassPath': 'tmp_jar',
                'spark.driver.extraJavaOptions': expected_log4j_opt,
            }
        )
    )
])
def test_spark_session_args(args, expected):

    yt_client = object()
    yt_client_patch = mock.patch(
        'dmp_suite.spark.client.get_yt_client',
        return_value=yt_client
    )
    default_spark_jar_patch = mock.patch(
        'dmp_suite.spark.client.default_spark_jar',
        return_value='test_jar_path'
    )
    spyt_patch = mock.patch('dmp_suite.spark.client.spyt')

    with yt_client_patch, default_spark_jar_patch, spyt_patch as spyt_mock:
        with settings.patch(spark=base_settings):
            with create_spark_session(**args) as session:
                pass
        spyt_mock.spark_session.assert_called_once_with(
            **expected, client=yt_client, discovery_path='test_path'
        )


@pytest.mark.parametrize(
    'spark_conf_args,expected',
    [
        (
            {'spark.sql.broadcastTimeout': "1800"},
            expected_spark_conf_args_broadcast,
        ),
        (
            {
                'spark.sql.broadcastTimeout': "3600",
                'spark.jars': 'tmp_jar',
            },
            {
                'spark.sql.autoBroadcastJoinThreshold': -1,
                'spark.sql.broadcastTimeout': "3600",
                'spark.jars': 'tmp_jar',
                'spark.driver.extraClassPath': 'tmp_jar',
                'spark.driver.extraJavaOptions': expected_log4j_opt,
            },
        )
    ]
)
def test_spark_session_args_patch(spark_conf_args, expected):

    default_spark_jar_patch = mock.patch(
        'dmp_suite.spark.client.default_spark_jar',
        return_value='test_jar_path'
    )

    with default_spark_jar_patch:
        with settings.patch(spark=base_settings):
            with patch_spark_session_args(spark_conf_args=spark_conf_args):
                assert _make_session_args()['spark_conf_args'] == expected


@pytest.mark.parametrize(
    'cont_1,cont_2',
    [
        ({'a': {'alpha': 5}}, {'Haha': 'I am in Config!'}),
        ({1: 100, 2: 200, 3: 300}, {2: {15: 100}}),
    ]
)
def test_spark_session_args_patch_nesting(cont_1, cont_2):
    """
    On each level assert that _spark_session_args is
    correctly updated by patch_spark_session_args(...).
    """
    true_cont_1 = copy.deepcopy(cont_1)
    true_cont_2 = copy.deepcopy(cont_1)
    deep_update_dict(true_cont_2, cont_2)

    def _assert_conf_args(expected):
        assert _spark_session_args.spark_conf_args == expected

    _assert_conf_args({})
    with patch_spark_session_args(spark_conf_args=cont_1):
        _assert_conf_args(true_cont_1)
        with patch_spark_session_args(spark_conf_args=cont_2):
            _assert_conf_args(true_cont_2)
        _assert_conf_args(true_cont_1)
    _assert_conf_args({})

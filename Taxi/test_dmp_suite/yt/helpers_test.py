# coding: utf-8
import mock
import pytest
from datetime import datetime

from dmp_suite.yt import YTMeta, String, YTTable, ETLTable
from connection.yt import get_yt_client
from dmp_suite.yt.helpers import write_target
from test_dmp_suite.yt import utils
from dmp_suite.extract_utils import const

TEST_DATA = [
    dict(id='1', name='hello'),
    dict(id='2', name='world'),
    dict(id='3', name='!!!')
]
EXPECTED_DATA = [
    dict(id='1', name='hello', reversed_name='olleh'),
    dict(id='2', name='world', reversed_name='dlrow'),
    dict(id='3', name='!!!', reversed_name='!!!')
]
MOCK_UTCNOW = datetime(2099, 5, 5, 12)
CUSTOM_ETL_UPDATED = "2019-11-19 12:34:56"


class TestTable(YTTable):
    __unique_keys__ = True

    id = String(sort_key=True, sort_position=0)
    name = String()
    reversed_name = String()


class TestETLTable(TestTable, ETLTable):
    pass


def extract_reversed_name(data):
    return data["name"][::-1]


def pass_meta_to_write_target(table, *args, **kwargs):
    return write_target(YTMeta(table), *args, **kwargs)


test_table = utils.fixture_random_yt_table(TestTable)
test_etl_table = utils.fixture_random_yt_table(TestETLTable)


@pytest.mark.slow
@pytest.mark.parametrize("write_target", [write_target, pass_meta_to_write_target])
def test_write_target(write_target, test_table):
    write_target(test_table, TEST_DATA, reversed_name=extract_reversed_name)

    path = YTMeta(test_table).target_path()
    assert get_yt_client().exists(path)

    yt_data = list(get_yt_client().read_table(path))
    assert EXPECTED_DATA == yt_data


@pytest.mark.slow
@mock.patch("dmp_suite.datetime_utils.utcnow", mock.MagicMock(return_value=MOCK_UTCNOW))
def test_write_target_etl_table(test_etl_table):
    write_target(test_etl_table, TEST_DATA, reversed_name=extract_reversed_name)

    path = YTMeta(test_etl_table).target_path()
    assert get_yt_client().exists(path)

    yt_data = list(get_yt_client().read_table(path))
    for row in yt_data:
        assert "2099-05-05 12:00:00" == row.pop("etl_updated")
    assert EXPECTED_DATA == yt_data


@pytest.mark.slow
@mock.patch("dmp_suite.datetime_utils.utcnow", mock.MagicMock(return_value=MOCK_UTCNOW))
def test_write_target_etl_table_custom_updated(test_etl_table):
    write_target(
        test_etl_table,
        TEST_DATA,
        reversed_name=extract_reversed_name,
        etl_updated=const(CUSTOM_ETL_UPDATED)
    )

    path = YTMeta(test_etl_table).target_path()
    assert get_yt_client().exists(path)

    yt_data = list(get_yt_client().read_table(path))
    for row in yt_data:
        assert CUSTOM_ETL_UPDATED == row.pop("etl_updated")
    assert EXPECTED_DATA == yt_data

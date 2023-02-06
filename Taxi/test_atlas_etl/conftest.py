# pylint: disable=redefined-outer-name
import datetime
import os

import pytest

import atlas_etl.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from atlas_etl.utils import common


pytest_plugins = ['atlas_etl.generated.service.pytest_plugins']


@pytest.fixture
def yaml_name():
    return ''


@pytest.fixture
def clickhouse_table_config(yaml_name):
    yaml_path = os.path.join(
        os.path.dirname(__file__), 'lib', 'clickhouse_table', yaml_name,
    )
    return common.read_yaml(yaml_path)


@pytest.fixture
def fix_ch_insert_data():
    def _fix_ch_insert_data(data):
        for row in data:
            for column in row:
                if isinstance(row[column], datetime.datetime):
                    row[column] = row[column].isoformat()

        return data

    return _fix_ch_insert_data

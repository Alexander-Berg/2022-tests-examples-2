# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name

import json
import os
from typing import AsyncGenerator
from typing import List
from typing import Optional
from typing import Union

import aiohttp.web
import pytest

import atlas_backend.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from atlas_backend.generated.web.yt_wrapper import plugin
from atlas_backend.utils import common

pytest_plugins = ['atlas_backend.generated.service.pytest_plugins']


@pytest.fixture
def username():
    return 'omnipotent_user'


@pytest.fixture
def atlas_blackbox_mock(username, mockserver):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def handler(request):  # pylint: disable=unused-variable
        assert request.query['method'] == 'sessionid'
        assert request.query['sessionid'] == ''
        assert request.query['userip'] == '127.0.0.1'

        if username is None:
            return {}

        data = {
            'login': username,
            'uid': {'value': '01234'},
            'status': {'value': 'VALID'},
        }
        return data


@pytest.fixture
def first_metric_dict_filtered():
    return {
        '_id': 'requests_share_burnt',
        'absolute': 'requests_volume',
        'agg_func': 'AVG',
        'class_any_exists': False,
        'color': '#4651a0',
        'database': 'atlas_orders',
        'db': ['pixel', 'realtime'],
        'default': True,
        'default_leaderboard': False,
        'desc': '',
        'desc_en': 'Share of requests burnt',
        'divide_by': 1.0,
        'en': 'Burnt Requests Share, %',
        'id': 'requests_share_burnt',
        'ifnull': 0,
        'main_class_if_any': False,
        'map': True,
        'metric': 'Сгоревших заказов, %',
        'metrics': ['requests_share_burnt', 'requests_volume'],
        'monitoring': False,
        'optgroup': 'Заказы',
        'optgroup_en': 'Requests',
        'primary': True,
        'relative': True,
        'selection_rules': [
            'SUM(requests_share_burnt) / SUM(requests_volume)',
            'SUM(requests_volume) AS requests_volume, '
            'SUM(requests_share_burnt) AS requests_share_burnt',
            'SUM(requests_volume) AS requests_volume, '
            'SUM(requests_share_burnt) AS requests_share_burnt',
            'requests_volume, requests_share_burnt*requests_volume '
            'AS requests_share_burnt',
        ],
        'server': 'clickhouse_back_man',
        'signal': 'positive',
        'skip_primary_keys': [],
        'sql_query_raw': None,
        'table': 'orders',
        'target': 0.05,
        'version': 2,
        'quadkey_size': 15,
        'protected_edit': False,
    }


@pytest.fixture
def second_metric_dict_filtered():
    return {
        '_id': 'requests_share_found',
        'absolute': 'requests_volume',
        'agg_func': 'AVG',
        'class_any_exists': False,
        'color': '#4651a0',
        'database': 'atlas',
        'db': ['pixel', 'realtime'],
        'default': False,
        'default_leaderboard': False,
        'desc': '',
        'desc_en': '',
        'divide_by': 1.0,
        'en': 'requests_share_found',
        'id': 'requests_share_found',
        'main_class_if_any': False,
        'map': True,
        'metric': 'Водителей найдено (found), %',
        'metrics': ['requests_share_found', 'requests_volume'],
        'monitoring': False,
        'optgroup': 'Заказы',
        'optgroup_en': 'Requests',
        'primary': True,
        'quadkey_size': 17,
        'relative': True,
        'selection_rules': [
            'SUM(requests_share_found) / SUM(requests_volume)',
            'SUM(requests_volume) AS requests_volume, '
            'SUM(requests_share_found) AS requests_share_found',
            'SUM(requests_volume) AS requests_volume, '
            'SUM(requests_share_found) AS requests_share_found',
            'requests_volume, requests_share_found*requests_volume '
            'AS requests_share_found',
        ],
        'server': 'clickhouse_cluster',
        'signal': 'positive',
        'skip_primary_keys': [],
        'sql_query_raw': None,
        'table': 'ods_order',
        'version': 2,
        'protected_edit': False,
    }


@pytest.fixture
def test_polygon():
    return {
        '_id': '5bc06be494c1420934994ab4',
        'city': 'Владивосток',
        'name': 'pol1',
        'polygons': [
            [
                [43.10598543545184, 131.9393866723632],
                [43.0818311400623, 131.9393866723632],
                [43.09139336264617, 131.97921211181637],
                [43.10598543545184, 131.9393866723632],
            ],
        ],
        'quadkeys': [
            '130333211121023',
            '130333211121032',
            '130333211121201',
            '130333211121203',
            '130333211121210',
            '130333211121211',
            '130333211121212',
            '130333211121213',
            '130333211121221',
            '130333211121230',
            '130333211121300',
            '130333211121302',
        ],
        'user': 'vladivostok_user',
        'details': [{'days_of_week': '1-2'}],
        'tariff_zones': ['vladivostok'],
    }


class MockAsyncYTClient(plugin.AsyncYTClient):
    async def mkdir(self, *args, **kwargs):
        pass

    async def find_free_subpath(self, *args, **kwargs):
        return '//temp_table_path'

    async def remove(self, *args, **kwargs):
        pass

    async def exists(self, *args, **kwargs):
        return True

    async def get(self, *args, **kwargs):
        return [
            {'name': 'dt', 'type': 'string', 'required': True},
            {'name': 'dttm_utc_1_min', 'type': 'string', 'required': True},
            {'name': 'city', 'type': 'string', 'required': True},
            {'name': 'ts_1_min', 'type': 'int32', 'required': True},
        ]


@pytest.fixture
def user_deliveries_mock(patch, clickhouse_client_mock):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        return [[1559225390]]

    @patch(
        'atlas_backend.internal.user_deliveries.'
        'YqlManager.yql_request_wrapper',
    )
    async def _yql_request_wrapper(*args, **kwargs):
        pass

    @patch('atlas_backend.generated.web.yt_wrapper.plugin.AsyncYTClient')
    def _yt_client_mock(*args, **kwargs):
        return MockAsyncYTClient(*args, **kwargs)


@pytest.fixture
def yaml_name():
    return ''


@pytest.fixture
def clickhouse_table_config(yaml_name):
    yaml_path = os.path.join(
        os.path.dirname(__file__), 'lib', 'clickhouse_table', yaml_name,
    )
    return common.read_yaml(yaml_path)


class MockMysqlPoolWrapper:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    async def fetchall(
            self, query: str, params: Optional[Union[tuple, dict]] = None,
    ) -> List:
        return [record async for record in self.fetch(query, params)]

    async def fetch(
            self, query: str, params: Optional[Union[tuple, dict]] = None,
    ) -> AsyncGenerator:
        yield


@pytest.fixture
def atlas_mysql_client_mock(patch):
    @patch('atlas_backend.lib.connections.mysql.client.MysqlPoolWrapper')
    def _mysql_client_mock(*args, **kwargs):
        return MockMysqlPoolWrapper(*args, **kwargs)


@pytest.fixture
def positions_data(open_file):
    with open_file('positions_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)
    return test_data


@pytest.fixture
def mock_positions(positions_data, mock_driver_trackstory):
    @mock_driver_trackstory('/positions')
    def _driver_trackstory_positions(request):
        requested_ids = request.json['driver_ids']
        positions = []
        for courier_id in requested_ids:
            position = positions_data.get(courier_id)
            if position is not None:
                positions.append({'driver_id': courier_id, **position})
        return aiohttp.web.json_response({'results': positions})

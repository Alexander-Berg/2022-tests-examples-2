import datetime
from typing import List
from typing import Optional
from typing import Tuple

from clickhouse_driver import errors as clickhouse_errors
import pytest

NOW = datetime.datetime(2020, 12, 25, 0, 10, 0)

DATA_TYPES = (
    ('user_id', 'Nullable(String)'),
    ('created_first', 'DateTime(\'UTC\')'),
    ('created_last', 'DateTime(\'UTC\')'),
    ('created_order', 'DateTime(\'UTC\')'),
    ('order_id', 'Nullable(String)'),
    ('forced_surges', 'Array(Nullable(Float32))'),
    ('car_classes', 'Array(String)'),
    ('geopoint_a', 'Array(Float32)'),
    ('geopoint_b', 'Array(Float32)'),
    ('estimated_waiting', 'Array(Nullable(Float32))'),
    ('tariff_zone', 'String'),
)
TYPE = Tuple[
    Optional[str],
    str,
    str,
    str,
    Optional[str],
    List[Optional[float]],
    List[str],
    List[float],
    List[float],
    List[Optional[float]],
    str,
]
WITH_ORDER: TYPE = (
    '4bb8a3d0199941248092a947a3d872ef',
    '2020-12-25T03:06:22.812000+03:00',
    '2020-12-25T03:07:59.999000+03:00',
    '2020-12-25T03:06:22.812000+03:00',
    '12e7c469591b6050869443b2c2b66603',
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [
        'business',
        'cargo',
        'comfortplus',
        'demostand',
        'econom',
        'maybach',
        'mkk_antifraud',
        'suv',
        'vip',
    ],
    [37.6173, 55.755826],
    [],
    [315.0, 691.0, None, None, 315.0, 315.0, None, None, 315.0],
    'moscow',
)

WITHOUT_ORDER: TYPE = (
    '12sadad199941248092a947a3d872ef',
    '2020-12-25T03:06:21.812000+03:00',
    '2020-12-25T03:07:59.999000+03:00',
    '2020-12-25T03:06:22.812000+03:00',
    None,
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [
        'business',
        'cargo',
        'comfortplus',
        'demostand',
        'econom',
        'maybach',
        'mkk_antifraud',
        'suv',
        'vip',
    ],
    [37.6173, 55.755826],
    [],
    [315.0, 691.0, None, None, 315.0, 315.0, None, None, 315.0],
    'moscow',
)
WITH_POINT_B: TYPE = (
    'fSDSdad199941248092a947a3d872ef',
    '2020-12-25T03:07:24.812000+03:00',
    '2020-12-25T03:07:59.999000+03:00',
    '2020-12-25T03:07:30.812000+03:00',
    '45sdsdlk13',
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [
        'business',
        'cargo',
        'comfortplus',
        'demostand',
        'econom',
        'maybach',
        'mkk_antifraud',
        'suv',
        'vip',
    ],
    [37.6173, 55.755826],
    [37.7, 55.6],
    [315.0, 691.0, None, None, 315.0, 315.0, None, None, 315.0],
    'moscow',
)

VLADIVOSTOK = (
    '12sddad199941248092a947a3d872ef',
    '2020-12-25T03:07:24.812000+03:00',
    '2020-12-25T03:07:59.999000+03:00',
    '2020-12-25T03:07:30.812000+03:00',
    '45sdsdlk13',
    [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    [
        'business',
        'cargo',
        'comfortplus',
        'demostand',
        'econom',
        'maybach',
        'mkk_antifraud',
        'suv',
        'vip',
    ],
    [132.0, 43.1],
    [132.01, 43.11],
    [315.0, 691.0, None, None, 315.0, 315.0, None, None, 315.0],
    'vladivostok',
)

PERMISSION_CITIES = pytest.mark.config(
    ATLAS_BACKEND_MAP_PERMISSION_SWITCH={'pins': 'cities', 'orders': 'cities'},
)
PERMISSION_GEO_HIERARCHY = pytest.mark.config(
    ATLAS_BACKEND_MAP_PERMISSION_SWITCH={
        'pins': 'geo_hierarchy',
        'orders': 'geo_hierarchy',
    },
)

PG_TARIFF_ZONES = pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_tariff_zone_permission.sql'],
)

MARKS_CHECK_CITIES = [PERMISSION_CITIES, PG_TARIFF_ZONES]
MARKS_CHECK_GEO_HIERARCHY = [PERMISSION_GEO_HIERARCHY, PG_TARIFF_ZONES]


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_pins(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [DATA_TYPES, WITH_ORDER, WITHOUT_ORDER, WITH_POINT_B]
            for item in data:
                yield item

        return _result()

    request_body = {'tl': [56, 37], 'br': [55, 38], 'last_minutes': 5}
    response = await web_app_client.post('/api/map/pins', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == 3
    assert sorted(content, key=lambda x: x['created_first'])[1] == {
        '_id': {'user_id': '4bb8a3d0199941248092a947a3d872ef'},
        'created_first': '2020-12-25T03:06:22.812000+03:00',
        'created_last': '2020-12-25T03:07:59.999000+03:00',
        'created_order': '2020-12-25T03:06:22.812000+03:00',
        'estimated_waiting': {
            'business': 315.0,
            'cargo': 691.0,
            'econom': 315.0,
            'maybach': 315.0,
            'vip': 315.0,
        },
        'forced_surges': {
            'business': 1.0,
            'cargo': 1.0,
            'comfortplus': 1.0,
            'demostand': 1.0,
            'econom': 1.0,
            'maybach': 1.0,
            'mkk_antifraud': 1.0,
            'suv': 1.0,
            'vip': 1.0,
        },
        'geopoint': [pytest.approx(37.6173), pytest.approx(55.755826)],
        'order_id': '12e7c469591b6050869443b2c2b66603',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_pins_has_order(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    request_body = {
        'tl': [56, 37],
        'br': [55, 38],
        'last_minutes': 10,
        'has_order': True,
    }

    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [DATA_TYPES, WITH_ORDER, WITHOUT_ORDER, WITH_POINT_B]
            for item in data:
                yield item

        return _result()

    response = await web_app_client.post('/api/map/pins', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == 2
    assert all(pin['order_id'] for pin in content)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_pins_has_point_b(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [DATA_TYPES, WITH_ORDER, WITHOUT_ORDER, WITH_POINT_B]
            for item in data:
                yield item

        return _result()

    request_body = {
        'tl': [56, 37],
        'br': [55, 38],
        'last_minutes': 10,
        'has_point_b': True,
    }
    response = await web_app_client.post('/api/map/pins', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == 1
    assert all(pin['geopoint_b'] for pin in content)


@pytest.mark.parametrize(
    'username, pins_count',
    [
        pytest.param('omnipotent_user', 3, marks=MARKS_CHECK_CITIES),
        pytest.param('city_user', 3, marks=MARKS_CHECK_CITIES),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_CITIES),
        pytest.param('omnipotent_user', 3, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('city_user', 3, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_GEO_HIERARCHY),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_pins_permissions(
        clickhouse_client_mock,
        web_app_client,
        atlas_blackbox_mock,
        username,
        patch,
        pins_count,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [DATA_TYPES, WITH_ORDER, WITHOUT_ORDER, WITH_POINT_B]
            for item in data:
                yield item

        return _result()

    request_body = {'tl': [56, 37], 'br': [55, 38], 'last_minutes': 10}
    response = await web_app_client.post('/api/map/pins', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == pins_count


@pytest.mark.parametrize(
    'username, pins_count',
    [
        pytest.param('omnipotent_user', 1, marks=MARKS_CHECK_CITIES),
        pytest.param('city_user', 0, marks=MARKS_CHECK_CITIES),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_CITIES),
        pytest.param('omnipotent_user', 1, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('city_user', 0, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_GEO_HIERARCHY),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_pins_permissions_vladivostok(
        clickhouse_client_mock,
        web_app_client,
        atlas_blackbox_mock,
        username,
        pins_count,
        patch,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [DATA_TYPES, VLADIVOSTOK]
            for item in data:
                yield item

        return _result()

    request_body = {'tl': [44, 131], 'br': [42, 133], 'last_minutes': 10}
    response = await web_app_client.post('/api/map/pins', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == pins_count


async def test_get_pins_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/map/pins',
        json={'tl': [56, 37], 'br': [55, 38], 'last_minutes': 5},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TimeoutExceeded',
        'message': 'Timeout exceeded',
    }


PIN_INFO_TYPE = (
    ('user_id', 'Nullable(String)'),
    ('created_first', 'DateTime(\'UTC\')'),
    ('created_last', 'DateTime(\'UTC\')'),
    ('created_order', 'DateTime(\'UTC\')'),
    ('order_id', 'Nullable(String)'),
    ('category', 'Array(String)'),
    ('cost', 'Array(Nullable(Float32))'),
    ('value', 'Array(Nullabale(Float32))'),
    ('value_raw', 'Array(Nullable(Float32))'),
    ('value_smooth', 'Array(Nullable(Float32))'),
    ('value_smooth_b', 'Array(Nullable(Float32))'),
    ('surcharge', 'Array(Nullable(Float32))'),
    ('surcharge_alpha', 'Array(Nullable(Float32))'),
    ('surcharge_beta', 'Array(Nullable(Float32))'),
    ('geopoint_a', 'Array(Float32)'),
    ('geopoint_b', 'Array(Float32)'),
    ('estimated_waiting', 'Array(Nullable(Float32))'),
    ('tariff_zone', 'String'),
)
PIN = Tuple[
    str,
    str,
    str,
    str,
    Optional[str],
    List[str],
    List[Optional[float]],
    List[Optional[float]],
    List[Optional[float]],
    List[Optional[float]],
    List[Optional[float]],
    List[Optional[float]],
    List[Optional[float]],
    List[float],
    List[float],
    List[float],
    List[Optional[float]],
    str,
]
PIN_INFO: PIN = (
    'za2ee11ccab34c428acdc77e5c6442b6',
    '2020-12-25T03:04:14.651000+03:00',
    '2020-12-25T03:04:14.651000+03:00',
    '2020-12-25T03:04:14.651000+03:00',
    None,
    ['econom'],
    [49.0],
    [1.0],
    [1.0],
    [1.0],
    [None],
    [0.0],
    [1.0],
    [0.0],
    [37.8668314387, 55.97075534],
    [],
    [None],
    'moscow',
)


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_pin_info(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    request_body = {
        'user_id': 'za2ee11ccab34c428acdc77e5c6442b6',
        'point': [0, 0],
    }

    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [PIN_INFO_TYPE, PIN_INFO]
            for item in data:
                yield item

        return _result()

    response = await web_app_client.post(
        '/api/map/pin-info', json=request_body,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        '_id': {'user_id': 'za2ee11ccab34c428acdc77e5c6442b6'},
        'created_first': '2020-12-25T03:04:14.651000+03:00',
        'created_last': '2020-12-25T03:04:14.651000+03:00',
        'created_order': '2020-12-25T03:04:14.651000+03:00',
        'estimated_waiting': {},
        'forced_surges': {'econom': 1.0},
        'forced_surges_info': [
            {
                'category': 'econom',
                'cost': 49.0,
                'surcharge': 0.0,
                'surcharge_alpha': 1.0,
                'surcharge_beta': 0.0,
                'value': 1.0,
                'value_raw': 1.0,
                'value_smooth': 1.0,
                'value_smooth_b': None,
            },
        ],
        'geopoint': [pytest.approx(37.8668314387), pytest.approx(55.97075534)],
        'order_id': None,
    }


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_pin_info_non_existent(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [PIN_INFO_TYPE]
            for item in data:
                yield item

        return _result()

    request_body = {'user_id': 'qweqwe', 'point': [0, 0]}
    response = await web_app_client.post(
        '/api/map/pin-info', json=request_body,
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'username, response_status',
    [
        pytest.param('omnipotent_user', 200, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('city_user', 200, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('anomaly_viewer', 403, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('omnipotent_user', 200, marks=MARKS_CHECK_CITIES),
        pytest.param('city_user', 200, marks=MARKS_CHECK_CITIES),
        pytest.param('anomaly_viewer', 403, marks=MARKS_CHECK_CITIES),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_pin_info_permissions(
        clickhouse_client_mock,
        web_app_client,
        atlas_blackbox_mock,
        patch,
        username,
        response_status,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        async def _result():
            data = [PIN_INFO_TYPE, PIN_INFO]
            for item in data:
                yield item

        return _result()

    request_body = {
        'user_id': 'za2ee11ccab34c428acdc77e5c6442b6',
        'point': [0, 0],
    }
    response = await web_app_client.post(
        '/api/map/pin-info', json=request_body,
    )
    assert response.status == response_status


@pytest.mark.now(NOW.isoformat())
async def test_get_pin_info_with_exceeded_timeout(
        clickhouse_client_mock, web_app_client, atlas_blackbox_mock, patch,
):
    @patch('atlas_backend.utils.clickhouse.get_mdb_cluster_client')
    def _get() -> str:
        return 'atlastest_mdb'

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute_iter')
    async def _execute_iter(*args, **kwargs):
        raise clickhouse_errors.ServerException(
            message='', code=clickhouse_errors.ErrorCodes.TIMEOUT_EXCEEDED,
        )

    response = await web_app_client.post(
        '/api/map/pin-info',
        json={'user_id': 'za2ee11ccab34c428acdc77e5c6442b6', 'point': [0, 0]},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'BadRequest::TimeoutExceeded',
        'message': 'Timeout exceeded',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_orders(web_app_client, db, atlas_blackbox_mock):
    request_body = {
        'tl': [56, 37],
        'br': [55, 38],
        'last_minutes': 10,
        'city': 'Москва',
        'has_performer': False,
    }
    response = await web_app_client.post('/api/map/orders', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == 2
    assert sorted(content, key=lambda x: x['created'])[1] == {
        '_id': '1f17e9c2-05b9-4c77-956e-84512af8e257',
        'created': '2020-12-25T03:03:00.294000+03:00',
        'request': {
            'source': {
                'geopoint': [
                    pytest.approx(37.47869092),
                    pytest.approx(55.66895046),
                ],
            },
        },
        'status': 'finished',
        'taxi_status': 'complete',
        'user_id': 'aa8e0df17961e6007330b7392b3d7250',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_orders_has_performer(
        web_app_client, db, atlas_blackbox_mock,
):
    request_body = {
        'tl': [56, 37],
        'br': [55, 38],
        'last_minutes': 10,
        'city': 'Москва',
        'has_performer': True,
    }
    response = await web_app_client.post('/api/map/orders', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == 1


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_orders_status(web_app_client, db, atlas_blackbox_mock):
    request_body = {
        'tl': [57, 60],
        'br': [56, 61],
        'last_minutes': 10,
        'city': 'Екатеринбург',
        'has_performer': False,
        'status': 'rider_cancelled',
    }
    response = await web_app_client.post('/api/map/orders', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == 1


@pytest.mark.parametrize(
    'username, orders_count',
    [
        pytest.param('omnipotent_user', 2, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('city_user', 2, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('omnipotent_user', 2, marks=MARKS_CHECK_CITIES),
        pytest.param('city_user', 2, marks=MARKS_CHECK_CITIES),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_CITIES),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_orders_permissions_moscow(
        web_app_client, db, atlas_blackbox_mock, username, orders_count,
):
    request_body = {
        'tl': [56, 37],
        'br': [55, 38],
        'last_minutes': 10,
        'city': 'Москва',
        'has_performer': False,
    }
    response = await web_app_client.post('/api/map/orders', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == orders_count


@pytest.mark.parametrize(
    'username, orders_count',
    [
        pytest.param('omnipotent_user', 3, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('city_user', 0, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('omnipotent_user', 3, marks=MARKS_CHECK_CITIES),
        pytest.param('city_user', 0, marks=MARKS_CHECK_CITIES),
        pytest.param('anomaly_viewer', 0, marks=MARKS_CHECK_CITIES),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_get_orders_permissions_spb(
        web_app_client, db, atlas_blackbox_mock, username, orders_count,
):
    request_body = {
        'tl': [61, 30],
        'br': [59, 31],
        'last_minutes': 10,
        'city': 'Санкт-Петербург',
        'has_performer': False,
    }
    response = await web_app_client.post('/api/map/orders', json=request_body)
    assert response.status == 200

    content = await response.json()
    assert len(content) == orders_count


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_order_info(web_app_client, db, atlas_blackbox_mock):
    request_body = {
        'order_id': '90e7915a-81f6-4986-b9f0-fb01d3e234f6',
        'point': [0, 0],
    }
    response = await web_app_client.post(
        '/api/map/order-info', json=request_body,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        '_id': '90e7915a-81f6-4986-b9f0-fb01d3e234f6',
        'created': '2020-12-25T03:00:01.870000+03:00',
        'performer': {
            'clid': '400000025130',
            'uuid': '320cc40b27404973ba75baa63ad41d0c',
        },
        'request': {
            'destinations': [],
            'source': {'geopoint': [37.524254, 55.674568]},
        },
        'status': 'finished',
        'user_id': '2e19fef949f25d604fbab456d0677d34',
    }


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_order_info_non_existent(
        web_app_client, db, atlas_blackbox_mock,
):
    request_body = {'order_id': 'qweqwe', 'point': [0, 0]}
    response = await web_app_client.post(
        '/api/map/order-info', json=request_body,
    )
    assert response.status == 404

    content = await response.json()
    assert content == {'message': 'Order with id: qweqwe was not found!'}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param(marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_order_info_extra_data_emit(
        web_app_client, db, atlas_blackbox_mock,
):
    request_body = {
        'order_id': '813e6aac-9b4d-4703-91a4-c96804f6173b',
        'point': [0, 0],
    }
    response = await web_app_client.post(
        '/api/map/order-info', json=request_body,
    )
    assert response.status == 200

    content = await response.json()
    assert len(content['request']['destinations']) == 1
    destination = content['request']['destinations'][0]
    assert len(destination['uris']) == 1
    assert len(destination['uris'][0]) == 299

    destination['uris'] = []
    assert destination == {
        'country': 'Россия',
        'description': 'Санкт-Петербург, Россия',
        'fullname': 'Россия, Санкт-Петербург, улица Рентгена, 5А',
        'geopoint': [30.32012, 59.963226],
        'locality': 'Санкт-Петербург',
        'object_type': 'другое',
        'premisenumber': '5А',
        'short_text': 'улица Рентгена, 5А',
        'thoroughfare': 'улица Рентгена',
        'type': 'address',
        'uris': [],
        'oid': '57434659',
    }


@pytest.mark.parametrize(
    'username, response_status',
    [
        pytest.param('omnipotent_user', 200, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('city_user', 200, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('anomaly_viewer', 403, marks=MARKS_CHECK_GEO_HIERARCHY),
        pytest.param('omnipotent_user', 200, marks=MARKS_CHECK_CITIES),
        pytest.param('city_user', 200, marks=MARKS_CHECK_CITIES),
        pytest.param('anomaly_viewer', 403, marks=MARKS_CHECK_CITIES),
    ],
)
async def test_get_order_info_permissions(
        web_app_client, db, atlas_blackbox_mock, username, response_status,
):
    request_body = {
        'order_id': '90e7915a-81f6-4986-b9f0-fb01d3e234f6',
        'point': [0, 0],
    }
    response = await web_app_client.post(
        '/api/map/order-info', json=request_body,
    )
    assert response.status == response_status

# pylint: disable=C1801
import datetime
from typing import Optional
from typing import Tuple

import pytest

from tests_driver_weariness import const
from tests_driver_weariness import weariness_tools


_BEGIN = datetime.datetime(2020, 1, 1)
_PLUS1 = _BEGIN + datetime.timedelta(hours=1)


# only status and address_from are needed
RESULT_ORDERS = [
    {
        'id': 'order0',
        'short_id': 1,
        'status': 'complete',
        'created_at': '2019-05-01T07:00:00+00:00',
        'ended_at': '2019-05-01T07:20:00+00:00',
        'driver_profile': {'id': 'driver_id_0', 'name': 'driver_name_0'},
        'car': {
            'id': 'car_id_0',
            'brand_model': 'car_model_0',
            'license': {'number': 'car_number_0'},
            'callsign': 'callsign_0',
        },
        'booked_at': '2019-05-01T07:05:00+00:00',
        'provider': 'partner',
        'address_from': {
            'address': 'Москва, Рядом с: улица Островитянова, 47',
            'lat': 0.1,
            'lon': 0.1,
        },
        'route_points': [
            {
                'address': 'Россия, Химки, Нагорная улица',
                'lat': 55.123,
                'lon': 37.1,
            },
            {'address': 'Москва, Улица 1', 'lat': 55.5111, 'lon': 37.222},
            {
                'address': 'Москва, Гостиница Прибалтийская',
                'lat': 55.5545,
                'lon': 37.8989,
            },
        ],
        'cancellation_description': 'canceled',
        'mileage': '1500.0000',
        'type': {'id': 'request_type_0', 'name': 'request_type_name'},
        'category': 'vip',
        'amenities': ['animal_transport'],
        'payment_method': 'corp',
        'driver_work_rule': {
            'id': 'work_rule_id_1',
            'name': 'work_rule_name_1',
        },
        'price': '159.9991',
        'park_details': {
            'passenger': {
                'name': 'client_id_0',
                'phones': ['phone1', 'phone2', 'phone3'],
            },
            'company': {
                'id': 'company_id_0',
                'name': 'company_name_0',
                'slip': 'company_slip_0',
                'comment': 'company_comment_0',
            },
            'tariff': {'id': 'tariff_id_0', 'name': 'tariff_name_0'},
        },
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T07:10:00+00:00',
            },
            {
                'order_status': 'waiting',
                'event_at': '2019-05-01T07:15:00+00:00',
            },
            {
                'order_status': 'calling',
                'event_at': '2019-05-01T07:16:00+00:00',
            },
            {
                'order_status': 'transporting',
                'event_at': '2019-05-01T07:17:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T07:20:00+00:00',
            },
        ],
    },
    {
        'id': 'order0',
        'short_id': 1,
        'status': 'waiting',
        'created_at': '2019-05-01T07:00:00+00:00',
        'ended_at': '2019-05-01T07:20:00+00:00',
        'driver_profile': {'id': 'driver_id_0', 'name': 'driver_name_0'},
        'car': {
            'id': 'car_id_0',
            'brand_model': 'car_model_0',
            'license': {'number': 'car_number_0'},
            'callsign': 'callsign_0',
        },
        'booked_at': '2019-05-01T07:05:00+00:00',
        'provider': 'partner',
        'address_from': {
            'address': 'Москва, Рядом с: улица Островитянова, 47',
            'lat': 1.1,
            'lon': 1.1,
        },
        'route_points': [
            {
                'address': 'Россия, Химки, Нагорная улица',
                'lat': 55.123,
                'lon': 37.1,
            },
            {'address': 'Москва, Улица 1', 'lat': 55.5111, 'lon': 37.222},
            {
                'address': 'Москва, Гостиница Прибалтийская',
                'lat': 55.5545,
                'lon': 37.8989,
            },
        ],
        'cancellation_description': 'canceled',
        'mileage': '1500.0000',
        'type': {'id': 'request_type_0', 'name': 'request_type_name'},
        'category': 'vip',
        'amenities': ['animal_transport'],
        'payment_method': 'corp',
        'driver_work_rule': {
            'id': 'work_rule_id_1',
            'name': 'work_rule_name_1',
        },
        'price': '159.9991',
        'park_details': {
            'passenger': {
                'name': 'client_id_0',
                'phones': ['phone1', 'phone2', 'phone3'],
            },
            'company': {
                'id': 'company_id_0',
                'name': 'company_name_0',
                'slip': 'company_slip_0',
                'comment': 'company_comment_0',
            },
            'tariff': {'id': 'tariff_id_0', 'name': 'tariff_name_0'},
        },
        'events': [
            {
                'order_status': 'driving',
                'event_at': '2019-05-01T07:10:00+00:00',
            },
            {
                'order_status': 'waiting',
                'event_at': '2019-05-01T07:15:00+00:00',
            },
            {
                'order_status': 'calling',
                'event_at': '2019-05-01T07:16:00+00:00',
            },
            {
                'order_status': 'transporting',
                'event_at': '2019-05-01T07:17:00+00:00',
            },
            {
                'order_status': 'complete',
                'event_at': '2019-05-01T07:20:00+00:00',
            },
        ],
    },
]


def _get_coordinates(db, udid: str) -> Optional[Tuple[float, float]]:
    cursor = db.cursor()
    cursor.execute(
        f'SELECT lon, lat FROM weariness.driver_order_coords '
        f'INNER JOIN weariness.unique_driver_ids ON driver_id=id '
        f'WHERE value=\'{udid}\'',
    )
    rows = list(row for row in cursor)
    if len(rows) == 0:
        return None
    return rows[0]


def _compare_float(x: float, y: float) -> bool:
    return abs(x - y) < 1e-3


@pytest.mark.now(_PLUS1.isoformat())
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.config(
    DRIVER_WEARINESS_ORDERS_FETCH_SETTINGS={
        'enabled': True,
        'bucket_size': 2,
        'ranges_to_view': 3,
        'orders_per_driver': 5,
        'orders_ttl_h': 24,
    },
)
@pytest.mark.pgsql(
    'drivers_status_ranges',
    queries=[weariness_tools.insert_range(f'dbid_uuid40', _BEGIN, _PLUS1)],
)
@pytest.mark.parametrize(
    'result_orders, lon_lat_res, should_call',
    [
        pytest.param(
            [RESULT_ORDERS[0]],
            (0.1, 0.1),
            True,
            id='usual driver, new coordinate',
            marks=pytest.mark.pgsql(
                'drivers_status_ranges',
                queries=[
                    weariness_tools.insert_driver(4, 'unique4'),
                    weariness_tools.insert_coordinate(
                        4, 5.0, 5.0, _BEGIN - datetime.timedelta(minutes=1),
                    ),
                ],
            ),
        ),
        pytest.param(
            [RESULT_ORDERS[1]],
            None,
            True,
            id='driver without completed orders',
        ),
        pytest.param(
            [RESULT_ORDERS[1], RESULT_ORDERS[0]],
            (0.1, 0.1),
            True,
            id='driver with completed order before failed',
        ),
        pytest.param([], None, True, id='driver without orders'),
        pytest.param(
            [RESULT_ORDERS[0]],
            (5.0, 5.0),
            False,
            marks=pytest.mark.pgsql(
                'drivers_status_ranges',
                queries=[
                    weariness_tools.insert_driver(4, 'unique4'),
                    weariness_tools.insert_coordinate(
                        4, 5.0, 5.0, _PLUS1 + datetime.timedelta(minutes=1),
                    ),
                ],
            ),
            id='driver with known coordinate',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config.json')
async def test_coordinates_fetcher(
        taxi_driver_weariness,
        pgsql,
        result_orders,
        lon_lat_res: Optional[Tuple[float, float]],
        should_call,
        mockserver,
        experiments3,
):
    weariness_tools.add_experiment(
        experiments3, weariness_tools.WearinessConfig(1000, 1000, 1000),
    )

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def handler(request):
        body = request.json['query']['park']
        assert request.json['limit'] == 5
        assert body['id'] == 'dbid'
        assert body['driver_profile']['id'] == 'uuid40'

        assert (
            body['order']['booked_at']['from']
            == (_PLUS1 - datetime.timedelta(hours=24)).isoformat() + '+00:00'
        )
        assert (
            body['order']['booked_at']['to'] == _PLUS1.isoformat() + '+00:00'
        )

        return {'orders': result_orders, 'limit': 5}

    await taxi_driver_weariness.invalidate_caches()
    await weariness_tools.activate_task(
        taxi_driver_weariness, 'coordinates-fetcher',
    )

    assert handler.times_called == (1 if should_call else 0)

    coords = _get_coordinates(pgsql['drivers_status_ranges'], 'unique4')
    if lon_lat_res is None:
        assert coords is None
    else:
        assert coords is not None
        assert _compare_float(coords[0], lon_lat_res[0])
        assert _compare_float(coords[1], lon_lat_res[1])


def _get_min_revision(db) -> int:
    cursor = db.cursor()
    cursor.execute(f'SELECT MIN(revision) FROM weariness.working_ranges')
    return list(row for row in cursor)[0][0]


def _get_last_updated_revision(db) -> int:
    cursor = db.cursor()
    cursor.execute(
        f'SELECT revision FROM weariness.last_revision_coord_fetched',
    )
    return list(row for row in cursor)[0][0]


def _get_time_shift(index: int):
    if index < 6:
        return datetime.timedelta(days=10)
    return datetime.timedelta()


@pytest.mark.now(_PLUS1.isoformat())
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.config(
    DRIVER_WEARINESS_ORDERS_FETCH_SETTINGS={
        'enabled': True,
        'bucket_size': 2,
        'ranges_to_view': 2,
        'orders_per_driver': 5,
        'orders_ttl_h': 24,
    },
)
@pytest.mark.pgsql(
    'drivers_status_ranges',
    queries=[
        weariness_tools.insert_range(
            f'dbid_uuid{i}{i%2}',
            _BEGIN - _get_time_shift(i),
            _PLUS1 - _get_time_shift(i),
        )
        for i in range(4, 10)
    ],
)
async def test_multiple_coordinates_fetcher(
        taxi_driver_weariness, pgsql, mockserver, experiments3,
):
    weariness_tools.add_experiment(
        experiments3, weariness_tools.WearinessConfig(1000, 1000, 1000),
    )

    db = pgsql['drivers_status_ranges']
    min_revision = _get_min_revision(db)

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def handler(request):
        body = request.json['query']['park']
        assert request.json['limit'] == 5
        assert body['id'] == 'dbid'

        assert (
            body['order']['booked_at']['from']
            == (_PLUS1 - datetime.timedelta(hours=24)).isoformat() + '+00:00'
        )
        assert (
            body['order']['booked_at']['to'] == _PLUS1.isoformat() + '+00:00'
        )

        driver_number = body['driver_profile']['id'][4]
        if driver_number == '7':
            return mockserver.make_response('{}', status=400)
        return {'orders': [RESULT_ORDERS[0]], 'limit': 5}

    await taxi_driver_weariness.invalidate_caches()

    for i in range(3):
        await weariness_tools.activate_task(
            taxi_driver_weariness, 'coordinates-fetcher',
        )

        last_processed = _get_last_updated_revision(db)
        assert last_processed == min_revision + i * 2 + 1
        # first two times driver-orders should be called, because too old
        # ranges included in cache too
        assert handler.times_called == (i + 1) * 2

    for i in range(4, 10):
        coords = _get_coordinates(db, f'unique{i}')
        # no coords for seventh driver, no answer for him from driver-orders
        # but too old ranges for 4 and 5 will have coords
        if i == 7:
            assert coords is None
        else:
            assert _compare_float(coords[0], 0.1)
            assert _compare_float(coords[1], 0.1)

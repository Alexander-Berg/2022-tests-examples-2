# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime

from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
import psycopg2.extras
import pytest

from eats_customer_slots_plugins import *  # noqa: F403 F401

from tests_eats_customer_slots import utils

MONTH_NAMES = [
    'января',
    'февраля',
    'марта',
    'апреля',
    'мая',
    'июня',
    'июля',
    'августа',
    'сентября',
    'октября',
    'ноября',
    'декабря',
]


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture for eats-catalog-storage places cache',
    )


@pytest.fixture(name='make_expected_slots')
def _make_expected_slots(mocked_time):
    def do_make_expected_slots(timepoint, brand_id, working_intervals):
        today = utils.localize(mocked_time.now(), timepoint.tzinfo).date()
        expected_slots = []
        daily_slots = utils.BRAND_CONFIG[brand_id]['daily_slots']
        for item in daily_slots:
            day = item['day']
            slots = item['slots']
            for slot in slots:
                start = utils.make_datetime(
                    utils.add_days(today, day),
                    slot['start'],
                    timepoint.tzinfo,
                )
                end = utils.make_datetime(
                    utils.add_days(
                        today, day + int(slot['start'] >= slot['end']),
                    ),
                    slot['end'],
                    timepoint.tzinfo,
                )
                if start >= timepoint:
                    for working_interval in working_intervals:
                        if (
                                start
                                >= datetime.datetime.fromisoformat(
                                    working_interval['start'],
                                )
                                and end
                                < datetime.datetime.fromisoformat(
                                    working_interval['end'],
                                )
                        ):
                            expected_slots.append(
                                {
                                    'start': start.isoformat(),
                                    'end': end.isoformat(),
                                    'estimated_delivery_timepoint': (
                                        start.isoformat()
                                    ),
                                },
                            )
                            break
        return expected_slots

    return do_make_expected_slots


@pytest.fixture(name='mock_calculate_load', autouse=True)
def _mock_calculate_load(mockserver, now):
    @mockserver.json_handler(
        '/eats-picker-dispatch/api/v1/places/calculate-load',
    )
    def do_mock_calculate_load(request):
        return mockserver.make_response(**do_mock_calculate_load.response)

    time_zone = 'Europe/Moscow'
    now = utils.localize(now, time_zone)
    do_mock_calculate_load.place_load_info_stub = {
        'place_id': 123456,
        'brand_id': 1,
        'country_id': 1,
        'region_id': 1,
        'time_zone': time_zone,
        'city': 'Москва',
        'enabled': True,
        'working_intervals': utils.make_working_intervals(
            now,
            [
                {
                    'day_from': 0,
                    'time_from': '00:00',
                    'day_to': 1,
                    'time_to': '00:00',
                },
                {
                    'day_from': 1,
                    'time_from': '00:00',
                    'day_to': 2,
                    'time_to': '00:00',
                },
            ],
        ),
        'estimated_waiting_time': 0,
        'free_pickers_count': 2,
        'total_pickers_count': 2,
        'is_place_closed': False,
        'is_place_overloaded': False,
    }
    do_mock_calculate_load.response = {
        'json': {
            'places_load_info': [
                do_mock_calculate_load.place_load_info_stub.copy(),
            ],
        },
    }

    return do_mock_calculate_load


@pytest.fixture(name='mock_partner_average_delivery_slots', autouse=True)
# pylint: disable=invalid-name
def mock_partner_average_delivery_slots(mockserver):
    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-average-delivery-slots',
    )
    # pylint: disable=invalid-name
    def do_mock_partner_average_delivery_slots(request):
        if 'delivery_point' in request.json:
            assert 'latitude' in request.json['delivery_point']
            assert 'longitude' in request.json['delivery_point']
        places_origin_ids = [
            place['place_origin_id'] for place in request.json['places']
        ]
        return mockserver.make_response(
            status=200,
            json={
                'slots_by_place': [
                    utils.make_partner_place_delivery_slots(place_origin_id)
                    for place_origin_id in places_origin_ids
                ],
            },
        )

    return do_mock_partner_average_delivery_slots


@pytest.fixture(name='mock_partner_delivery_slots', autouse=True)
def mock_partner_delivery_slots(mockserver):
    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-delivery-slots',
    )
    def do_mock_partner_delivery_slots(request):
        return mockserver.make_response(
            status=200,
            json={
                'slots': utils.make_partner_place_delivery_slots(
                    request.json['place_origin_id'],
                ),
            },
        )

    return do_mock_partner_delivery_slots


@pytest.fixture(name='catalog_storage_cache')
def _load_catalog_storage_cache(load_json):
    catalog_storage_cache = load_json('catalog_storage_cache.json')
    return {p['id']: p for p in catalog_storage_cache}


@pytest.fixture(name='partner_picking_slots')
def _load_partner_picking_slots(load_json):
    partner_picking_slots = load_json('partner_picking_slots.json')
    return {p['place_id']: p for p in partner_picking_slots}


@pytest.fixture(name='mock_partner_picking_slots', autouse=True)
def _mock_partner_picking_slots(
        mockserver, catalog_storage_cache, partner_picking_slots,
):
    origin_id_to_place_id = {
        place['origin_id']: place_id
        for place_id, place in catalog_storage_cache.items()
        if 'origin_id' in place
    }

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    def do_mock_get_picking_slots(request):
        place_origin_id = request.json['place_origin_id']
        if place_origin_id in origin_id_to_place_id:
            place_id = origin_id_to_place_id[place_origin_id]
            if place_id in partner_picking_slots:
                slots = partner_picking_slots[place_id]['slots']
                if slots is not None:
                    return mockserver.make_response(
                        json={'picking_slots': slots},
                    )
                return mockserver.make_response(
                    status=404,
                    json={'code': 'not_found', 'message': 'Not Found'},
                )
            return mockserver.make_response(
                status=400,
                json={'code': 'bad_request', 'message': 'Bad Request'},
            )
        return mockserver.make_response(
            status=500,
            json={
                'code': 'server_internal_error',
                'message': 'Server Internal Error',
            },
        )

    return do_mock_get_picking_slots


def make_text(now, delivery_timepoint, text_type):
    delivery_timepoint = delivery_timepoint.astimezone(now.tzinfo)
    days_delta = (delivery_timepoint.date() - now.date()).days
    if days_delta == 0:
        fmt = utils.DEFAULT_TEXT_FORMATS[f'{text_type}_text_today']
    elif days_delta == 1:
        fmt = utils.DEFAULT_TEXT_FORMATS[f'{text_type}_text_tomorrow']
    else:
        fmt = utils.DEFAULT_TEXT_FORMATS[f'{text_type}_text_x_days']
    fmt = fmt.replace('%B', MONTH_NAMES[delivery_timepoint.month - 1])
    return delivery_timepoint.strftime(fmt)


def make_short_text(now, delivery_timepoint):
    return make_text(now, delivery_timepoint, 'short')


def make_full_text(now, delivery_timepoint):
    return make_text(now, delivery_timepoint, 'full')


@pytest.fixture(name='make_expected_delivery_time_info')
def _make_expected_delivery_time_info(make_expected_slots):
    def _make_delivery_time_info(
            place_id, now, asap_availability=False, delivery_timepoint=None,
    ):
        delivery_time_info = {
            'place_id': place_id,
            'asap_availability': asap_availability,
        }
        if delivery_timepoint is None:
            delivery_time_info['slots_availability'] = False
            delivery_time_info['delivery_eta'] = 0
            if asap_availability:
                delivery_time_info['short_text'] = utils.DEFAULT_TEXT_FORMATS[
                    'short_text_slots_unavailable'
                ]
                delivery_time_info['full_text'] = utils.DEFAULT_TEXT_FORMATS[
                    'full_text_slots_unavailable'
                ]
            else:
                delivery_time_info['short_text'] = utils.DEFAULT_TEXT_FORMATS[
                    'short_text_delivery_unavailable'
                ]
                delivery_time_info['full_text'] = utils.DEFAULT_TEXT_FORMATS[
                    'full_text_delivery_unavailable'
                ]
        else:
            delivery_time_info['slots_availability'] = True
            delivery_time_info['delivery_eta'] = int(
                (delivery_timepoint - now).total_seconds(),
            )
            delivery_time_info['short_text'] = make_short_text(
                now, delivery_timepoint,
            )
            delivery_time_info['full_text'] = make_full_text(
                now, delivery_timepoint,
            )
        return delivery_time_info

    return _make_delivery_time_info


@pytest.fixture(name='get_cursor')
def _get_cursor(pgsql):
    def do_get_cursor():
        return pgsql['eats_customer_slots'].dict_cursor()

    return do_get_cursor


class IntervalCapacityCaster(psycopg2.extras.CompositeCaster):
    def make(self, values):
        return dict(zip(self.attnames, values))


@pytest.fixture(name='get_all_places_intervals')
def _get_all_places_intervals(get_cursor):
    def do_get_all_places_intervals():
        cursor = get_cursor()
        psycopg2.extras.register_composite(
            name='eats_customer_slots.interval_capacity_v1',
            conn_or_curs=cursor,
            factory=IntervalCapacityCaster,
        )
        cursor.execute(
            """SELECT place_id, logistics_group_id, capacities
            FROM eats_customer_slots.places
            ORDER BY place_id""",
        )
        return list(map(dict, cursor.fetchall()))

    return do_get_all_places_intervals


@pytest.fixture(name='mock_get_preorders', autouse=True)
def _mock_get_preorders(mockserver):
    @mockserver.json_handler('/eats-picker-orders/api/v1/orders/preorders')
    def do_mock_get_preorders(request):
        return mockserver.make_response(status=200, json={'preorders': []})

    return do_mock_get_preorders


@pytest.fixture(name='create_place_intervals')
def _create_place_intervals(get_cursor):
    def do_create_place_intervals(
            place_id=1, logistics_group_id=1, capacities=None,
    ):
        cursor = get_cursor()
        psycopg2.extras.register_composite(
            name='eats_customer_slots.interval_capacity_v1',
            conn_or_curs=cursor,
            factory=IntervalCapacityCaster,
        )
        if not capacities:
            capacities = []
        cursor.execute(
            """INSERT INTO eats_customer_slots.places
            (place_id, logistics_group_id, capacities)
            VALUES(%s, %s,
            CAST(%s AS eats_customer_slots.interval_capacity_v1[]))
            RETURNING id;
            """,
            (place_id, logistics_group_id, capacities),
        )
        return cursor.fetchone()[0]

    return do_create_place_intervals

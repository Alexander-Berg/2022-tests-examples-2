# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import datetime
from urllib import parse as urlparse

from eats_bigb import eats_bigb  # noqa: F403 F401
from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
import pytest
from umlaas_eats_plugins import *  # noqa: F403 F401


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture for eats-catalog-storage places cache',
    )
    config.addinivalue_line(
        'markers', 'bigb: [bigb]' 'fixture for bigb client',
    )


@pytest.fixture(name='catalog_v1')
def catalog_v1(taxi_umlaas_eats):
    async def send_request(
            request: dict,
            service_name='pytest',
            place_list_context='common',
            request_id='value_request_id',
            user_uid=1184610,
            sort=None,
            headers=None,
    ):
        params = dict(
            service_name=service_name,
            place_list_context=place_list_context,
            request_id=request_id,
            user_uid=user_uid,
        )
        if sort is not None:
            params['sort'] = sort

        query = urlparse.urlencode(params)
        if headers is None:
            headers = {}

        if 'X-Eats-User' not in headers and user_uid is not None:
            headers['X-Eats-User'] = f'user_id={user_uid}'

        return await taxi_umlaas_eats.post(
            f'umlaas-eats/v1/catalog?{query}', request, headers=headers,
        )

    return send_request


@pytest.fixture(autouse=True)
def eda_surge_calculator(mockserver, load_json):
    @mockserver.json_handler('/eda-surge-calculator/v1/extended-supply')
    def _extended_supply_handler(request):
        return load_json('eda_surge_calculator_extended_supply_response.json')


@pytest.fixture(autouse=True)
def retail_queue_length(mockserver, load_json):
    @mockserver.json_handler('/eats-picker-orders/api/v1/places/queue-length')
    def _queue_handler(request):
        requested_ids = request.json['place_ids']
        data = load_json('retail_queue_length_response.json')
        return {
            'orders': [
                place
                for place in data['orders']
                if place['place_id'] in requested_ids
            ],
        }


@pytest.fixture(autouse=True)
def regional_offset_calculator(mockserver, load_json):
    @mockserver.json_handler('/eats-surge-resolver/api/v2/surge-level')
    def _load_level_calculator(request):
        data = load_json('load_level_response.json')
        requested_ids = request.json['placeIds']
        return [
            place
            for place in data['result']
            if place['placeId'] in requested_ids
        ]


@pytest.fixture(autouse=True)
def real_time_statistics_provider(mockserver, load_json):
    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/places-event-counters',
    )
    def _real_time_statistics_provider(request):
        data = load_json('real_time_statistics_response.json')

        return {
            'data': [
                place
                for place in data['data']
                if place['place_id'] in request.json['place_ids']
            ],
        }


@pytest.fixture(autouse=True)
def retail_queue_length_filter(mockserver, load_json):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/'
        'eats-catalog-storage/v1/search/places/list',
    )
    def _queue_filter_handler(request):
        ids_with_our_picking = (919191,)
        requested_id = request.json['place_ids'][0]
        data = load_json('retail_queue_length_filter_response.json')
        if requested_id in ids_with_our_picking:
            data['places'][0]['place_id'] = requested_id
        else:
            data['places'][0]['place_id'] = requested_id
            data['places'][0]['place']['features'][
                'shop_picking_type'
            ] = 'shop_picking'
        return {
            'not_found_place_ids': [],
            'not_found_place_slugs': [],
            'places': data['places'],
        }


@pytest.fixture(autouse=True)
def retail_pickers_info(mockserver):
    @mockserver.json_handler(
        '/eats-picker-dispatch/api/v1/places/calculate-load',
    )
    def _retail_pickers_info(request):
        requested_ids = request.json['place_ids']
        valid_ids = (919191,)
        return {
            'places_load_info': [
                {
                    'place_id': requested_id,
                    'brand_id': 100500,
                    'country_id': 1,
                    'region_id': 1,
                    'time_zone': 'Moscow/Europe',
                    'city': 'Moscow',
                    'enabled': True,
                    'working_intervals': [
                        {
                            'start': '2021-07-28T06:00:00+00:00',
                            'end': '2021-07-28T21:00:00+00:00',
                        },
                    ],
                    'estimated_waiting_time': 600,
                    'free_pickers_count': 2,
                    'total_pickers_count': 3,
                    'is_place_closed': False,
                    'is_place_overloaded': False,
                }
                for requested_id in requested_ids
                if requested_id in valid_ids
            ],
        }


@pytest.fixture(autouse=True)
def get_picking_slots(mockserver):
    @mockserver.json_handler(
        '/eats-customer-slots/api/v1/partner/get-picking-slots',
    )
    def _get_picking_slots(request):
        requested_id = request.json['place_id']
        assert request.json['user_id'] == '1184610'
        # let's ignore cart items here
        slot_start = datetime.datetime.now(
            datetime.timezone.utc,
        ) + datetime.timedelta(minutes=15)
        slot_end = datetime.datetime.now(
            datetime.timezone.utc,
        ) + datetime.timedelta(minutes=30)
        return {
            'place_id': requested_id,
            'place_origin_id': 'some_id',
            'picking_slots': [
                {
                    'picking_slot_id': 'some_id',
                    'picking_slot_start': (
                        slot_start + datetime.timedelta(minutes=15)
                    ).isoformat(),
                    'picking_slot_end': (
                        slot_end + datetime.timedelta(minutes=15)
                    ).isoformat(),
                    'picking_duration': 600,
                },
                {
                    'picking_slot_id': 'some_other_id',
                    'picking_slot_start': slot_start.isoformat(),
                    'picking_slot_end': slot_end.isoformat(),
                    'picking_duration': 600,
                },
            ],
        }


@pytest.fixture(autouse=True)
def get_average_picking_slots(mockserver):
    @mockserver.json_handler(
        '/eats-customer-slots/api/v1/partner/get-average-picking-slots',
    )
    def _get_average_picking_slots(request):
        requested_id = request.json['places'][0]['place_id']
        slot_start = datetime.datetime.now(
            datetime.timezone.utc,
        ) + datetime.timedelta(minutes=15)
        slot_end = datetime.datetime.now(
            datetime.timezone.utc,
        ) + datetime.timedelta(minutes=30)
        return {
            'places_picking_slots': [
                {
                    'place_id': requested_id,
                    'place_origin_id': 'some_id',
                    'picking_slots': [
                        {
                            'picking_slot_id': 'some_id',
                            'picking_slot_start': slot_start.isoformat(),
                            'picking_slot_end': slot_end.isoformat(),
                        },
                    ],
                },
            ],
        }


@pytest.fixture(autouse=True)
def _mock_grocery_suggest_stocks(mockserver, load_json):
    @mockserver.json_handler(
        '/overlord-catalog/v1/catalog/availableforsale/', prefix=True,
    )
    def _mock(request):
        return load_json('grocery_suggest_stocks_response.json')

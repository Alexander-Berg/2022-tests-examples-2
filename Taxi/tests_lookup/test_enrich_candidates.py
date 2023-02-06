import uuid

import pytest

from tests_lookup import mock_candidates


def create_params(**kwargs):
    order_id = uuid.uuid4()
    user_id = uuid.uuid4()
    lookup_params = {
        'order_id': str(order_id),
        'order': {
            '_type': kwargs.get('type', 'soon'),
            'user_id': str(user_id),
            'nearest_zone': 'moscow',
            'svo_car_number': kwargs.get('svo_car_number', None),
            'request': {
                'source': {'geopoint': [15.0, 15.0]},
                'destinations': [{'geopoint': [3.0, 4.0]}],
                'sp': kwargs.get('surge_price', 1.0),
                'spr': kwargs.get('surge_price_required', None),
                'class': kwargs.get('tariffs', ['econom']),
            },
            'feedback': {  # специальные флаги для заказов-проверок
                'mqc': False,
            },
            'calc': {
                'distance': 10000.01,
                'time': 600.01,
                'alternative_type': '',
            },
            'fixed_price': {
                'price': 121,  # опционально
                'paid_supply_price': None,  # опционально
                'paid_supply_info': {
                    'distance': kwargs.get('max_route_distance', None),
                    'time': kwargs.get('max_route_time', None),
                },
            },
            'user_phone_id': 'phone_id',
            'discount': {
                'by_classes': [
                    {
                        'class': 'express',
                        'description': 'master_yt_ru_delivery_25_05_2020',
                        'driver_less_coeff': 0,
                        'id': '12b64b17-31c2-4bd2-ad60-76651454c147',
                        'is_cashback': False,
                        'limited_rides': False,
                        'max_absolute_value': 3000,
                        'method': 'subvention-fix',
                        'price': 282.1971249547082,
                        'reason': 'for_all',
                        'value': 0.1,
                    },
                    {
                        'class': 'econom',
                        'description': 'test_strikethrough',
                        'driver_less_coeff': 0.5,
                        'id': 'f4adea2d-3a73-4a0b-a6c1-945cae00792e',
                        'is_cashback': False,
                        'is_price_strikethrough': True,
                        'limited_rides': False,
                        'method': 'full',
                        'price': 564.0695475067487,
                        'reason': 'for_all',
                        'value': 0.3,
                    },
                    {
                        'class': 'courier',
                        'description': 'master_yt_ru_delivery_25_05_2020',
                        'driver_less_coeff': 0,
                        'id': '12b64b17-31c2-4bd2-ad60-76651454c147',
                        'is_cashback': False,
                        'limited_rides': False,
                        'max_absolute_value': 3000,
                        'method': 'subvention-fix',
                        'price': 236.8194802985191,
                        'reason': 'for_all',
                        'value': 0.1,
                    },
                    {
                        'class': 'business',
                        'description': 'test_strikethrough',
                        'driver_less_coeff': 0.5,
                        'id': 'f4adea2d-3a73-4a0b-a6c1-945cae00792e',
                        'is_cashback': False,
                        'is_price_strikethrough': True,
                        'limited_rides': False,
                        'method': 'full',
                        'price': 454.4051132397755,
                        'reason': 'for_all',
                        'value': 0.3,
                    },
                ],
            },
        },
        'payment_tech': {'type': 'cash'},
        'active_candidates': [],
        'aliases': [],
    }
    # поколение и версия
    if (
            kwargs.get('generation')
            and kwargs.get('version')
            and kwargs.get('wave')
    ):
        lookup_params['lookup'] = {
            'generation': kwargs.get('generation'),
            'version': kwargs.get('version'),
            'wave': kwargs.get('wave'),
        }
    return lookup_params


@pytest.mark.now('2020-04-09 14:56:18.926246')
async def test_enrich_candidates(taxi_lookup, mockserver):
    request = {}
    request['params'] = create_params()
    request['candidates'] = mock_candidates.make_candidates()['candidates']
    response = await taxi_lookup.post('enrich-candidates', request)
    assert response.status_code == 200
    body = response.json()
    candidate = body['candidates'][0]
    # inconstant values
    candidate['car'].pop('dbcar_id', None)
    candidate.pop('due', None)
    candidate.pop('car_model', None)
    candidate.pop('alias_id', None)
    assert candidate == {
        'id': (
            '7f74df331eb04ad78bc2ff25ff88a8f2_4bb5a0018d9641c681c1a854b21ec9ab'
        ),
        'autoaccept': None,
        'clid': '12345',
        'uuid': '4bb5a0018d9641c681c1a854b21ec9ab',
        'status': {'driver': 'free', 'online_start': 1571216339},
        'driver_license': 'number-67666d1b64314ff4a8d82ee89cd9d111',
        'license_id': '67666d1b64314ff4a8d82ee89cd9d111',
        'unique_driver_id': '5dcbf13eb8e3f87968f01111',
        'car_number': 'А100ВR777',
        'classes': ['econom'],
        'driver_classes': ['econom', 'business'],
        'taximeter_version': '9.07 (1234)',
        'dbid': '7f74df331eb04ad78bc2ff25ff88a8f2',
        'adjusted_point': {
            'speed': 35,
            'direction': 214,
            'lat': 55.4183979995,
            'lon': 37.8954151234,
            'timestamp': 1533817820,
        },
        'position': [37.642907, 55.735141],
        'route_info': {'approximate': True, 'distance': 125, 'time': 18},
        'in_extended_radius': False,
        'phone_pd_id': '+799999999',
        'phone': 'number-+799999999',
        'first_name': 'Maxim',
        'name': 'Urev Maxim Dmitrievich',
        'hiring_details': {'date': None, 'type': 'type'},
        'tags': ['tag0', 'tag1', 'tag2', 'tag3'],
        'metadata': {'some_field': 'some_value-1'},
        'car': {
            'raw_color': 'red',
            'color': 'Red',
            'color_code': 'red_code',
            'model': 'BMW X2',
        },
        'gprs_time': 20.0,
        'metrica_device_id': '112233',
        'tariff_info': {
            'category_id': 'b7c4d5f6aa3b40a3807bb74b3bc042af',
            'category_name': 'econom',
            'currency': 'RUB',
            'zone_ids': [],
        },
        'driver_metrics': {
            'type': 'fallback',
            'activity_blocking': {
                'activity_threshold': 30,
                'duration_sec': 3600,
            },
            'activity_prediction': {'c': 0},
            'activity': 100,
            'id': None,
            'dispatch': None,
            'properties': None,
        },
        'discount': {
            'class': 'econom',
            'description': 'test_strikethrough',
            'driver_less_coeff': 0.5,
            'id': 'f4adea2d-3a73-4a0b-a6c1-945cae00792e',
            'is_cashback': False,
            'is_price_strikethrough': True,
            'limited_rides': False,
            'method': 'full',
            'price': 564.0695475067487,
            'reason': 'for_all',
            'value': 0.3,
        },
    }


async def test_enrich_candidates_error(taxi_lookup, mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return {'drivers': []}

    request = {}
    request['params'] = create_params()
    request['candidates'] = mock_candidates.make_candidates()['candidates']
    response = await taxi_lookup.post('enrich-candidates', request)
    assert response.status_code == 200
    body = response.json()
    assert len(body['errors']) == 3

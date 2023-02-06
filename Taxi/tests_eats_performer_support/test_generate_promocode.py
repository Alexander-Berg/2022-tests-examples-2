import json

import pytest
from . import conftest

# time in moscow
NOW = '2021-06-09T23:00:00+0000'

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaEda-CourierId': '1',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.65 (5397)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


# 1
@pytest.fixture(name='get_courier_from_msk')
async def _get_courier_from_msk(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/1',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 1,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 1,
                    'name': 'MSK',
                    'timezone': 'Europe/Moscow',  # UTC+3
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


# 8 / 7
@pytest.fixture(name='get_courier_from_los_angeles')
async def _get_courier_from_los_angeles(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/8',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 8,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 8,
                    'name': 'NVS',
                    'timezone': 'America/Los_Angeles',  # UTC-8 / UTC-7
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.fixture(name='generate_promocode')
async def _get_generated_promocode(mockserver):
    @mockserver.json_handler('/coupons/internal/generate')
    def _mock_handler(request):
        return {
            'promocode': 'code',
            'promocode_params': {
                'value': 30,
                'expire_at': '2021-05-20T00:00:00+00:00',
                'currency_code': 'RUB',
            },
        }


@pytest.fixture(name='mock_user_api')
async def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _mock_handler(request):
        return {
            'id': 'user_phone_id',
            'phone': '+70009999987',
            'type': 'yandex',
            'is_taxi_staff': False,
            'is_yandex_staff': False,
            'is_loyal': False,
            'stat': {
                'total': 0,
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
            },
        }


@pytest.fixture(name='shift_ends_before_time_generation')
async def _get_shift_ends_before_time_generation(mockserver):
    @mockserver.json_handler('/eats-shifts/server-api/couriers/1/near-shifts')
    def _mock_handler(request):
        return {
            'data': {
                'previous': {
                    'startsAt': '2021-06-09T14:37:56+03:00',
                    'endsAt': '2021-06-09T22:59:00+03:00',
                    'hasEarlyLeaving': False,
                    'shiftType': 'planned',
                    'store': False,
                },
                'current': None,
                'next': None,
            },
        }


@pytest.fixture(name='shift_ends_after_time_generation')
async def _get_shift_ends_after_time_generation(mockserver):
    @mockserver.json_handler('/eats-shifts/server-api/couriers/8/near-shifts')
    def _mock_handler(request):
        return {
            'data': {
                'previous': {
                    'startsAt': '2021-06-09T14:37:56-08:00',
                    'endsAt': '2021-06-10T05:01:00-08:00',
                    'hasEarlyLeaving': False,
                    'shiftType': 'planned',
                    'store': False,
                },
                'current': None,
                'next': None,
            },
        }


@pytest.fixture(name='one_day_generation')
async def _get_one_day_generation(mockserver):
    @mockserver.json_handler('/eats-shifts/server-api/couriers/1/near-shifts')
    def _mock_handler(request):
        return {
            'data': {
                'previous': {
                    'startsAt': '2021-06-09T14:37:56+03:00',
                    'endsAt': '2021-06-10T01:00:00+03:00',
                    'hasEarlyLeaving': False,
                    'shiftType': 'planned',
                    'store': False,
                },
                'current': None,
                'next': None,
            },
        }


@pytest.fixture(name='two_days_generation')
async def _get_two_days_generation(mockserver):
    @mockserver.json_handler('/eats-shifts/server-api/couriers/8/near-shifts')
    def _mock_handler(request):
        return {
            'data': {
                'previous': {
                    'startsAt': '2021-06-09T14:37:56-07:00',
                    'endsAt': '2021-06-09T23:56:00-07:00',
                    'hasEarlyLeaving': False,
                    'shiftType': 'planned',
                    'store': False,
                },
                'current': None,
                'next': None,
            },
        }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_shift_ends_before_time_generation(
        taxi_eats_performer_support,
        shift_ends_before_time_generation,
        get_courier_from_msk,
):
    response = await taxi_eats_performer_support.post(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/generate',
        headers=DEFAULT_HEADERS,
        json={'type': 'after_shift'},
    )

    assert response.status_code == 400


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3_big_generate_ttl.json')
async def test_shift_ends_after_time_generation(
        taxi_eats_performer_support,
        shift_ends_after_time_generation,
        get_courier_from_los_angeles,
):
    response = await taxi_eats_performer_support.post(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/generate',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '8'}},
        json={'type': 'after_shift'},
    )

    assert response.status_code == 400


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3_one_day_generation.json')
async def test_shift_one_day_generation(
        taxi_eats_performer_support,
        one_day_generation,
        get_courier_from_msk,
        mock_user_api,
        generate_promocode,
):
    response = await taxi_eats_performer_support.post(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/generate',
        headers=DEFAULT_HEADERS,
        json={'type': 'after_shift'},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '01:00',
                'code': 'code',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now('2021-06-10T07:00:00+0000')
@pytest.mark.experiments3()
async def test_shift_two_days_generation(
        taxi_eats_performer_support,
        two_days_generation,
        get_courier_from_los_angeles,
        mock_user_api,
        generate_promocode,
):
    response = await taxi_eats_performer_support.post(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/generate',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '8'}},
        json={'type': 'after_shift'},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '23:00',
                'code': 'code',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.fixture(name='in_same_day_generation')
async def _get_in_same_day_generation(mockserver):
    @mockserver.json_handler('/eats-shifts/server-api/couriers/10/near-shifts')
    def _mock_handler(request):
        return {
            'data': {
                'previous': {
                    'startsAt': '2021-06-30T13:13:56+03:00',
                    'endsAt': '2021-06-30T13:14:00+03:00',
                    'hasEarlyLeaving': False,
                    'shiftType': 'planned',
                    'store': False,
                },
                'current': None,
                'next': None,
            },
        }


@pytest.fixture(name='get_courier_in_same_day')
async def _get_courier_in_same_day(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/10',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 8,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 1,
                    'name': 'Москва',
                    'timezone': 'Europe/Moscow',  # UTC-8 / UTC-7
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.mark.now('2021-06-30T11:25:17+0000')
@pytest.mark.experiments3(filename='experiments3_in_same_day.json')
@pytest.mark.config(
    EATS_PERFORMER_SUPPORT_FEATURE_FLAGS={'enable_work_mode_check': True},
)
async def test_shift_generation_in_same_day(
        taxi_eats_performer_support,
        in_same_day_generation,
        get_work_mode_in_same_day,
        get_courier_in_same_day,
        mock_user_api,
        generate_promocode,
):
    response = await taxi_eats_performer_support.post(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/generate',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '10'}},
        json={'type': 'after_shift'},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '10:00',
                'code': 'code',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.fixture(name='mock_user_api_not_found_phone_id')
async def _mock_user_api_not_found_phone_id(mockserver):
    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def _mock_handler(request):
        return mockserver.make_response(
            response=json.dumps(
                {
                    'code': 'more machine-readable error codes, more, please',
                    'message': 'human-readable message',
                },
            ),
            content_type='application/json',
            status=404,
        )


@pytest.mark.now('2021-06-30T11:25:17+0000')
@pytest.mark.experiments3(filename='experiments3_in_same_day.json')
async def test_shift_generation_taxi_phone_id_not_exists(
        taxi_eats_performer_support,
        in_same_day_generation,
        get_courier_in_same_day,
        mock_user_api_not_found_phone_id,
        generate_promocode,
):
    response = await taxi_eats_performer_support.post(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/generate',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '10'}},
        json={'type': 'after_shift'},
    )

    assert response.json() == {
        'code': (
            'eats_performer_support.promocode_generation.taxi_client_not_found'
        ),
        'message': (
            'Для того, чтобы воспользоваться промокодом, вам необходимо'
            ' создать учетную запись в Яндекс.Go'
        ),
    }

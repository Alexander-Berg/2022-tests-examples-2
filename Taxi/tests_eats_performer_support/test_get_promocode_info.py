# import psycopg2
import pytest


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


@pytest.fixture(name='get_courier_from_samara')
async def _get_courier_from_samara(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/2',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 2,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 2,
                    'name': 'SMR',
                    'timezone': 'Europe/Samara',  # UTC+4
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.fixture(name='get_courier_from_novokuznetsk')
async def _get_courier_from_novokuznetsk(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/3',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 3,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 3,
                    'name': 'SMR',
                    'timezone': 'Asia/Novokuznetsk',  # UTC+7
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.fixture(name='get_courier_from_vladivostok')
async def _get_courier_from_vladivostok(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/4',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 4,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 4,
                    'name': 'VLD',
                    'timezone': 'Asia/Vladivostok',  # UTC+10
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.fixture(name='get_courier_from_new_york')
async def _get_courier_from_new_york(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/5',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 5,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 5,
                    'name': 'NVS',
                    'timezone': 'America/New_York',  # UTC-5
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.fixture(name='get_courier_from_chicago')
async def _get_courier_from_chicago(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/6',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 6,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 6,
                    'name': 'NVS',
                    'timezone': 'America/Chicago',  # UTC-6
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.fixture(name='get_courier_from_phoenix')
async def _get_courier_from_phoenix(mockserver):
    @mockserver.json_handler(
        '/couriers-core/api/v1/general-information/couriers/7',
    )
    def _mock_handler(request):
        return {
            'courier': {
                'id': 7,
                'first_name': 'first_name',
                'last_name': 'last_name',
                'phone_number': '5eb48fee85134dc6bc00d592ecfe7df4',
                'billing_type': 'courier_service',
                'courier_type': 'bicycle',
                'registration_country': {'name': 'Россия', 'code': 'RU'},
                'work_region': {
                    'id': 7,
                    'name': 'NVS',
                    'timezone': 'America/Phoenix',  # UTC-7
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


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
                    'timezone': 'America/Los_Angeles',  # UTC-8
                    'currency': {'code': 'RUB', 'sign': '₽'},
                },
                'work_status': 'active',
                'work_status_updated_at': '2021-06-09T22:10:00+0000',
                'project_type': 'eda',
            },
        }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_msk_courier(taxi_eats_performer_support, get_courier_from_msk):

    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers=DEFAULT_HEADERS,
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '31.00',
                'available_from': '23:00',
                'code': 'code_1',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_samara_courier(
        taxi_eats_performer_support, get_courier_from_samara,
):
    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '2'}},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '23:00',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_novokuznetsk_courier(
        taxi_eats_performer_support, get_courier_from_novokuznetsk,
):

    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '3'}},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '23:00',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_vladivostok_courier(
        taxi_eats_performer_support, get_courier_from_vladivostok,
):

    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '4'}},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '23:00',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_new_york_courier(
        taxi_eats_performer_support, get_courier_from_new_york,
):
    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '5'}},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '31.00',
                'available_from': '23:00',
                'code': 'code_5',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_chicago_courier(
        taxi_eats_performer_support, get_courier_from_chicago,
):

    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '6'}},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '23:00',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_phoenix_courier(
        taxi_eats_performer_support, get_courier_from_phoenix,
):
    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '7'}},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '23:00',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3()
async def test_los_angeles_courier(
        taxi_eats_performer_support, get_courier_from_los_angeles,
):

    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers={**DEFAULT_HEADERS, **{'X-YaEda-CourierId': '8'}},
    )

    assert response.json() == {
        'data': {
            'promocode': {
                'amount': '500.00',
                'available_from': '23:00',
                'currency': '₽',
                'ttl': '3600',
                'type': 'after_shift',
            },
        },
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3_without_config.json')
async def test_without_config(
        taxi_eats_performer_support, get_courier_from_msk,
):

    response = await taxi_eats_performer_support.get(
        path='/driver/v1/eats-performer-support/v1/taxi/promocode/info/'
        '?promocode_type=after_shift',
        headers=DEFAULT_HEADERS,
    )

    assert response.json() == {'data': {'promocode': None}}

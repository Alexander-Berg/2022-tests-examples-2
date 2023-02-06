import pytest

from testsuite.utils import matching

from fleet_drivers_scoring.stq import checks
from test_fleet_drivers_scoring.stq import mocks_setup
import test_fleet_drivers_scoring.utils as global_utils

DRIVER_PROFILE_OK = {
    'profiles_by_license': [
        {
            'driver_license': 'licence_pd',
            'profiles': [
                {
                    'data': {
                        'park_id': 'park1',
                        'car_id': 'car1',
                        'uuid': 'driver1',
                    },
                    'revision': '0_1234567_4',
                    'park_driver_profile_id': 'park1_driver1',
                },
                {
                    'data': {
                        'park_id': 'park2',
                        'car_id': 'car2',
                        'uuid': 'driver2',
                    },
                    'revision': '0_1234567_4',
                    'park_driver_profile_id': 'park2_driver2',
                },
            ],
        },
    ],
}

DRIVER_PROFILE_NO_CAR = {
    'profiles_by_license': [
        {
            'driver_license': 'licence_pd',
            'profiles': [
                {
                    'data': {'park_id': 'park1', 'uuid': 'driver1'},
                    'revision': '0_1234567_4',
                    'park_driver_profile_id': 'park1_driver1',
                },
            ],
        },
    ],
}


DRIVER_PROFILE_NOT_IN_PARK = {
    'profiles_by_license': [
        {
            'driver_license': 'licence_pd',
            'profiles': [
                {
                    'data': {
                        'park_id': 'park2',
                        'car_id': 'car2',
                        'uuid': 'driver2',
                    },
                    'revision': '0_1234567_4',
                    'park_driver_profile_id': 'park2_driver2',
                },
            ],
        },
    ],
}


FLEET_VEHICLES_OK_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'brand': 'BMW',
                'cert_verification': True,
                'model': 'X6',
                'number': 'AA001777',
                'number_normalized': 'AA001777',
                'registration_cert': 'XW8ED45J7DK123456',
            },
            'park_id_car_id': 'park1_car1',
        },
    ],
}

FLEET_VEHICLES_NO_CERT_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'brand': 'BMW',
                'cert_verification': True,
                'model': 'X6',
                'number': 'AA001777',
                'number_normalized': 'AA001777',
            },
            'park_id_car_id': 'park1_car1',
        },
    ],
}

FLEET_VEHICLES_CERT_NOT_VERIFIED_RESPONSE = {
    'vehicles': [
        {
            'data': {
                'brand': 'BMW',
                'cert_verification': False,
                'model': 'X6',
                'number': 'AA001777',
                'number_normalized': 'AA001777',
                'registration_cert': 'XW8ED45J7DK123456',
            },
            'park_id_car_id': 'park1_car1',
        },
    ],
}

DRIVER_ORDERS_EMPTY_RESPONSE = {
    'park1': {'orders': [], 'limit': 1},
    'park2': {'orders': [], 'limit': 1},
}

PARAMS = [
    (
        DRIVER_PROFILE_OK,
        FLEET_VEHICLES_OK_RESPONSE,
        None,
        'car_orders_history_stored.json',
    ),
    (
        DRIVER_PROFILE_NO_CAR,
        FLEET_VEHICLES_OK_RESPONSE,
        None,
        'car_orders_history_no_car.json',
    ),
    (
        DRIVER_PROFILE_NOT_IN_PARK,
        FLEET_VEHICLES_OK_RESPONSE,
        None,
        'car_orders_history_no_driver_in_fleet.json',
    ),
    (
        DRIVER_PROFILE_OK,
        FLEET_VEHICLES_NO_CERT_RESPONSE,
        None,
        'car_orders_history_cert_not_verified.json',
    ),
    (
        DRIVER_PROFILE_OK,
        FLEET_VEHICLES_CERT_NOT_VERIFIED_RESPONSE,
        None,
        'car_orders_history_cert_not_verified.json',
    ),
    (
        DRIVER_PROFILE_OK,
        FLEET_VEHICLES_OK_RESPONSE,
        DRIVER_ORDERS_EMPTY_RESPONSE,
        'car_orders_history_empty.json',
    ),
]


@pytest.mark.now('2020-01-01T03:00:00+03:00')
@pytest.mark.pgsql('fleet_drivers_scoring', files=['state.sql'])
@pytest.mark.parametrize(
    'driver_profiles_response, '
    'fleet_vehicles_response, '
    'driver_orders_response, expected_response_json',
    PARAMS,
)
async def test_car_orders_history(
        stq3_context,
        pgsql,
        _mock_driver_profiles,
        _mock_unique_drivers,
        _mock_fleet_parks,
        _mock_billing_replication,
        _mock_parks_replica,
        _mock_tariffs,
        _mock_agglomerations,
        _mock_billing_orders,
        _mock_territories,
        _mock_parks_activation,
        _mock_fleet_payouts,
        _mock_fleet_vehicles,
        _mock_driver_orders,
        load_json,
        driver_profiles_response,
        fleet_vehicles_response,
        driver_orders_response,
        expected_response_json,
):
    mocks_setup.setup_mocks(
        _mock_driver_profiles,
        _mock_unique_drivers,
        _mock_fleet_parks,
        _mock_billing_replication,
        _mock_parks_replica,
        _mock_tariffs,
        _mock_agglomerations,
        _mock_billing_orders,
        _mock_territories,
        _mock_parks_activation,
        _mock_fleet_payouts,
        _mock_fleet_vehicles,
        _mock_driver_orders,
        driver_profiles_response=driver_profiles_response,
        fleet_vehicles_response=fleet_vehicles_response,
        driver_orders_response=driver_orders_response,
    )

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='req_1',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    assert all_checks == [
        {
            'check_id': 'req_1',
            'idempotency_token': 'req_1',
            'license_pd_id': 'license_pd_id',
            'park_id': 'park1',
            'status': 'done',
            'status_meta_info': None,
            'ratings_history_id': None,
            'is_ratings_history_calculated': True,
            'orders_statistics_id': None,
            'is_orders_statistics_calculated': True,
            'quality_metrics_id': None,
            'is_quality_metrics_calculated': True,
            'high_speed_driving_id': None,
            'is_high_speed_driving_calculated': True,
            'passenger_tags_id': None,
            'is_passenger_tags_calculated': True,
            'car_orders_history_id': matching.uuid_string,
            'is_car_orders_history_calculated': True,
            'driving_style_id': None,
            'is_driving_style_calculated': True,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': 100500,
            'discount_type': 'basic_price',
        },
    ]

    car_orders_history = global_utils.fetch_check_part(
        pgsql, all_checks[0]['car_orders_history_id'],
    )
    car_orders_history.pop('created_at')
    assert (
        car_orders_history.pop('id') == all_checks[0]['car_orders_history_id']
    )
    assert global_utils.date_parsed(
        car_orders_history,
    ) == global_utils.date_parsed(load_json(expected_response_json))

import pytest

from fleet_drivers_scoring.stq import checks
from test_fleet_drivers_scoring.stq import mocks_setup
import test_fleet_drivers_scoring.utils as global_utils


def _get_mock_query(mock_call):
    return {k: v for k, v in mock_call['request'].query.items()}


PARKS_ACTIVATION_RESPONSE_NO_CASH = {
    'parks_activation': [
        {
            'revision': 221206,
            'last_modified': '2019-11-21T12:12:29.602',
            'park_id': '100500',
            'city_id': 'Москва',
            'data': {
                'deactivated': False,
                'can_cash': False,
                'can_card': True,
                'can_corp': True,
                'can_coupon': True,
            },
        },
    ],
}


@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_parts_ready.sql'])
async def test_billing_payment(
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
        mock_yt,
        load_json,
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
    assert all_checks[0]['status'] == 'done'

    assert _mock_parks_replica.parks_replica.times_called == 1
    assert _get_mock_query(_mock_parks_replica.parks_replica.next_call()) == {
        'consumer': 'fleet-drivers-scoring',
        'park_id': 'clid1',
    }

    assert _mock_billing_replication.billing_replication.times_called == 1
    assert _get_mock_query(
        _mock_billing_replication.billing_replication.next_call(),
    ) == {'client_id': 'bill_clid', 'type': 'GENERAL'}

    assert _mock_tariffs.tariffs.times_called == 1
    assert _get_mock_query(_mock_tariffs.tariffs.next_call()) == {
        'city_ids': 'city1',
        'locale': 'ru',
    }

    assert _mock_agglomerations.agglomerations.times_called == 1
    assert _get_mock_query(
        _mock_agglomerations.agglomerations.next_call(),
    ) == {'tariff_zone': 'spb'}

    assert _mock_billing_orders.billing_orders.times_called == 1
    billing_orders = _mock_billing_orders.billing_orders.next_call()[
        'request'
    ].json
    assert (
        billing_orders['orders'][0]['data']['payments'][0].pop('invoice_date')
        is not None
    )
    assert (
        billing_orders['orders'][0]['data'].pop('topic_begin_at') is not None
    )
    assert billing_orders['orders'][0].pop('event_at') is not None
    assert billing_orders == {
        'orders': [
            {
                'data': {
                    'event_version': 1,
                    'payments': [
                        {
                            'amount': '100',
                            'billing_client_id': 'bill_clid',
                            'contract_id': '1234',
                            'currency': 'RUB',
                            'payload': {
                                'agglomeration': 'ASKc',
                                'alias_id': 'park1_req_1',
                                'amount_details': {
                                    'base_amount': '100',
                                    'base_currency': 'RUB',
                                    'contract_currency_rate': '1.00000',
                                    'vat': '0.0000',
                                },
                                'driver_details': {
                                    'clid': 'clid1',
                                    'db_id': 'park1',
                                },
                                'nearest_zone': 'spb',
                            },
                            'payment_kind': 'partner_scoring',
                        },
                    ],
                    'schema_version': 'v1',
                },
                'external_ref': '1',
                'kind': 'partner_scoring',
                'topic': 'taxi/partner_scoring/park1/park1_req_1',
            },
        ],
    }


@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_parts_ready.sql'])
@pytest.mark.config(FLEET_DRIVERS_SCORING_TAKE_MONEY_ENABLED=False)
async def test_take_money_dissabled(
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
        mock_yt,
        load_json,
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
    assert all_checks[0]['status'] == 'done'
    assert _mock_billing_orders.billing_orders.times_called == 0


FLEET_PARKS_RESPONSE_1 = [
    {
        'parks': [
            {
                'id': 'park1',
                'login': 'login1',
                'name': 'super_park1',
                'is_active': True,
                'city_id': 'city1',
                'locale': 'locale1',
                'is_billing_enabled': False,
                'is_franchising_enabled': False,
                'demo_mode': False,
                'country_id': 'rus',
                'provider_config': {'clid': 'clid1', 'type': 'production'},
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            },
        ],
    },
]

FLEET_PARKS_RESPONSE_2 = [
    {
        'parks': [
            {
                'id': 'park1',
                'login': 'login1',
                'name': 'super_park1',
                'is_active': True,
                'city_id': 'city1',
                'locale': 'locale1',
                'is_billing_enabled': False,
                'is_franchising_enabled': False,
                'demo_mode': False,
                'country_id': 'rus',
                'provider_config': {'clid': 'clid2', 'type': 'production'},
                'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
            },
        ],
    },
]


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_PRICES_2={
        'countries': {
            'rus': {
                'main_amount': '200',
                'simple_version_amount': '20',
                'basic_version_amount': '2',
                'currency': 'RUB',
            },
        },
        'clids': {
            'clid1': {
                'main_amount': '100',
                'simple_version_amount': '10',
                'basic_version_amount': '1',
                'currency': 'RUB',
            },
        },
    },
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_parts_ready.sql'])
@pytest.mark.parametrize(
    'fleet_parks_response, fleet_version_response, expected_price',
    [
        (FLEET_PARKS_RESPONSE_1, {'fleet_version': 'simple'}, '10'),
        (FLEET_PARKS_RESPONSE_1, {'fleet_version': 'basic'}, '1'),
        (FLEET_PARKS_RESPONSE_2, {'fleet_version': 'simple'}, '20'),
        (FLEET_PARKS_RESPONSE_2, {'fleet_version': 'basic'}, '2'),
    ],
)
async def test_prices_config(
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
        mock_yt,
        load_json,
        taxi_config,
        fleet_parks_response,
        fleet_version_response,
        expected_price,
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
        fleet_parks_response=fleet_parks_response,
        fleet_payouts_response=fleet_version_response,
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
    assert all_checks[0]['status'] == 'done'
    assert _mock_billing_orders.billing_orders.times_called == 1
    billing_orders = _mock_billing_orders.billing_orders.next_call()[
        'request'
    ].json

    assert (
        billing_orders['orders'][0]['data']['payments'][0]['payload'][
            'amount_details'
        ]['base_amount']
        == expected_price
    )
    assert (
        billing_orders['orders'][0]['data']['payments'][0]['amount']
        == expected_price
    )


@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_parts_ready.sql'])
async def test_not_enough_money(
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
        mock_yt,
        load_json,
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
        parks_activation_response=PARKS_ACTIVATION_RESPONSE_NO_CASH,
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
            'status': 'failed',
            'status_meta_info': {'reason': 'not_enough_money'},
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
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': True,
            'driving_style_id': None,
            'is_driving_style_calculated': True,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': None,
            'discount_type': None,
        },
    ]

    assert _mock_parks_activation.parks_activation.times_called == 1
    parks_activation_request = (
        _mock_parks_activation.parks_activation.next_call()['request'].json
    )
    assert parks_activation_request == {'ids_in_set': ['clid1']}

    assert _mock_billing_orders.billing_orders.times_called == 0


@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_parts_ready.sql'])
async def test_nearestzone_ok(
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
        _mock_protocol,
        mock_yt,
        load_json,
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
        tariffs_response={'zones': []},
    )

    _mock_fleet_parks.set_cities_retrieve_response(
        {
            'cities_by_name': [
                {
                    'cities': [{'id': 'some', 'data': {'lat': 20, 'lon': 10}}],
                    'name': 'some_city',
                },
            ],
        },
    )

    _mock_protocol.set_nearestzone_response({'nearest_zone': 'ekb'})

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='req_1',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    assert all_checks[0]['status'] == 'done'
    assert _mock_fleet_parks.cities_retrieve.times_called == 1
    assert _mock_protocol.nearestzone.times_called == 1
    nearestzone_request = _mock_protocol.nearestzone.next_call()[
        'request'
    ].json

    assert nearestzone_request == {'point': [10, 20]}

    assert _mock_billing_orders.billing_orders.times_called == 1
    billing_orders = _mock_billing_orders.billing_orders.next_call()[
        'request'
    ].json

    assert (
        billing_orders['orders'][0]['data']['payments'][0]['payload'][
            'nearest_zone'
        ]
        == 'ekb'
    )


@pytest.mark.pgsql('fleet_drivers_scoring', files=['check_parts_ready.sql'])
@pytest.mark.parametrize(
    'cities_response, nearestzone_response, nearestzone_times_called',
    [
        (
            {
                'cities_by_name': [
                    {
                        'cities': [
                            {'id': 'some', 'data': {'lat': 20, 'lon': 10}},
                        ],
                        'name': 'some_city',
                    },
                ],
            },
            {
                'response': {'error': {'code': 404, 'message': 'msg'}},
                'status_code': 404,
            },
            1,
        ),
        (
            {'cities_by_name': []},
            {'response': {'nearest_zone': 'ekb'}, 'status_code': 200},
            0,
        ),
        (
            {
                'cities_by_name': [
                    {
                        'cities': [{'id': 'some', 'data': {}}],
                        'name': 'some_city',
                    },
                ],
            },
            {'response': {'nearest_zone': 'ekb'}, 'status_code': 200},
            0,
        ),
    ],
)
async def test_nearestzone_failed(
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
        _mock_protocol,
        mock_yt,
        load_json,
        cities_response,
        nearestzone_response,
        nearestzone_times_called,
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
        tariffs_response={'zones': []},
    )

    _mock_fleet_parks.set_cities_retrieve_response(cities_response)
    _mock_protocol.set_nearestzone_response(**nearestzone_response)

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='req_1',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    assert all_checks[0]['status'] == 'internal_error'
    assert _mock_protocol.nearestzone.times_called == nearestzone_times_called

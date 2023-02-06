import json

import dateutil.parser
import pytest

from testsuite.utils import matching

from fleet_drivers_scoring.stq import checks
from test_fleet_drivers_scoring.stq import mocks_setup
import test_fleet_drivers_scoring.utils as global_utils


# config that matches tariff_name -> tariff_name.
# matching to tariff_group will be tested separately

FLEET_DRIVERS_SCORING_TARIFF_GROUPS = {
    'FLEET_DRIVERS_SCORING_TARIFF_GROUPS': {
        'tariff_groups': [
            {'group_name': 'uberx', 'order_tariffs': ['uberx']},
            {'group_name': 'child_tariff', 'order_tariffs': ['child_tariff']},
            {'group_name': 'econom', 'order_tariffs': ['econom']},
        ],
    },
}


@pytest.mark.config(**FLEET_DRIVERS_SCORING_TARIFF_GROUPS)
@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['ratings_history_yt_updates.sql'],
)
async def test_ok(
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
        _mock_fleet_vehicles,
        _mock_driver_orders,
    )

    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/ratings/2020-05-04',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='ratings_history_ok.json',
    )

    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/orders/2020-05-05',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='orders_statistics_ok.json',
    )

    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/quality/2020-05-06',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='quality_metrics_ok.json',
    )

    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/'
        'high_speed_driving/2020-05-06',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='high_speed_driving_ok.json',
    )

    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/'
        'passenger_tags/2020-05-06',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='passenger_tags_ok.json',
    )

    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/'
        'driving_style/2020-05-06',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='driving_style_ok.json',
    )

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='100000000',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    assert all_checks == [
        {
            'check_id': matching.any_string,
            'idempotency_token': '100000000',
            'license_pd_id': 'extra_super_driver_license1_pd',
            'park_id': 'park1',
            'status': 'done',
            'status_meta_info': None,
            'ratings_history_id': matching.uuid_string,
            'is_ratings_history_calculated': True,
            'orders_statistics_id': matching.uuid_string,
            'is_orders_statistics_calculated': True,
            'quality_metrics_id': matching.uuid_string,
            'is_quality_metrics_calculated': True,
            'high_speed_driving_id': matching.uuid_string,
            'is_high_speed_driving_calculated': True,
            'driving_style_id': matching.uuid_string,
            'is_driving_style_calculated': True,
            'passenger_tags_id': matching.uuid_string,
            'is_passenger_tags_calculated': True,
            'car_orders_history_id': matching.uuid_string,
            'is_car_orders_history_calculated': True,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': 100500,
            'discount_type': 'basic_price',
        },
    ]

    ratings_history = global_utils.fetch_check_part(
        pgsql, all_checks[0]['ratings_history_id'],
    )
    ratings_history.pop('created_at')
    assert ratings_history.pop('id') == all_checks[0]['ratings_history_id']
    assert (
        global_utils.date_parsed(ratings_history)
        == global_utils.date_parsed(
            load_json('ratings_history_ok_pg_stored.json'),
        )
    )

    orders_statistics = global_utils.fetch_check_part(
        pgsql, all_checks[0]['orders_statistics_id'],
    )
    orders_statistics.pop('created_at')
    assert orders_statistics.pop('id') == all_checks[0]['orders_statistics_id']
    assert (
        global_utils.date_parsed(orders_statistics)
        == global_utils.date_parsed(
            load_json('orders_statistics_ok_pg_stored.json'),
        )
    )

    quality_metrics = global_utils.fetch_check_part(
        pgsql, all_checks[0]['quality_metrics_id'],
    )
    quality_metrics.pop('created_at')
    assert quality_metrics.pop('id') == all_checks[0]['quality_metrics_id']
    assert (
        global_utils.date_parsed(quality_metrics)
        == global_utils.date_parsed(
            load_json('quality_metrics_ok_pg_stored.json'),
        )
    )
    assert _mock_driver_profiles.retrieve_by_license.times_called == 1
    retrieve_by_license_request = (
        _mock_driver_profiles.retrieve_by_license.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(retrieve_by_license_request) == {
        'driver_license_in_set': ['extra_super_driver_license1_pd'],
    }

    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1
    retrieve_by_profiles_request = (
        _mock_unique_drivers.retrieve_by_profiles.next_call()[
            'request'
        ].get_data()
    )
    assert json.loads(retrieve_by_profiles_request) == {
        'profile_id_in_set': ['park1_driver1', 'park2_driver2'],
    }


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['ratings_history_yt_updates.sql'],
)
@pytest.mark.parametrize(
    'driver_profiles_response, unique_drivers_response',
    [
        (
            {
                'profiles_by_license': [
                    {'driver_license': 'licence_pd', 'profiles': []},
                ],
            },
            None,
        ),
        (
            {'profiles_by_license': [mocks_setup.DRIVER_PROFILE1]},
            {
                'uniques': [
                    {'park_driver_profile_id': 'park1_driver1'},
                    {'park_driver_profile_id': 'park2_driver2'},
                ],
            },
        ),
    ],
)
async def test_no_unique_driver(
        stq3_context,
        pgsql,
        _mock_driver_profiles,
        _mock_unique_drivers,
        driver_profiles_response,
        unique_drivers_response,
        _mock_fleet_parks,
        _mock_billing_replication,
        _mock_parks_replica,
        _mock_tariffs,
        _mock_agglomerations,
        _mock_billing_orders,
        _mock_territories,
        _mock_parks_activation,
        _mock_fleet_payouts,
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
        driver_profiles_response=driver_profiles_response,
        unique_drivers_response=unique_drivers_response,
    )

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='100000000',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    assert _mock_driver_profiles.retrieve_by_license.times_called == 1
    if unique_drivers_response:
        assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1
    else:
        assert _mock_unique_drivers.retrieve_by_profiles.times_called == 0

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    all_checks[0].pop('check_id')
    assert all_checks == [
        {
            'idempotency_token': '100000000',
            'license_pd_id': 'extra_super_driver_license1_pd',
            'park_id': 'park1',
            'status': 'done',
            'status_meta_info': None,
            'is_ratings_history_calculated': True,
            'ratings_history_id': None,
            'is_orders_statistics_calculated': True,
            'orders_statistics_id': None,
            'is_quality_metrics_calculated': True,
            'quality_metrics_id': None,
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
            'billing_doc_id': 100500,
            'discount_type': 'basic_price',
        },
    ]


@pytest.mark.config(**FLEET_DRIVERS_SCORING_TARIFF_GROUPS)
@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['ratings_history_yt_updates.sql'],
)
@pytest.mark.parametrize(
    'db_state, is_new_ratings_history, is_new_orders_statistics, '
    'is_new_quality_metrics',
    [
        ('state1.sql', True, True, True),
        ('state2.sql', False, True, True),
        ('state3.sql', False, True, True),
        ('state4.sql', False, False, True),
        ('state5.sql', False, False, True),
        ('state6.sql', False, False, False),
        ('state7.sql', False, False, False),
    ],
)
async def test_retry_ok(
        stq3_context,
        pgsql,
        load,
        load_json,
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
        db_state,
        is_new_ratings_history,
        is_new_orders_statistics,
        is_new_quality_metrics,
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
    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/ratings/2020-05-04',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='ratings_history_ok_one_rating_entry.json',
    )
    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/orders/2020-05-05',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='orders_statistics_ok_small.json',
    )
    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/quality/2020-05-06',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename='quality_metrics_ok.json',
    )
    global_utils.execute_file(pgsql, load, db_state)

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='req_1',
        license_pd_id='license_pd_id',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    all_checks[0].pop('check_id')

    ratings_history_id = all_checks[0].pop('ratings_history_id')
    orders_statistics_id = all_checks[0].pop('orders_statistics_id')
    quality_metrics_id = all_checks[0].pop('quality_metrics_id')

    if not is_new_ratings_history:
        assert ratings_history_id == 'id1'
    if not is_new_orders_statistics:
        assert orders_statistics_id == 'id2'
    if not is_new_quality_metrics:
        assert quality_metrics_id == 'id3'
    assert all_checks == [
        {
            'idempotency_token': 'req_1',
            'license_pd_id': 'license_pd_id',
            'park_id': 'park1',
            'status': 'done',
            'status_meta_info': None,
            'is_ratings_history_calculated': True,
            'is_orders_statistics_calculated': True,
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
            'billing_doc_id': 100500,
            'discount_type': 'basic_price',
        },
    ]

    ratings_history = global_utils.fetch_check_part(pgsql, ratings_history_id)
    ratings_history_created_at = ratings_history.pop('created_at')
    if not is_new_ratings_history:
        assert ratings_history_created_at == dateutil.parser.isoparse(
            '2020-04-20T00:00:00+00:00',
        )
    assert ratings_history.pop('id') == ratings_history_id
    assert (
        global_utils.date_parsed(ratings_history)
        == global_utils.date_parsed(
            load_json('ratings_history_ok_pg_one_rating_entry.json'),
        )
    )

    orders_statistics = global_utils.fetch_check_part(
        pgsql, orders_statistics_id,
    )
    orders_statistics_created_at = orders_statistics.pop('created_at')
    if not is_new_orders_statistics:
        assert orders_statistics_created_at == dateutil.parser.isoparse(
            '2020-04-20T00:00:00+00:00',
        )
    assert orders_statistics.pop('id') == orders_statistics_id
    assert (
        global_utils.date_parsed(orders_statistics)
        == global_utils.date_parsed(
            load_json('orders_statistics_ok_small_pg_stored.json'),
        )
    )

    quality_metrics = global_utils.fetch_check_part(pgsql, quality_metrics_id)
    quality_metrics_created_at = quality_metrics.pop('created_at')
    if not is_new_quality_metrics:
        assert quality_metrics_created_at == dateutil.parser.isoparse(
            '2020-04-20T00:00:00+00:00',
        )
    assert quality_metrics.pop('id') == quality_metrics_id
    assert (
        global_utils.date_parsed(quality_metrics)
        == global_utils.date_parsed(
            load_json('quality_metrics_ok_pg_stored.json'),
        )
    )
    assert _mock_driver_profiles.retrieve_by_license.times_called == 1
    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 1


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['ratings_history_yt_updates.sql'],
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['done_check.sql'])
async def test_retry_done(
        stq3_context,
        pgsql,
        load,
        load_json,
        _mock_driver_profiles,
        _mock_unique_drivers,
):
    updated_at_before = global_utils.fetch_all_checks(pgsql)[0]['updated_at']
    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='req_1',
        license_pd_id='license_pd_id',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')

    assert all_checks == [
        {
            'park_id': 'park1',
            'check_id': 'req_1',
            'idempotency_token': 'req_1',
            'license_pd_id': 'license_pd_id',
            'status': 'done',
            'status_meta_info': None,
            'ratings_history_id': 'id1',
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
            'updated_at': updated_at_before,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': None,
            'discount_type': None,
        },
    ]

    assert _mock_driver_profiles.retrieve_by_license.times_called == 0
    assert _mock_unique_drivers.retrieve_by_profiles.times_called == 0


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_retry_failed.sql'])
async def test_retry_failed(stq3_context, pgsql):
    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='100000000',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    for check in all_checks:
        check.pop('created_at')
        check.pop('updated_at')
        check.pop('check_id')
    assert all_checks == [
        {
            'idempotency_token': '100000000',
            'license_pd_id': 'license_pd_id',
            'park_id': 'park1',
            'status': 'internal_error',
            'status_meta_info': None,
            'ratings_history_id': None,
            'is_ratings_history_calculated': False,
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


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['ratings_history_yt_updates.sql'],
)
@pytest.mark.parametrize('yt_ratings', ['bad1.json', 'bad2.json', 'bad3.json'])
async def test_bad_ratings_history_data(
        stq3_context,
        pgsql,
        _mock_driver_profiles,
        _mock_unique_drivers,
        mock_yt,
        load_json,
        yt_ratings,
):
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [mocks_setup.DRIVER_PROFILE1]},
    )
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        mocks_setup.UNIQUE_DRIVERS_RESPONSE_OK,
    )
    mock_yt.add_lookup_rows_response(
        table='//home/opteum/fm/testing/features/scoring/ratings/2020-05-04',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename=yt_ratings,
    )

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='100000000',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    all_checks[0].pop('check_id')
    assert all_checks == [
        {
            'idempotency_token': '100000000',
            'license_pd_id': 'extra_super_driver_license1_pd',
            'park_id': 'park1',
            'status': 'internal_error',
            'status_meta_info': None,
            'ratings_history_id': None,
            'is_ratings_history_calculated': False,
            'orders_statistics_id': None,
            'is_orders_statistics_calculated': False,
            'quality_metrics_id': None,
            'is_quality_metrics_calculated': False,
            'high_speed_driving_id': None,
            'is_high_speed_driving_calculated': False,
            'passenger_tags_id': None,
            'is_passenger_tags_calculated': False,
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': False,
            'driving_style_id': None,
            'is_driving_style_calculated': False,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': None,
            'discount_type': None,
        },
    ]


async def test_no_ratings_history_yt_table(
        stq3_context, pgsql, _mock_driver_profiles, _mock_unique_drivers,
):
    _mock_driver_profiles.set_retrieve_by_license_resp(
        {'profiles_by_license': [mocks_setup.DRIVER_PROFILE1]},
    )
    _mock_unique_drivers.set_retrieve_by_profiles_resp(
        mocks_setup.UNIQUE_DRIVERS_RESPONSE_OK,
    )

    await checks.task(
        stq3_context,
        park_id='park1',
        idempotency_token='100000000',
        license_pd_id='extra_super_driver_license1_pd',
        log_extra={},
    )

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    all_checks[0].pop('check_id')
    assert all_checks == [
        {
            'idempotency_token': '100000000',
            'license_pd_id': 'extra_super_driver_license1_pd',
            'park_id': 'park1',
            'status': 'internal_error',
            'status_meta_info': None,
            'ratings_history_id': None,
            'is_ratings_history_calculated': False,
            'orders_statistics_id': None,
            'is_orders_statistics_calculated': False,
            'quality_metrics_id': None,
            'is_quality_metrics_calculated': False,
            'high_speed_driving_id': None,
            'is_high_speed_driving_calculated': False,
            'passenger_tags_id': None,
            'is_passenger_tags_calculated': False,
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': False,
            'driving_style_id': None,
            'is_driving_style_calculated': False,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': None,
            'discount_type': None,
        },
    ]


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['test_new_part_type_while_pending.sql'],
)
async def test_new_part_type_while_pending(
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
        license_pd_id='license_pd_id',
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
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': True,
            'driving_style_id': None,
            'is_driving_style_calculated': True,
            'offer': None,
            'requested_by': None,
            'billing_doc_id': 100500,
            'discount_type': 'basic_price',
        },
    ]

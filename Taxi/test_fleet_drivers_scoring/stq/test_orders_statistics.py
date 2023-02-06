import typing

import pytest

from testsuite.utils import matching

from fleet_drivers_scoring.generated.service.swagger import models
from fleet_drivers_scoring.stq import checks
from fleet_drivers_scoring.stq import orders_statistics
from test_fleet_drivers_scoring.stq import mocks_setup
import test_fleet_drivers_scoring.utils as global_utils

FLEET_DRIVERS_SCORING_TARIFF_GROUPS = {
    'tariff_groups': [
        {'group_name': 'child', 'order_tariffs': ['child_tariff', 'uberkids']},
        {'group_name': 'comfort', 'order_tariffs': ['business', 'uberselect']},
        {'group_name': 'courier', 'order_tariffs': ['courier']},
        {
            'group_name': 'econom',
            'order_tariffs': ['econom', 'uberx', 'express'],
        },
        {'group_name': 'lab', 'order_tariffs': ['premium_suv']},
        {'group_name': 'other', 'order_tariffs': ['mkk_antifraud']},
    ],
}


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_TARIFF_GROUPS=FLEET_DRIVERS_SCORING_TARIFF_GROUPS,
)
@pytest.mark.pgsql('fleet_drivers_scoring', files=['state.sql'])
@pytest.mark.parametrize('in_yt, out_pg', [('yt_ok.json', 'pg_ok.json')])
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
        mock_yt,
        load_json,
        in_yt,
        out_pg,
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
        table='//home/opteum/fm/testing/features/scoring/'
        'orders_statistics/2020-05-06',
        source_data=[{'unique_driver_id': 'udid1'}],
        filename=in_yt,
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
            'orders_statistics_id': matching.uuid_string,
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

    pg_stored = global_utils.fetch_check_part(
        pgsql, all_checks[0]['orders_statistics_id'],
    )
    pg_stored.pop('created_at')
    assert pg_stored.pop('id') == all_checks[0]['orders_statistics_id']
    assert global_utils.date_parsed(pg_stored) == global_utils.date_parsed(
        load_json(out_pg),
    )


def load_input(
        serialized: typing.List[dict],
) -> typing.List[models.api.OrdersStatisticsItem]:
    return [
        models.api.OrdersStatisticsItem.deserialize(item)
        for item in serialized
    ]


def save_result(
        result: typing.List[models.api.OrdersStatisticsItem],
) -> typing.List[dict]:
    return [x.serialize() for x in result]


@pytest.mark.parametrize(
    'yt_orders, expected',
    [
        ('other_in_config_input.json', 'other_in_config_output.json'),
        ('other_left_input.json', 'other_left_output.json'),
        (
            'other_left_and_in_config_input.json',
            'other_left_and_in_config_output.json',
        ),
        ('two_month_1_input.json', 'two_month_1_output.json'),
        ('no_in_config_input.json', 'no_in_config_output.json'),
    ],
)
def test_top_calculation(load_json, yt_orders, expected):
    config = orders_statistics.make_map_tariff_to_group(
        FLEET_DRIVERS_SCORING_TARIFF_GROUPS,
    )
    yt_orders_loaded = load_input(load_json(yt_orders))
    result = orders_statistics.group_statistics(yt_orders_loaded, config)
    assert global_utils.date_parsed(
        save_result(result),
    ) == global_utils.date_parsed(load_json(expected))

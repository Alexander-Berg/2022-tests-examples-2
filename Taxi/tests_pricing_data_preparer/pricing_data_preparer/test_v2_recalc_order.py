# pylint: disable=redefined-outer-name, import-only-modules, import-error
# flake8: noqa F401
import copy

import pytest
import bson

import dateutil.parser

from testsuite import utils

from pricing_extended.mocking_base import check_not_called

from .plugins import test_utils
from .plugins import utils_request
from .plugins.mock_order_core import mock_order_core
from .plugins.mock_order_core import OrderIdRequestType
from .plugins.mock_order_core import order_core
from .round_values import round_values


@pytest.mark.parametrize(
    'order_id, code, expected',
    [
        ('not_found_order', 404, None),
        ('no_pricing_data', 404, None),
        (
            'fix_price_order',
            200,
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 70,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (
            'no_fix_price_order',
            200,
            {
                'total_distance': 0,
                'total_time': 0,
                'waiting_time': 143,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (
            'order_with_paid_supply',
            200,
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 120,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
                'paid_supply_price': 150,
            },
        ),
        (
            'order_with_incorrect_paid_supply',
            200,
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 120,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (
            'order_by_transfer',
            200,
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 253,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (
            'order_with_paid_supply_without_performer',
            200,
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 120,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
                'paid_supply_price': 150,
            },
        ),
        (
            'cargo_broken_order',
            200,
            {
                'total_distance': 0,
                'total_time': 0,
                'waiting_time': 143,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
    ],
    ids=[
        'not_found_order',
        'no_pricing_data',
        'fix_price_order',
        'no_fix_price_order',
        'order_with_paid_supply',
        'order_with_incorrect_paid_supply',
        'order_by_transfer',
        'order_with_paid_supply_without_performer',
        'cargo_broken_order',
    ],
)
@pytest.mark.parametrize(
    'overrides',
    [
        None,
        {
            'trip_details': {
                'total_distance': 5000,
                'total_time': 600,
                'waiting_time': 300,
                'waiting_in_transit_time': 450,
                'waiting_in_destination_time': 600,
                'user_options': {},
            },
        },
    ],
    ids=['no_overrides', 'override_trip_details'],
)
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.now('2020-11-10T17:25:00Z')
async def test_v2_recalc_order(
        taxi_pricing_data_preparer,
        order_id,
        code,
        expected,
        overrides,
        order_core,
        mock_order_core,
):
    response = await taxi_pricing_data_preparer.post(
        'v2/recalc_order',
        params={'order_id': order_id},
        json={'overrides': overrides} if overrides else {},
    )
    assert response.status_code == code

    if code == 200:
        data = response.json()
        assert data['price']['user']['meta'] == data['price']['driver']['meta']
        meta = data['price']['user']['meta']
        if not overrides:
            assert meta == expected
        else:
            override_expected = copy.deepcopy(overrides['trip_details'])
            override_expected.pop('user_options')
            if order_id in (
                    'order_with_paid_supply',
                    'order_with_paid_supply_without_performer',
            ):
                override_expected['paid_supply_price'] = 150
            assert meta == override_expected


@pytest.mark.parametrize(
    'order_id, now, expected',
    [
        (  # 'now_before_than_due_and_waiting'
            'order_with_due_later_than_waiting',
            '2020-11-10T17:37:00Z',
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 0,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (  # 'now_between_due_and_waiting'
            'order_with_due_later_than_waiting',
            '2020-11-10T17:39:00Z',
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 0,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (  # 'now_between_waiting_and_due'
            'order_with_due_before_than_waiting',
            '2020-11-10T17:39:00Z',
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 0,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (  # 'due_later_than_waiting'
            'order_with_due_later_than_waiting',
            '2020-11-10T17:45:00Z',
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 120,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (  # 'due_before_than_waiting'
            'order_with_due_before_than_waiting',
            '2020-11-10T17:45:00Z',
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 120,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (  # 'waiting_time_from_wating_till_transporting'
            'order_with_due_later_than_waiting',
            '2020-11-10T18:00:00Z',
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 240,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
        (  # 'waiting_time_from_due_till_transporting'
            'order_with_due_before_than_waiting',
            '2020-11-10T18:00:00Z',
            {
                'total_distance': 4900,
                'total_time': 540,
                'waiting_time': 240,
                'waiting_in_transit_time': 0,
                'waiting_in_destination_time': 0,
            },
        ),
    ],
    ids=[
        'now_before_than_due_and_waiting',
        'now_between_due_and_waiting',
        'now_between_waiting_and_due',
        'due_later_than_waiting',
        'due_before_than_waiting',
        'waiting_time_from_wating_till_transporting',
        'waiting_time_from_due_till_transporting',
    ],
)
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.now()
async def test_v2_recalc_order_check_waiting_time(
        taxi_pricing_data_preparer,
        mocked_time,
        order_id,
        expected,
        now,
        order_core,
        mock_order_core,
):
    mocked_time.set(utils.to_utc(dateutil.parser.parse(now)))
    await taxi_pricing_data_preparer.invalidate_caches()

    response = await taxi_pricing_data_preparer.post(
        'v2/recalc_order', params={'order_id': order_id}, json={},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['price']['user']['meta'] == data['price']['driver']['meta']
    assert data['price']['user']['meta'] == expected


@pytest.mark.parametrize('order_proc_source', ['mongo', 'order-core'])
@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.now('2020-11-10T17:25:00Z')
async def test_v2_recalc_order_read_from_order_core(
        taxi_pricing_data_preparer,
        mockserver,
        mongodb,
        experiments3,
        order_proc_source,
        order_core,
        mock_order_core,
):
    order_id = 'fix_price_order'

    experiments3.add_config(
        consumers=['pricing-data-preparer/pricing_components'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        name='read_order_proc_from_order_core',
        default_value={
            '__default__': 'mongo',
            'recalc_order': order_proc_source,
        },
    )

    order_core.set_expected_projection(
        {
            'fields': [
                '_id',
                'order.pricing_data',
                'order.performer',
                'order.user_id',
                'order.request.due',
                'order.request.source',
                'order.request.destinations',
                'candidates.driver_id',
                'candidates.udid',
                'candidates.tags',
                'order_info.statistics.status_updates.c',
                'order_info.statistics.status_updates.t',
                'order.fixed_price',
            ],
        },
    )
    order_core.set_expected_key(
        order_id, OrderIdRequestType.exact_id, require_latest=True,
    )
    response = await taxi_pricing_data_preparer.post(
        'v2/recalc_order', params={'order_id': order_id}, json={},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['price']['user']['meta'] == data['price']['driver']['meta']


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
async def test_v2_recalc_order_rule_with_user_meta(
        taxi_pricing_data_preparer, order_core, mock_order_core,
):
    response = await taxi_pricing_data_preparer.post(
        'v2/recalc_order', params={'order_id': 'fix_price_order'}, json={},
    )
    assert response.status_code == 200

    data = response.json()
    user_meta = data['price']['user']['meta']
    driver_meta = data['price']['driver']['meta']
    assert 'foo' in user_meta and not bool(user_meta['foo'])
    assert 'foo' in driver_meta and bool(driver_meta['foo'])

# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import copy
import datetime

import pytest

from tests_pricing_taximeter.plugins.mock_order_core import mock_order_core
from tests_pricing_taximeter.plugins.mock_order_core import OrderIdRequestType
from tests_pricing_taximeter.plugins.mock_order_core import order_core

USER_FIXED = {
    'rounded_price': 150,
    'base_price': {
        'boarding': 1,
        'time': 1,
        'distance': 1,
        'requirements': 1,
        'waiting': 1,
        'transit_waiting': 1,
        'destination_waiting': 1,
    },
    'trip_details': {
        'boarding': 10,
        'total_time': 10,
        'total_distance': 10,
        'requirements': 10,
        'waiting_time': 10,
        'waiting_in_transit_time': 10,
        'waiting_in_destination_time': 10,
        'user_options': {},
    },
}

USER_TAXIMETER = {
    'rounded_price': 100,
    'base_price': {
        'boarding': 10,
        'time': 10,
        'distance': 10,
        'requirements': 10,
        'waiting': 10,
        'transit_waiting': 10,
        'destination_waiting': 10,
    },
    'trip_details': {
        'boarding': 1,
        'total_time': 3,
        'total_distance': 1,
        'requirements': 1,
        'waiting_time': 1,
        'waiting_in_transit_time': 1,
        'waiting_in_destination_time': 1,
        'user_options': {},
    },
}

DRIVER_TAXIMETER = {
    'rounded_price': 200,
    'base_price': {
        'boarding': 2,
        'time': 2,
        'distance': 2,
        'requirements': 2,
        'waiting': 2,
        'transit_waiting': 2,
        'destination_waiting': 2,
    },
    'trip_details': {
        'boarding': 2,
        'total_time': 2,
        'total_distance': 2,
        'requirements': 2,
        'waiting_time': 2,
        'waiting_in_transit_time': 2,
        'waiting_in_destination_time': 2,
        'user_options': {},
    },
}

DRIVER_FIXED = {
    'rounded_price': 200,
    'base_price': {
        'boarding': 22,
        'time': 22,
        'distance': 22,
        'requirements': 22,
        'waiting': 22,
        'transit_waiting': 22,
        'destination_waiting': 22,
    },
    'trip_details': {
        'boarding': 22,
        'total_time': 22,
        'total_distance': 22,
        'requirements': 22,
        'waiting_time': 22,
        'waiting_in_transit_time': 22,
        'waiting_in_destination_time': 22,
        'user_options': {},
    },
}

REQUEST = {
    'price_calc_version': '100500',
    'order_id': 'alias_id_normal_order',
    'order_state': 'transporting',
    'user': {
        'selected_calc_method': 'fixed',
        'taximeter': USER_TAXIMETER,
        'fixed': USER_FIXED,
    },
    'driver': {
        'selected_calc_method': 'taximeter',
        'taximeter': DRIVER_TAXIMETER,
    },
    'location': {'lat': 60, 'lon': 40},
}

AUTH = {
    'park_id': 'park_id_000',
    'session': 'session_000',
    'uuid': 'driverid000',
}

USER_AGENT = 'Taximeter-DEV 9.21 (2147483647)'

DEFAULT_HEADERS = {
    'X-Driver-Session': AUTH['session'],
    'User-Agent': USER_AGENT,
}


@pytest.mark.now('2020-11-10T17:25:00')
@pytest.mark.parametrize(
    'case',
    [
        'all_off',
        'recalc_not_use_save',
        'save_not_use',
        'off_but_save',
        'skip_prices',
        'change_meta_save',
        'lta_change_save',
    ],
)
async def test_v1_order_recalculate_clutch(
        taxi_pricing_taximeter,
        driver_authorizer,
        case,
        experiments3,
        mocked_time,
        mockserver,
        mongodb,
        mock_order_core,
        order_core,
):
    if case == 'recalc_not_use_save':
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='recalculate_order_price_for_taximeter',
            consumers=['pricing-taximeter/order_recalculate'],
            clauses=[],
            default_value={'enabled': True},
        )
    elif case in ['save_not_use', 'change_meta_save', 'lta_change_save']:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='recalculate_order_price_for_taximeter',
            consumers=['pricing-taximeter/order_recalculate'],
            clauses=[],
            default_value={'enabled': True, 'save_prices': True},
        )
    elif case in ['off_but_save', 'skip_prices']:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='recalculate_order_price_for_taximeter',
            consumers=['pricing-taximeter/order_recalculate'],
            clauses=[],
            default_value={'enabled': False, 'save_prices': True},
        )
    mongodb.order_proc.update_one(
        {'_id': 'normal_order'},
        {'$set': {'order_info.lta': mocked_time.now()}},
    )
    if case == 'skip_prices':
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'}, {'$set': {'order_info.cc': 150}},
        )
    if case == 'change_meta_save':
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order_info.cc': 150,
                    'order.pricing_data.published.fixed.meta.user': {
                        'new_meta': 1,
                    },
                },
            },
        )
    if case == 'lta_change_save':
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order_info.cc': 150,
                    'order_info.lta': mocked_time.now() - datetime.timedelta(
                        hours=5,
                    ),
                },
            },
        )
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/order/recalculate',
        json=REQUEST,
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'user': {'price': 150, 'calc_method': 'fixed'},
        'driver': {'price': 200, 'calc_method': 'taximeter'},
    }
    if 'save' not in case:
        assert order_core.times_called == 1
    else:
        if case != 'skip_prices':
            assert order_core.times_called == 2


EMPTY_REQUEST = {
    'price_calc_version': '100500',
    'order_id': 'alias_id_normal_order',
    'user': {},
    'driver': {},
    'location': {'lat': 60, 'lon': 40},
}

POLLING_DELAY_SETTINGS = {
    '__default__': {'__default__': 30},
    'waiting': {'__default__': 10},
    'waiting_in_transit': {'__default__': 10},
    'waiting_in_destination': {'__default__': 10},
    'transporting': {'__default__': 30, 'fixed': 60, 'taximeter': 30},
}

ADDITIONAL_PRICES_WITH_PAID_SUPPLY = {
    'paid_supply': {
        'meta': {},
        'modifications': {'for_fixed': [2], 'for_taximeter': [2]},
        'price': {'strikeout': 195, 'total': 111.0},
    },
}


@pytest.mark.parametrize(
    'case, order_state, response, exp_enabled',
    [
        (
            'full_four',
            'transporting',
            {
                'driver': {'calc_method': 'fixed', 'price': 3088.0},
                'user': {'calc_method': 'fixed', 'price': 4504.0},
            },
            True,
        ),
        (
            'no_fixed_user',
            'transporting',
            {
                'driver': {'calc_method': 'fixed', 'price': 3088.0},
                'user': {'calc_method': 'taximeter', 'price': 70.0},
            },
            True,
        ),
        (
            'no_fixed_driver',
            'transporting',
            {
                'driver': {'calc_method': 'taximeter', 'price': 14.0},
                'user': {'calc_method': 'taximeter', 'price': 70.0},
            },
            True,
        ),
        (
            'only_tax',
            'transporting',
            {
                'driver': {'calc_method': 'taximeter', 'price': 14.0},
                'user': {'calc_method': 'taximeter', 'price': 70.0},
            },
            True,
        ),
        (
            'only_tax_with_rounding',
            'transporting',
            {
                'driver': {'calc_method': 'taximeter', 'price': 14.0},
                'user': {'calc_method': 'taximeter', 'price': 70.1},
            },
            True,
        ),
        (
            'only_tax',
            'driving',
            {
                'driver': {'calc_method': 'taximeter', 'price': 200.0},
                'user': {'calc_method': 'taximeter', 'price': 100.0},
            },
            True,
        ),
        (
            'disabled_exp',
            'transporting',
            {
                'driver': {'calc_method': 'fixed', 'price': 200.0},
                'user': {'calc_method': 'fixed', 'price': 150.0},
            },
            False,
        ),
        (
            'trip_depended',
            'transporting',
            {
                'driver': {'calc_method': 'fixed', 'price': 30880.0},
                'user': {'calc_method': 'taximeter', 'price': 210.0},
                'meta': {'answer': 14},
            },
            True,
        ),
        (
            'usual_paid_supply',
            'transporting',
            {
                'driver': {'calc_method': 'fixed', 'price': 308800.0},
                'user': {'calc_method': 'fixed', 'price': 450400.0},
            },
            True,
        ),
        (
            'paid_supply_no_performer',
            'transporting',
            {
                'driver': {'calc_method': 'fixed', 'price': 308800.0},
                'user': {'calc_method': 'fixed', 'price': 450400.0},
            },
            True,
        ),
    ],
)
@pytest.mark.config(
    PRICING_POLLING_DELAY_FOR_RECALCULATE=POLLING_DELAY_SETTINGS,
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.experiments3(
    is_config=True,
    consumers=['pricing-data-preparer/pricing_components'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    name='read_order_proc_from_order_core',
    default_value={'__default__': 'order-core'},
)
async def test_v1_order_recalculate(
        taxi_pricing_taximeter,
        driver_authorizer,
        case,
        order_state,
        exp_enabled,
        testpoint,
        experiments3,
        response,
        mongodb,
        mockserver,
        order_core,
        mock_order_core,
):
    order_core.set_expected_key(
        'alias_id_normal_order',
        OrderIdRequestType.alias_id,
        require_latest=False,
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': exp_enabled},
        name='recalculate_order_price_for_taximeter',
        consumers=['pricing-taximeter/order_recalculate'],
        clauses=[],
        default_value={
            'enabled': True,
            'use_recalculated_prices': True,
            'save_prices': True,
        },
    )
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    @testpoint('auction_check')
    def tp_auction_check(data):
        pass

    request = copy.deepcopy(EMPTY_REQUEST)
    request['order_state'] = order_state

    if case in [
            'full_four',
            'disabled_exp',
            'usual_paid_supply',
            'paid_supply_no_performer',
    ]:
        request['user'] = {
            'selected_calc_method': 'fixed',
            'fixed': USER_FIXED,
            'taximeter': USER_TAXIMETER,
        }
        request['driver'] = {
            'selected_calc_method': 'fixed',
            'fixed': DRIVER_FIXED,
            'taximeter': DRIVER_TAXIMETER,
        }
    elif case == 'no_fixed_user':
        request['user'] = {
            'selected_calc_method': 'taximeter',
            'taximeter': USER_TAXIMETER,
        }
        request['driver'] = {
            'selected_calc_method': 'fixed',
            'fixed': DRIVER_FIXED,
            'taximeter': DRIVER_TAXIMETER,
        }
    elif case == 'no_fixed_driver':
        request['user'] = {
            'selected_calc_method': 'taximeter',
            'fixed': USER_FIXED,
            'taximeter': USER_TAXIMETER,
        }
        request['driver'] = {
            'selected_calc_method': 'taximeter',
            'taximeter': DRIVER_TAXIMETER,
        }
    elif case == 'only_tax':
        request['user'] = {
            'selected_calc_method': 'taximeter',
            'taximeter': USER_TAXIMETER,
        }
        request['driver'] = {
            'selected_calc_method': 'taximeter',
            'taximeter': DRIVER_TAXIMETER,
        }
    elif case == 'only_tax_with_rounding':
        request['user'] = {
            'selected_calc_method': 'taximeter',
            'taximeter': copy.deepcopy(USER_TAXIMETER),
        }
        request['user']['taximeter']['base_price']['boarding'] = 10.01
        request['user']['taximeter']['rounded_price'] = 70.01
        request['driver'] = {
            'selected_calc_method': 'taximeter',
            'taximeter': DRIVER_TAXIMETER,
        }
    elif case == 'trip_depended':
        request['user'] = {
            'selected_calc_method': 'taximeter',
            'taximeter': USER_TAXIMETER,
        }
        request['driver'] = {
            'selected_calc_method': 'fixed',
            'fixed': DRIVER_FIXED,
            'taximeter': DRIVER_TAXIMETER,
        }
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order.pricing_data.driver.modifications': {
                        'for_fixed': [95],
                        'for_taximeter': [95],
                    },
                    'order.pricing_data.user.modifications': {
                        'for_taximeter': [95],
                    },
                },
            },
        )
    if case == 'usual_paid_supply':
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order.performer.paid_supply': True,
                    'order.pricing_data.driver.additional_prices': (
                        ADDITIONAL_PRICES_WITH_PAID_SUPPLY
                    ),
                    'order.pricing_data.user.additional_prices': (
                        ADDITIONAL_PRICES_WITH_PAID_SUPPLY
                    ),
                },
            },
        )
    elif case == 'paid_supply_no_performer':
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order.pricing_data.driver.additional_prices': (
                        ADDITIONAL_PRICES_WITH_PAID_SUPPLY
                    ),
                    'order.pricing_data.user.additional_prices': (
                        ADDITIONAL_PRICES_WITH_PAID_SUPPLY
                    ),
                    'candidates.0.paid_supply': True,
                },
                '$unset': {'order.performer': None},
            },
        )
    else:
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order.performer.paid_supply': False,
                    'order.pricing_data.driver.additional_prices': {},
                    'order.pricing_data.user.additional_prices': {},
                    'candidates.0.paid_supply': False,
                },
            },
        )

    resp = await taxi_pricing_taximeter.post(
        'v1/order/recalculate',
        json=request,
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert resp.status_code == 200
    assert not tp_auction_check.times_called

    if (request['order_state'] == 'driving') or (not exp_enabled):
        assert resp.headers.get('X-Polling-Power-Policy') == 'full=disabled'
        assert resp.headers.get('X-Polling-Delay') is None
    else:
        assert resp.headers.get('X-Polling-Power-Policy') is None
        order_state = request['order_state']
        calc_method = (
            'taximeter'
            if (
                (request['user']['selected_calc_method'] == 'taximeter')
                or (request['driver']['selected_calc_method'] == 'taximeter')
            )
            else 'fixed'
        )
        assert resp.headers.get('X-Polling-Delay') == str(
            POLLING_DELAY_SETTINGS[order_state][calc_method],
        )
    data = resp.json()
    if exp_enabled and order_state == 'transporting':
        if case == 'trip_depended':
            del response['meta']
    assert data == response


@pytest.mark.now('2020-11-10T17:25:00')
@pytest.mark.parametrize('status', ['finished', 'cancelled', 'whatever'])
async def test_v1_order_recalculate_check_terminal_order(
        taxi_pricing_taximeter,
        driver_authorizer,
        status,
        mocked_time,
        testpoint,
        mockserver,
        mongodb,
        mock_order_core,
        order_core,
):
    @testpoint('terminal_check')
    def tp_terminal_check(data):
        pass

    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    mongodb.order_proc.update_one(
        {'_id': 'normal_order'},
        {
            '$set': {
                'order_info.lta': mocked_time.now(),
                'order.status': status,
            },
        },
    )
    resp = await taxi_pricing_taximeter.post(
        'v1/order/recalculate',
        json=REQUEST,
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert resp.status_code == 200

    if status != 'whatever':
        assert tp_terminal_check.times_called
    else:
        assert not tp_terminal_check.times_called


@pytest.mark.now('2020-11-10T17:25:00')
@pytest.mark.parametrize('selected_calc_method', ['fixed', 'taximeter'])
@pytest.mark.parametrize(
    'exp_data_published_taximeter_changes_check', [False, True],
)
@pytest.mark.parametrize(
    'case', ['write_always', 'skip_always', 'write_only_exp'],
)
async def test_v1_order_recalculate_write_costs(
        taxi_pricing_taximeter,
        driver_authorizer,
        case,
        selected_calc_method,
        exp_data_published_taximeter_changes_check,
        experiments3,
        mocked_time,
        mockserver,
        mongodb,
        mock_order_core,
        order_core,
):
    request = copy.deepcopy(REQUEST)
    request['user']['selected_calc_method'] = selected_calc_method
    mongodb.order_proc.update_one(
        {'_id': 'normal_order'},
        {
            '$set': {
                'order_info.lta': mocked_time.now(),
                'order.pricing_data.published': {
                    'taximeter': {'cost': {'user': {'total': 150}}},
                    'fixed': {'cost': {'user': {'total': 150}}},
                },
            },
        },
    )
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='pricing_taximeter_publish_costs',
        consumers=[
            'stq/current_prices_calculator',
            'pricing-taximeter/order_recalculate',
        ],
        clauses=[],
        default_value={
            'enabled': True,
            'taximeter_always_check_changes': (
                exp_data_published_taximeter_changes_check
            ),
            'change_delta': 0.1,
        },
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='recalculate_order_price_for_taximeter',
        consumers=['pricing-taximeter/order_recalculate'],
        clauses=[],
        default_value={'enabled': True, 'save_prices': True},
    )
    if case == 'write_always':
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'}, {'$set': {'order_info.cc': 300}},
        )
    elif case == 'skip_always':
        request['user']['taximeter']['rounded_price'] = (
            155 if selected_calc_method == 'fixed' else 150
        )  # 155 < 150 + 150 * delta(0.1)
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order_info.cc': 150,
                    'pricing_data.published.taximeter.cost.user.total': 150,
                },
            },
        )
    elif case == 'write_only_exp':
        if selected_calc_method == 'taximeter':
            request['user']['taximeter']['rounded_price'] = 150
        else:
            request['user']['taximeter']['rounded_price'] = 300
        mongodb.order_proc.update_one(
            {'_id': 'normal_order'},
            {
                '$set': {
                    'order_info.cc': 150,
                    'order.pricing_data.published.taximeter.cost.user.total': (
                        200
                    ),
                },
            },
        )
    driver_authorizer.set_session(
        AUTH['park_id'], AUTH['session'], AUTH['uuid'],
    )

    response = await taxi_pricing_taximeter.post(
        'v1/order/recalculate',
        json=request,
        headers=DEFAULT_HEADERS,
        params={'park_id': AUTH['park_id']},
    )
    assert response.status_code == 200
    if case == 'write_always' or (
            case == 'write_only_exp'
            and exp_data_published_taximeter_changes_check
    ):
        assert order_core.times_called == 2
    else:
        assert order_core.times_called == 1

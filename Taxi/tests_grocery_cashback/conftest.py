# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import typing

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from grocery_cashback_plugins import *  # noqa: F403 F401

from . import consts
from . import headers
from . import helpers


@pytest.fixture
def check_cashback_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert stq.universal_cashback_processing.times_called == times_called
        if times_called == 0:
            return

        args = stq.universal_cashback_processing.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def check_eats_cashback_emission(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert stq.eats_plus_cashback_emission.times_called == times_called

        if times_called == 0:
            return

        args = stq.eats_plus_cashback_emission.next_call()

        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        _check_kwargs(args['kwargs'], kwargs)

    return _inner


@pytest.fixture
def run_stq_cashback_compensation(mockserver, stq_runner):
    async def _inner(
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            **kwargs,
    ):

        await stq_runner.grocery_cashback_compensation.call(
            task_id='task_id',
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture
def run_stq_cashback_reward(mockserver, stq_runner):
    async def _inner(
            expect_fail: bool = False,
            exec_tries: typing.Optional[int] = None,
            **kwargs,
    ):

        await stq_runner.grocery_cashback_reward.call(
            task_id='task_id',
            kwargs=kwargs,
            expect_fail=expect_fail,
            exec_tries=exec_tries,
        )

    return _inner


@pytest.fixture(name='grocery_cashback_create_compensation')
def _grocery_cashback_create_compensation(taxi_grocery_cashback, transactions):
    async def _inner(compensation_id, payload):
        request = {
            'compensation_id': compensation_id,
            'order_id': consts.ORDER_ID,
            'payload': payload,
            'country_iso3': consts.COUNTRY_ISO3,
            'user_info': {
                'yandex_uid': headers.YANDEX_UID,
                'personal_phone_id': 'personal_phone_id',
                'user_ip': 'user_ip',
                'taxi_user_id': 'taxi_user_id',
            },
        }

        return await taxi_grocery_cashback.post(
            '/cashback/v1/create-compensation', json=request,
        )

    return _inner


@pytest.fixture(name='grocery_cashback_compensation_calculator')
def _grocery_cashback_compensation_calculator(taxi_grocery_cashback):
    async def _inner(compensation_id):
        invoice_id = helpers.make_invoice_id(compensation_id)
        params = {'order_id': invoice_id}

        return await taxi_grocery_cashback.post(
            '/cashback/v1/compensation-calculator', params=params, json={},
        )

    return _inner


@pytest.fixture(name='grocery_cashback_reward_calculator')
def _grocery_cashback_reward_calculator(taxi_grocery_cashback):
    async def _inner(order_id, status_code=200):
        compensation_id = helpers.make_reward_compensation_id(order_id)
        invoice_id = helpers.make_invoice_id(compensation_id)
        params = {'order_id': invoice_id}

        response = await taxi_grocery_cashback.post(
            '/cashback/v1/compensation-calculator', params=params, json={},
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@pytest.fixture(name='grocery_cashback_reward')
async def _grocery_cashback_reward(taxi_grocery_cashback):
    async def _do(status_code=200, **kwargs):
        response = await taxi_grocery_cashback.post(
            '/lavka/v1/cashback/v1/reward',
            json={
                'order_id': consts.ORDER_ID,
                'amount': '10',
                'reward_type': 'tracking_game',
                **kwargs,
            },
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


@pytest.fixture(name='grocery_orders')
def mock_grocery_orders(grocery_orders_lib):
    moked_order = grocery_orders_lib.add_order()
    moked_order_dict = moked_order.as_dict()
    moked_order_dict['order_id'] = consts.ORDER_ID
    moked_order.update(yandex_uid=headers.YANDEX_UID)
    moked_order.update(grocery_flow_version=consts.BASIC_FLOW_VERSION)

    return grocery_orders_lib


@pytest.fixture(name='cashback_order_calculator')
def _grocery_cashback_calc(taxi_grocery_cashback):
    async def _inner(order_id):
        params = {'order_id': order_id}
        request = {'cleared': '1000', 'held': '1000', 'currency': 'RUB'}
        return await taxi_grocery_cashback.post(
            '/cashback/v1/order-calculator', params=params, json=request,
        )

    return _inner


@pytest.fixture(name='cashback_reward_retrieve')
def _grocery_cashback_reward_retrieve(taxi_grocery_cashback):
    async def _do(order_id=consts.ORDER_ID, status_code=200):
        request = {'order_id': order_id}

        response = await taxi_grocery_cashback.post(
            '/lavka/v1/cashback/v1/reward/retrieve',
            json=request,
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


@pytest.fixture
def check_cashback_reward_stq_event(stq):
    def _inner(times_called=1, stq_event_id=None, **kwargs):
        assert stq.grocery_cashback_reward.times_called == times_called
        if times_called == 0:
            return

        args = stq.grocery_cashback_reward.next_call()
        if stq_event_id is not None:
            assert args['id'] == stq_event_id

        if kwargs:
            _check_kwargs(args['kwargs'], kwargs)

    return _inner


def _check_kwargs(args, kwargs):
    mock_helpers.assert_dict_contains(args, kwargs)

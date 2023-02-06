import typing

import pytest

from eats_integration_offline_orders.components.notifications import (
    base_notifier,
)


class _Sentinel:
    pass


DEFAULT_PLACE_ID = '3fa85f64-5717-4562-b3fc-2c963f66afa6'
DEFAULT_WAITER_ID = '1965cdbe-cac1-44ba-9355-d5da6fd87009'
SENTINEL = _Sentinel()


def value_or_default(value, default):
    return default if value is SENTINEL else value


def _format_params_waiter(
        place_id: typing.Optional[str] = DEFAULT_PLACE_ID,
        waiter_id: typing.Optional[str] = DEFAULT_WAITER_ID,
        table: typing.Optional[str] = '0',
        comment: typing.Optional[str] = '',
        call_waiter_type: str = 'call',
):
    return {
        'place_id': place_id,
        'waiter_id': waiter_id,
        'table': table,
        'comment': comment,
        'call_waiter_type': call_waiter_type,
    }


def _format_params_paid(
        place_id: typing.Optional[str] = DEFAULT_PLACE_ID,
        waiter_id: typing.Optional[str] = DEFAULT_WAITER_ID,
        table: typing.Optional[str] = '0',
        amount: typing.Optional[float] = 1.1,
        order_uuid: typing.Optional[str] = '111-111-11',
        inner_order_id: typing.Optional[str] = '0',
):
    return {
        'place_id': place_id,
        'waiter_id': waiter_id,
        'table': table,
        'amount': amount,
        'order_uuid': order_uuid,
        'inner_order_id': inner_order_id,
    }


def make_pytest_param_waiter(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        params: typing.Any = SENTINEL,
        success_call: typing.Any = SENTINEL,
        except_message: typing.Any = SENTINEL,
        i_w_status: typing.Any = SENTINEL,
):
    return pytest.param(
        value_or_default(params, _format_params_waiter()),
        value_or_default(success_call, True),
        value_or_default(except_message, ''),
        value_or_default(i_w_status, 202),
        id=id,
        marks=marks,
    )


def make_pytest_param_paid(
        *,
        id: str,  # pylint: disable=redefined-builtin, invalid-name
        marks=(),
        params: typing.Any = SENTINEL,
        success_call: typing.Any = SENTINEL,
        except_message: typing.Any = SENTINEL,
        i_w_status: typing.Any = SENTINEL,
):
    return pytest.param(
        value_or_default(params, _format_params_paid()),
        value_or_default(success_call, True),
        value_or_default(except_message, ''),
        value_or_default(i_w_status, 202),
        id=id,
        marks=marks,
    )


@pytest.mark.parametrize(
    ('params', 'success_call', 'except_message', 'i_w_status'),
    (
        make_pytest_param_waiter(id='success'),
        make_pytest_param_waiter(
            id='wrong-place_id',
            params=_format_params_waiter(place_id='wrong_id'),
            success_call=False,
            except_message='IIKO waiter for place_id wrong_id not found.',
        ),
        make_pytest_param_waiter(
            id='disable_place',
            params=_format_params_waiter(
                place_id='336a0f1e-6b0a-4fa4-8aba-f64dd2368d24',
            ),
            success_call=False,
            except_message='IIKO waiter for place_id '
            '336a0f1e-6b0a-4fa4-8aba-f64dd2368d24 is disabled',
        ),
        make_pytest_param_waiter(
            id='without_user',
            params=_format_params_waiter(waiter_id=None),
            success_call=False,
            except_message='waiter_id незаполнен',
        ),
        make_pytest_param_waiter(
            id='i-w_wrong_status',
            i_w_status=400,
            success_call=False,
            except_message='IIKO waiter send status 400: Bad Request',
        ),
        make_pytest_param_waiter(
            id='i-w_bad_response',
            i_w_status=500,
            success_call=False,
            except_message='IIKO waiter send status 500: '
            'Internal Server Error',
        ),
        make_pytest_param_waiter(
            id='success_cash_payment',
            params=_format_params_waiter(call_waiter_type='cash_payment'),
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db_iiko_waiter.sql'],
)
@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_IIKO_WAITER={'host': '$mockserver'},
)
async def test_iiko_waiter_notifier_waiter(
        web_context,
        load_json,
        mockserver,
        params,
        success_call,
        except_message,
        i_w_status,
):
    @mockserver.handler('/api/v1/notifications/mobile/waiter-call')
    def get_test_call_waiter(request):
        assert request.json['userId'] == params['waiter_id']
        return mockserver.make_response('', status=i_w_status)

    @mockserver.handler(
        '/api/v1/notifications/mobile/waiter-call/cash-payment',
    )
    def get_test_call_waiter_cash(request):
        assert request.json['userId'] == params['waiter_id']
        return mockserver.make_response('', status=i_w_status)

    try:
        await web_context.iiko_waiter_notifier.call_waiter(**params)
    except base_notifier.NotifyError as exc:
        assert str(exc) == except_message
    if success_call:
        if params['call_waiter_type'] == 'cash_payment':
            assert get_test_call_waiter_cash.has_calls
        else:
            assert get_test_call_waiter.has_calls


@pytest.mark.parametrize(
    ('params', 'success_call', 'except_message', 'i_w_status'),
    (
        make_pytest_param_paid(id='success'),
        make_pytest_param_paid(
            id='wrong-place_id',
            params=_format_params_paid(place_id='wrong_id'),
            success_call=False,
            except_message='IIKO waiter for place_id wrong_id not found.',
        ),
        make_pytest_param_paid(
            id='i-w_wrong_status',
            i_w_status=400,
            success_call=False,
            except_message='IIKO waiter send status 400: Bad Request',
        ),
        make_pytest_param_paid(
            id='i-w_bad_response',
            i_w_status=500,
            success_call=False,
            except_message='IIKO waiter send status 500: '
            'Internal Server Error',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db_iiko_waiter.sql'],
)
@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_IIKO_WAITER={'host': '$mockserver'},
)
async def test_iiko_waiter_notifier_paid(
        web_context,
        load_json,
        mockserver,
        params,
        success_call,
        except_message,
        i_w_status,
):
    @mockserver.handler('/api/v1/notifications/mobile/order-paid')
    def get_test_call_waiter(request):
        assert request.json['userId'] == params['waiter_id']
        return mockserver.make_response('', status=i_w_status)

    try:
        await web_context.iiko_waiter_notifier.check_paid(**params)
    except base_notifier.NotifyError as exc:
        assert str(exc) == except_message
    if success_call:
        assert get_test_call_waiter.has_calls


@pytest.mark.parametrize(
    'place_id, name_selector',
    (
        pytest.param(
            '3fa85f64-5717-4562-b3fc-2c963f66afa6', 'iiko', id='i-w selector',
        ),
        pytest.param(
            '336a0f1e-6b0a-4fa4-8aba-f64dd2368d24',
            None,
            id='i-w selector-disable',
        ),
        pytest.param('wrong_id', None, id='i-w selector-wrong_id'),
        pytest.param('place_id__1', 'telegram', id='telegram selector'),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db.sql', 'db_iiko_waiter.sql'],
)
async def test_iiko_waiter_notifier_selector(
        web_context, load_json, mockserver, place_id, name_selector,
):
    types_selectors = {
        'iiko': web_context.iiko_waiter_notifier,
        'telegram': web_context.telegram_bot,
    }
    selector = await web_context.notifier_selector.get_selector(place_id)
    assert selector == types_selectors.get(name_selector)

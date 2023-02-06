import pytest

from tests_coupons import util
from tests_coupons.mocks import order_core as order_core_mocks


DEFAULT_ORDER_ID = 'test_order_id'
DEFAULT_APPLICATION = 'test_application'
DEFAULT_PHONE_ID = '0123456789abcdef0123f001'
DEFAULT_PERSONAL_PHONE_ID = '209348023228'
DEFAULT_YANDEX_UID = 'test_yandex_uid'

DEFAULT_COUPON_ID = 'test_coupon'
EATS_COUPON_ID = 'EATS_COUPON'
DEFAULT_COUPON_VALUE = 123
DEFAULT_TOKEN = 'test_token'


def get_coupon_id(service='taxi'):
    return EATS_COUPON_ID if service == 'eats' else DEFAULT_COUPON_ID


def get_task_kwargs(was_coupon_used=True, service='taxi'):
    return {
        'phone_id': DEFAULT_PHONE_ID,
        'personal_phone_id': DEFAULT_PERSONAL_PHONE_ID,
        'service': service,
        'order_id': DEFAULT_ORDER_ID,
        'yandex_uid': DEFAULT_YANDEX_UID,
        'application': DEFAULT_APPLICATION,
        'cost': 1234,
        'token': 'test_token',
        'coupon': {
            'id': get_coupon_id(service),
            'used': was_coupon_used,
            'value': DEFAULT_COUPON_VALUE,
        },
    }


def get_promocode_usages2(
        mongo, reserve, service='taxi', separate_flows_enabled=False,
):
    db_reserve = reserve if service == 'taxi' else service + '_' + reserve
    result = util.collection_promocode_usages2(
        mongo, service, separate_flows_enabled,
    ).find({'usages.reserve': db_reserve})
    return list(result)


def get_order_coupon(
        value=DEFAULT_COUPON_VALUE,
        was_used=True,
        valid=True,
        coupon_id=DEFAULT_COUPON_ID,
):
    return {
        'id': coupon_id,
        'was_used': was_used,
        'valid': valid,
        'value': value,
    }


def get_order_current_prices(
        use_cost_includes_coupon=1.0, coupon_value=DEFAULT_COUPON_VALUE,
):
    return {
        'final_cost_meta': {
            'user': {
                'use_cost_includes_coupon': use_cost_includes_coupon,
                'coupon_value': coupon_value,
            },
        },
    }


def get_order_fields_response(
        order_id=DEFAULT_ORDER_ID,
        status='finished',
        taxi_status='complete',
        coupon=None,
        current_prices=None,
        service='taxi',
):
    if coupon is None:
        coupon = get_order_coupon(coupon_id=get_coupon_id(service))

    if current_prices is None:
        current_prices = {}

    fields = {
        'order': {
            '_id': order_id,
            'cost': 1234,
            'status': status,
            'taxi_status': taxi_status,
            'coupon': coupon,
            'current_prices': current_prices,
        },
        'performer': {'candidate_index': 0},
    }
    return {
        'fields': fields,
        'order_id': order_id,
        'replica': 'secondary',
        'version': 'test_version',
    }


@pytest.fixture(name='task_client_mocks')
def _task_client_mocks(mockserver):
    class Context:
        # /order-core/v1/tc/order-fields
        order_fields = None

    context = Context()
    context.order_fields = order_core_mocks.v1_tc_order_fields(mockserver)
    return context


@pytest.mark.parametrize('was_coupon_used', [True, False])
@pytest.mark.parametrize(
    'service',
    [
        pytest.param(
            'taxi', marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            'taxi', marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
        pytest.param(
            'eats', marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
    ],
)
@pytest.mark.parametrize('_', util.PROMOCODES_DB_MODE_PARAMS)
async def test_ok(
        stq_runner,
        mongodb,
        task_client_mocks,
        taxi_config,
        was_coupon_used,
        service,
        _,
):
    task_kwargs = get_task_kwargs(
        was_coupon_used=was_coupon_used, service=service,
    )
    separate_flows_enabled = taxi_config.get('COUPONS_SEPARATE_FLOWS')

    task_client_mocks.order_fields.set_expectations(order_id=DEFAULT_ORDER_ID)
    task_client_mocks.order_fields.set_response(
        get_order_fields_response(
            coupon=get_order_coupon(
                was_used=was_coupon_used, coupon_id=get_coupon_id(service),
            ),
        ),
    )

    await stq_runner.finish_coupon.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    services_to_update_args = {'taxi'}
    assert task_client_mocks.order_fields.times_called == (
        1 if was_coupon_used and service in services_to_update_args else 0
    )

    usages = get_promocode_usages2(
        mongodb, DEFAULT_ORDER_ID, service, separate_flows_enabled,
    )
    assert len(usages) == 1
    usage = usages[0]['usages'][0]
    if was_coupon_used:
        assert usage['cost_usage'] == DEFAULT_COUPON_VALUE
    else:
        assert usage['cancel_tokens'] == [DEFAULT_TOKEN]


@pytest.mark.parametrize(
    'status_code, is_retriable', [(500, True), (404, False)],
)
async def test_order_core_error(
        stq_runner, mockserver, mongodb, status_code, is_retriable,
):
    task_kwargs = get_task_kwargs()

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _order_core_v1_tc_order_fields_mock(request):
        return mockserver.make_response(
            json={'code': str(status_code), 'message': 'err'},
            status=status_code,
        )

    usages_before = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)
    await stq_runner.finish_coupon.call(
        task_id='whatever',
        args=[],
        kwargs=task_kwargs,
        expect_fail=is_retriable,
    )

    usages_after = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)
    assert _order_core_v1_tc_order_fields_mock.times_called > 0
    assert usages_before == usages_after


@pytest.mark.parametrize(
    'has_no_order, has_no_coupon, is_coupon_valid',
    [
        pytest.param(True, False, True, id='No order in order_proc'),
        pytest.param(False, True, True, id='No coupon in order_proc.order'),
        pytest.param(False, False, False, id='Coupon is not valid'),
    ],
)
async def test_invalid_order_proc(
        stq_runner,
        mongodb,
        task_client_mocks,
        has_no_order,
        has_no_coupon,
        is_coupon_valid,
):
    task_kwargs = get_task_kwargs()
    usages_before = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)

    order_fields_response = get_order_fields_response(
        coupon=get_order_coupon(valid=is_coupon_valid),
    )
    if has_no_coupon:
        order_fields_response['fields']['order'].pop('coupon')
    if has_no_order:
        order_fields_response['fields'].pop('order')

    task_client_mocks.order_fields.set_response(order_fields_response)

    await stq_runner.finish_coupon.call(
        task_id='whatever', args=[], kwargs=task_kwargs, expect_fail=False,
    )

    usages_after = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)
    assert task_client_mocks.order_fields.times_called == 1
    assert usages_before == usages_after


@pytest.mark.config(TASK_COUPON_FINISH_MAX_EXEC_TRIES=123)
@pytest.mark.parametrize(
    'exec_count, is_retry_count_exceeded', [(122, False), (123, True)],
)
async def test_inconsitent_state_retry_count(
        stq_runner,
        mongodb,
        task_client_mocks,
        exec_count,
        is_retry_count_exceeded,
):
    task_kwargs = get_task_kwargs(was_coupon_used=True)
    task_client_mocks.order_fields.set_response(
        get_order_fields_response(status='not_finished'),
    )

    usages_before = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)
    await stq_runner.finish_coupon.call(
        task_id='whatever',
        args=[],
        kwargs=task_kwargs,
        exec_tries=exec_count,
        expect_fail=not is_retry_count_exceeded,
    )

    assert task_client_mocks.order_fields.times_called == 1
    usages_after = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)

    if is_retry_count_exceeded:
        assert usages_after[0]['usages'][0]['cancel_tokens'] == [DEFAULT_TOKEN]
    else:
        assert usages_before == usages_after


@pytest.mark.parametrize(
    'use_cost_includes_coupon, new_flow_coupon_value, is_new_flow',
    [
        pytest.param(None, DEFAULT_COUPON_VALUE + 123, False, id='Null flag'),
        pytest.param(0.0, DEFAULT_COUPON_VALUE + 456, False, id='Old flow'),
        pytest.param(1.0, None, False, id='coupon_value is null'),
        pytest.param(1.0, DEFAULT_COUPON_VALUE + 789, True, id='New flow'),
    ],
)
@pytest.mark.parametrize(
    'service',
    [
        pytest.param(
            'taxi', marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
        pytest.param(
            'taxi', marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=False)],
        ),
        pytest.param(
            'eats', marks=[pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)],
        ),
    ],
)
async def test_new_cost_flow(
        stq_runner,
        mongodb,
        task_client_mocks,
        taxi_config,
        use_cost_includes_coupon,
        new_flow_coupon_value,
        is_new_flow,
        service,
):
    task_kwargs = get_task_kwargs(was_coupon_used=True, service=service)
    separate_flows_enabled = taxi_config.get('COUPONS_SEPARATE_FLOWS')
    task_client_mocks.order_fields.set_response(
        get_order_fields_response(
            current_prices=get_order_current_prices(
                use_cost_includes_coupon=use_cost_includes_coupon,
                coupon_value=new_flow_coupon_value,
            ),
            service=service,
        ),
    )

    await stq_runner.finish_coupon.call(
        task_id='whatever', args=[], kwargs=task_kwargs,
    )

    services_to_update_args = {'taxi'}
    assert task_client_mocks.order_fields.times_called == (
        1 if service in services_to_update_args else 0
    )
    usages = get_promocode_usages2(
        mongodb,
        DEFAULT_ORDER_ID,
        service=service,
        separate_flows_enabled=separate_flows_enabled,
    )

    usage = usages[0]['usages'][0]

    if is_new_flow and service in services_to_update_args:
        assert usage['cost_usage'] == new_flow_coupon_value
    else:
        assert usage['cost_usage'] == DEFAULT_COUPON_VALUE


async def test_invalid_new_cost_flow(stq_runner, mongodb, task_client_mocks):
    task_client_mocks.order_fields.set_response(
        get_order_fields_response(
            current_prices=get_order_current_prices(
                use_cost_includes_coupon=1.0, coupon_value=0.0,
            ),
        ),
    )

    task_kwargs = get_task_kwargs()
    usages_before = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)
    await stq_runner.finish_coupon.call(
        task_id='whatever', args=[], kwargs=task_kwargs, expect_fail=False,
    )

    usages_after = get_promocode_usages2(mongodb, DEFAULT_ORDER_ID)
    assert task_client_mocks.order_fields.times_called == 1
    assert usages_before == usages_after

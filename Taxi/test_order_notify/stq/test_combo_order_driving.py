from bson.objectid import ObjectId
import pytest

from test_order_notify.mocks.order_core import OrderProcGetFieldsContext
from test_order_notify.mocks.ucommunications import UserPushContext

TRANSLATIONS_NOTIFY = {
    'order_notify.combo_order.driving.inner.title': {
        'ru': 'inner driving title',
    },
    'order_notify.combo_order.driving.inner.text': {
        'ru': 'inner driving text',
    },
    'order_notify.combo_order.driving.outer.title': {
        'ru': 'outer driving title',
    },
    'order_notify.combo_order.driving.outer.text': {
        'ru': 'outer driving text',
    },
}

EXP3_CONSUMER = 'order-notify/stq/order_notify_combo_order_driving'
PEOPLE_COMBO_ORDER_EXP3_NAME = 'people_combo_order'
EXP_TRANSLATIONS_NOTIFY = {
    'order_notify.exp.inner.title': {'ru': 'inner exp title'},
    'order_notify.exp.inner.text': {'ru': 'inner exp text'},
    'order_notify.exp.outer.title': {'ru': 'outer exp title'},
    'order_notify.exp.outer.text': {'ru': 'outer exp text'},
}

DEFAULT_KWARGS = {
    'outer_order_id': 'test_outer_order_id',
    'inner_order_id': 'test_inner_order_id',
}

ORDER_CORE_FIELDS = [
    'order.calc.alternative_type',
    'order.nz',
    'order.user_id',
    'order.user_locale',
    'order.user_phone_id',
]

COMBO_TYPE_TO_USER_PHONE_ID = {
    'outer': ObjectId('56964567ed2c89a5e0aaaaaa'),
    'inner': ObjectId('56964567ed2c89a5e0aaaaab'),
}

IDEMPOTENCY_TOKENS = {
    'outer': 'db5461dfb601aadcf9d5f12027b19a759c84dcc8',
    'inner': 'f693ae98180cc3aa0a522d61b2f11e0b05e0fdaa',
}


def make_combo_order_exp_value(combo_type):
    return {
        f'combo_{combo_type}': {
            'combo_notification': {
                'title': f'exp.{combo_type}.title',
                'subtitle': f'exp.{combo_type}.text',
            },
        },
    }


def make_combo_order_exp_args(phone_id, zone='test_zone'):
    return [
        {'name': 'phone_id', 'type': 'string', 'value': phone_id},
        {'name': 'zone', 'type': 'string', 'value': zone},
    ]


def make_order(
        order_id, user_id, user_phone_id, alternative_type, user_locale,
):
    return {
        '_id': order_id,
        'order': {
            'nz': 'test_zone',
            'user_id': user_id,
            'user_locale': user_locale,
            'user_phone_id': user_phone_id,
            'calc': {'alternative_type': alternative_type},
        },
    }


def make_combo_order(combo_type):
    return make_order(
        f'test_{combo_type}_order_id',
        f'test_{combo_type}_user_id',
        COMBO_TYPE_TO_USER_PHONE_ID[combo_type],
        alternative_type=f'combo_{combo_type}',
        user_locale='ru',
    )


def make_combo_order_v2(combo_type):
    return make_order(
        f'test_v2_{combo_type}_order_id',
        f'test_v2_{combo_type}_user_id',
        COMBO_TYPE_TO_USER_PHONE_ID[combo_type],
        alternative_type=f'combo_{combo_type}',
        user_locale='ru',
    )


def make_user_push_call(combo_type):
    push_call = UserPushContext.Call()
    push_call.expected.title = f'{combo_type} driving title'
    push_call.expected.text = f'{combo_type} driving text'
    push_call.expected.intent = f'taxi_combo_order.driving.{combo_type}'
    push_call.expected.order_id = f'test_{combo_type}_order_id'
    push_call.expected.idempotency_token = IDEMPOTENCY_TOKENS[combo_type]
    return push_call


def make_user_push_call_v2(combo_type):
    push_call = UserPushContext.Call()
    push_call.expected.title = f'{combo_type} driving title'
    push_call.expected.text = f'{combo_type} driving text'
    push_call.expected.intent = f'taxi_combo_order.driving.{combo_type}'
    push_call.expected.order_id = ''
    push_call.expected.idempotency_token = None
    return push_call


def make_order_core_call(combo_type):
    order_core_call = OrderProcGetFieldsContext.Call()
    order_core_call.expected.fields = ORDER_CORE_FIELDS
    if combo_type == 'inner':
        order_core_call.expected.require_latest = True
    order_core_call.response.order = make_combo_order(combo_type)
    return order_core_call


def make_order_core_call_v2(combo_type):
    order_core_call = OrderProcGetFieldsContext.Call()
    order_core_call.expected.fields = ORDER_CORE_FIELDS
    order_core_call.expected.order_id_type = 'exact_id'
    if combo_type == 'inner':
        order_core_call.expected.require_latest = True
    order_core_call.response.order = make_combo_order_v2(combo_type)
    return order_core_call


@pytest.fixture(name='combo_order_driving_mock_context')
def _combo_order_driving_mock_context(
        mock_ucommunications_user_push, mock_order_core_get_fields,
):
    user_push_mock = mock_ucommunications_user_push()
    user_push_mock.calls = {
        'test_outer_user_id': make_user_push_call('outer'),
        'test_inner_user_id': make_user_push_call('inner'),
        'test_v2_outer_user_id': make_user_push_call_v2('outer'),
        'test_v2_inner_user_id': make_user_push_call_v2('inner'),
    }

    order_core_get_fields_mock = mock_order_core_get_fields()
    order_core_get_fields_mock.calls = {
        'test_outer_order_id': make_order_core_call('outer'),
        'test_inner_order_id': make_order_core_call('inner'),
        'test_v2_outer_order_id': make_order_core_call_v2('outer'),
        'test_v2_inner_order_id': make_order_core_call_v2('inner'),
    }

    class Context:
        user_push = user_push_mock
        order_core_get_fields = order_core_get_fields_mock

    return Context()


@pytest.mark.translations(notify=TRANSLATIONS_NOTIFY)
async def test_ok(stq_runner, combo_order_driving_mock_context):
    context = combo_order_driving_mock_context

    await stq_runner.order_notify_combo_order_driving.call(
        task_id='whatever', args=[], kwargs=DEFAULT_KWARGS,
    )

    assert context.order_core_get_fields.times_called == 2
    assert context.user_push.times_called == 2


@pytest.mark.parametrize(
    'error_user_id',
    [
        pytest.param(None, id='ok'),
        pytest.param('test_outer_user_id', id='outer push error'),
        pytest.param('test_inner_user_id', id='inner push error'),
    ],
)
@pytest.mark.parametrize(
    'error_order_id',
    [
        pytest.param(None, id='ok'),
        pytest.param('test_outer_order_id', id='outer order error'),
        pytest.param('test_inner_order_id', id='inner order error'),
    ],
)
@pytest.mark.translations(notify=TRANSLATIONS_NOTIFY)
async def test_client_errors(
        stq_runner,
        combo_order_driving_mock_context,
        error_user_id,
        error_order_id,
):
    context = combo_order_driving_mock_context

    if error_user_id:
        context.user_push.calls[error_user_id].response.error_code = 500

    if error_order_id:
        context.order_core_get_fields.calls[
            error_order_id
        ].response.error_code = 500

    expect_fail = error_user_id is not None or error_order_id is not None

    acutally_failed = False
    try:
        await stq_runner.order_notify_combo_order_driving.call(
            task_id='whatever', args=[], kwargs=DEFAULT_KWARGS,
        )
    except RuntimeError:  # pytest.raises doesn't work for some reason
        acutally_failed = True

    assert acutally_failed == expect_fail


@pytest.mark.parametrize(
    'bad_type_order_id',
    [
        pytest.param(None, id='ok'),
        pytest.param('test_outer_order_id', id='outer order bad type'),
        pytest.param('test_inner_order_id', id='inner order bad type'),
    ],
)
@pytest.mark.parametrize(
    'not_found_order_id',
    [
        pytest.param(None, id='ok'),
        pytest.param('test_outer_order_id', id='outer order not found'),
        pytest.param('test_inner_order_id', id='inner order not found'),
    ],
)
@pytest.mark.translations(notify=TRANSLATIONS_NOTIFY)
async def test_skippable_errors(
        stq_runner,
        combo_order_driving_mock_context,
        bad_type_order_id,
        not_found_order_id,
):
    context = combo_order_driving_mock_context

    if bad_type_order_id:
        bad_call = context.order_core_get_fields.calls[bad_type_order_id]
        bad_call.response.set_alternative_type('gibberish')
    if not_found_order_id:
        del context.order_core_get_fields.calls[not_found_order_id]

    await stq_runner.order_notify_combo_order_driving.call(
        task_id='whatever', args=[], kwargs=DEFAULT_KWARGS,
    )

    is_push_sent = bad_type_order_id is None and not_found_order_id is None
    assert context.order_core_get_fields.times_called == 2
    assert context.user_push.times_called == (2 if is_push_sent else 0)


@pytest.mark.parametrize(
    'is_outer_exp_enabled',
    [
        pytest.param(False, id='outer exp off'),
        pytest.param(
            True,
            marks=[
                pytest.mark.client_experiments3(
                    consumer=EXP3_CONSUMER,
                    experiment_name=PEOPLE_COMBO_ORDER_EXP3_NAME,
                    args=make_combo_order_exp_args(
                        str(COMBO_TYPE_TO_USER_PHONE_ID['outer']),
                    ),
                    value=make_combo_order_exp_value('outer'),
                ),
            ],
            id='outer exp on',
        ),
    ],
)
@pytest.mark.parametrize(
    'is_inner_exp_enabled',
    [
        pytest.param(False, id='inner exp off'),
        pytest.param(
            True,
            marks=[
                pytest.mark.client_experiments3(
                    consumer=EXP3_CONSUMER,
                    experiment_name=PEOPLE_COMBO_ORDER_EXP3_NAME,
                    args=make_combo_order_exp_args(
                        str(COMBO_TYPE_TO_USER_PHONE_ID['inner']),
                    ),
                    value=make_combo_order_exp_value('inner'),
                ),
            ],
            id='inner exp on',
        ),
    ],
)
@pytest.mark.translations(
    notify={**TRANSLATIONS_NOTIFY, **EXP_TRANSLATIONS_NOTIFY},
)
async def test_exp_tanker_keys(
        stq_runner,
        combo_order_driving_mock_context,
        is_outer_exp_enabled,
        is_inner_exp_enabled,
):
    context = combo_order_driving_mock_context
    if is_outer_exp_enabled:
        context.user_push.calls[
            'test_outer_user_id'
        ].expected.title = 'outer exp title'
        context.user_push.calls[
            'test_outer_user_id'
        ].expected.text = 'outer exp text'

    if is_inner_exp_enabled:
        context.user_push.calls[
            'test_inner_user_id'
        ].expected.title = 'inner exp title'
        context.user_push.calls[
            'test_inner_user_id'
        ].expected.text = 'inner exp text'

    await stq_runner.order_notify_combo_order_driving.call(
        task_id='whatever', args=[], kwargs=DEFAULT_KWARGS,
    )

    assert context.user_push.times_called == 2
    assert context.order_core_get_fields.times_called == 2


@pytest.mark.translations(notify=TRANSLATIONS_NOTIFY)
async def test_ok_v2(stq_runner, combo_order_driving_mock_context):
    context = combo_order_driving_mock_context

    v2_kwargs = {
        'outer_order_id': '',
        'inner_order_id': '',
        'outer_taxi_order_id': 'test_v2_outer_order_id',
        'inner_taxi_order_id': 'test_v2_inner_order_id',
    }
    await stq_runner.order_notify_combo_order_driving.call(
        task_id='whatever', args=[], kwargs=v2_kwargs,
    )
    assert context.order_core_get_fields.times_called == 2
    assert context.user_push.times_called == 2

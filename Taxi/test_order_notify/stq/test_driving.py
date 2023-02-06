import copy

import pytest

from order_notify.notifications.base import UcommunicationsError
from order_notify.stq import order_client_notification
from test_order_notify.conftest import BASE_PAYLOAD
from test_order_notify.conftest import TRANSLATIONS_NOTIFY

DEFAULT_ARGS = {
    'order_id': 'order_1',
    'event_key': 'handle_driving',
    'user_id': 'user_1',
    'phone_id': 'phone_1',
    'locale': 'ru',
    'payload_doc': BASE_PAYLOAD,
}


@pytest.mark.now('2021-05-07T10:48')
@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY, color={'FAFBFB': {'ru': 'белый'}},
)
@pytest.mark.parametrize(
    'with_override',
    [
        pytest.param(False, id='simple'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                NOTIFICATION_SUFFIX_BY_TARIFF={
                    'econom': {
                        'notifications': ['driving'],
                        'suffix': 'econom_suffix',
                    },
                },
            ),
            id='with_override',
        ),
    ],
)
@pytest.mark.parametrize(
    'event_key',
    [
        pytest.param('handle_driving', id='simple'),
        pytest.param('handle_assigning', id='override event'),
    ],
)
async def test_task(stq3_context, mockserver, with_override, event_key):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _handler(request):
        title = 'Такси'
        text = 'Через 3–5 мин. приедет Белый Kia Optima Е 001 КХ 777'
        if with_override:
            title += ' | econom_suffix'
            text += ' | econom_suffix'

        assert request.json['data']['payload'] == {
            'title': title,
            # – En Dash
            'text': text,
            'extra': {
                'id': '00000000000040008000000000000000',
                'order_id': 'order_1',
            },
        }
        return {}

    args = DEFAULT_ARGS
    args['event_key'] = event_key

    await order_client_notification.task(stq3_context, **args)

    # pylint: disable=protected-access
    sensor = 'notify.success.send_push.taxi_driving'
    assert stq3_context.stats.get_counter({'sensor': sensor})._value == 1


@pytest.mark.now('2021-05-07T10:48')
@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY, color={'FAFBFB': {'ru': 'белый'}},
)
@pytest.mark.parametrize(
    'error_code',
    [
        pytest.param(400, id='simple exception'),
        pytest.param(500, id='need retry stq'),
    ],
)
async def test_task_client_error(stq3_context, mockserver, error_code):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _handler(request):
        return mockserver.make_response(
            status=error_code,
            json={'code': 'SOME_ERROR', 'message': 'some error'},
        )

    if error_code >= 500:
        with pytest.raises(UcommunicationsError):
            await order_client_notification.task(stq3_context, **DEFAULT_ARGS)
        return

    await order_client_notification.task(stq3_context, **DEFAULT_ARGS)

    err_prefix = 'notify.error.send_push.taxi_driving'

    err_400 = f'{err_prefix}.UserNotificationPushPost400'
    err_total = f'notify.error_total.send_push'

    # pylint: disable=protected-access
    assert stq3_context.stats.get_counter({'sensor': err_400})._value == 1
    assert stq3_context.stats.get_counter({'sensor': err_total})._value == 1


@pytest.mark.now('2021-05-07T10:48')
@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY, color={'FAFBFB': {'ru': 'белый'}},
)
async def test_task_tanker_error(stq3_context, mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _handler(request):
        return mockserver.make_response(
            status=400, json={'code': 'SOME_ERROR', 'message': 'some error'},
        )

    args = DEFAULT_ARGS
    args['locale'] = 'en'
    # TranslationNotFoundError
    await order_client_notification.task(stq3_context, **args)

    err_prefix = 'notify.error.send_push.taxi_driving'

    err_trans = f'{err_prefix}.TranslationNotFoundError'
    err_total = f'notify.error_total.send_push'

    # pylint: disable=protected-access
    assert stq3_context.stats.get_counter({'sensor': err_trans})._value == 1
    assert stq3_context.stats.get_counter({'sensor': err_total})._value == 1


@pytest.mark.now('2021-05-07T10:48')
@pytest.mark.translations(
    notify=TRANSLATIONS_NOTIFY, color={'FAFBFB': {'ru': 'белый'}},
)
@pytest.mark.parametrize(
    ['autoreorder_reason', 'event_key', 'push_text', 'sensor'],
    [
        pytest.param(
            'cancel-autoreorder',
            'handle_driving',
            'Водитель отменил заказ, но мы уже нашли новую машину. '
            'Через 3–5 мин. приедет Белый Kia Optima Е 001 КХ 777',
            'notify.success.send_push.taxi_driving.autoreorder_by_cancel',
        ),
        pytest.param(
            'eta-autoreorder',
            'handle_assigning',
            'Водитель задерживается, но мы уже нашли новую машину. '
            'Через 3–5 мин. приедет Белый Kia Optima Е 001 КХ 777',
            'notify.success.send_push.taxi_driving.autoreorder_by_eta',
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/order_notify_push_after_reorder',
    experiment_name='push_after_reorder',
    args=[
        {'name': 'user_id', 'type': 'string', 'value': 'user_1'},
        {
            'name': 'autoreorder_reason',
            'type': 'string',
            'value': 'cancel-autoreorder',
        },
    ],
    value={'tanker_key': 'driving.autoreorder_by_cancel'},
)
@pytest.mark.client_experiments3(
    consumer='order-notify/stq/order_notify_push_after_reorder',
    experiment_name='push_after_reorder',
    args=[
        {'name': 'user_id', 'type': 'string', 'value': 'user_1'},
        {
            'name': 'autoreorder_reason',
            'type': 'string',
            'value': 'eta-autoreorder',
        },
    ],
    value={'tanker_key': 'driving.autoreorder_by_eta'},
)
async def test_driving_after_autoreorder(
        stq3_context,
        mockserver,
        autoreorder_reason,
        event_key,
        push_text,
        sensor,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def _handler(request):
        title = 'Такси'
        text = push_text

        assert request.json['data']['payload'] == {
            'title': title,
            'text': text,
            'extra': {
                'id': '00000000000040008000000000000000',
                'order_id': 'order_1',
            },
        }
        return {}

    args = copy.deepcopy(DEFAULT_ARGS)
    # из-за того, что предыдущий тест меняет глобальные аргументы
    # ключ locale становится en и тест флапает. Возвращаю ru
    args['locale'] = 'ru'
    args['event_key'] = event_key
    args['payload_doc']['autoreorder_reason'] = autoreorder_reason

    await order_client_notification.task(stq3_context, **args)
    # pylint: disable=protected-access
    assert stq3_context.stats.get_counter({'sensor': sensor})._value == 1

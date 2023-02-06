import datetime

import pytest

from metrics_processing.rules.common import RuleType
from metrics_processing.rules.common.rule import Rule
from metrics_processing.utils.action_journal import ActionJournal
from taxi.clients.communications import DRIVER_CHECK_CODE

from taxi_driver_metrics.common.models import Events
from taxi_driver_metrics.common.models.action import InvalidTankerKeyError
from taxi_driver_metrics.common.models.action import SendPushAction
from taxi_driver_metrics.common.models.action import WrongCodeError

TIMESTAMP = datetime.datetime.utcnow().replace(microsecond=0)

ORDER_ID = 'df308741efd553b6b97416880b6ac8d8'
UDID = '5b05621ee6c22ea2654849c0'


@pytest.mark.filldb()
@pytest.mark.translations(
    taximeter_messages={
        'driverpush.DriverMessageReceivedMessage': {
            'ru': 'Сообщение пришло',
            'fr': 'Meesagous recifed',
            'en': 'Message received',
        },
        'driverpush.DriverMessageReceivedTitle': {
            'ru': 'Заголовок',
            'fr': 'Teetle',
            'en': 'Title',
        },
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': True}},
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': False}},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'event, code, tanker_key_template, exception, voice_over',
    (
        (
            {
                'v': 2,
                'timestamp': str(TIMESTAMP),
                'handler': 'complete',
                'order_id': ORDER_ID,
                'reason_code': None,
                'reason': None,
                'update_index': 2,
                'udid': UDID,
                'candidate_index': 0,
                'driver_id': 'testdbid_testuuid',
                'license': '2',
                'zone': 'spb',
                'dp_values': {},
            },
            100,
            'driverpush.DriverMessageReceived',
            None,
            True,
        ),
        (
            {
                'v': 2,
                'timestamp': str(TIMESTAMP),
                'handler': 'complete',
                'order_id': ORDER_ID,
                'reason_code': None,
                'reason': None,
                'update_index': 2,
                'udid': UDID,
                'candidate_index': 0,
                'driver_id': 'testdbid_testuuid',
                'license': '2',
                'zone': 'spb',
                'dp_values': {},
            },
            DRIVER_CHECK_CODE,
            'driverpush.DriverMessageReceived',
            None,
            False,
        ),
        (
            {
                'v': 2,
                'timestamp': str(TIMESTAMP),
                'handler': 'complete',
                'order_id': ORDER_ID,
                'reason_code': None,
                'reason': None,
                'update_index': 2,
                'udid': UDID,
                'candidate_index': 0,
                'driver_id': 'testdbid_testuuid',
                'license': '2',
                'zone': 'spb',
                'dp_values': {},
            },
            100,
            'driverpush.fake',
            InvalidTankerKeyError,
            False,
        ),
        (
            {
                'v': 2,
                'timestamp': str(TIMESTAMP),
                'handler': 'complete',
                'order_id': ORDER_ID,
                'reason_code': None,
                'reason': None,
                'update_index': 2,
                'udid': UDID,
                'candidate_index': 0,
                'driver_id': 'testdbid_testuuid',
                'license': '2',
                'zone': 'spb',
                'dp_values': {},
            },
            'fake',
            'driverpush.DriverMessageReceived',
            WrongCodeError,
            False,
        ),
    ),
)
async def test_send_push_action(
        stq3_context,
        patch,
        event,
        code,
        tanker_key_template,
        exception,
        voice_over,
        order_core_mock,
):
    #  TODO: move to mockserver
    @patch('generated.clients.client_notify.ClientNotifyClient.v2_push_post')
    async def patch_send(*args, body, **kwargs):
        return body

    tst_rule = Rule(
        name='a_rule',
        zone='ZONE',
        additional_params={
            'events_period_sec': 3600,
            'events_to_trigger_cnt': 1,
        },
        events=[],
        actions=[],
        disabled=False,
    )

    event = await Events.OrderEvent.make_from_raw_event(
        stq3_context, order_id=ORDER_ID, event=event,
    )

    send_action = SendPushAction(
        stq3_context,
        event=event,
        rule=tst_rule,
        code=code,
        keyset='taximeter_messages',
        tanker_key_template=tanker_key_template,
        raise_error=True,
        voice_over=voice_over,
    )
    journal = ActionJournal()

    if not exception:
        await journal.do_action(action=send_action)
        assert len(journal.actions) == 1
        pushes = journal.actions[RuleType.PUSH]
        assert len(pushes) == 1
        data = pushes[0].action
        assert data._code == code  # pylint: disable=protected-access
    else:
        with pytest.raises(exception):
            await journal.do_action(action=send_action)
        return

    if code != DRIVER_CHECK_CODE:
        message = {
            'key': f'{tanker_key_template}Message',
            'keyset': 'taximeter_messages',
        }
        title = {
            'key': f'{tanker_key_template}Title',
            'keyset': 'taximeter_messages',
        }
    else:
        message = None
        title = ''

    calls = patch_send.calls.copy()

    expected_flags = ['fullscreen']
    if voice_over:
        expected_flags.append('voiceover')
    assert calls[0]['body'].serialize() == {
        'client_id': (
            'd4158ba9e98c4b0882c4157782e0237d-'
            '09e3f01aa64759cf24cd87f8df36c0cb'
        ),
        'data': {'code': code, 'flags': expected_flags},
        'intent': 'MessageNew',
        'notification': {'text': message, 'title': title} if message else {},
        'service': 'taximeter',
    }

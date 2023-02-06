import pytest

from tests_ivr_dispatcher import utils


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.filldb(ivr_disp_order_stats='already_filled')
@pytest.mark.now('2019-01-01T00:00:00')
async def test_ivr_sms_sending(
        stq_runner, taxi_ivr_dispatcher, mock_ucommunications, stq,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_sms_sending.call(
        task_id=utils.DEFAULT_SESSION_ID,
        kwargs={
            'sms_id': utils.DEFAULT_SESSION_ID,
            'text': 'text',
            'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
            'created_at': '2019-01-01T00:00:00.000Z',
            'consumer': 'some_worker',
            'sms_type': 'new_cool_sms',
            'ivr_application': utils.DEFAULT_APPLICATION,
            'order_id': utils.DEFAULT_ORDER_ID,
        },
    )
    assert mock_ucommunications.send_sms.times_called == 1
    request = mock_ucommunications.send_sms.next_call()['request']
    assert request.json['meta']['order_id'] == utils.DEFAULT_ORDER_ID


@pytest.mark.config(IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS)
@pytest.mark.filldb(ivr_disp_order_stats='already_filled')
@pytest.mark.now('2019-01-01T00:00:00')
async def test_ivr_sms_sending_cannot_send(
        stq_runner, taxi_ivr_dispatcher, mockserver, stq,
):
    @mockserver.json_handler('/ucommunications/user/sms/send', prefix=True)
    async def _send_sms(request):
        return mockserver.make_response(
            status=500,
            json={'message': 'ERROR', 'code': '500', 'status': 'error'},
        )

    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_sms_sending.call(
        task_id=utils.DEFAULT_SESSION_ID,
        kwargs={
            'sms_id': utils.DEFAULT_SESSION_ID,
            'text': 'text',
            'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
            'created_at': '2019-01-01T00:00:00.000Z',
            'consumer': 'some_worker',
            'sms_type': 'new_cool_sms',
            'ivr_application': utils.DEFAULT_APPLICATION,
            'order_id': utils.DEFAULT_ORDER_ID,
        },
    )
    assert _send_sms.times_called
    assert stq.ivr_sms_sending.times_called == 1


@pytest.mark.config(
    IVR_DISPATCHER_SMS_SENDING_SETTINGS={
        '__default__': {
            'max_attempts': 1,
            'sleep_period': 1,
            'hanged_cutoff': 30,
            'eta': 0,
        },
    },
    IVR_SETTINGS=utils.DEFAULT_IVR_SETTINGS,
)
@pytest.mark.now('2019-01-01T00:00:31')
@pytest.mark.filldb(ivr_disp_order_stats='already_filled')
async def test_ivr_sms_sending_hanged(
        stq_runner, taxi_ivr_dispatcher, mock_ucommunications, stq,
):
    await taxi_ivr_dispatcher.invalidate_caches()
    await stq_runner.ivr_sms_sending.call(
        task_id=utils.DEFAULT_SESSION_ID,
        kwargs={
            'sms_id': utils.DEFAULT_SESSION_ID,
            'text': 'text',
            'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
            'created_at': '2019-01-01T00:00:00.000Z',
            'consumer': 'some_worker',
            'sms_type': 'new_cool_sms',
            'ivr_application': utils.DEFAULT_APPLICATION,
            'order_id': utils.DEFAULT_ORDER_ID,
        },
    )
    assert not mock_ucommunications.send_sms.times_called

    await stq_runner.ivr_sms_sending.call(
        task_id=utils.DEFAULT_SESSION_ID,
        kwargs={
            'sms_id': utils.DEFAULT_SESSION_ID,
            'text': 'text',
            'personal_phone_id': utils.DEFAULT_PERSONAL_PHONE_ID,
            'created_at': '2019-01-01T00:00:01.000Z',
            'consumer': 'some_worker',
            'sms_type': 'new_cool_sms',
            'ivr_application': utils.DEFAULT_APPLICATION,
            'order_id': utils.DEFAULT_ORDER_ID,
        },
    )
    assert mock_ucommunications.send_sms.times_called == 1

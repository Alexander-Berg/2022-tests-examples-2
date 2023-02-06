import datetime

import pytest


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/user_phones/by-natural-id')
    def _phones_retrieve(request):
        return {
            'id': '557f191e810c19729de860ea',
            'phone': '+70001112233',
            'personal_phone_id': '775f191e810c19729de860ea',
            'stat': {
                'big_first_discounts': 10,
                'complete': 200,
                'complete_card': 180,
                'complete_apple': 2,
                'complete_google': 14,
                'fake': 0,
                'total': 222,
            },
            'is_loyal': True,
            'is_yandex_staff': True,
            'is_taxi_staff': True,
            'type': 'yandex',
        }


def _check_fallback_queue_full(db):
    default_sms_ttl = 48 * 60 * 60
    today = datetime.datetime(2019, 10, 11, 12, 13, 14)
    max_sms_processing_dttm = today + datetime.timedelta(days=3)

    items = sorted(
        list(db.sms_fallback_queue.find({}, {'_id': False})),
        key=lambda item: item['payload']['recipient_type'],
    )
    assert len(items) == 3

    for item in items:
        del item['payload']['id']

    assert items == [
        {
            'created': today,
            'delete_after': max_sms_processing_dttm,
            'ttl': default_sms_ttl,
            'payload': {
                'intent': 'greeting',
                'mask_text': False,
                'phone': '+70001112233',
                'phone_id': '557f191e810c19729de860ea',
                'provider': 'yasms',
                'recipient_id': {
                    'park_id': 'PARK_ID',
                    'driver_profile_id': 'DRIVER_ID',
                },
                'recipient_type': 'driver',
                'text': 'Добрый день!',
            },
        },
        {
            'created': today,
            'delete_after': max_sms_processing_dttm,
            'ttl': default_sms_ttl,
            'payload': {
                'intent': 'greeting',
                'mask_text': False,
                'phone': '+70001112233',
                'phone_id': '557f191e810c19729de860ea',
                'provider': 'yasms',
                'recipient_type': 'general',
                'text': 'Добрый день!',
            },
        },
        {
            'created': today,
            'delete_after': max_sms_processing_dttm,
            'ttl': default_sms_ttl,
            'payload': {
                'intent': 'info',
                'mask_text': False,
                'phone': '+70001112233',
                'phone_id': '775f191e810c19729de860ea',
                'provider': 'infobip',
                'recipient_id': {'user_id': '557f191e810c19729de860ea'},
                'recipient_type': 'user',
                'text': 'Информационное сообщение',
            },
        },
    ]


@pytest.mark.now('2019-10-11T12:13:14Z')
@pytest.mark.config(
    COMMUNICATIONS_SMS_FALLBACK_QUEUE_ENABLED=True,
    COMMUNICATIONS_SMS_INFOBIP_RETRIES=1,
    COMMUNICATIONS_PASSPORT_YASMS_RETRIES=1,
)
async def test_fallback_queue_add_task(
        taxi_ucommunications,
        mockserver,
        mock_personal,
        mock_user_api,
        load_json,
        stq,
        stq_runner,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms')
    async def mock_yasms_timeout(request):
        raise mockserver.TimeoutError()

    response = await taxi_ucommunications.post(
        'driver/sms/send',
        json={
            'park_id': 'PARK_ID',
            'driver_id': 'DRIVER_ID',
            'text': 'Добрый день!',
            'intent': 'custom_ttl',
        },
    )
    assert response.status_code == 200
    assert mock_yasms_timeout.times_called > 0

    assert stq.sms_fallback_queue.times_called == 1
    task_info = stq.sms_fallback_queue.next_call()

    ethalon_task_info = load_json('sms_fallback_queue_task.json')
    ethalon_task_info['id'] = task_info['id']
    ethalon_task_info['kwargs']['payload']['id'] = task_info['kwargs'][
        'payload'
    ]['id']
    ethalon_task_info['kwargs']['log_extra']['_link'] = task_info['kwargs'][
        'log_extra'
    ]['_link']

    assert task_info == ethalon_task_info


@pytest.mark.now('2019-10-11T12:13:14Z')
@pytest.mark.config(
    COMMUNICATIONS_SMS_FALLBACK_QUEUE_ENABLED=True,
    COMMUNICATIONS_SMS_INFOBIP_RETRIES=1,
    COMMUNICATIONS_PASSPORT_YASMS_RETRIES=1,
)
async def test_fallback_queue_perform_task(
        taxi_ucommunications,
        mockserver,
        mock_personal,
        mock_user_api,
        load_json,
        stq_runner,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms')
    async def mock_yasms_ok(request):
        return mockserver.make_response(
            '<doc><message-sent id="127000000003456" /></doc>', 200,
        )

    task_info = load_json('sms_fallback_queue_task.json')

    await stq_runner.sms_fallback_queue.call(
        task_id=task_info['id'], kwargs=task_info['kwargs'],
    )

    assert mock_yasms_ok.times_called == 1


@pytest.mark.now('2019-10-11T12:13:14Z')
@pytest.mark.config(
    COMMUNICATIONS_SMS_FALLBACK_QUEUE_ENABLED=True,
    COMMUNICATIONS_SMS_INFOBIP_RETRIES=1,
    COMMUNICATIONS_PASSPORT_YASMS_RETRIES=1,
)
async def test_fallback_queue_reshedule_task(
        taxi_ucommunications,
        mockserver,
        mock_personal,
        mock_user_api,
        load_json,
        stq_runner,
        testpoint,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms')
    async def mock_yasms_timeout(request):
        raise mockserver.TimeoutError()

    @testpoint('sms_fallback_queue_reshedule')
    def sms_fallback_queue_reshedule(data):
        pass

    task_info = load_json('sms_fallback_queue_task.json')

    await stq_runner.sms_fallback_queue.call(
        task_id=task_info['id'], kwargs=task_info['kwargs'], expect_fail=True,
    )

    assert mock_yasms_timeout.times_called == 1
    assert sms_fallback_queue_reshedule.times_called == 1


@pytest.mark.now('2019-10-11T14:13:14Z')
@pytest.mark.config(
    COMMUNICATIONS_SMS_FALLBACK_QUEUE_ENABLED=True,
    COMMUNICATIONS_SMS_INFOBIP_RETRIES=1,
    COMMUNICATIONS_PASSPORT_YASMS_RETRIES=1,
)
async def test_fallback_queue_too_late(
        taxi_ucommunications,
        mockserver,
        mock_personal,
        mock_user_api,
        load_json,
        stq_runner,
        testpoint,
):
    @mockserver.json_handler('/sms-intents-admin/v1/internal/dump')
    def _dump(request):
        return load_json('sms_intents.json')

    @mockserver.json_handler('/yasms/sendsms')
    async def mock_yasms_timeout(request):
        raise mockserver.TimeoutError()

    @testpoint('sms_fallback_queue_too_late')
    def sms_fallback_queue_too_late(data):
        pass

    task_info = load_json('sms_fallback_queue_task.json')

    await stq_runner.sms_fallback_queue.call(
        task_id=task_info['id'], kwargs=task_info['kwargs'],
    )

    assert mock_yasms_timeout.times_called == 0
    assert sms_fallback_queue_too_late.times_called == 1

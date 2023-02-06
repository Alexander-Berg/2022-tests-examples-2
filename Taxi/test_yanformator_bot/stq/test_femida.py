import datetime

import pytest
import pytz

TIMEZONE = pytz.timezone('Europe/Moscow')
UTCNOW_STR = '2021-04-12T10:00:19Z'
UTCNOW = datetime.datetime.strptime(UTCNOW_STR, '%Y-%m-%dT%H:%M:%SZ')
NOW = TIMEZONE.fromutc(UTCNOW)


@pytest.mark.now(UTCNOW_STR)
@pytest.mark.config(
    YANFORMATOR_BOT_SETTINGS={
        'task_retry_count': 1,
        'task_delay': 10,
        'max_summary_length': 100,
        'max_notify_length': 4000,
    },
    YANFORMATOR_BOT_FEMIDA_NOTIFICATION_SETTINGS={
        'vacancy_to_tg': [
            {'vacancy_ids': ['999999'], 'telegram_chats': ['10012341234']},
        ],
        'tasks_period': 30,
    },
)
async def test_femida(
        mockserver, testpoint, stq_runner, load_json, taxi_config, redis_store,
):
    @testpoint('messages')
    async def _get_messages(data):
        return data

    @mockserver.json_handler('/femida/api/applications/')
    def _applications(request):
        return load_json('applications.json')

    @mockserver.json_handler('/femida/api/applications/111111/')
    def _application(request):
        return load_json('application.json')

    @mockserver.json_handler('/femida/api/considerations/555555/')
    def _considerations(request):
        return load_json('consideration.json')

    @mockserver.json_handler(
        '/telegram/bot666666666:AAAAAAAAAA_WWWWWWWWWWWWWWWWWWWWWWWW'
        '/sendMessage',
    )
    def _telegram(request):
        assert request.json['text'] == load_json('message.json')[0]
        return {'ok': True}

    redis_store.sadd('femida:notifed_candidates', '666666_777777')

    await stq_runner.yanformator_bot_femida_applications.call(
        task_id='femida_applications', args=[],
    )

    assert redis_store.smembers('femida:notifed_candidates') == {
        b'666666_777777',
        b'111111_222222',
    }

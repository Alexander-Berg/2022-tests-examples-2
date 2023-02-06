import pytest

from tests_grocery_performer_communications import constants as const

INTENT = 'test_push_notification'


@pytest.mark.experiments3(filename='experiments3.json')
async def test_push_notification_success(stq_runner, mockserver, testpoint):
    # For contractor-locale library
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_driver_profiles_driver_app_profiles_retrieve(request):
        return {
            'profiles': [
                {
                    'data': {'locale': 'ru'},
                    'park_driver_profile_id': const.PERFORMER_ID,
                },
            ],
        }

    # client-push mock
    @mockserver.json_handler('client-notify/v2/push')
    def client_notify(request):
        assert request.headers['X-Idempotency-Token'] == const.TASK_ID
        assert request.json == {
            'client_id': f'{const.PARK_ID}-{const.PROFILE_ID}',
            'intent': 'test_push_notification',
            'locale': 'ru',
            'notification': {
                'text': {
                    'keyset': 'grocery_performer_communications',
                    'key': 'text_tanker_key',
                    'params': {'str_var': 'str_text'},
                },
                'title': {
                    'keyset': 'grocery_performer_communications',
                    'key': 'title_tanker_key',
                    'params': {'str_var': 'str_title'},
                },
                'link': 'link_url',
                'sound': 'sound_str',
            },
            'service': 'taximeter',
        }
        return mockserver.make_response(
            status=200, json={'notification_id': '1'},
        )

    @testpoint('push_notification_task_finished_success')
    def task_finished(params):
        pass

    await stq_runner.grocery_performer_communications_push_notification.call(
        task_id=const.TASK_ID,
        args=[
            const.PERFORMER_ID,
            INTENT,
            {
                'key': 'title_tanker_key',
                'args': [
                    {
                        'name': 'str_var',
                        'value': {'value': 'str_title', 'type': 'string'},
                    },
                ],
            },
            {
                'key': 'text_tanker_key',
                'args': [
                    {
                        'name': 'str_var',
                        'value': {'value': 'str_text', 'type': 'string'},
                    },
                ],
            },
            'link_url',
            'sound_str',
        ],
    )

    assert client_notify.times_called == 1
    assert task_finished.times_called == 1

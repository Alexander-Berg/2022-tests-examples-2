import pytest


@pytest.fixture(name='mock_ucommunications_push')
def _mock_ucommunications_push(
        mockserver, build_ucommunications_body, get_default_order_id,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _push(request):
        context.times_called += 1
        assert request.json == context.expected_request
        return {}

    class Context:
        def __init__(self):
            self.expected_request = None
            self.handler = _push
            self.times_called = 0

    context = Context()
    return context


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_info(request):
        return {
            'id': 'some_user_id',
            'yandex_uid': request.json['yandex_uid'],
            'token_only': True,
            'authorized': True,
            'application': 'iphone',
            'application_version': '4.90.0',
        }


async def test_phoenix_push(
        mock_ucommunications_push, mock_user_api, stq_runner,
):
    mock_ucommunications_push.expected_request = {
        'data': {
            'repack': {
                'apns': {
                    'aps': {
                        'content-available': 1,
                        'alert': {
                            'title': 'Владелец бизнеса',
                            'body': 'Вам доступна корпоративная карта в Go',
                        },
                    },
                },
                'gcm': {
                    'notification': {
                        'title': 'Владелец бизнеса',
                        'body': 'Вам доступна корпоративная карта в Go',
                    },
                },
                'hms': {
                    'notification': {
                        'title': 'Владелец бизнеса',
                        'body': 'Вам доступна корпоративная карта в Go',
                    },
                },
            },
            'payload': {
                'notification': {
                    'title': 'Владелец бизнеса',
                    'body': 'Вам доступна корпоративная карта в Go',
                },
            },
        },
        'ttl': 1000,
        'user': 'some_user_id',
        'intent': 'phoenix_notifications_intent',
    }

    await stq_runner.cargo_c2c_phoenix_notifications.call(
        task_id='1', args=['some_yandex_uid', 'owner', 'ru'],
    )

    assert mock_ucommunications_push.times_called == 1

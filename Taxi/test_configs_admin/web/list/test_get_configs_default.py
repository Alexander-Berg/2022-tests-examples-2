import pytest


@pytest.mark.config(TVM_ENABLED=True)
async def test_get_defaults(web_app_client, patcher_tvm_ticket_check):
    patcher_tvm_ticket_check('configs-admin')
    response = await web_app_client.get('/v1/configs/defaults/')
    assert response.status == 200

    result = await response.json()
    assert result == {
        'commit': '4805804d8b5ce277903492c549055f4b5a86ed0a',
        'defaults': {
            'BILLING_REPORTS_YT_INPUT_ROW_LIMIT': 100000000,
            'CONFIG_WITH_BLOCKED_UPDATE_MAIN_VALUE': {'value': 90},
            'DEVICENOTIFY_USER_TTL': 90,
            'FRIEND_BRANDS': [['yataxi', 'yango']],
            'SOME_CONFIG_WITH_DEFINITIONS': {'value': 90},
            'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES': ['YANDEXTAXI'],
        },
    }

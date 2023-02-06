import pytest


@pytest.mark.parametrize(
    'data,expected_result,expected_status,expected_error_message',
    [
        pytest.param(
            {'name': 'Me_CoNFIg'},
            [
                {
                    'description': 'Some config with definitions',
                    'group': 'devicenotify',
                    'name': 'SOME_CONFIG_BY_SERVICE',
                },
                {
                    'description': 'Some config with definitions',
                    'group': 'devicenotify',
                    'name': 'SOME_CONFIG_BY_SERVICE_DISALLOWED',
                },
            ],
            200,
            None,
        ),
        pytest.param(
            {
                'name': 'Me_CoNFIg',
                'last_viewed_config': 'SOME_CONFIG_BY_SERVICE',
            },
            [
                {
                    'description': 'Some config with definitions',
                    'group': 'devicenotify',
                    'name': 'SOME_CONFIG_BY_SERVICE_DISALLOWED',
                },
            ],
            200,
            None,
        ),
        pytest.param({'name': 'mMe_CoNFIg'}, [], 200, None),
        pytest.param(
            {'groups': ['devicenotify'], 'limit': 2},
            [
                {
                    'description': 'Some config with definitions',
                    'group': 'devicenotify',
                    'name': 'BLOCKED_CONFIG',
                },
                {
                    'description': 'Some config',
                    'group': 'devicenotify',
                    'name': 'DEVICENOTIFY_USER_TTL',
                },
            ],
            200,
            None,
        ),
        pytest.param(
            {'tags': ['is_technical', 'group']},
            [
                {
                    'description': 'Get group',
                    'group': 'new_group',
                    'name': 'GET_GROUP',
                },
            ],
            200,
            None,
        ),
    ],
)
@pytest.mark.filldb(uconfigs_meta='default')
async def test_get_configs_list(
        web_app_client,
        patcher_tvm_ticket_check,
        data,
        expected_result,
        expected_status,
        expected_error_message,
):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        '/v1/configs/list/',
        json=data,
        headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == 200
    result = await response.json()
    assert result == expected_result

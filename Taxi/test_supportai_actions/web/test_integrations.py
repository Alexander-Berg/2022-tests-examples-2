import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_actions', files=['default.sql']),
]


async def test_get_integrations(web_app_client, mockserver):
    response = await web_app_client.get(
        '/v1/integrations?project_slug=test_project&user_id=123',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['integrations']) == 1
    integration = response_json['integrations'][0]
    assert integration['title'] == 'Выписать промокод'


async def test_create_integration(web_app_client, mockserver):
    response = await web_app_client.post(
        '/v1/integrations?project_slug=test_project&user_id=123',
        json={
            'title': 'Выписать промокод 2.0',
            'project_slug': 'test_project',
            'is_active': True,
            'input_features': ['order_id'],
            'integration_type': 'change',
            'output_features': ['promocode'],
            'api_parameters': [
                {'title': 'Размер', 'slug': 'size', 'type': 'int'},
            ],
            'api_request': {
                'url': 'https://test_project.dev/api/promo_1/{some}',
                'method': 'POST',
                'body': '{ \'size\': {{size}}, \'order_id\': {{order_id}} }',
                'authorization': {
                    'login': 'some_awesome_login',
                    'password': '******',
                    'encoding': 'latin1',
                },
                'response_mapping': [
                    {'key': 'promocode', 'value': '$.promocode'},
                ],
            },
        },
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/integrations?project_slug=test_project&user_id=123',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['integrations']) == 2


async def test_update_integration(web_app_client, mockserver):
    response = await web_app_client.put(
        '/v1/integrations/1?project_slug=test_project&user_id=123',
        json={
            'title': 'Выписать промокод 2.0',
            'description': 'give promocode',
            'is_active': False,
            'project_slug': 'test_project',
            'integration_type': 'change',
            'input_features': ['order_id'],
            'output_features': ['promocode'],
            'api_parameters': [
                {'title': 'Размер', 'slug': 'size', 'type': 'int'},
            ],
            'api_request': {
                'url': 'https://test_project.dev/api/promo_2',
                'method': 'POST',
                'body': '{ \'size\': {{size}}, \'order_id\': {{order_id}} }',
                'authorization': {'service': 'supportai'},
                'response_mapping': [
                    {'key': 'promocode', 'value': '$.promocode'},
                ],
            },
        },
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/integrations?project_slug=test_project&user_id=123',
    )
    assert response.status == 200
    response_json = await response.json()
    assert len(response_json['integrations']) == 1
    integration = response_json['integrations'][0]
    assert integration['title'] == 'Выписать промокод 2.0'
    assert not integration['is_active']
    assert 'description' in integration

    assert (
        integration['api_request']['authorization']['service'] == 'supportai'
    )


async def test_delete_integration(web_app_client):
    response = await web_app_client.delete(
        '/v1/integrations/1?project_slug=test_project&user_id=123',
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/integrations?project_slug=test_project&user_id=123',
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['integrations']

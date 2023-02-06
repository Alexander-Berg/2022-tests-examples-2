import pytest


@pytest.mark.translations(
    client_messages={
        'shared_payments.default_account_name_family': {
            'ru': 'Семейный аккаунт',
        },
    },
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_simple(mock_all_api, web_app_client, load_json):
    response = await web_app_client.get('/v1/admin/detail?account_id=acc1')
    assert response.status == 200
    content = await response.json()
    content.pop('updated_at')
    expected_response = load_json('expected_response.json')
    assert content == expected_response

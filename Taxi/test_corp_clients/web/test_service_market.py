import pytest


@pytest.mark.parametrize(
    ['client_id', 'request_body', 'expected_code'],
    [
        pytest.param(
            'client_id_1',
            {'is_active': False, 'is_visible': False},
            200,
            id='success_path',
        ),
        pytest.param(
            'client_id_1',
            {'is_active': False, 'is_visible': True},
            400,
            id='validation_error',
        ),
        pytest.param(
            'non-existent-client',
            {'is_active': False, 'is_visible': False},
            400,
            id='non-existent-client',
        ),
    ],
)
async def test_service_market_update(
        web_app_client,
        db,
        corp_billing_mock,
        client_id,
        request_body,
        expected_code,
):
    projection = {'created': False, 'updated': False, 'updated_at': False}

    old_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_1'}, projection=projection,
    )

    expected_client = old_client
    expected_client['services']['market'] = request_body

    response = await web_app_client.patch(
        '/v1/services/market',
        params={'client_id': client_id},
        json=request_body,
    )

    assert response.status == expected_code
    if response.status == 200:
        client = await db.secondary.corp_clients.find_one(
            {'_id': 'client_id_1'}, projection=projection,
        )
        assert client == expected_client

import pytest

from test_taxi_protocol import plugins as conftest


@pytest.mark.parametrize(
    'uid,expected_code,expected_result',
    [
        ('123', 200, {'is_vip': True}),
        ('1234', 200, {'is_vip': False}),
        ('12346', 401, {'error': {'code': 'MISSING_USER'}}),
    ],
)
async def test_is_vip_user(
        monkeypatch,
        protocol_client,
        protocol_app,
        mock_get_users,
        uid,
        expected_code,
        expected_result,
):
    monkeypatch.setattr(
        protocol_app, 'passport', conftest.MockPassportClient(),
    )
    headers = {'X-Real-IP': '1.1.1.1', 'Authorization': 'Bearer %s' % uid}

    response = await protocol_client.get('/1.0/is_vip_user', headers=headers)

    assert response.status == expected_code
    assert await response.json() == expected_result

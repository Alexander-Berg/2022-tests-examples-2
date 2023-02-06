import pytest


@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[{'name': 'phone', 'type': 'string', 'value': '+79219201566'}],
    value='taxi',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[{'name': 'phone', 'type': 'string', 'value': '+79219201666'}],
    value='yandex',
)
@pytest.mark.client_experiments3(
    consumer='example_service_consumer',
    experiment_name='phone_type',
    args=[{'name': 'phone', 'type': 'string', 'value': '+79219202666'}],
    value='regular',
)
@pytest.mark.usefixtures('territories_mock')
@pytest.mark.parametrize(
    'phone,answer,code,phones',
    [
        (
            None,
            ['taxi', 'yandex', 'regular', 'unknown'],
            200,
            ['79219201566', '79219201666', '79219202666', '7'],
        ),
    ],
)
async def test_who_are_you_all(phone, answer, code, phones, web_app_client):
    response = await web_app_client.get(
        '/who_you_all', params={'phones': ','.join(phones)},
    )
    assert response.status == 200
    assert (await response.json()) == answer

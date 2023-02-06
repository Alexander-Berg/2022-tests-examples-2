import pytest

RU_HEADERS = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'ru-RU'}


@pytest.mark.parametrize(
    'body,headers,status,response_data',
    [
        ({}, RU_HEADERS, 400, ''),
        (
            {'key': 'taxi', 'name': 'Taxi category'},
            RU_HEADERS,
            201,
            {'key': 'taxi', 'name': 'Taxi category'},
        ),
        ({'key': 'dev', 'name': 'Dev category'}, RU_HEADERS, 409, {}),
    ],
)
async def test_create_category(
        web_app_client, body, headers, status, response_data,
):
    response = await web_app_client.post(
        '/channel_category/create', headers=headers, json=body,
    )
    assert response.status == status
    if response.status == 201:
        content = await response.json()
        assert content == response_data

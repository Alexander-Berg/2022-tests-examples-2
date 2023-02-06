import aiohttp.web
import pytest


@pytest.mark.translations(
    opteum_support_chat_form={
        'base.callback.inputs.park_contact.title': {
            'ru': 'Контакт таксопарка',
        },
        'base.callback.topic.title': {'ru': 'Заказать обратный звонок'},
    },
)
async def test_success(
        web_app_client, headers, mock_fleet_parks, load_json, patch,
):
    stub = load_json('success.json')

    @mock_fleet_parks('/v1/parks/contacts')
    async def _contacts(request):
        return aiohttp.web.json_response(stub['fleet_parks_response'])

    response = await web_app_client.get(
        '/support-chat-api/v1/callback/contacts/park', headers=headers,
    )

    assert response.status == 200
    data = await response.json()
    assert data == stub['service_response']

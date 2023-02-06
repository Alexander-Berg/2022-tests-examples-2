from aiohttp import web
import pytest

from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _(_):
        return {'id': 'personal_phone_id_value', 'value': '+79991234567'}

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve_bulk')
    async def _(request):
        assert request.json['items'][0]['type'] == 'yandex'
        return web.json_response(
            data={
                'items': [
                    {
                        'id': 'phone_id',
                        'phone': '+79991234567',
                        'type': 'type',
                    },
                ],
            },
        )

    @mockserver.json_handler('/user-api/users/search')
    async def _(_):
        return web.json_response(
            data={
                'items': [
                    {
                        'id': 'user_id',
                        'yandex_uid': 'yandex_uid',
                        'phone_id': 'phone_id',
                        'sourceid': 'call_center',
                    },
                ],
            },
        )


@pytest.fixture(name='default_state')
def _get_default_state():
    return state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'callcenter_number', 'value': '+799976543321'},
                {'key': 'abonent_number', 'value': '+79991234567'},
                {
                    'key': 'last_user_message',
                    'value': 'this text just should be nonempty',
                },
            ],
        ),
    )

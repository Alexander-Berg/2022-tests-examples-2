from testsuite.utils import http

from fleet_rent.entities import park_user
from fleet_rent.generated.web import web_context as context_module


async def test_driver_info_service(
        web_context: context_module.Context, mock_dispatcher_access_control,
):
    @mock_dispatcher_access_control('/v1/parks/users/list')
    async def _retrieve(request: http.Request):
        assert request.json == {
            'query': {'park': {'id': 'park_id'}, 'user': {'is_enabled': True}},
            'offset': 0,
        }
        return {
            'users': [
                {
                    'id': 'user_id',
                    'park_id': 'park_id',
                    'display_name': 'name',
                    'email': 'email',
                    'is_superuser': True,
                    'is_confirmed': True,
                    'is_enabled': True,
                    'is_usage_consent_accepted': True,
                },
            ],
            'offset': 0,
        }

    user = await web_context.external_access.park_users.find_park_owner(
        park_id='park_id',
    )

    assert user == park_user.ParkUser(
        id='user_id',
        park_id='park_id',
        name='name',
        email='email',
        is_superuser=True,
    )

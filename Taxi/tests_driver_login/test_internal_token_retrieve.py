import enum
import hashlib

import pytest

ENDPOINT = '/internal/v1/tokens/retrieve'

# Generated using `tvmknife unittest service -s 512 -d 1024`
SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIgAQQgAg:'
    'KG0QAiKznPbfj6kOJggUxoy-Xwkf0BbzOmf'
    'Ywq70_ddeu0ev6ivbI7IeFcqKOD6xLhzK_'
    'k9zX0udKdsOgVvYw4xOu58_6bJHjayyhJQNvr7ExJiYkMAc37vXkVNP'
    '-BSkx6xhTFVGiZCWGMQEiatQ_AUQrTrTwfERcOVk77fuJik'
)

PARK_ID = 'halopark'
DRIVER_PROFILE_ID = 'seser'
PHONE = '+79997776655'
PHONE_PD_ID = f'{PHONE}_id'
SECRET = 'DRIVER_LOGIN_SECRET'

INVALID_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIvAkQgAg:'
    'BGk7sp8bg9EUUlSN1nEW2VRqVRMLuFOdfuCeD4V0p9KdH49fbMjD5n7hgN'
    '-g0GYsRvPjDsY1SL8b1Ke5E8lU6K61mNxj-'
    'goK_XybkBxgzz9KBDgSjRzG32tOsO7stPj9EscH4-'
    'j4NV2iIgXri8QGQuJwqWiPvPQEpmVZ40GxxA0'
)


def my_hash(key):
    return hashlib.sha256((key + SECRET).encode('utf-8')).hexdigest()


class ResponseType(enum.Enum):
    ALL_OK = 'ALL_OK'
    NOT_FOUND = 'NOT_FOUND'
    NO_PHONE = 'NO_PHONE'


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver):
    class Context:
        def __init__(self):
            self.response_type = ResponseType.ALL_OK

        def set_response_type(self, value):
            self.response_type = value

    context = Context()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_driver_profiles_search(request):
        data_dict = {}  # ResponseType.NOT_FOUND
        if context.response_type == ResponseType.ALL_OK:
            data_dict = {'data': {'phone_pd_ids': [{'pd_id': PHONE_PD_ID}]}}
        elif context.response_type == ResponseType.NO_PHONE:
            data_dict = {'data': {'phone_pd_ids': []}}

        return {
            'profiles': [
                {
                    'park_driver_profile_id': f'{PARK_ID}_{DRIVER_PROFILE_ID}',
                    **data_dict,
                },
            ],
        }

    return context


@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_ok(taxi_driver_login, redis_store, driver_profiles):
    response = await taxi_driver_login.post(
        ENDPOINT,
        params={'park_id': PARK_ID, 'driver_profile_id': DRIVER_PROFILE_ID},
        headers={'X-Ya-Service-Ticket': SERVICE_TICKET},
    )
    assert response.status == 200, response.text
    body = response.json()
    assert body['phone'] == PHONE
    stored = redis_store.get('Driver:AuthToken:' + my_hash(body['phone']))
    assert stored == my_hash(body['token']).encode('utf-8')


@pytest.mark.parametrize(
    'service_ticket,park_id,code',
    [(INVALID_SERVICE_TICKET, 'seser', 403), (SERVICE_TICKET, 'seser', 403)],
)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_not_ok(
        taxi_driver_login, driver_profiles, service_ticket, park_id, code,
):
    response = await taxi_driver_login.post(
        ENDPOINT,
        params={'park_id': park_id, 'driver_profile_id': DRIVER_PROFILE_ID},
        headers={'X-Ya-Service-Ticket': service_ticket},
    )
    assert response.status == code, response.text


@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_not_found(taxi_driver_login, driver_profiles):
    driver_profiles.set_response_type(ResponseType.NOT_FOUND)
    response = await taxi_driver_login.post(
        ENDPOINT,
        params={'park_id': PARK_ID, 'driver_profile_id': 'not_found'},
        headers={'X-Ya-Service-Ticket': SERVICE_TICKET},
    )
    assert response.status == 404, response.text


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_tvm_disabled(taxi_driver_login, driver_profiles):
    response = await taxi_driver_login.post(
        ENDPOINT,
        params={'park_id': PARK_ID, 'driver_profile_id': DRIVER_PROFILE_ID},
        headers={'X-Ya-Service-Ticket': SERVICE_TICKET},
    )
    assert response.status == 500, response.text


@pytest.mark.now('2019-04-18T13:10:00.786Z')
async def test_no_phone_in_driver(taxi_driver_login, driver_profiles):
    driver_profiles.set_response_type(ResponseType.NO_PHONE)
    response = await taxi_driver_login.post(
        ENDPOINT,
        params={'park_id': PARK_ID, 'driver_profile_id': DRIVER_PROFILE_ID},
        headers={'X-Ya-Service-Ticket': SERVICE_TICKET},
    )
    assert response.status == 500, response.text

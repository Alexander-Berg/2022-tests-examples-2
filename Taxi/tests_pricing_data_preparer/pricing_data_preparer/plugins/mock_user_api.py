# pylint: disable=redefined-outer-name, import-error
import json

from pricing_extended import mocking_base
import pytest


def is_zuser(user_id):
    return user_id[0] == 'z'


class UserApiContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.phone_error = False
        self.users_error = False
        self.user = {
            'id': 'some_user_id',
            'phone_id': 'PHONE_ID',
            'yandex_uid': 'YANDEX_UID',
            'apns_token': 'APNS_TOKEN',
            'gcm_token': 'GCM_TOKEN',
            'device_id': 'DEVICE_ID',
            'has_ya_plus': False,
            'has_cashback_plus': False,
        }
        self.phone = {
            'id': 'some_phone_id',
            'stat': {
                'big_first_discounts': 0,
                'complete': 1,
                'complete_card': 2,
                'complete_apple': 3,
                'complete_google': 4,
                'total': 5,
                'fake': 6,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'phone': '+78122917953',
            'type': 'PHONE-TYPE',
            'personal_phone_id': 'PERSONAL_PHONE_ID',
            'phone_hash': 'PHONE_HASH',
        }

    def set_yaplus(self, ya_plus):
        self.user['has_ya_plus'] = ya_plus

    def set_cashback_plus(self, cashback_plus):
        self.user['has_cashback_plus'] = cashback_plus

    def set_user_id(self, new_id):
        self.user['id'] = new_id
        self.phone['id'] = new_id

    def set_phone_id(self, new_id):
        self.user['phone_id'] = new_id

    def set_yandex_uid(self, uid):
        self.user['yandex_uid'] = uid

    def check_request(self, data):
        assert 'id' in data
        assert not is_zuser(data['id'])
        assert data['id'] == self.user['id']

    def crack_users(self):
        self.users_error = True

    def crack_phone(self):
        self.phone_error = True


@pytest.fixture
def user_api():
    return UserApiContext()


@pytest.fixture
def mock_user_api_get_users(mockserver, user_api):
    @mockserver.json_handler('/user-api/users/get')
    async def user_api_get_users_handler(request):
        data = json.loads(request.get_data())
        user_api.check_request(data)
        user_api.response = user_api.user
        if user_api.users_error:
            user_api.must_crack()
            user_api.users_error = False
        return user_api.process(mockserver)

    return user_api_get_users_handler


@pytest.fixture
def mock_user_api_get_phones(mockserver, user_api):
    @mockserver.json_handler('/user-api/user_phones/by-natural-id')
    async def user_api_get_phones_handler(request):
        user_api.check_request(request.args)
        user_api.response = user_api.phone
        if user_api.phone_error:
            user_api.must_crack()
            user_api.phone_error = False
        return user_api.process(mockserver)

    return user_api_get_phones_handler

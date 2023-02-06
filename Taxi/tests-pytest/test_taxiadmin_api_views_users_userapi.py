import pytest
import json

from taxi.core import async
from taxi.external import userapi

from django import test as django_test


@pytest.fixture
def mock_user_phones_factory(patch, inject_user_api_token):
    class Factory:
        @staticmethod
        def not_found(phone_id, primary_replica):
            @patch('taxi.external.userapi.get_user_phone')
            @async.inline_callbacks
            def impl(req_id, req_from_master, *args, **kwargs):
                assert req_id == phone_id
                assert req_from_master == primary_replica
                raise userapi.NotFoundError()
            return impl

        @staticmethod
        def predefined(phone_id, primary_replica, phone):
            @patch('taxi.external.userapi.get_user_phone')
            @async.inline_callbacks
            def impl(req_id, req_from_master, *args, **kwargs):
                assert req_id == phone_id
                assert req_from_master == primary_replica
                response = {
                    'id': phone_id,
                    'phone': phone,
                    'type': 'yandex',
                    'personal_phone_id': '123',
                    'created': '2019-02-01T13:00:00+0000',
                    'updated': '2019-02-01T13:00:00+0000',
                    'stat': {
                        'big_first_discounts': 0,
                        'complete': 0,
                        'complete_card': 0,
                        'complete_apple': 0,
                        'complete_google': 0
                    },
                    'is_loyal': False,
                    'is_yandex_staff': False,
                    'is_taxi_staff': False,
                    'was_yauber_migrated': False,
                }
                yield
                async.return_value(response)
            return impl

    return Factory()


@pytest.mark.parametrize(
    'phone,status,body',
    [
        (
            None,
            404,
            {
                'status': 'error',
                'message': 'userapi.get_user_phone not found',
                'code': 'not_found',
            },
        ),
        (
            '+79991112233',
            200,
            [
                {
                    'phone': '+79991112233',
                    'phone_type': 'yandex',
                    'phone_can_be_deleted': True,
                    'uber_id': 'some_uber_id',
                    'user_id': 'some_user_id',
                    'yandex_uid': 'some_yandex_uid',
                    'yandex_uuid': 'some_uuid_enlarged_to_32_symbols',
                    'user_phone_id': '5c1122bfcb688c63c949f557',
                },
            ],
        ),
    ],
    ids=[
        'not found',
        '+79991112233',
    ],
)
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY2=True)
@pytest.mark.asyncenv('blocking')
def test_get_user_info_not_found(
        mock_user_phones_factory,
        phone,
        status,
        body
):
    url = '/api/user_info/get_users_info/?user_id=some_user_id'

    phone_id = '5c1122bfcb688c63c949f557'

    if phone:
        mock_user_phones_factory.predefined(phone_id, True, phone)
    else:
        mock_user_phones_factory.not_found(phone_id, True)

    response = django_test.Client().get(url)
    assert response.status_code == status
    assert json.loads(response.content) == body

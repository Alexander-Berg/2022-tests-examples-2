import copy

import bson
import pytest

from taxi import discovery
from taxi.clients import tvm
from taxi.clients import user_api


@pytest.mark.parametrize('with_tvm', [True, False])
@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
@pytest.mark.config(TVM_RULES=[{'src': 'test-service', 'dst': 'user-api'}])
@pytest.mark.config(TVM_ENABLED=True)
async def test_get_user_phone(
        test_taxi_app,
        mockserver,
        patch,
        unittest_settings,
        db,
        simple_secdist,
        with_tvm,
):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def _get_ticket(*args, **kwargs):
        return 'test_ticket'

    @mockserver.json_handler('/user-api/user_phones/get')
    def _mock_user_api(request):
        assert request.json == {
            'id': '5d1b8b17d9d35f1c264a0687',
            'primary_replica': True,
        }

        if with_tvm:
            assert request.headers['X-Ya-Service-Ticket'] == 'test_ticket'
        else:
            assert request.headers['X-YaTaxi-API-Key'] == 'user_api'

        return {
            'id': '5d1b8b17d9d35f1c264a0687',
            'phone': '+71112223344',
            'type': 'yandex',
            'stat': {},
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_outstaff': True,
            'is_taxi_staff': False,
        }

    secdist = copy.deepcopy(simple_secdist)

    if with_tvm:
        secdist['client_apikeys'].pop('user_api')
        tvm_client = tvm.TVMClient(
            'test-service',
            secdist,
            test_taxi_app.config,
            test_taxi_app.session,
        )
    else:
        tvm_client = None

    user_api_client = user_api.UserApiClient(
        discovery.find_service('user-api').url,
        secdist=secdist,
        config=test_taxi_app.config,
        session=test_taxi_app.session,
        database=db,
        personal_settings=user_api.PersonalSettings(
            source='py3-test-user-api', settings=unittest_settings,
        ),
        tvm_client=tvm_client,
    )

    user_phone = await user_api_client.get_user_phone(
        phone_id='5d1b8b17d9d35f1c264a0687',
        primary_replica=True,
        log_extra={'_link': 'request_id'},
    )

    assert user_phone == {
        '_id': bson.ObjectId('5d1b8b17d9d35f1c264a0687'),
        'phone': '+71112223344',
        'type': 'yandex',
        'stat': {},
        'loyal': False,
        'yandex_staff': False,
        'taxi_outstaff': True,
        'taxi_staff': False,
    }
    assert _mock_user_api.times_called == 1


async def test_get_users(
        test_taxi_app, mockserver, unittest_settings, db, simple_secdist,
):
    @mockserver.json_handler('/user-api/users/get')
    def _mock_user_api(request):
        assert request.json == {
            'id': '5d1b8b17d9d35f1c264a0687',
            'lookup_uber': False,
            'primary_replica': False,
        }
        return {
            'id': '5d1b8b17d9d35f1c264a0687',
            'yandex_uid': 'yandex_uid_1',
            'yandex_uid_type': 'portal',
            'phone_id': 'user_phone_id_1',
            'application': 'iphone',
            'apns_token': 'apns_token_1',
            'gcm_token': 'gcm_token_1',
            'uber_id': 'uber_id_123',
        }

    user_api_client = user_api.UserApiClient(
        discovery.find_service('user-api').url,
        secdist=simple_secdist,
        config=test_taxi_app.config,
        session=test_taxi_app.session,
        database=db,
        personal_settings=user_api.PersonalSettings(
            source='py3-test-user-api', settings=unittest_settings,
        ),
    )

    user = await user_api_client.get_user(
        user_id='5d1b8b17d9d35f1c264a0687', log_extra={'_link': 'request_id'},
    )

    assert user == {
        'id': '5d1b8b17d9d35f1c264a0687',
        'yandex_uid': 'yandex_uid_1',
        'yandex_uid_type': 'portal',
        'phone_id': 'user_phone_id_1',
        'application': 'iphone',
        'apns_token': 'apns_token_1',
        'gcm_token': 'gcm_token_1',
        'uber_id': 'uber_id_123',
    }
    assert _mock_user_api.times_called == 1


async def test_search_users(
        test_taxi_app, mockserver, unittest_settings, db, simple_secdist,
):
    current_request = 0
    requests_count = 10
    bulk_size = 10

    @mockserver.json_handler('/user-api/users/search')
    def _mock_user_api(request):
        nonlocal current_request

        assert request.json['yandex_uids'] == ['1', '2', '3']
        if current_request == 0:
            assert 'cursor' not in request.json
        else:
            assert 'cursor' in request.json

        cursor = request.json.get('cursor', 0)
        response = {
            'items': [{'id': i} for i in range(cursor, cursor + bulk_size)],
        }

        current_request += 1
        if current_request < requests_count:
            response['cursor'] = cursor + bulk_size
        return response

    user_api_client = user_api.UserApiClient(
        discovery.find_service('user-api').url,
        secdist=simple_secdist,
        config=test_taxi_app.config,
        session=test_taxi_app.session,
        database=db,
        personal_settings=user_api.PersonalSettings(
            source='py3-test-user-api', settings=unittest_settings,
        ),
    )

    users = await user_api_client.search_users(
        payload={'yandex_uids': ['1', '2', '3']},
    )

    assert users == [{'id': i} for i in range(requests_count * bulk_size)]
    assert _mock_user_api.times_called == requests_count

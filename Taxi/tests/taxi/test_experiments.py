import bson
import pytest

from taxi import discovery
from taxi import experiments
from taxi.clients import user_api


_USERS_DOCUMENTS = {
    'user1': {
        '_id': 'user1',
        'gcm_token': 'gcm1',
        'phone_id': bson.ObjectId('539eb65be7e5b1f53980dfa8'),
    },
    'user2': {
        '_id': 'user2',
        'apns_token': 'apns2',
        'phone_id': bson.ObjectId('539eb65be7e5b1f53980dfa8'),
    },
    'user4': {'_id': 'user4'},
}


@pytest.fixture
def mongodb_collections():
    return ['static', 'user_phones', 'vip_users']


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'user_id,expected',
    [
        ('user1', ['user1', 'staff', 'all']),
        ('user2', ['staff', 'all']),
        ('user4', ['all']),
        ('unknown', ['all']),
    ],
)
async def test_get_experiments_for_user(
        test_taxi_app,
        db,
        unittest_settings,
        simple_secdist,
        user_id,
        expected,
):
    user_doc = _USERS_DOCUMENTS.get(user_id, {})

    user_api_client = user_api.UserApiClient(
        discovery.find_service('user-api').url,
        secdist=simple_secdist,
        config=test_taxi_app.config,
        session=None,
        database=db,
        personal_settings=user_api.PersonalSettings(
            source='py3-test-experiments', settings=unittest_settings,
        ),
    )

    result = await experiments.get_experiments_for_user(
        db, user_api_client, {}, user_doc,
    )
    assert result == expected


@pytest.mark.config(USER_API_USE_USER_PHONES_RETRIEVAL_PY3=True)
async def test_get_experiments_for_user_user_api(
        test_taxi_app, db, unittest_settings, mockserver, simple_secdist,
):
    user_id = 'user1'
    expected = ['user1', 'staff', 'all']
    user_doc = _USERS_DOCUMENTS.get(user_id, {})

    @mockserver.json_handler('/user-api/user_phones/get')
    def _mock_user_api(request):
        assert request.json == {
            'id': '539eb65be7e5b1f53980dfa8',
            'primary_replica': False,
        }
        return {
            'id': '539eb65be7e5b1f53980dfa8',
            'phone': '+71112223344',
            'type': 'yandex',
            'stat': {},
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }

    user_api_client = user_api.UserApiClient(
        discovery.find_service('user-api').url,
        secdist=simple_secdist,
        config=test_taxi_app.config,
        session=test_taxi_app.session,
        database=db,
        personal_settings=user_api.PersonalSettings(
            source='py3-test-experiments', settings=unittest_settings,
        ),
    )

    result = await experiments.get_experiments_for_user(
        db, user_api_client, {}, user_doc,
    )
    assert result == expected

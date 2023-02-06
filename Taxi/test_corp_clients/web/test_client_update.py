# pylint: disable=redefined-outer-name

import copy
import datetime

import pytest

from taxi.clients import billing_v2

# fmt: off
HEADERS = {
    'X-Yandex-Login': 'login',
    'X-Yandex-UID': '1234567890',
    'X-Real-IP': 'remote_ip',
}
REQUEST = {
    'name': 'name',
    'billing_name': 'OOO',
    'country': 'rus',
    'yandex_login': ' yandex_loGin_1 ',
}

BASE_SERVICES = {
    'taxi': {
        'is_active': True,
        'is_visible': True,
        'comment': 'Держи дверь, стой у входа!',
    },
    'cargo': {
        'is_active': True,
        'is_visible': True,
        'next_day_delivery': True,
    },
    'drive': {
        'is_active': True,
        'is_visible': True,
        'parent_id': 12345,
    },
    'eats': {
        'is_active': True,
        'is_visible': True,
    },
    'eats2': {
        'is_active': True,
        'is_visible': True,
    },
    'market': {
        'is_active': True,
        'is_visible': True,
    },
    'tanker': {
        'is_active': True,
        'is_visible': True,
    },
}

BASE_CLIENT = {
    '_id': 'client_id_1',
    'name': 'name',
    'billing_name': 'OOO',
    'phone': '+79777777777',
    'description': 'corp_client_1 description',
    'country': 'rus',
    'created': datetime.datetime(2021, 7, 1, 10, 0),
    'city': 'Москва',
    'features': [],
    'is_trial': False,
    'email_id': 'email_id_1',
    'billing_id': '100001',
    'yandex_id': 'yandex_uid_1',
    'yandex_login': 'yandex_login_1',
    'yandex_login_id': 'yandex_login_id_1',
    'services': BASE_SERVICES,
    'tz': 'Europe/Moscow',
    'without_vat_contract': False,
}
# fmt: on


# test for unknown client
async def test_unknown_client(web_app_client):
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'unknown'},
        json=REQUEST,
        headers=HEADERS,
    )
    assert response.status == 404


# test for changed country
async def test_changed_country(web_app_client):
    client = copy.copy(REQUEST)
    client['country'] = 'kaz'
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'},
        json=client,
        headers=HEADERS,
    )
    assert response.status == 400


# test for changed email to ''
async def test_base_client_email(
        web_app_client, db, personal_mock, corp_billing_mock,
):
    original_client = await db.secondary.corp_clients.find_one(
        {'_id': 'client_id_1'},
    )
    assert original_client['email_id'] == 'email_id_1'

    client = {'email': ''}
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'},
        json=client,
        headers=HEADERS,
    )
    assert response.status == 200

    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})
    assert client['email_id'] is None
    assert client['email'] == ''


# test for successful client update
async def test_base_client_update(
        web_app_client, db, mockserver, personal_mock, corp_billing_mock,
):
    @mockserver.json_handler('/corp-managers/v1/managers/update')
    def _mock_update_manager(request):
        assert request.headers.get('X-Remote-Ip')
        assert request.query['yandex_uid'] == BASE_CLIENT['yandex_id']

        assert request.json == {
            'yandex_login': BASE_CLIENT['yandex_login'],
            'role': 'client',
        }
        return mockserver.make_response(json={}, status=200)

    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'},
        json=REQUEST,
        headers=HEADERS,
    )
    assert response.status == 200
    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})
    assert isinstance(client.pop('updated'), datetime.datetime)
    assert client.pop('updated_at')
    assert client == BASE_CLIENT


# test for is_trial update (set announcements)
async def test_is_trial_update(
        web_app_client, db, stq, mockserver, personal_mock, corp_billing_mock,
):
    @mockserver.json_handler('/corp-managers/v1/managers/update')
    def _mock_update_manager(request):
        assert request.headers.get('X-Remote-Ip')
        assert request.query['yandex_uid'] == 'yandex_uid_2'

        assert request.json == {
            'yandex_login': 'yandex_login_2',
            'role': 'client',
        }
        return mockserver.make_response(json={}, status=200)

    client_id = 'client_id_2'
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': client_id},
        json={'is_trial': False},
        headers=HEADERS,
    )
    assert response.status == 200
    assert stq.corp_set_announcements_to_client.times_called == 1
    assert stq.corp_set_announcements_to_client.next_call()['kwargs'] == {
        'client_id': client_id,
    }


# test for tz update
@pytest.mark.parametrize(
    ('timezone', 'status'),
    [
        pytest.param('Europe/Helsinki', 200, id='correct tz'),
        pytest.param('Asia/Moscow', 400, id='incorrect tz'),
    ],
)
async def test_tz_client_update(
        web_app_client, db, personal_mock, corp_billing_mock, timezone, status,
):
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'},
        json={'tz': timezone},
        headers=HEADERS,
    )
    assert response.status == status

    if response.status == 200:
        client = await db.secondary.corp_clients.find_one(
            {'_id': 'client_id_1'},
        )
        assert client['tz'] == timezone


# test for description update
async def test_changed_description(
        web_app_client, patch, db, personal_mock, corp_billing_mock,
):
    client = copy.copy(REQUEST)
    client['description'] = 'new_description'
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'},
        json=client,
        headers=HEADERS,
    )
    assert response.status == 200
    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})
    assert client['description'] == 'new_description'


# test for yandex_login update
async def test_changed_login(
        web_app_client,
        patch,
        db,
        mockserver,
        personal_mock,
        corp_billing_mock,
        blackbox_mock,
):
    @mockserver.json_handler('/corp-managers/v1/managers/update')
    def _mock_update_manager(request):
        return mockserver.make_response(json={}, status=200)

    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    async def _create_user_client_association(
            operator_uid, client_id, customer_uid,
    ):
        return 0, ''

    client = copy.copy(REQUEST)
    client['yandex_login'] = 'new_yandex_login'
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'},
        json=client,
        headers=HEADERS,
    )
    assert response.status == 200
    client = await db.secondary.corp_clients.find_one({'_id': 'client_id_1'})
    assert client['yandex_id'] == 'new_yandex_uid'
    assert client['yandex_login'] == 'new_yandex_login'


async def test_changed_login_duplicate(
        web_app_client,
        patch,
        db,
        mockserver,
        personal_mock,
        corp_billing_mock,
        blackbox_mock,
):
    @mockserver.json_handler('/corp-managers/v1/managers/update')
    def _mock_update_manager(request):
        return mockserver.make_response(
            json={'code': 'duplicate_uid', 'message': 'duplicate uid'},
            status=400,
        )

    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    async def _create_user_client_association(
            operator_uid, client_id, customer_uid,
    ):
        return 0, ''

    client = copy.copy(REQUEST)
    client['yandex_login'] = 'new_yandex_login'
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'},
        json=client,
        headers=HEADERS,
    )
    assert response.status == 400


# fmt: off
@pytest.mark.parametrize(
    ['error', 'code'],
    [
        pytest.param(
            billing_v2.UserClientAssociationError,
            400,
            id='UserClientAssociationError',
        ),
        pytest.param(
            billing_v2.BillingError,
            400,
            id='BillingError',
        ),
        pytest.param(
            billing_v2.RequestTimeoutError,
            500,
            id='RequestTimeoutError',
        ),
    ],
)
# fmt: on
async def test_association_errors(
        web_app_client,
        patch,
        db,
        personal_mock,
        corp_billing_mock,
        blackbox_mock,
        error,
        code,
):
    @patch('taxi.clients.billing_v2.BalanceClient.'
           'create_user_client_association')
    async def _create_user_client_association(
            operator_uid, client_id, customer_uid,
    ):
        raise error

    client = copy.copy(REQUEST)
    client['yandex_login'] = 'new_yandex_login'
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_1'}, json=client, headers=HEADERS,
    )
    assert response.status == code


@pytest.mark.config(
    CORP_ALLOWED_FEATURES_SETTINGS={
        'feature1': {},
        'feature2': {},
        'readonly_feature1': {'readonly': True},
        'readonly_feature2': {'readonly': True},
    },
)
@pytest.mark.parametrize(
    ['features', 'code'],
    [
        pytest.param(['feature1', 'readonly_feature1', 'feature2'], 200),
        pytest.param(['readonly_feature1'], 200),
        pytest.param(
            ['feature1', 'readonly_feature1', 'readonly_feature2'], 400,
        ),
        pytest.param(['feature1'], 400),
    ],
)
async def test_readonly_features(
        web_app_client,
        patch,
        db,
        personal_mock,
        corp_billing_mock,
        blackbox_mock,
        features,
        code,
):
    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    async def _create_user_client_association(
            operator_uid, client_id, customer_uid,
    ):
        return 0, ''

    client = {'features': features}
    response = await web_app_client.patch(
        '/v1/clients',
        params={'client_id': 'client_id_5'},
        json=client,
        headers=HEADERS,
    )
    assert response.status == code

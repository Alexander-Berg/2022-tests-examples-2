import copy
import datetime

import pytest

from test_corp_clients.web import test_utils

NOW = datetime.datetime.utcnow().replace(microsecond=0)

HEADERS = {
    'X-Yandex-Login': 'login',
    'X-Yandex-UID': '1234567890',
    'X-Real-IP': 'remote_ip',
}
BASE_CLIENT_PARAMS = {
    'name': 'name',
    'country': 'rus',
    'yandex_login': ' yandex_loGin ',
    'is_trial': True,
    'city': 'Москва',
    'phone': '+79991234567',
}
COST_CENTERS_CREATION_ENABLED = {
    'CORP_COST_CENTERS_NEW_CLIENTS_ENABLED': '2000-07-01T00:00:00+00:00',
    'CORP_COST_CENTERS_TEMPLATES': [test_utils.COST_CENTER_TEMPLATE],
    'CORP_COUNTRIES_SUPPORTED': test_utils.CORP_COUNTRIES_SUPPORTED,
}
CORP_FEATURES_SETTINGS = [
    {
        'country': '__default__',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                ],
            },
            {'name': '__on_create__', 'features': [{'name': 'new_limits'}]},
        ],
    },
    {
        'country': 'isr',
        'feature_groups': [
            {
                'name': '__default__',
                'features': [
                    {'name': 'api_allowed'},
                    {'name': 'combo_orders_allowed'},
                ],
            },
        ],
    },
]
CORP_ALLOWED_FEATURES_SETTINGS = {'new_limits': {'readonly': True}}


async def check_cost_centers(db, country, should_exist, client_id=None):
    if client_id is None:
        query = {'client_id': client_id}
    else:
        query = {}
    cost_centers = await db.corp_cost_center_options.find(query).to_list(None)
    if should_exist:
        assert len(cost_centers) == 1
        cost_center = cost_centers[0]
        expected_template = copy.deepcopy(test_utils.COST_CENTER_TEMPLATE)
        if country == 'rus':
            locale = 'ru'
        else:
            locale = 'en'
        keyset = test_utils.TRANSLATIONS['corp']
        expected_name = keyset[expected_template.pop('name_key')][locale]
        expected_template['name'] = expected_name
        for field in expected_template['field_settings']:
            field['title'] = keyset[field.pop('title_key')][locale]
        for key, value in expected_template.items():
            assert cost_center[key] == value
    else:
        assert cost_centers == []


# test for invalid request
@pytest.mark.config(CORP_FEATURES_SETTINGS=CORP_FEATURES_SETTINGS)
async def test_invalid_features(web_app_client):
    client = copy.copy(BASE_CLIENT_PARAMS)
    client['features'] = ['invalid']
    response = await web_app_client.post(
        '/v1/clients/create', json=client, headers=HEADERS,
    )
    assert response.status == 400


# test for duplicating client login
@pytest.mark.filldb(corp_clients='duplicate_error')
@pytest.mark.config(
    CORP_FEATURES_SETTINGS=CORP_FEATURES_SETTINGS,
    CORP_ALLOWED_FEATURES_SETTINGS=CORP_ALLOWED_FEATURES_SETTINGS,
)
async def test_duplicate_client(web_app_client, blackbox_mock):
    response = await web_app_client.post(
        '/v1/clients/create', json=BASE_CLIENT_PARAMS, headers=HEADERS,
    )
    response_json = await response.json()

    assert response.status == 406
    assert response_json['details'] == {
        'reason': 'Duplicate client yandex-login',
        'client_id': 'duplicate',
    }


# test for successful client creation
@pytest.mark.parametrize(
    [
        'check_cost_centers_creation',
        'country',
        'is_trial',
        'expected_features',
    ],
    [
        pytest.param(
            False,
            'rus',
            True,
            ['new_limits'],
            id='rus-cost-centers-not-created',
        ),
        pytest.param(
            False, 'isr', False, [], id='isr-cost-centers-not-created',
        ),
        pytest.param(
            True,
            'rus',
            False,
            ['new_limits'],
            marks=pytest.mark.config(**COST_CENTERS_CREATION_ENABLED),
            id='rus-cost-centers-created',
        ),
        pytest.param(
            True,
            'isr',
            True,
            [],
            marks=pytest.mark.config(**COST_CENTERS_CREATION_ENABLED),
            id='isr-cost-centers-created',
        ),
    ],
)
@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED=COST_CENTERS_CREATION_ENABLED[
        'CORP_COUNTRIES_SUPPORTED'
    ],
    CORP_FEATURES_SETTINGS=CORP_FEATURES_SETTINGS,
    CORP_ALLOWED_FEATURES_SETTINGS=CORP_ALLOWED_FEATURES_SETTINGS,
)
@pytest.mark.translations(**test_utils.TRANSLATIONS)
async def test_create_client(
        web_app_client,
        load_json,
        db,
        mockserver,
        blackbox_mock,
        personal_mock,
        corp_billing_mock,
        stq,
        check_cost_centers_creation,
        country,
        is_trial,
        expected_features,
):
    @mockserver.json_handler('/corp-managers/v1/managers/create')
    def _mock_create_manager(request):
        assert request.headers.get('X-Remote-Ip')

        assert request.json.pop('client_id')
        assert request.json == {
            'yandex_login': 'yandex_login',
            'role': 'client',
        }
        return mockserver.make_response(
            json={'id': 'created_manager_id'}, status=200,
        )

    await check_cost_centers(db, country, should_exist=False)
    json_request = dict(BASE_CLIENT_PARAMS, country=country)
    json_request['is_trial'] = is_trial

    response = await web_app_client.post(
        '/v1/clients/create', json=json_request, headers=HEADERS,
    )
    assert response.status == 200

    client = await db.secondary.corp_clients.find_one(
        {'yandex_login': BASE_CLIENT_PARAMS['yandex_login'].strip().lower()},
    )
    client_id = client.pop('_id')
    assert client_id
    await check_cost_centers(
        db,
        country,
        should_exist=check_cost_centers_creation,
        client_id=client_id,
    )

    created = client.pop('created')
    updated = client.pop('updated')
    updated_at = client.pop('updated_at')
    assert isinstance(created, datetime.datetime)
    assert isinstance(updated, datetime.datetime)
    assert updated_at

    cabinet_only_group_id = client.pop('cabinet_only_role_id')
    expected_client = load_json('expected_clients.json')['create_client']
    expected_client['country'] = country
    expected_client['is_trial'] = is_trial
    expected_client['features'] = expected_features
    corp_countries = COST_CENTERS_CREATION_ENABLED['CORP_COUNTRIES_SUPPORTED']
    expected_client['tz'] = corp_countries[json_request['country']]['tz']
    assert client == expected_client

    cabinet_only_group = await db.secondary.corp_roles.find_one(
        {'_id': cabinet_only_group_id},
    )
    assert cabinet_only_group

    assert stq.corp_registration_notices_tmp.times_called == 1
    assert stq.corp_registration_notices_tmp.next_call()['kwargs'] == {
        'client_id': client_id,
    }
    if not is_trial:
        assert stq.corp_set_announcements_to_client.times_called == 1
        assert stq.corp_set_announcements_to_client.next_call()['kwargs'] == {
            'client_id': client_id,
        }


# test for common_validators
def test_common_normalizers():
    from corp_clients.api.common import client_common

    client = copy.copy(BASE_CLIENT_PARAMS)
    client['email'] = ' emaiL@email.ru '
    client_common.common_normalizers(client)
    assert client['email'] == 'email@email.ru'
    assert client['yandex_login'] == 'yandex_login'

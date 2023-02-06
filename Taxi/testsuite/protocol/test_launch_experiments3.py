import json
import uuid

import bson
import pytest

OAUTH_QUERY = {
    'method=oauth',
    'userip=',
    'format=json',
    'dbfields=subscription.suid.669',
    'aliases=1%2C10%2C16',
    'oauth_token=test_token',
    'getphones=bound',
    'get_login_id=yes',
    'phone_attributes=102%2C107%2C4',
    'attributes=1015',
}

USER_AGENT = (
    'ru.yandex.ytaxi/4.03.11463 (iPhone; ' 'iPhone5,2; iOS 10.3.3; Darwin)'
)

CHECK_PLUS_RESP = {'has_plus': False}

CHECK_PLUS_QUERY = {
    'method=check_has_plus',
    'format=json',
    'phone_number=72222222222',
}

OAUTH_RESP = {
    'uid': {'value': '123'},
    'status': {'value': 'VALID'},
    'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
    'aliases': {'10': 'phne-edcsaypw'},
    'phones': [
        {'attributes': {'102': '+71111111111'}, 'id': '1111'},
        {'attributes': {'102': '+72222222222', '107': '1'}, 'id': '2222'},
    ],
}


@pytest.fixture(scope='function', autouse=True)
def personal_phones_store(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def mock_personal_phones_store(request):
        return {'id': 'personal_phone_id', 'value': '+72222222222'}


@pytest.fixture(scope='function', autouse=True)
def blackbox(mockserver):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        query = set(request.query_string.decode().split('&'))
        if query == OAUTH_QUERY:
            return OAUTH_RESP
        elif query == CHECK_PLUS_QUERY:
            return CHECK_PLUS_RESP
        assert False


@pytest.fixture(scope='function', autouse=True)
def feedback_service(mockserver):
    @mockserver.json_handler('/feedback/1.0/wanted/retrieve')
    def mock_service(request):
        assert request.headers['YaTaxi-Api-Key'] == 'feedback_apikey'
        data = json.loads(request.get_data())
        assert sorted(data.keys()) == ['id', 'newer_than', 'phone_id']
        return {'orders': []}


@pytest.mark.translations(
    client_messages={'capybara': {'ru': 'капибара', 'en': 'capybara'}},
)
@pytest.mark.experiments3(filename='experiments3_01_translation.json')
@pytest.mark.user_experiments('ya_plus')
def test_launch_with_token_and_exp3_server_with_translation(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/launch',
        {},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['typed_experiments']['items']) == 1
    exp = data['typed_experiments']['items'][0]
    assert exp['name'] == 'ACQUIRE_TIMEOUT_MS'
    assert exp['value']['l10n']['animal'] == 'capybara'
    assert exp['value']['a'] == 50


@pytest.mark.experiments3(filename='experiments3_not_authorized.json')
@pytest.mark.user_experiments('ya_plus')
def test_launch_simple(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/launch',
        {'id': '536b24fa2816451b855d9a3e640215c3'},
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['authorized']
    items = data['typed_experiments']['items']
    assert len(items) == 1
    assert items[0]['name'] == 'not_authorized'


# @pytest.mark.parametrize('use_headers', [True, False])
# @pytest.mark.config(LAUNCH_OBTAIN_DATA_FROM_HEADERS=True)
# def test_launch_yandex_uuid_and_device_id_in_headers(
#         experiments3, taxi_protocol, use_headers,
# ):
#     yandex_uuid = uuid.uuid4().hex
#     device_id = uuid.uuid4().hex
#
#     experiments = [
#         {'name': 'YANDEX_UUID', 'id': yandex_uuid},
#         {'name': 'DEVICE_ID', 'id': device_id},
#     ]
#     for exp in experiments:
#         experiments3.add_experiment(
#             match={'predicate': {'type': 'true'}, 'enabled': True},
#             name=exp['name'],
#             consumers=['launch', 'client_protocol/launch'],
#             clauses=[
#                 {
#                     'predicate': {
#                         'type': 'eq',
#                         'init': {
#                             'arg_type': 'string',
#                             'arg_name': exp['name'].lower(),
#                             'value': exp['id'],
#                         },
#                     },
#                     # TODO(detinin): add 'value' field
#                 },
#             ],
#         )
#
#     def form_query_string(uuid, dev_id):
#         return '3.0/launch?uuid=' + uuid + '&metrica_device_id=' + dev_id
#
#     url = (
#         form_query_string('a' * 32, 'b' * 32)
#         if use_headers
#         else form_query_string(yandex_uuid, device_id)
#     )
#
#     headers = (
#         {'X-AppMetrica-UUID': yandex_uuid,
#           'X-AppMetrica-DeviceId': device_id}
#         if use_headers
#         else {}
#     )
#
#     response = taxi_protocol.post(url, {}, headers=headers)
#     assert response.status_code == 200
#     data = response.json()
#
#     assert data['uuid'] == yandex_uuid
#     assert data['device_id'] == device_id
#
#     assert set([exp['name'] for exp in experiments]) == set(
#         [exp['name'] for exp in data['typed_experiments']['items']],
#     )


@pytest.mark.user_experiments('ya_plus')
@pytest.mark.experiments3(filename='experiments3_02.json')
def test_launch_with_disabled_exps(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/launch',
        {},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['typed_experiments']['items']) == 0


@pytest.mark.user_experiments('ya_plus')
@pytest.mark.experiments3(
    match={
        'predicate': {'type': 'true'},
        'enabled': 'true',
        'applications': [
            {'name': 'android', 'version_range': {'from': '0.0.0'}},
        ],
    },
    name='FUN',
    consumers=['launch', 'client_protocol/launch'],
    clauses=[],
    default_value=50,
)
def test_launch_with_non_matching_application(taxi_protocol, now):
    response = taxi_protocol.post(
        '3.0/launch',
        {},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['typed_experiments']['items']) == 0


@pytest.mark.user_experiments('ya_plus')
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_launch_with_token_and_exp3_server(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/launch',
        {},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['typed_experiments']['items']) == 1
    exp = data['typed_experiments']['items'][0]
    assert exp['name'] == 'ACQUIRE_TIMEOUT_MS'
    assert exp['value'] == 50


@pytest.mark.experiments3(filename='experiments3_yandex_uuid.json')
def test_launch_with_yandex_uuid(taxi_protocol):
    yandex_uuid = '980b54b3b4daf69d4eb7f113eb2e69b7'
    response = taxi_protocol.post(
        '3.0/launch?uuid=' + yandex_uuid,
        {'id': '136b24fa2816451b855d9a3e640215c1'},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    exp = data['typed_experiments']['items'][0]
    assert exp['name'] == 'YANDEX_UUID'
    assert exp['value'] == 50


@pytest.mark.experiments3(filename='experiments3_yandex_uuid.json')
def test_launch_with_yandex_uuid_nonexisting_user(taxi_protocol):
    yandex_uuid = '980b54b3b4daf69d4eb7f113eb2e69b7'
    zuser_id = 'z' + uuid.uuid4().hex[:31]
    response = taxi_protocol.post(
        '3.0/launch?uuid=' + yandex_uuid,
        {'id': zuser_id},
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    exp = data['typed_experiments']['items'][0]
    assert exp['name'] == 'YANDEX_UUID'
    assert exp['value'] == 50


@pytest.mark.experiments3(filename='experiments3_unauthorized.json')
@pytest.mark.parametrize('omit_unauthorized_kwargs', [True, False])
def test_launch_unauthorized_kwargs(
        taxi_protocol, config, omit_unauthorized_kwargs,
):
    config.set_values(
        dict(
            LAUNCH_OMIT_UNAUTHORIZED_USER_EXP3_KWARGS=omit_unauthorized_kwargs,
        ),
    )
    yandex_uuid = '980b54b3b4daf69d4eb7f113eb2e69b7'
    user_id = '536b24fa2816451b855d9a3e640215c3'
    response = taxi_protocol.post(
        '3.0/launch?uuid=' + yandex_uuid,
        {'id': user_id},
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    experiment_names = {
        exp['name'] for exp in data['typed_experiments']['items']
    }
    assert 'YANDEX_UUID' in experiment_names
    assert 'USER_ID' in experiment_names
    assert ('PHONE_ID' not in experiment_names) == omit_unauthorized_kwargs


@pytest.mark.parametrize(
    'personal_phone_id, expected_experiment_response',
    [
        ('personal_phone_id', {'name': 'PERSONAL_PHONE_ID_TEST', 'value': 50}),
        ('invalid_personal_phone_id', None),
    ],
)
@pytest.mark.experiments3(filename='experiments3_personal_phone_id.json')
@pytest.mark.config(LAUNCH_THROW_ERROR_ON_PHONISH_PHONE_ID_MISMATCH=True)
def test_launch_with_personal_phone_id(
        taxi_protocol,
        personal_phone_id,
        mockserver,
        expected_experiment_response,
        db,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    def mock_personal_phones_store(request):
        return {'id': personal_phone_id, 'value': '+72222222222'}

    db.user_phones.find_and_modify(
        {'_id': bson.ObjectId('594baaba779fb30a39a5381e')},
        {'$set': {'personal_phone_id': personal_phone_id}},
    )
    response = taxi_protocol.post(
        '3.0/launch',
        {'id': '7c5cea02692a49a5b5e277e4582af45b'},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    exps = data['typed_experiments']['items']
    if expected_experiment_response is not None:
        assert len(exps) == 1
        exp = exps[0]
        assert exp == expected_experiment_response
    else:
        assert len(exps) == 0


@pytest.mark.translations(
    client_messages={'capybara': {'ru': 'капибара', 'en': 'capybara'}},
)
@pytest.mark.user_experiments('ya_plus')
@pytest.mark.experiments3(
    filename='experiments3_01_translation_not_found.json',
)
def test_launch_with_with_translation_not_found(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/launch',
        {},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['typed_experiments']['items']) == 1
    exp = data['typed_experiments']['items'][0]
    assert exp['name'] == 'ACQUIRE_TIMEOUT_MS'
    assert exp['value']['l10n']['animal'] == 'cat'
    assert exp['value']['a'] == 50


@pytest.mark.translations(
    client_messages={'capybara': {'ru': 'капибара', 'en': 'capybara'}},
)
@pytest.mark.user_experiments('ya_plus')
@pytest.mark.experiments3(filename='experiments3_01_broken_l10n.json')
def test_launch_with_broken_translation(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/launch',
        {},
        bearer='test_token',
        headers={'User-Agent': USER_AGENT},
    )
    assert response.status_code == 200
    data = response.json()
    items = data['typed_experiments']['items']
    assert len(items) == 1
    assert items[0]['value']['l10n']
    assert 'key' not in items[0]['value']['l10n'][0]


FRANCE_IP = '89.185.38.136'
RUSSIA_IP = '2.60.1.1'
DUMMY_IP = '0.0.0.0'


@pytest.mark.config()
@pytest.mark.parametrize(
    'remote_ip,expected_id,expected_region',
    [
        (RUSSIA_IP, 'us_ru_id', 'ru'),
        (FRANCE_IP, None, None),
        (DUMMY_IP, None, None),
    ],
)
@pytest.mark.config(
    HOSTS_OVERRIDE=[
        {
            'countries': ['en'],
            'hosts': [
                {
                    'ID': 'en_id',
                    'TAXI_TEST': {'host': 'en_host', 'ips': [], 'url': ''},
                },
            ],
        },
        {
            'countries': ['us', 'ru'],
            'hosts': [
                {
                    'ID': 'us_ru_id',
                    'TAXI_TEST': {'host': 'us_ru_host', 'ips': [], 'url': ''},
                },
            ],
        },
    ],
    LAUNCH_THROW_ERROR_ON_PHONISH_PHONE_ID_MISMATCH=True,
)
@pytest.mark.experiments3(filename='experiments3_hosts_override.json')
@pytest.mark.user_experiments('ya_plus')
def test_hosts_override(
        taxi_protocol,
        mockserver,
        remote_ip,
        expected_id,
        expected_region,
        now,
):
    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        oauth_query = {
            'method=oauth',
            'userip={}'.format(remote_ip),
            'format=json',
            'dbfields=subscription.suid.669',
            'aliases=1%2C10%2C16',
            'oauth_token=test_token',
            'getphones=bound',
            'get_login_id=yes',
            'phone_attributes=102%2C107%2C4',
            'attributes=1015',
        }

        query = set(request.query_string.decode().split('&'))
        if query == oauth_query:
            return OAUTH_RESP
        elif query == CHECK_PLUS_QUERY:
            return CHECK_PLUS_RESP
        assert False

    response = taxi_protocol.post(
        '3.0/launch',
        {
            'id': '536b24fa2816451b855d9a3e640215c3',
            'supported_features': [],
            'device_id': 'test_device_id',
        },
        bearer='test_token',
        headers={
            'User-Agent': (
                'ru.yandex.ytaxi/4.03.11463 (iPhone; '
                'iPhone5,2; iOS 10.3.3; Darwin)'
            ),
        },
        x_real_ip=remote_ip,
    )

    assert response.status_code == 200

    data = response.json()
    parameters = data['parameters']
    if expected_id and expected_region:
        assert 'regional_policy' in parameters
        regional_policy = parameters['regional_policy']
        assert regional_policy['region'] == expected_region
        assert regional_policy['hosts'][0]['ID'] == expected_id
    else:
        assert 'regional_policy' not in parameters

    items = data['typed_experiments']['items']
    assert data['typed_experiments']['version'] == 1
    assert len(items) == 1

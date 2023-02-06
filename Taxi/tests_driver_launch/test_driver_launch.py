import random

import pytest

USER_AGENT_HEADER = 'Taximeter 9.13 (8421)'

FRANCE_IP = '89.185.38.136'
RUSSIA_IP = '2.60.1.1'
DUMMY_IP = '0.0.0.0'


async def test_launch_endpoint_stub(taxi_driver_launch):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1'},
        headers={
            'X-Remote-IP': '1.2.3.4',
            'Accept-Language': 'ru',
            'User-Agent': USER_AGENT_HEADER,
        },
    )

    assert response.status_code == 200


@pytest.mark.config(GDPR_COUNTRIES=['us', 'fr'], NEED_ACCEPT_GDPR=True)
@pytest.mark.parametrize(
    'remote_ip,expected_gdpr_text',
    [
        ('87.250.250.242', None),
        ('173.194.222.101', 'gdpr.usa'),
        ('127.0.0.1', 'gdpr'),
        ('89.185.38.136', 'gdpr'),
    ],
)
async def test_launch_eula(remote_ip, expected_gdpr_text, taxi_driver_launch):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1'},
        headers={
            'X-Remote-IP': remote_ip,
            'User-Agent': USER_AGENT_HEADER,
            'Accept-Language': 'ru',
        },
    )

    assert response.status_code == 200
    response_body = response.json()
    if expected_gdpr_text:
        assert 'need_acceptance' in response_body
        eulas = response_body['need_acceptance']
        assert list(eulas)
        assert len(eulas) == 1
        gdpr = eulas[0]
        assert gdpr['type'] == 'gdpr'
        assert gdpr['title']
        assert gdpr['content'] == expected_gdpr_text
    else:
        assert 'need_acceptance' not in response_body


@pytest.mark.parametrize(
    'remote_ip,country_code',
    [(RUSSIA_IP, 'RU'), (FRANCE_IP, 'FR'), (DUMMY_IP, None)],
)
async def test_launch_country(taxi_driver_launch, remote_ip, country_code):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1'},
        headers={'X-Remote-IP': remote_ip, 'User-Agent': USER_AGENT_HEADER},
    )

    assert response.status_code == 200
    response_body = response.json()
    if country_code:
        assert 'country' in response_body
        assert response_body['country']['code'] == country_code
    else:
        assert 'country' not in response_body


_METRICA_ID_EXP3 = {
    'match': {
        'predicate': {'init': {}, 'type': 'true'},
        'enabled': True,
        'applications': [
            {
                'name': 'taximeter',
                'version_range': {'from': '0.0.0', 'to': '99.9.9'},
            },
        ],
    },
    'name': 'my_exp',
    'consumers': ['driver-launch/v1/launch'],
    'clauses': [
        {
            'value': {},
            'predicate': {
                'init': {
                    'arg_name': 'metrica_id',
                    'divisor': 100,
                    'range_from': 50,
                    'range_to': 100,
                    'salt': 'abcd',
                },
                'type': 'mod_sha1_with_salt',
            },
        },
    ],
}

_METRICA_ID_EXP3_2 = {
    'match': {
        'predicate': {'init': {}, 'type': 'true'},
        'enabled': True,
        'applications': [
            {
                'name': 'taximeter',
                'version_range': {'from': '0.0.0', 'to': '99.9.9'},
            },
        ],
    },
    'name': 'my_exp2',
    'consumers': ['driver-launch/v1/launch'],
    'clauses': [
        {
            'value': {},
            'predicate': {
                'init': {
                    'arg_name': 'metrica_id',
                    'divisor': 100,
                    'range_from': 50,
                    'range_to': 100,
                    'salt': 'abcd',
                },
                'type': 'mod_sha1_with_salt',
            },
        },
    ],
}


@pytest.mark.experiments3(**_METRICA_ID_EXP3)
@pytest.mark.experiments3(**_METRICA_ID_EXP3_2)
@pytest.mark.config(NEED_ACCEPT_GDPR=False)
async def test_launch_experiments_exists(taxi_driver_launch):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1'},
        headers={
            'X-Remote-IP': '1.2.3.4',
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.13 (8421)',
        },
    )
    assert response.status_code == 200
    response_body = response.json()
    assert 'experiments' in response_body
    experiments = response_body['experiments']
    assert len(experiments) == 2
    sorted_experiments = list(experiments)
    sorted_experiments.sort()
    assert sorted_experiments[0] == 'my_exp'
    assert sorted_experiments[1] == 'my_exp2'


async def test_launch_experiments_empty(taxi_driver_launch):
    response = await taxi_driver_launch.get(
        'v1/launch?metrica_id=a1',
        headers={
            'X-Remote-IP': '1.2.3.4',
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.13 (8421)',
        },
    )
    assert response.status_code == 200
    response_body = response.json()
    assert 'experiments' not in response_body


@pytest.mark.config(GDPR_COUNTRIES=['ua', 'fr'])
@pytest.mark.parametrize(
    'remote_ip,expected_sync_flag',
    [(RUSSIA_IP, False), (FRANCE_IP, True), (DUMMY_IP, False)],
)
async def test_disable_background_data_sync(
        taxi_driver_launch, remote_ip, expected_sync_flag,
):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1'},
        headers={'X-Remote-IP': remote_ip, 'User-Agent': USER_AGENT_HEADER},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert (
        response_body['parameters']['disable_background_data_sync']
        == expected_sync_flag
    )


_COUNTRY_CODE_EXP3 = {
    'match': {'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    'name': 'hosts_override',
    'consumers': ['driver_launch/v1/launch_hosts_override'],
    'clauses': [
        {
            'title': 'Водитель в эксперименте',
            'value': {'is_enabled': True},
            'predicate': {
                'type': 'in_set',
                'init': {
                    'arg_name': 'country_code',
                    'set_elem_type': 'string',
                    'set': ['ru', 'us'],
                },
            },
        },
    ],
}


@pytest.mark.experiments3(**_COUNTRY_CODE_EXP3)
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
)
@pytest.mark.parametrize(
    'remote_ip,expected_id,expected_region',
    [
        (RUSSIA_IP, 'us_ru_id', 'ru'),
        (FRANCE_IP, None, None),
        (DUMMY_IP, None, None),
    ],
)
async def test_hosts_override(
        now, taxi_driver_launch, remote_ip, expected_id, expected_region,
):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1'},
        headers={'X-Remote-IP': remote_ip, 'User-Agent': USER_AGENT_HEADER},
    )
    assert response.status_code == 200
    response_body = response.json()
    parameters = response_body['parameters']
    if expected_id and expected_region:
        assert 'regional_policy' in parameters
        regional_policy = parameters['regional_policy']
        assert regional_policy['region'] == expected_region
        assert regional_policy['hosts'][0]['ID'] == expected_id
    else:
        assert 'regional_policy' not in parameters


@pytest.mark.config(NEED_ACCEPT_GDPR=True, GDPR_COUNTRIES=['ru', 'us', 'au'])
@pytest.mark.config(
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'uberdriver': {
            'issue_managers': [],
            'stop_words': [],
            'supported_languages': [],
            'override_keysets': {'taximeter_messages': 'override_uberdriver'},
        },
    },
)
async def test_uberdriver_launch(taxi_driver_launch):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1'},
        headers={
            'X-Remote-IP': '1.2.3.4',
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter-Uber 9.13 (8421)',
        },
    )
    assert response.status_code == 200
    response_body = response.json()
    assert response_body['need_acceptance'] == [
        {'content': 'buber', 'title': 'buber', 'type': 'gdpr'},
    ]


@pytest.fixture(name='mock_territories')
def _mock_territories(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _users_create_handler(request):
        countries_list = load_json('countries.json')
        random.shuffle(countries_list['countries'])
        territories_response = {'countries': []}
        for country in countries_list['countries']:
            key_value_list = list(country.items())
            random.shuffle(key_value_list)
            country_response = dict(key_value_list)
            territories_response['countries'].append(country_response)
        return territories_response


def _shuffle_configs(configs):
    for key, value in configs.items():
        if isinstance(value, dict):
            _shuffle_configs(value)
            value_list = list(value.items())
            random.shuffle(value_list)
            configs[key] = dict(value_list)
        elif isinstance(value, list):
            random.shuffle(value)


@pytest.mark.parametrize(
    'params',
    [
        {'metrica_id': 'a1', 'countries_hash': '4551553204181160400'},
        {'metrica_id': 'a1', 'global_hash': '9250975354091663575'},
    ],
)
async def test_loc_config_only_one_hash(
        taxi_driver_launch, mock_territories, params,
):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params=params,
        headers={'X-Remote-IP': RUSSIA_IP, 'User-Agent': USER_AGENT_HEADER},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'need_both_hashes',
        'message': 'Need send both global_hash and countries_hash',
    }


async def test_loc_config(
        taxi_driver_launch, mock_territories, load_json, taxi_config,
):
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1', 'global_hash': '0', 'countries_hash': '0'},
        headers={'X-Remote-IP': RUSSIA_IP, 'User-Agent': USER_AGENT_HEADER},
    )

    assert response.status_code == 200
    assert response.json()['hashed_taximeter_client_config'] == load_json(
        'loc_config.json',
    )


async def test_loc_config_hashes_not_changed(
        taxi_driver_launch, mock_territories, load_json, taxi_config,
):
    configs = load_json('config.json')
    for _ in range(5):
        _shuffle_configs(configs)
        taxi_config.set_values(configs)
        await taxi_driver_launch.invalidate_caches()
        response = await taxi_driver_launch.get(
            'v1/launch',
            params={
                'metrica_id': 'a1',
                'global_hash': '0',
                'countries_hash': '0',
            },
            headers={
                'X-Remote-IP': RUSSIA_IP,
                'User-Agent': USER_AGENT_HEADER,
            },
        )

        assert response.status_code == 200
        expected_loc_config = load_json('loc_config.json')
        assert (
            response.json()['hashed_taximeter_client_config']['global_hash']
            == expected_loc_config['global_hash']
        )
        assert (
            response.json()['hashed_taximeter_client_config']['countries_hash']
            == expected_loc_config['countries_hash']
        )

    taxi_config.set_values(load_json('config.json'))
    await taxi_driver_launch.invalidate_caches()


async def test_loc_config_changed_global(
        taxi_driver_launch, mock_territories, load_json, taxi_config,
):
    configs = load_json('config.json')
    configs['TAXIMETER_CLIENT_URLS']['__default__'].update(
        {
            'ZENDESK_API': 'https://yataxidrivers.zendesk.com',
            'ZENDESK_DOMAIN': 'https://yataxi.zendesk.com',
        },
    )
    configs['TAXIMETER_DEFAULT_SETTINGS_JSON']['__default__'].update(
        {
            'client_chat_vocalize': {
                'defaultValue': 'true',
                'killSwitch': 'false',
                'type': 'switcher',
            },
        },
    )
    taxi_config.set_values(configs)
    await taxi_driver_launch.invalidate_caches()

    expected_json = load_json('loc_config_changed_global.json')
    our_global_hash = '4524340816770468486'
    assert our_global_hash != expected_json['global_hash']

    response = await taxi_driver_launch.get(
        'v1/launch',
        params={
            'metrica_id': 'a1',
            'global_hash': our_global_hash,
            'countries_hash': expected_json['countries_hash'],
        },
        headers={'X-Remote-IP': RUSSIA_IP, 'User-Agent': USER_AGENT_HEADER},
    )

    assert response.status_code == 200
    assert response.json()['hashed_taximeter_client_config'] == expected_json


async def test_loc_config_changed_countries(
        taxi_driver_launch, mock_territories, load_json, taxi_config,
):
    configs = load_json('config.json')
    configs['TAXIMETER_CLIENT_URLS']['ltu'].update(
        {'URL_SUPPORT': 'https://yandex.ru/support/zout_taxi-drivers/'},
    )
    taxi_config.set_values(configs)
    await taxi_driver_launch.invalidate_caches()

    expected_json = load_json('loc_config_changed_countries.json')
    our_countries_hash = '4524340816770468486'
    assert our_countries_hash != expected_json['countries_hash']

    response = await taxi_driver_launch.get(
        'v1/launch',
        params={
            'metrica_id': 'a1',
            'global_hash': expected_json['global_hash'],
            'countries_hash': our_countries_hash,
        },
        headers={'X-Remote-IP': RUSSIA_IP, 'User-Agent': USER_AGENT_HEADER},
    )

    assert response.status_code == 200
    assert response.json()['hashed_taximeter_client_config'] == expected_json


@pytest.mark.parametrize(
    'new_bad_url, new_bad_country, remove_default',
    [
        (
            {
                'URL_NOT_REPRESENTED_IN_DEFAULT': (
                    'https://yandex.ru/support/zout_taxi-drivers/'
                ),
            },
            None,
            False,
        ),
        (
            None,
            {
                'zzz': {
                    'ACTIVITY_INFO_URL': (
                        'https://driver.yandex/lt-lt/base/activity?type=iframe'
                    ),
                    'URL_HOW_TO_FIX_RATING': (
                        'https://driver.yandex/lt-lt/base/raiting'
                    ),
                },
            },
            False,
        ),
        (None, None, True),
    ],
)
async def test_loc_config_update_failed(
        taxi_driver_launch,
        mock_territories,
        load_json,
        taxi_config,
        new_bad_url,
        new_bad_country,
        remove_default,
):
    configs = load_json('config.json')
    taxi_config.set_values(configs)
    await taxi_driver_launch.invalidate_caches()
    if new_bad_url:
        configs['TAXIMETER_CLIENT_URLS']['ltu'].update(new_bad_url)
    if new_bad_country:
        configs['TAXIMETER_CLIENT_URLS'].update(new_bad_country)
    if remove_default:
        configs['TAXIMETER_CLIENT_URLS'].pop('__default__')
    taxi_config.set_values(configs)
    await taxi_driver_launch.invalidate_caches()
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1', 'global_hash': '0', 'countries_hash': '0'},
        headers={'X-Remote-IP': RUSSIA_IP, 'User-Agent': USER_AGENT_HEADER},
    )

    assert response.status_code == 200
    assert response.json()['hashed_taximeter_client_config'] == load_json(
        'loc_config.json',
    )


_TAXIMETER_LOC_CONFIG_OVERRIDES = {
    'match': {'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    'name': 'taximeter_localization_config_overrides',
    'consumers': ['driver-launch/v1/launch-taximeter-loc-config'],
    'clauses': [
        {
            'value': {
                'default_settings_override': {
                    '__default__': {
                        'preferences': {
                            'app_sounds_section': {'killSwitch': 'true'},
                        },
                    },
                    'LT': {
                        'preferences': {
                            'voiceover_mute': {
                                'defaultValue': 'true',
                                'killSwitch': 'false',
                                'type': 'switcher',
                                'values': ['waze', 'yandex', 'yamaps'],
                            },
                        },
                    },
                },
            },
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'application',
                                'value': 'taximeter',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'version',
                                'value': '5.13.17',
                                'arg_type': 'version',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'arg_name': 'version',
                                'value': '8.14.1',
                                'arg_type': 'version',
                            },
                            'type': 'lte',
                        },
                    ],
                },
                'type': 'all_of',
            },
        },
        {
            'value': {
                'client_urls_override': {
                    '__default__': {'URL_JOB_INITIAL_UA': 'http://azaza.com'},
                    'RO': {
                        'URL_JOB_INITIAL_COMMON': (
                            'https://tympyrym.yandex.com/driver/'
                        ),
                    },
                },
            },
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'application',
                                'value': 'taximeter',
                                'arg_type': 'string',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'version',
                                'value': '9.14.1',
                                'arg_type': 'version',
                            },
                            'type': 'gte',
                        },
                        {
                            'init': {
                                'arg_name': 'version',
                                'value': '99.9.9',
                                'arg_type': 'version',
                            },
                            'type': 'lte',
                        },
                    ],
                },
                'type': 'all_of',
            },
        },
    ],
}


def _update_loc_config(loc_config, update_loc_config_fields):
    for key, value in update_loc_config_fields.items():
        if key == 'countries':
            for elem in value:
                for country in loc_config['countries']:
                    if country['country_code'] == elem['country_code']:
                        _update_loc_config(country, elem)
        elif isinstance(value, dict):
            if loc_config.get(key) is None:
                loc_config[key] = {}
            _update_loc_config(loc_config[key], value)
        else:
            loc_config[key] = value


@pytest.mark.experiments3(**_TAXIMETER_LOC_CONFIG_OVERRIDES)
@pytest.mark.parametrize(
    'update_loc_config_fields, user_agent',
    [
        (
            {
                'config': {
                    'global': {
                        'preferences': {
                            'app_sounds_section': {'killSwitch': 'true'},
                        },
                    },
                    'countries': [
                        {
                            'country_code': 'LT',
                            'preferences': {
                                'voiceover_mute': {
                                    'defaultValue': 'true',
                                    'killSwitch': 'false',
                                    'type': 'switcher',
                                    'values': ['waze', 'yandex', 'yamaps'],
                                },
                            },
                        },
                    ],
                },
                'global_hash': '14264965921968802255',
                'countries_hash': '1020375602300830502',
            },
            'Taximeter 6.13 (8421)',
        ),
        ({}, 'Taximeter 5.11 (8421)'),
        ({}, 'Taximeter 8.15 (8421)'),
        (
            {
                'config': {
                    'global': {
                        'urls': {'URL_JOB_INITIAL_UA': 'http://azaza.com'},
                    },
                    'countries': [
                        {
                            'country_code': 'RO',
                            'urls': {
                                'URL_JOB_INITIAL_COMMON': (
                                    'https://tympyrym.yandex.com/driver/'
                                ),
                            },
                        },
                    ],
                },
                'global_hash': '9749177842084038831',
                'countries_hash': '7997878630420229011',
            },
            'Taximeter 9.15 (8421)',
        ),
    ],
)
async def test_loc_config_with_overrides(
        taxi_driver_launch,
        mock_territories,
        load_json,
        taxi_config,
        update_loc_config_fields,
        user_agent,
):
    configs = load_json('config.json')
    taxi_config.set_values(configs)
    await taxi_driver_launch.invalidate_caches()
    response = await taxi_driver_launch.get(
        'v1/launch',
        params={'metrica_id': 'a1', 'global_hash': '0', 'countries_hash': '0'},
        headers={'X-Remote-IP': RUSSIA_IP, 'User-Agent': user_agent},
    )

    assert response.status_code == 200
    loc_config = load_json('loc_config.json')
    _update_loc_config(loc_config, update_loc_config_fields)
    assert response.json()['hashed_taximeter_client_config'] == loc_config


async def test_v1_localization_config_get(
        taxi_driver_launch, mock_territories, load_json,
):
    response = await taxi_driver_launch.get(
        '/internal/driver-launch/v1/taximeter-localization-config',
    )

    assert response.status_code == 200
    assert response.json() == load_json('loc_config.json')

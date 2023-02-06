import pytest

import tests_bank_client_experiments.exp3_helpers as exp3

DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YANDEX_BUID = 'buid_1'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_REQUEST_LANGUAGE = 'ru'
DEFAULT_STAFF_LOGIN = 'staff_login_1'


def _build_headers_list(locale=DEFAULT_REQUEST_LANGUAGE):
    return [
        {'X-YaBank-SessionUUID': DEFAULT_YABANK_SESSION_UUID},
        {'X-YaBank-PhoneID': DEFAULT_YABANK_PHONE_ID},
        {'X-Yandex-BUID': DEFAULT_YANDEX_BUID},
        {'X-Yandex-UID': DEFAULT_YANDEX_UID},
        {'X-Request-Application': 'app_name=android'},
        {'X-Request-Language': locale},
        {'X-YaBank-Yandex-Team-Login': DEFAULT_STAFF_LOGIN},
    ]


def _build_headers(locale, exclude_headers=None):
    all_headers = {}
    for header in _build_headers_list(locale):
        all_headers.update(header)

    if not exclude_headers:
        return all_headers

    for header_to_exclude in exclude_headers:
        all_headers.pop(header_to_exclude, None)

    return all_headers


def _build_typed_experiment(exp_name, exp_value, need_add_l10n, version):
    if need_add_l10n:
        val = {'l10n': exp_value}
    else:
        val = exp_value

    return {
        'cache_status': 'updated',
        'name': exp_name,
        'value': val,
        'version': version,
    }


def _get_phrase_by_locale(locale):
    if locale == 'en':
        return 'Phrase to translate from experiment '

    return 'Фраза для перевода из эксперимента '


def _build_experiment_result_by_locale(locale):
    typed_experiments = []
    typed_experiments.append(
        _build_typed_experiment(
            'exp1',
            {
                'phrase_to_translate_from_exp_1': (
                    _get_phrase_by_locale(locale) + '1'
                ),
            },
            need_add_l10n=True,
            version='1:0:{}'.format(locale),
        ),
    )
    typed_experiments.append(
        _build_typed_experiment(
            'exp2',
            {
                'phrase_to_translate_from_exp_2': (
                    _get_phrase_by_locale(locale) + '2'
                ),
            },
            need_add_l10n=True,
            version='2:0:{}'.format(locale),
        ),
    )
    return typed_experiments


def _build_experiment_result():
    typed_experiments = []
    typed_experiments.append(
        _build_typed_experiment(
            'exp1', {'value': 'exp1_value'}, False, '1:0:ru',
        ),
    )
    typed_experiments.append(
        _build_typed_experiment(
            'exp2', {'value': 'exp2_value'}, False, '2:0:ru',
        ),
    )
    return typed_experiments


def _add_l10n_info(value):
    return {
        'l10n': [
            {
                'default': 'default_string',
                'key': value,
                'tanker': {'key': value, 'keyset': 'bank_backend'},
            },
        ],
    }


def _create_experiment(
        exp_name, exp_value_without_localization, locale, need_localize,
):
    exp_value = exp_value_without_localization
    if need_localize:
        exp_value = _add_l10n_info(exp_value_without_localization)

    return exp3.create_experiment(
        name=exp_name,
        consumers=['client_wallet_sdk'],
        predicates=[
            exp3.create_eq_predicate(
                'bank_session_uuid', DEFAULT_YABANK_SESSION_UUID,
            ),
            exp3.create_eq_predicate('request_language', locale),
            exp3.create_eq_predicate('yandex_uid', DEFAULT_YANDEX_UID),
            exp3.create_eq_predicate('bank_phone_id', DEFAULT_YABANK_PHONE_ID),
            exp3.create_eq_predicate('buid', DEFAULT_YANDEX_BUID),
            exp3.create_eq_predicate('application.platform', 'android'),
            exp3.create_eq_predicate('staff_login', DEFAULT_STAFF_LOGIN),
        ],
        value=exp_value,
    )


def _create_localized_experiment(
        exp_name, exp_value_without_localization, locale,
):
    return _create_experiment(
        exp_name, exp_value_without_localization, locale, True,
    )


def _create_non_localized_experiment(
        exp_name, exp_value_without_localization, locale,
):
    return _create_experiment(
        exp_name, exp_value_without_localization, locale, False,
    )


async def test_remote_config_with_staff_login(
        taxi_bank_client_experiments, experiments3,
):
    exp_name = 'some_exp_for_staff'
    exp_value = {'some_key': 'some_value'}
    experiments3.add_experiment(
        **exp3.create_experiment(
            name=exp_name,
            consumers=['client_wallet_sdk'],
            predicates=[
                exp3.create_eq_predicate('staff_login', DEFAULT_STAFF_LOGIN),
                exp3.create_eq_predicate(
                    arg_name='bank_sdk', value=True, arg_type='bool',
                ),
                exp3.create_gte_predicate(
                    arg_name='sdk_version', value='0.11.0', arg_type='version',
                ),
            ],
            value=exp_value,
        ),
        trait_tags=['cache-on-clients'],
    )

    headers = _build_headers(DEFAULT_REQUEST_LANGUAGE)
    headers[
        'X-Request-Application'
    ] = 'bank_sdk=true,sdk_ver1=0,sdk_ver2=12,sdk_ver3=0'

    await taxi_bank_client_experiments.invalidate_caches()
    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config', headers=headers, json={},
    )

    expected_experiments = []
    expected_experiments.append(
        _build_typed_experiment(
            exp_name=exp_name,
            exp_value=exp_value,
            need_add_l10n=False,
            version=f'1:0:{DEFAULT_REQUEST_LANGUAGE}',
        ),
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert len(response_experiments) == 1
    assert response_experiments == expected_experiments


@pytest.mark.parametrize('locale', ['', 'ru', 'en'])
async def test_remote_config_with_localization(
        taxi_bank_client_experiments, locale, experiments3,
):
    experiments3.add_experiment(
        **_create_localized_experiment(
            'exp1', 'phrase_to_translate_from_exp_1', locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_experiment(
        **_create_localized_experiment(
            'exp2', 'phrase_to_translate_from_exp_2', locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    await taxi_bank_client_experiments.invalidate_caches()
    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert len(response_experiments) == 2
    assert response_experiments == _build_experiment_result_by_locale(locale)


async def test_remote_config_without_localization(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp1', {'value': 'exp1_value'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp2', {'value': 'exp2_value'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    await taxi_bank_client_experiments.invalidate_caches()
    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert len(response_experiments) == 2
    assert response_experiments == _build_experiment_result()


@pytest.mark.parametrize('excluded_header', _build_headers_list())
async def test_remote_config_no_matches(
        taxi_bank_client_experiments, excluded_header, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_localized_experiment(
            'exp1', 'phrase_to_translate_from_exp_1', locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_experiment(
        **_create_localized_experiment(
            'exp2', 'phrase_to_translate_from_exp_2', locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    await taxi_bank_client_experiments.invalidate_caches()
    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale, excluded_header),
        json={},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == []


async def test_experiment_and_config_name_collision(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'collision_name', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_config(
        **_create_non_localized_experiment(
            'collision_name', {'type': 'config'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    await taxi_bank_client_experiments.invalidate_caches()
    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert len(response_experiments) == 1
    assert response_experiments[0]['value']['type'] == 'config'


async def test_remote_config_with_known_experiments(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp1', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp2', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )

    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={'typed_experiments': [{'name': 'exp2'}], 'version': 'MjowOnJ1'},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == [
        {
            'name': 'exp1',
            'version': '1:0:ru',
            'value': {'type': 'experiment'},
            'cache_status': 'updated',
        },
        {
            'name': 'exp2',
            'version': '2:0:ru',
            'value': {'type': 'experiment'},
            'cache_status': 'updated',
        },
    ]
    assert response.json()['version'] == 'ZXhwMSwxOjA6cnU7ZXhwMiwyOjA6cnU='


async def test_remote_config_without_known_experiments(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp1', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp2', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )

    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={'typed_experiments': []},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == [
        {
            'name': 'exp1',
            'version': '1:0:ru',
            'value': {'type': 'experiment'},
            'cache_status': 'updated',
        },
        {
            'name': 'exp2',
            'version': '2:0:ru',
            'value': {'type': 'experiment'},
            'cache_status': 'updated',
        },
    ]
    assert response.json()['version'] == 'ZXhwMSwxOjA6cnU7ZXhwMiwyOjA6cnU='


async def test_remote_config_with_all_known_experiments(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp1', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp2', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )

    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={'version': 'ZXhwMSwxOjA6cnU7ZXhwMiwyOjA6cnU='},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == []
    assert response.json()['version'] == 'ZXhwMSwxOjA6cnU7ZXhwMiwyOjA6cnU='


async def test_remote_config_empty_experiments(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE

    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={'version': ''},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == []
    assert response.json()['version'] == ''


async def test_no_cash_with_known_experiments(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp1', {'type': 'experiment'}, locale,
        ),
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp2', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )

    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={'typed_experiments': [{'name': 'exp2'}], 'version': 'MjowOnJ1'},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == [
        {
            'name': 'exp2',
            'version': '2:0:ru',
            'value': {'type': 'experiment'},
            'cache_status': 'updated',
        },
    ]
    assert response.json()['version'] == 'ZXhwMiwyOjA6cnU='


async def test_no_cash_without_known_experiments(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp1', {'type': 'experiment'}, locale,
        ),
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp2', {'type': 'experiment'}, locale,
        ),
        trait_tags=['cache-on-clients'],
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp3', {'type': 'experiment'}, locale,
        ),
    )

    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={'typed_experiments': []},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == [
        {
            'name': 'exp2',
            'version': '2:0:ru',
            'value': {'type': 'experiment'},
            'cache_status': 'updated',
        },
    ]
    assert response.json()['version'] == 'ZXhwMiwyOjA6cnU='


async def test_no_cash_empty_answer(
        taxi_bank_client_experiments, experiments3,
):
    locale = DEFAULT_REQUEST_LANGUAGE
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp1', {'type': 'experiment'}, locale,
        ),
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp2', {'type': 'experiment'}, locale,
        ),
    )
    experiments3.add_experiment(
        **_create_non_localized_experiment(
            'exp3', {'type': 'experiment'}, locale,
        ),
    )

    response = await taxi_bank_client_experiments.post(
        'v1/client-experiments/v1/get_remote_config',
        headers=_build_headers(locale),
        json={'typed_experiments': []},
    )

    assert response.status_code == 200
    response_experiments = response.json()['typed_experiments']
    assert response_experiments == []
    assert response.json()['version'] == ''

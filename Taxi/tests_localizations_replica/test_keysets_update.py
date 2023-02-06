import pytest

CONFIG_LOCALIZATIONS_KEYSETS = {
    'keysets': {
        'color': {
            'mongo_collection_name': 'localization.taxi.color',
            'tanker_keyset_id': 'blocks-common:i-color-label',
            'tanker_project_id': 'taxi',
        },
        'geoareas': {
            'mongo_collection_name': 'localization.taxi.geoareas',
            'tanker_keyset_id': 'backend.geoareas',
            'tanker_project_id': 'taxi',
        },
        'notify': {
            'mongo_collection_name': 'localization.taxi.notify',
            'tanker_keyset_id': 'backend.notify',
            'tanker_project_id': 'taxi',
        },
        'stopwords': {
            'mongo_collection_name': 'localization.taxi.stopwords',
            'tanker_keyset_id': 'backend.stopwords',
            'tanker_project_id': 'taxi',
        },
        'bad_placeholder': {
            'mongo_collection_name': 'localization.taxi.bad_placeholder',
            'tanker_keyset_id': 'backend.bad_placeholder',
            'tanker_project_id': 'taxi',
        },
        'override': {
            'mongo_collection_name': 'localization.taxi.override',
            'tanker_keyset_id': 'backend.override',
            'tanker_project_id': 'taxi',
        },
        'empty_keyset': {
            'mongo_collection_name': 'localization.taxi.empty_keyset',
            'tanker_keyset_id': 'backend.empty_keyset',
            'tanker_project_id': 'taxi',
        },
    },
}
CONFIG_LOCALIZATIONS_KEYSETS_WITHOUT_NOTIFY = {
    'keysets': {
        'color': {
            'mongo_collection_name': 'localization.taxi.color',
            'tanker_keyset_id': 'blocks-common:i-color-label',
            'tanker_project_id': 'taxi',
        },
        'geoareas': {
            'mongo_collection_name': 'localization.taxi.geoareas',
            'tanker_keyset_id': 'backend.geoareas',
            'tanker_project_id': 'taxi',
        },
    },
}
CONFIG_LOCALIZATIONS_VALIDATOR = {
    'placeholder_strict_mode': True,
    'placeholder_supported_types': ['d', 's'],
}
CONFIG_LOCALIZATIONS_VALIDATOR_WITHOUT_S_TYPE = {
    'placeholder_strict_mode': True,
    'placeholder_supported_types': ['d'],
}
CONFIG_OVERRIDE_KEYSETS = {
    'color': 'ignore',
    'geoareas': 'notify',
    'notify': 'ignore,',
    'bad_placeholder': 'ignore',
}
CONFIG_OVERRIDE_KEYSETS_STOP_WORDS = {
    'color': 'ignore',
    'geoareas': 'notify',
    'notify': 'ignore,',
    'bad_placeholder': 'ignore',
    'stopwords': 'notify',
}
CONFIG_OVERRIDE_KEYSETS_OVERRIDE_STOP_WORDS = {
    'color': 'ignore',
    'geoareas': 'stopwords',
    'notify': 'ignore,',
    'bad_placeholder': 'ignore',
    'stopwords': 'ignore',
}
CONFIG_OVERRIDE_KEYSETS_BAD_STOP_WORDS = {
    'color': 'ignore',
    'geoareas': 'notify',
    'notify': 'ignore,',
    'bad_placeholder': 'ignore',
    'stopwords': 'override',
}
CONFIG_STOP_WORDS = [
    'Яндекс',
    'Яндекс.Такси',
    'Yandeks',
    'Yandex.Taksi',
    'Yandeks.Taksi',
]
CONFIG_SUPPORTED_LANGUAUGE = ['ru', 'en']
CONFIG_MAINTAINER = 'ivankolosov'
CONFIG_ISSUE_MANAGERS = ['kpugachev', 'dyuva']


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_PLACEHOLDER_VALIDATION_MAINTAINER=CONFIG_MAINTAINER,
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': CONFIG_OVERRIDE_KEYSETS,
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [({'keyset': ['color', 'geoareas']}, 200, {}), ({'id': 'color'}, 200, {})],
)
async def test_update_localizations_response_success(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code
    assert response.json() == response_body


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS_WITHOUT_NOTIFY,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': CONFIG_OVERRIDE_KEYSETS,
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [
        (
            {'keyset': ['color', 'geoareas']},
            400,
            {'code': 'general', 'status': 'error'},
        ),
    ],
)
async def test_update_localizations_response_override_missed(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code
    body = response.json()
    assert body['code'] == response_body['code']
    assert body['status'] == response_body['status']


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_PLACEHOLDER_VALIDATION_MAINTAINER=CONFIG_MAINTAINER,
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': CONFIG_OVERRIDE_KEYSETS,
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [
        (
            {'keyset': ['bad_placeholder', 'geoareas']},
            400,
            {'code': 'general', 'status': 'error'},
        ),
    ],
)
async def test_update_localizations_response_bad_placeholder(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code
    body = response.json()
    assert body['code'] == response_body['code']
    assert body['status'] == response_body['status']


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR_WITHOUT_S_TYPE,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_PLACEHOLDER_VALIDATION_MAINTAINER=CONFIG_MAINTAINER,
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': CONFIG_OVERRIDE_KEYSETS,
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [
        (
            {'keyset': ['color', 'geoareas']},
            400,
            {'code': 'general', 'status': 'error'},
        ),
    ],
)
async def test_update_localizations_response_unsupported_type(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code
    body = response.json()
    assert body['code'] == response_body['code']
    assert body['status'] == response_body['status']


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_PLACEHOLDER_VALIDATION_MAINTAINER=CONFIG_MAINTAINER,
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': CONFIG_OVERRIDE_KEYSETS_STOP_WORDS,
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [({'keyset': ['stopwords']}, 200, {'code': 'general', 'status': 'error'})],
)
async def test_update_localizations_response_stop_words_success(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_PLACEHOLDER_VALIDATION_MAINTAINER=CONFIG_MAINTAINER,
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': {
                'stopwords': 'empty_keyset',
                'empty_keyset': 'ignore',
            },
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [({'keyset': ['stopwords']}, 400, {'code': 'general', 'status': 'error'})],
)
async def test_update_localizations_response_stop_words_override_key_missing(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code
    body = response.json()
    assert body['code'] == response_body['code']
    assert body['status'] == response_body['status']
    assert (
        body['message']
        == 'Error while validating keyset \'stopwords\' - some keys contain '
        + 'stop words.\n\n'
        + 'If the keys below are yours, either remove stop words from your '
        + 'key or add override key without stop words (key with same name in '
        + 'keyset \'backend.empty_keyset\' in project \'taxi\'). Otherwise '
        + 'ask key owner to change it.\n\n'
        + 'Keys with problems:\nKey \'moscow\' contains stop words: '
        + '\'yandeks\' (ru)\n\n'
        + 'If nothing above helped, contact @kpugachev, @dyuva for more '
        + 'information.'
    )


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_PLACEHOLDER_VALIDATION_MAINTAINER=CONFIG_MAINTAINER,
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': {'stopwords': 'stopwords'},
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [({'keyset': ['stopwords']}, 400, {'code': 'general', 'status': 'error'})],
)
async def test_update_localizations_response_stop_words_override_key_bad(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code
    body = response.json()
    assert body['code'] == response_body['code']
    assert body['status'] == response_body['status']
    assert (
        body['message']
        == 'Error while validating keyset \'stopwords\' - some overrides in '
        + 'keyset \'backend.stopwords\' in project \'taxi\' contain stop '
        + 'words.\n\n'
        + 'If the keys below are yours, remove all stop words from overrides '
        + 'for your key. Otherwise ask key owner to change it.\n\n'
        + 'Keys with problems:\nKey \'moscow\' contains stop words: '
        + '\'yandeks\' (ru)\n\n'
        + 'If nothing above helped, contact @kpugachev, @dyuva for more '
        + 'information.'
    )


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.filldb(localizations_tanker_cache='translations')
@pytest.mark.config(
    LOCALIZATIONS_KEYSETS=CONFIG_LOCALIZATIONS_KEYSETS,
    LOCALIZATIONS_VALIDATOR=CONFIG_LOCALIZATIONS_VALIDATOR,
    LOCALES_KEYS_IGNORING_PLACEHOLDER_ERRORS=[],
    LOCALES_PLACEHOLDER_VALIDATION_MAINTAINER=CONFIG_MAINTAINER,
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'az': {
            'override_keysets': CONFIG_OVERRIDE_KEYSETS_BAD_STOP_WORDS,
            'supported_languages': CONFIG_SUPPORTED_LANGUAUGE,
            'stop_words': CONFIG_STOP_WORDS,
            'issue_managers': CONFIG_ISSUE_MANAGERS,
        },
    },
)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [({'keyset': ['stopwords']}, 400, {'code': 'general', 'status': 'error'})],
)
async def test_update_localizations_response_stop_words_error_bad_stopwords(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.post(
        'v1/keysets/update', json=params,
    )
    assert response.status_code == response_code
    body = response.json()
    assert body['code'] == response_body['code']
    assert body['status'] == response_body['status']

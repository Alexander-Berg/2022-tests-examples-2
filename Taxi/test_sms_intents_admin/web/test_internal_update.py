import pytest


USER_PARAMS = 'requests/user_general.json'


@pytest.mark.config(
    SMS_INTENTS_ADMIN_SUGGESTIONS={
        'business_group': ['Ride-Hailing', 'Food Tech', 'Logistics'],
        'cost_center': ['ride-hailing', 'YTMS85'],
        'meta_type': ['Demand'],
        'provider_settings': {
            'infobip': {'account': ['account']},
            'yasms': {'route': ['taxi'], 'sender': ['yango']},
        },
    },
)
@pytest.mark.pgsql('sms_intents_admin', files=['test_update.sql'])
async def test_update_settings(web_app_client, load_json):
    params = load_json(USER_PARAMS)
    params['intent'] = 'test_user'
    params['status'] = 'active'
    validate_response = await web_app_client.post(
        '/v1/internal/validate_update', json=params,
    )
    assert validate_response.status == 200
    content = await validate_response.json()
    assert content == {'data': params}

    response = await web_app_client.post('/v1/internal/update', json=params)
    assert response.status == 200


@pytest.mark.config(
    SMS_INTENTS_ADMIN_SUGGESTIONS={
        'business_group': ['Ride-Hailing', 'Food Tech', 'Logistics'],
        'cost_center': ['ride-hailing', 'YTMS85'],
        'meta_type': ['Demand'],
        'provider_settings': {
            'infobip': {'account': ['account']},
            'yasms': {'route': ['taxi'], 'sender': ['yango']},
        },
    },
)
@pytest.mark.pgsql('sms_intents_admin', files=['test_update.sql'])
async def test_archive(web_app_client, load_json):
    params = load_json(USER_PARAMS)
    params['intent'] = 'test_user'
    params['status'] = 'archived'
    validate_response = await web_app_client.post(
        '/v1/internal/validate_update', json=params,
    )
    assert validate_response.status == 200

    response = await web_app_client.post('/v1/internal/update', json=params)
    assert response.status == 200


@pytest.mark.config(
    SMS_INTENTS_ADMIN_SUGGESTIONS={
        'business_group': ['Ride-Hailing', 'Food Tech', 'Logistics'],
        'cost_center': ['ride-hailing', 'YTMS85'],
        'meta_type': ['Demand'],
        'provider_settings': {
            'infobip': {'account': ['account']},
            'yasms': {'route': ['taxi'], 'sender': ['yango']},
        },
    },
)
@pytest.mark.pgsql('sms_intents_admin', files=['test_update.sql'])
async def test_update_archivated_ok(web_app_client, load_json):
    params = load_json(USER_PARAMS)
    params['intent'] = 'archived_intent'
    params['status'] = 'active'
    validate_response = await web_app_client.post(
        '/v1/internal/validate_update', json=params,
    )
    assert validate_response.status == 200

    response = await web_app_client.post('/v1/internal/update', json=params)
    assert response.status == 200


@pytest.mark.config(
    SMS_INTENTS_ADMIN_SUGGESTIONS={
        'business_group': ['Ride-Hailing', 'Food Tech', 'Logistics'],
        'cost_center': ['ride-hailing', 'YTMS85'],
        'meta_type': ['Demand'],
        'provider_settings': {
            'infobip': {'account': ['account']},
            'yasms': {'route': ['taxi'], 'sender': ['yango']},
        },
    },
)
async def test_intent_not_exists(web_app_client, load_json):
    params = load_json(USER_PARAMS)
    params['intent'] = 'unexistent_intent'
    params['status'] = 'archived'
    validate_response = await web_app_client.post(
        '/v1/internal/validate_update', json=params,
    )
    assert validate_response.status == 404

    response = await web_app_client.post('/v1/internal/update', json=params)
    assert response.status == 404


@pytest.mark.config(
    SMS_INTENTS_ADMIN_SUGGESTIONS={
        'business_group': [],
        'cost_center': [],
        'meta_type': ['Demand'],
    },
)
@pytest.mark.pgsql('sms_intents_admin', files=['test_update.sql'])
async def test_update_400_suggest(web_app_client, load_json):
    params = load_json(USER_PARAMS)
    params['intent'] = 'test_user'
    params['status'] = 'active'
    validate_response = await web_app_client.post(
        '/v1/internal/validate_update', json=params,
    )
    assert validate_response.status == 400

    response = await web_app_client.post('/v1/internal/update', json=params)
    assert response.status == 400

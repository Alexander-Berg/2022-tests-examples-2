import pytest


USER_PARAMS = 'requests/user_general.json'
DRIVER_PARAMS = 'requests/driver.json'

NIS_PARAMS = 'notification_instead_sms.json'


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
@pytest.mark.parametrize(['request_file'], [(USER_PARAMS,), (DRIVER_PARAMS,)])
async def test_create_ok(web_app_client, load_json, request_file):
    params = load_json(request_file)
    validate_response = await web_app_client.post(
        '/v1/internal/validate_create', json=params,
    )
    assert validate_response.status == 200
    content = await validate_response.json()
    assert content == {'data': params}

    response = await web_app_client.post('/v1/internal/create', json=params)
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
async def test_create_400_nis(web_app_client, load_json):
    """NIS valid only for recipients_type: user"""
    params = load_json(DRIVER_PARAMS)
    params['notification_instead_sms'] = load_json(NIS_PARAMS)
    validate_response = await web_app_client.post(
        '/v1/internal/validate_create', json=params,
    )
    assert validate_response.status == 400

    response = await web_app_client.post('/v1/internal/create', json=params)
    assert response.status == 400


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
@pytest.mark.pgsql('sms_intents_admin', files=['test_create.sql'])
async def test_create_400_already_exists(web_app_client, load_json):
    """Trying to create intent with existing name"""
    params = load_json(USER_PARAMS)
    validate_response = await web_app_client.post(
        '/v1/internal/validate_create', json=params,
    )
    assert validate_response.status == 400

    response = await web_app_client.post('/v1/internal/create', json=params)
    assert response.status == 400


@pytest.mark.config(
    SMS_INTENTS_ADMIN_SUGGESTIONS={
        'business_group': [],
        'cost_center': [],
        'meta_type': ['Demand'],
    },
)
async def test_create_400_suggest(web_app_client, load_json):
    params = load_json(USER_PARAMS)
    validate_response = await web_app_client.post(
        '/v1/internal/validate_create', json=params,
    )
    assert validate_response.status == 400

    response = await web_app_client.post('/v1/internal/create', json=params)
    assert response.status == 400

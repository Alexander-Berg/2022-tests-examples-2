import pytest

USER_PARAMS = 'requests/user_general.json'
DRIVER_PARAMS = 'requests/driver.json'


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
@pytest.mark.now('2021-01-01T18:00:00')
async def test_lifecycle(web_app_client, load_json):
    intent = 'test_intent'
    creation_params = load_json(USER_PARAMS)
    creation_params['intent'] = intent

    # creation
    create_response = await web_app_client.post(
        '/v1/internal/create', json=creation_params,
    )
    assert create_response.status == 200

    get_response = await web_app_client.get(
        '/v1/internal/get', params={'intent': intent},
    )
    assert get_response.status == 200
    content = await get_response.json()
    assert content.pop('status') == 'active'
    assert content.pop('is_correct') is True
    assert content.pop('updated')
    assert content == creation_params

    # updation
    updation_params = load_json(DRIVER_PARAMS)
    updation_params['intent'] = intent
    updation_params['status'] = 'archived'

    update_response = await web_app_client.post(
        '/v1/internal/update', json=updation_params,
    )
    assert update_response.status == 200

    get_response = await web_app_client.get(
        '/v1/internal/get', params={'intent': intent},
    )
    assert get_response.status == 200
    content = await get_response.json()
    assert content.pop('is_correct') is True
    assert content.pop('updated')
    assert content == updation_params

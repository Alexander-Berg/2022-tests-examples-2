import pytest


SETTINGS = 'default_settings.json'
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
@pytest.mark.pgsql('sms_intents_admin', files=['test_dump.sql'])
async def test_upsert_and_dump(web_app_client, load_json):
    # default
    default_response = await web_app_client.post('/v1/internal/dump', json={})
    assert default_response.status == 200

    settings = load_json(SETTINGS)

    intents = (await default_response.json())['intents']
    intents.sort(key=lambda item: item['intent'])
    assert intents == [
        {
            'intent': 'int_2000',
            'is_correct': True,
            'status': 'active',
            'settings': settings,
            'updated': '2000-01-01T00:00:00+0300',
        },
        {
            'intent': 'int_2010',
            'is_correct': True,
            'status': 'archived',
            'settings': settings,
            'updated': '2010-01-01T00:00:00+0300',
        },
    ]

    # empty
    later_than = max(intent['updated'] for intent in intents)
    empty_response = await web_app_client.post(
        '/v1/internal/dump', json={'later_than': later_than},
    )
    assert empty_response.status == 200
    empty_content = await empty_response.json()
    assert empty_content == {'intents': []}

    # update and create
    updation_params = load_json(DRIVER_PARAMS)
    updation_params['intent'] = 'int_2000'
    updation_params['status'] = 'active'
    await web_app_client.post('/v1/internal/update', json=updation_params)

    creation_params = load_json(USER_PARAMS)
    creation_params['intent'] = 'test_intent'
    await web_app_client.post('/v1/internal/create', json=creation_params)

    response = await web_app_client.post(
        '/v1/internal/dump', json={'later_than': later_than},
    )
    assert response.status == 200
    content = await response.json()
    assert {intent['intent'] for intent in content['intents']} == {
        'int_2000',
        'test_intent',
    }

import pytest


TEST_USER = {
    'intent': 'test_user',
    'status': 'active',
    'is_correct': True,
    'description': 'Отправка SMS по тестированию на ковид',
    'business_group': 'Ride-Hailing',
    'cost_center': 'ride-hailing',
    'meta_type': 'Demand',
    'recipients_type': ['user', 'general'],
    'responsible': ['v-belikov', 'stasya-kh'],
}

ARCHIVED_INTENT = {
    'intent': 'archived_intent_test',
    'status': 'archived',
    'is_correct': True,
    'description': 'Архивный интент',
    'business_group': 'Logistics',
    'cost_center': 'YTMS85',
    'meta_type': 'Demand',
    'recipients_type': ['user', 'general'],
    'responsible': ['v-belikov', 'stasya-kh'],
}


@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_default(web_app_client):
    response = await web_app_client.post('/v1/internal/list', json={})
    assert response.status == 200

    content = await response.json()
    for item in content['intents']:
        assert item.pop('created')
    assert content == {
        'limit': 50,
        'offset': 0,
        'total': 2,
        'intents': [ARCHIVED_INTENT, TEST_USER],
    }


@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_filters(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/list',
        json={
            'intent': 'test',
            'responsible': ['v-belikov'],
            'status': ['archived'],
            'cost_center': ['ride-hailing', 'YTMS85', 'Unknown'],
            'business_group': ['Logistics', 'Food Tech'],
        },
    )
    assert response.status == 200

    intents = (await response.json())['intents']
    for item in intents:
        assert item.pop('created')
    assert intents == [ARCHIVED_INTENT]


@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_limit(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/list', json={'limit': 1},
    )
    assert response.status == 200

    content = await response.json()
    for item in content['intents']:
        assert item.pop('created')
    assert content == {
        'limit': 1,
        'offset': 0,
        'total': 2,
        'intents': [ARCHIVED_INTENT],
    }


@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_offset(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/list', json={'offset': 1},
    )
    assert response.status == 200

    content = await response.json()
    for item in content['intents']:
        assert item.pop('created')
    assert content == {
        'limit': 50,
        'offset': 1,
        'total': 2,
        'intents': [TEST_USER],
    }


@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_name(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/list', json={'intent': 'user'},
    )
    assert response.status == 200

    content = await response.json()
    for item in content['intents']:
        assert item.pop('created')
    assert content == {
        'limit': 50,
        'offset': 0,
        'total': 1,
        'intents': [TEST_USER],
    }


@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_archived_status(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/list', json={'status': ['archived']},
    )
    assert response.status == 200

    intents = (await response.json())['intents']
    for item in intents:
        assert item.pop('created')
    assert intents == [ARCHIVED_INTENT]


@pytest.mark.parametrize(
    ['responsible', 'have_items'],
    [
        (['stasya-kh', 'v-belikov'], True),
        (['v-belikov', 'stasya-kh'], True),
        (['v-belikov'], True),
        (['nobody'], False),
        (['v-belikov', 'nobody'], False),
    ],
)
@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_responsible(web_app_client, responsible, have_items):
    response = await web_app_client.post(
        '/v1/internal/list',
        json={'status': ['active', 'archived'], 'responsible': responsible},
    )
    assert response.status == 200
    intents = (await response.json())['intents']
    if have_items:
        for item in intents:
            assert item.pop('created')
        assert intents == [ARCHIVED_INTENT, TEST_USER]
    else:
        assert not intents


@pytest.mark.parametrize(
    ['cost_center', 'items'],
    [
        (['ride-hailing', 'YTMS85', 'Unknown'], [ARCHIVED_INTENT, TEST_USER]),
        (['ride-hailing'], [TEST_USER]),
        (['Unknown'], []),
    ],
)
@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_cost_center(web_app_client, cost_center, items):
    response = await web_app_client.post(
        '/v1/internal/list', json={'cost_center': cost_center},
    )
    assert response.status == 200

    intents = (await response.json())['intents']
    for item in intents:
        assert item.pop('created')
    assert intents == items


@pytest.mark.pgsql('sms_intents_admin', files=['test_list.sql'])
async def test_business_group(web_app_client):
    response = await web_app_client.post(
        '/v1/internal/list',
        json={'business_group': ['Ride-Hailing', 'Food Tech']},
    )
    assert response.status == 200

    intents = (await response.json())['intents']
    for item in intents:
        assert item.pop('created')
    assert intents == [TEST_USER]

import logging

import pytest

logger = logging.getLogger(__name__)
QUERY_EXISTED_ID_PARAMS = {'id': 'existed_id'}
EXISTED_DATA_CONTENT = {'random_data': 'random_data'}

QUERY_NEW_ID_PARAMS = {'id': 'new_id'}
FIRST_BODY_CONTENT = {'foo': True}
SECOND_BODY_CONTENT = {'bar': 'Some text'}

LIST_PATH = '/candidates/config-list/'
ENTITY_PATH = '/candidates/config/'


@pytest.mark.filldb(candidates_filter_configs='filled')
async def test_candidates_config_list(web_app_client, mongodb):
    logger.info('getter test started')
    response = await web_app_client.get(LIST_PATH)
    assert response.status == 200
    content = await response.json()
    assert set(content.get('names')) == {'existed_id', 'existed_id2'}
    assert len(content.get('names')) == 2


@pytest.mark.filldb(candidates_filter_configs='empty')
async def test_candidates_config_empty_list(web_app_client, mongodb):
    logger.info('getter test started')
    response = await web_app_client.get(LIST_PATH)
    assert response.status == 200
    content = await response.json()
    assert content.get('names') == []


@pytest.mark.filldb(candidates_filter_configs='filled')
async def test_candidates_config_deletion(web_app_client, mongodb):
    logger.info('deletion test started')
    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_EXISTED_ID_PARAMS,
        json={'data': {}, 'old_data': EXISTED_DATA_CONTENT},
    )
    assert response.status == 200
    response = await web_app_client.get(LIST_PATH)
    assert response.status == 200
    content = await response.json()
    assert set(content.get('names')) == {'existed_id2'}
    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_EXISTED_ID_PARAMS,
        json={'data': {}, 'old_data': {}},
    )
    assert response.status == 200
    response = await web_app_client.get(LIST_PATH)
    assert response.status == 200
    content = await response.json()
    assert set(content.get('names')) == {'existed_id2'}


@pytest.mark.filldb(candidates_filter_configs='empty')
async def test_candidates_config_conflicts(web_app_client, mongodb):
    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_NEW_ID_PARAMS,
        json={'data': FIRST_BODY_CONTENT, 'old_data': SECOND_BODY_CONTENT},
    )
    assert response.status == 409

    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_NEW_ID_PARAMS,
        json={'data': FIRST_BODY_CONTENT, 'old_data': {}},
    )
    assert response.status == 201

    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_NEW_ID_PARAMS,
        json={'data': FIRST_BODY_CONTENT, 'old_data': {}},
    )
    assert response.status == 409

    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_NEW_ID_PARAMS,
        json={'data': SECOND_BODY_CONTENT, 'old_data': FIRST_BODY_CONTENT},
    )
    assert response.status == 200


@pytest.mark.filldb(candidates_filter_configs='filled')
async def test_candidates_config(web_app_client, mongodb):
    logger.info('getter test started')
    response = await web_app_client.get(
        ENTITY_PATH, params=QUERY_NEW_ID_PARAMS,
    )
    assert response.status == 204

    response = await web_app_client.get(
        ENTITY_PATH, params=QUERY_EXISTED_ID_PARAMS,
    )
    assert response.status == 200
    content = await response.json()
    assert content.get('data') == EXISTED_DATA_CONTENT

    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_NEW_ID_PARAMS,
        json={'data': FIRST_BODY_CONTENT, 'old_data': {}},
    )
    assert response.status == 201

    response = await web_app_client.post(
        ENTITY_PATH,
        params=QUERY_NEW_ID_PARAMS,
        json={'data': SECOND_BODY_CONTENT, 'old_data': FIRST_BODY_CONTENT},
    )
    assert response.status == 200

    response = await web_app_client.get(
        ENTITY_PATH, params=QUERY_NEW_ID_PARAMS,
    )
    assert response.status == 200
    content = await response.json()
    assert content.get('data') == SECOND_BODY_CONTENT

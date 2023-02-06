import pytest

from tests_uapi_keys import utils


ENDPOINT = '/v2/keys/list'

OK_PARAMS = [
    (
        {},
        {'limit': 100, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    # limit
    (
        {'limit': 50},
        {'limit': 50, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    (
        {'limit': 3},
        {'limit': 3, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    (
        {'limit': 2},
        {'limit': 2, 'cursor': '1', 'keys': [utils.V2KEY_3, utils.V2KEY_2]},
    ),
    ({'limit': 1}, {'limit': 1, 'cursor': '2', 'keys': [utils.V2KEY_3]}),
    # cursor
    (
        {'cursor': '7'},
        {'limit': 100, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    (
        {'cursor': '3'},
        {'limit': 100, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    ({'cursor': '2'}, {'limit': 100, 'keys': [utils.V2KEY_2, utils.V2KEY_1]}),
    (
        {'limit': 1, 'cursor': '2'},
        {'limit': 1, 'cursor': '1', 'keys': [utils.V2KEY_2]},
    ),
    # query.consumer_id
    (
        {'query': {'consumer_id': 'fleet-api-internal'}},
        {'limit': 100, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    ({'query': {'consumer_id': 'fleet-api'}}, {'limit': 100, 'keys': []}),
    ({'query': {'consumer_id': 'trash'}}, {'limit': 100, 'keys': []}),
    # query.client_id
    (
        {'query': {'client_id': 'antontodua'}},
        {'limit': 100, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    ({'query': {'client_id': 'trash'}}, {'limit': 100, 'keys': []}),
    # query.consumer_id + query.client_id
    (
        {
            'query': {
                'consumer_id': 'fleet-api-internal',
                'client_id': 'antontodua',
            },
        },
        {'limit': 100, 'keys': [utils.V2KEY_3, utils.V2KEY_2, utils.V2KEY_1]},
    ),
    (
        {'query': {'consumer_id': 'fleet-api', 'client_id': 'antontodua'}},
        {'limit': 100, 'keys': []},
    ),
    (
        {
            'query': {
                'consumer_id': 'fleet-api-internal',
                'client_id': 'taxi/park/abc',
            },
        },
        {'limit': 100, 'keys': []},
    ),
    (
        {'query': {'consumer_id': 'fleet-api', 'client_id': 'taxi/park/abc'}},
        {'limit': 100, 'keys': []},
    ),
    # query.is_enabled
    (
        {'query': {'is_enabled': True}},
        {'limit': 100, 'keys': [utils.V2KEY_2, utils.V2KEY_1]},
    ),
    (
        {'query': {'is_enabled': False}},
        {'limit': 100, 'keys': [utils.V2KEY_3]},
    ),
    # query.entity_id
    (
        {'query': {'entity_id': 'Ferrari-Land'}},
        {'limit': 100, 'keys': [utils.V2KEY_3, utils.V2KEY_1]},
    ),
    (
        {'query': {'entity_id': 'Disneyland'}},
        {'limit': 100, 'keys': [utils.V2KEY_2]},
    ),
    ({'query': {'entity_id': 'trash'}}, {'limit': 100, 'keys': []}),
    # query.entity_id + query.is_enabled
    (
        {'query': {'is_enabled': True, 'entity_id': 'Ferrari-Land'}},
        {'limit': 100, 'keys': [utils.V2KEY_1]},
    ),
]


@pytest.mark.parametrize('request_json, response_json', OK_PARAMS)
async def test_list(taxi_uapi_keys, request_json, response_json):
    response = await taxi_uapi_keys.post(ENDPOINT, json=request_json)

    assert response.status_code == 200
    assert response.json() == response_json

import copy
import re
import string

import pytest

DTIME_RE = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}')

FILTER_NAME = 'filter_to_get'
FILTER_DESCRIPTION = 'Very cool grep filter'

QUERY_WORD = {'matchstring': 'kibanning'}

QUERY_ANOTHER_WORD = {'matchstring': 'akibanning'}

QUERY_SPACES = {'matchstring': 'kibanning with spaces'}

QUERY_NEWLINES = {'matchstring': 'kibanning \n with \n  new lines'}

QUERY_FIELD = {'field': 'message', 'matchstring': 'Message matchstring'}

CHARACTERS = string.ascii_letters + string.punctuation + string.digits + '\t'

RESPONSE_TEMPLATE = {
    'id': 1,
    'filter_information': {
        'description': FILTER_DESCRIPTION,
        'creator': 'defaultcreator',
        'query': {'rules': []},
        'for_all_groups': True,
        'enabled': True,
        'threshold': 0,
        'suppress_related_errors': False,
        'filter_interval_minutes': 15,
    },
}

HEADERS = {'X-YaTaxi-Api-Key': 'fake_token', 'X-Yandex-Login': 'testcreator'}


@pytest.mark.parametrize(
    'query', [QUERY_WORD, QUERY_SPACES, QUERY_NEWLINES, QUERY_FIELD],
)
async def test_get_filter(web_app_client, create_filter, query, auth):
    __query = copy.deepcopy(query)

    _query = {'rules': [__query]}

    await auth()
    filter_id = await create_filter(_query, FILTER_DESCRIPTION)

    response = await web_app_client.get(
        '/v1/filter/{}/'.format(filter_id), headers=HEADERS,
    )

    assert response.status == 200
    response_json = await response.json()
    assert DTIME_RE.match(response_json['filter_information']['created'])
    del response_json['filter_information']['created']

    expected_response = copy.deepcopy(RESPONSE_TEMPLATE)
    expected_response['filter_information']['query']['rules'] = [__query]

    assert response_json == expected_response


async def test_get_cgroup(web_app_client, create_filter, auth):
    _query = {'rules': [QUERY_WORD]}
    await auth()
    fid = await create_filter(
        _query, FILTER_DESCRIPTION, cgroup='taxi_api_fake',
    )

    response = await web_app_client.get(
        '/v1/filter/{}/'.format(fid), headers=HEADERS,
    )
    assert response.status == 200

    content = await response.json()
    assert content['filter_information']['cgroup'] == 'taxi_api_fake'


async def test_get_all_filters(web_app_client, create_filter, auth):
    _query = {'rules': [QUERY_WORD]}
    await auth()
    for i in range(100):
        await create_filter(_query, FILTER_DESCRIPTION, cgroup='taxi_api_fake')
        await create_filter(
            {'rules': []}, FILTER_DESCRIPTION, cgroup='taxi_api_fake',
        )

    for i in range(25, 50):
        await web_app_client.delete(f'/v1/filter/{i}/', headers=HEADERS)

    response = await web_app_client.get('/v1/filter/', headers=HEADERS)
    assert response.status == 200

    content = await response.json()
    assert len(content['filters']) == 50


async def test_get_filter_missing(web_app_client, create_filter, auth):
    _query = {'rules': [QUERY_WORD]}
    fid = await create_filter(_query, FILTER_DESCRIPTION)

    await auth()
    response = await web_app_client.get(
        '/v1/filter/{}/'.format(fid), headers=HEADERS,
    )
    assert response.status == 200

    delete_response = await web_app_client.delete(
        '/v1/filter/{}/'.format(fid), headers=HEADERS,
    )

    assert delete_response.status == 200

    response = await web_app_client.get(
        '/v1/filter/{}/'.format(fid), headers=HEADERS,
    )
    assert response.status == 404

    not_found_data = await response.json()
    assert not_found_data['code'] == 'NO_FILTER'

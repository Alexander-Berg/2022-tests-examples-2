# pylint: disable=unused-variable
import copy

FILTER_DESCRIPTION = 'Very cool filter'

QUERY_WORD = {'matchstring': 'kibanning'}

QUERY_ANOTHER_WORD = {'matchstring': 'akibanning'}

QUERY_SPACES = {'matchstring': 'kibanning with spaces'}

QUERY_NEWLINES = {'matchstring': 'kibanning \n with \n  new lines'}

QUERY_FIELD = {'field': 'message', 'matchstring': 'Message matchstring'}

BASIC_MATCH_FILTER_BODY = {
    'description': 'Description from test',
    'query': {'rules': [{'matchstring': 'some error message'}]},
}
HEADERS = {'X-YaTaxi-Api-Key': 'fake_token', 'X-Yandex-Login': 'testcreator'}


async def test_get_all_filters(web_app_client, create_filter, auth):
    queries = [QUERY_WORD, QUERY_SPACES, QUERY_NEWLINES, QUERY_FIELD]

    for i, query in enumerate(queries):
        _query = {'rules': [query]}
        await create_filter(_query, FILTER_DESCRIPTION, f'key{i}', f'cname{i}')

    await auth()
    response = await web_app_client.get('/v1/filter/', headers=HEADERS)

    assert response.status == 200

    data = await response.json()
    assert 'filters' in data

    assert len(data['filters']) == len(queries)


async def test_get_no_filters(web_app_client, auth):
    await auth()
    response = await web_app_client.get('/v1/filter/', headers=HEADERS)
    assert response.status == 200

    data = await response.json()
    assert 'filters' in data
    assert not data['filters']


async def test_no_combine_mode(web_app_client, auth):
    await auth()
    response = await web_app_client.get(
        '/v1/combine-filters/?mode=nonexistent', headers=HEADERS,
    )
    assert response.status == 400
    assert (await response.json())['code'] == 'WRONG_MODE'


async def test_creator(web_app_client, patch, auth):
    _filter = copy.deepcopy(BASIC_MATCH_FILTER_BODY)
    _filter['key'] = 'TAXI-1337'

    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    await auth()
    response = await web_app_client.post(
        f'/v1/filter/', json=_filter, headers=HEADERS,
    )
    assert response.status == 200

    content = await response.json()

    assert content['id'] == 1

    response = await web_app_client.get('/v1/filter/', headers=HEADERS)
    assert response.status == 200

    content = await response.json()

    assert len(content['filters']) == 1

    filter_information = content['filters'][0]['filter_information']

    assert filter_information['creator'] == 'testcreator'


async def test_strip(web_app_client, patch, auth):
    _filter = copy.deepcopy(BASIC_MATCH_FILTER_BODY)
    _filter['key'] = '  TAXI-1337  '

    await auth()

    @patch('logs_errors_filters.utils.st.validate_ticket')
    async def validate(key, context):
        return True

    response = await web_app_client.post(
        f'/v1/filter/', json=_filter, headers=HEADERS,
    )
    assert response.status == 200

    content = await response.json()

    assert content['id'] == 1

    response = await web_app_client.get('/v1/filter/', headers=HEADERS)
    assert response.status == 200

    content = await response.json()

    assert len(content['filters']) == 1

    filter_information = content['filters'][0]['filter_information']

    assert filter_information['key'] == _filter['key'].strip()

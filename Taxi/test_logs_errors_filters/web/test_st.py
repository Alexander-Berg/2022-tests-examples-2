# pylint: disable=unused-variable
import copy


BASIC_MATCH_FILTER_BODY = {
    'description': 'Description from test',
    'query': {'rules': [{'matchstring': 'some error message'}]},
}
HEADERS = {'X-YaTaxi-Api-Key': 'fake_token', 'X-Yandex-Login': 'testcreator'}


async def test_invalid_key(web_app_client, patch, auth):
    _filter = copy.deepcopy(BASIC_MATCH_FILTER_BODY)
    _filter['key'] = '  TAXI-1337  '

    await auth()

    @patch('taxi.clients.startrack.StartrackAPIClient.search')
    async def search(*args, **kwargs):
        return list()

    response = await web_app_client.post(
        f'/v1/filter/', json=_filter, headers=HEADERS,
    )
    assert response.status == 400

    content = await response.json()

    assert content['code'] == 'WRONG_TICKET'


async def test_valid_key(web_app_client, patch, auth):
    _filter = copy.deepcopy(BASIC_MATCH_FILTER_BODY)
    _filter['key'] = 'TAXI-1337'

    await auth()

    @patch('taxi.clients.startrack.StartrackAPIClient.search')
    async def search(*args, **kwargs):
        return list(['TAXI-1337'])

    response = await web_app_client.post(
        f'/v1/filter/', json=_filter, headers=HEADERS,
    )
    assert response.status == 200

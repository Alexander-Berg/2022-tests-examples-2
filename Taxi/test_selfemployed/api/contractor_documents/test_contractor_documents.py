import aiohttp.web


HEADERS = {
    'X-Request-Application-Version': '9.10',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-YaTaxi-Driver-Profile-Id': 'contractor_profile_id',
    'X-YaTaxi-Park-Id': 'park_id',
    'User-Agent': (
        'app:pro brand:yandex version:10.12 '
        'platform:ios platform_version:15.0.1'
    ),
}

QUERY = {'doc_name': 'doc_name'}


async def test_contractor_documents(
        mockserver, mock_fleet_parks, load_json, se_client,
):
    fleet_parks_check = load_json('fleet_parks_success.json')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == fleet_parks_check['request']['body']
        return aiohttp.web.json_response(fleet_parks_check['response'])

    @mockserver.json_handler(
        '/document-templator/v1/dynamic_documents/document_id/',
    )
    async def _document_id(request):
        return {'id': '5ff4901c583745e089e55bf1'}

    @mockserver.json_handler(
        '/document-templator/v1/dynamic_documents/last_valid/',
    )
    async def _last_valid(request):
        return {
            'id': '5ff4901c583745e089e55bf1',
            'name': 'qwe',
            'description': 'nice',
            'text': 'sometext',
            'version': 1,
            'modified_at': '20-02-2020',
        }

    response = await se_client.get(
        '/driver/v1/selfemployed/dynamic-documents',
        headers=HEADERS,
        params=QUERY,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'text': 'sometext'}

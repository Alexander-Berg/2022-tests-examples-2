import aiohttp.web
import pytest

ENDPOINT = '/api/v1/agreements/marketing-terms'


async def test_agreements_marketing_terms(
        web_app_client, headers, mock_parks, mock_api7,
):
    @mock_api7('/v1/parks/texts')
    async def _parks_texts(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        if request.query['text_type'] == 'driving_hiring':
            return aiohttp.web.json_response({'text': 'driving_hiring_text'})
        if request.query['text_type'] == 'marketing_terms':
            return aiohttp.web.json_response({'text': 'marketing_terms_text'})

    response = await web_app_client.get(ENDPOINT, headers=headers)
    assert response.status == 200

    data = await response.json()
    assert data == {'text': 'marketing_terms_textdriving_hiring_text'}


async def test_agreements_marketing_terms_driving_hiring_not_found(
        web_app_client, headers, mock_parks, mock_api7,
):
    @mock_api7('/v1/parks/texts')
    async def _parks_texts(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        if request.query['text_type'] == 'driving_hiring':
            return aiohttp.web.json_response(status=404, data={})
        if request.query['text_type'] == 'marketing_terms':
            return aiohttp.web.json_response({'text': 'marketing_terms_text'})

    response = await web_app_client.get(ENDPOINT, headers=headers)
    assert response.status == 200

    data = await response.json()
    assert data == {'text': 'marketing_terms_text'}


async def test_agreements_marketing_terms_marketing_terms_not_found(
        web_app_client, headers, mock_parks, mock_api7,
):
    @mock_api7('/v1/parks/texts')
    async def _parks_texts(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        if request.query['text_type'] == 'driving_hiring':
            return aiohttp.web.json_response({'text': 'driving_hiring_text'})

        if request.query['text_type'] == 'marketing_terms':
            return aiohttp.web.json_response(status=404, data={})

    response = await web_app_client.get(ENDPOINT, headers=headers)
    assert response.status == 200

    data = await response.json()
    assert data == {'text': 'driving_hiring_text'}


async def test_agreements_marketing_terms_not_found(
        web_app_client, headers, mock_parks, mock_api7,
):
    @mock_api7('/v1/parks/texts')
    async def _parks_texts(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        if request.query['text_type'] == 'driving_hiring':
            return aiohttp.web.json_response(status=404, data={})

        if request.query['text_type'] == 'marketing_terms':
            return aiohttp.web.json_response(status=404, data={})

    response = await web_app_client.get(ENDPOINT, headers=headers)
    assert response.status == 200

    data = await response.json()
    assert data == {'text': ''}


@pytest.mark.config(
    TAXI_FLEET_AGREEMENTS_MARKETING_TERMS_DOCUMENTS={
        'documents': [
            {
                'name': 'terms/Инза тест',
                'enable': True,
                'cities': [],
                'countries': [],
                'dbs': [],
            },
        ],
    },
)
async def test_agreements_marketing_terms_config(
        web_app_client, mock_parks, headers, mock_api7,
):
    @mock_api7('/v1/parks/texts')
    async def _parks_texts(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        if request.query['text_type'] == 'driving_hiring':
            return aiohttp.web.json_response({'text': 'driving_hiring_text'})
        if request.query['text_type'] == 'marketing_terms':
            return aiohttp.web.json_response({'text': 'marketing_terms_text'})

    @mock_api7('/v1/parks/dynamic-documents/document-id')
    async def _document_id(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        assert request.query['name'] == 'terms/Инза тест'
        return aiohttp.web.json_response({'id': 'test'})

    @mock_api7('/v1/parks/dynamic-documents/last-valid')
    async def _last_valid(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        return aiohttp.web.json_response(
            {'id': 'test', 'name': 'test', 'text': 'Test'},
        )

    response = await web_app_client.get(ENDPOINT, headers=headers)
    assert response.status == 200

    data = await response.json()
    assert data == {'text': 'Testdriving_hiring_text'}

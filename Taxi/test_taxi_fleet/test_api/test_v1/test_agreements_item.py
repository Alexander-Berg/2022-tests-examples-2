import aiohttp.web
import pytest

ENDPOINT = '/api/v1/agreements'

OK_PARAMS = [
    ('terms', 'terms/Москва', 'Test'),
    ('marketing_terms', 'marketing_terms/Москва', 'TestDrivingHiring'),
    ('taxi_offer', 'taxi_offer/rus', 'Test'),
    ('taxi_marketing_offer', 'taxi_marketing_offer/rus', 'Test'),
]


@pytest.mark.parametrize(
    'agreement_type, document_name, expected_response', OK_PARAMS,
)
async def test_agreements(
        web_app_client,
        mock_parks,
        headers,
        mock_api7,
        agreement_type,
        document_name,
        expected_response,
):
    @mock_api7('/v1/parks/dynamic-documents/document-id')
    async def _document_id(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        assert request.query['name'] == document_name
        return aiohttp.web.json_response({'id': 'test'})

    @mock_api7('/v1/parks/dynamic-documents/last-valid')
    async def _last_valid(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        return aiohttp.web.json_response(
            {'id': 'test', 'name': 'test', 'text': 'Test'},
        )

    @mock_api7('/v1/parks/texts')
    async def _parks_texts(request):
        assert request.query['text_type'] == 'driving_hiring'
        return aiohttp.web.json_response({'text': 'DrivingHiring'})

    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'agreement_type': agreement_type},
    )
    assert _document_id.times_called == 1
    assert _last_valid.times_called == 1
    assert _parks_texts.times_called == (
        1 if agreement_type == 'marketing_terms' else 0
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'text': expected_response}


FALLBACK_PARAMS = [
    ('terms', 1, 'Test'),
    ('marketing_terms', 2, 'TestDrivingHiring'),
    ('taxi_offer', 0, ''),
    ('taxi_marketing_offer', 0, ''),
]


@pytest.mark.parametrize(
    'agreement_type, parks_calls, expected_response', FALLBACK_PARAMS,
)
async def test_agreements_fallback(
        web_app_client,
        mock_parks,
        headers,
        mock_api7,
        agreement_type,
        parks_calls,
        expected_response,
):
    @mock_api7('/v1/parks/dynamic-documents/document-id')
    async def _document_id(request):
        return aiohttp.web.json_response(status=404, data={})

    @mock_api7('/v1/parks/texts')
    async def _parks_texts(request):
        if request.query['text_type'] == 'driving_hiring':
            return aiohttp.web.json_response({'text': 'DrivingHiring'})
        return aiohttp.web.json_response({'text': 'Test'})

    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'agreement_type': agreement_type},
    )

    assert _document_id.times_called == 1
    assert _parks_texts.times_called == parks_calls

    assert response.status == 200

    data = await response.json()
    assert data == {'text': expected_response}


@pytest.mark.config(
    TAXI_FLEET_AGREEMENTS_DOCUMENTS={
        'taxi_offer': [
            {
                'cities': ['Москва'],
                'countries': [],
                'dbs': [],
                'enable': True,
                'name': 'taxi_offer/mapped',
            },
        ],
    },
)
async def test_mapping(web_app_client, mock_parks, headers, mock_api7):
    @mock_api7('/v1/parks/dynamic-documents/document-id')
    async def _document_id(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        assert request.query['name'] == 'taxi_offer/mapped'
        return aiohttp.web.json_response({'id': 'test'})

    @mock_api7('/v1/parks/dynamic-documents/last-valid')
    async def _last_valid(request):
        assert request.query['park_id'] == headers['X-Park-Id']
        return aiohttp.web.json_response(
            {'id': 'test', 'name': 'test', 'text': 'Test'},
        )

    response = await web_app_client.get(
        ENDPOINT, headers=headers, params={'agreement_type': 'taxi_offer'},
    )
    assert _document_id.times_called == 1
    assert _last_valid.times_called == 1

    assert response.status == 200

    data = await response.json()
    assert data == {'text': 'Test'}

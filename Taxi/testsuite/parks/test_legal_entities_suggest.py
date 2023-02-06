import json

import pytest


ENDPOINT_URL = '/legal-entities/suggest'
DADATA_URL = '/dadata/suggestions/api/4_1/rs/findById/party'


@pytest.mark.parametrize(
    'ogrn, dadata_response, suggestions',
    [
        (
            '1',
            {
                'suggestions': [
                    {
                        'value': 'Petrov',
                        'data': {
                            'type': 'INDIVIDUAL',
                            'ogrn': '1',
                            'address': {'value': 'Loukhi'},
                        },
                    },
                ],
            },
            {
                'suggestions': [
                    {
                        'registration_number': '1',
                        'name': 'Petrov',
                        'address': 'Loukhi',
                        'legal_type': 'private',
                    },
                ],
            },
        ),
        ('2', {'suggestions': []}, {'suggestions': []}),
        (
            '3',
            {
                'suggestions': [
                    {
                        'value': 'OOO asd Head',
                        'data': {
                            'type': 'LEGAL',
                            'ogrn': '3',
                            'address': {'value': 'Msk Street 1'},
                        },
                    },
                    {
                        'value': 'OOO asd 1',
                        'data': {
                            'type': 'LEGAL',
                            'ogrn': '3',
                            'address': {'value': 'Spb Street 1'},
                        },
                    },
                ],
            },
            {
                'suggestions': [
                    {
                        'registration_number': '3',
                        'name': 'OOO asd Head',
                        'address': 'Msk Street 1',
                        'legal_type': 'legal',
                    },
                    {
                        'registration_number': '3',
                        'name': 'OOO asd 1',
                        'address': 'Spb Street 1',
                        'legal_type': 'legal',
                    },
                ],
            },
        ),
    ],
)
def test_ok(taxi_parks, mockserver, ogrn, dadata_response, suggestions):
    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        request.get_data()
        return dadata_response

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '123', 'registration_number': 'ogrn'},
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 200, response.text
    assert response.json() == suggestions


@pytest.mark.parametrize(
    'dadata_response, dadata_code',
    [('some error', 403), (json.dumps({'SuGGeSt': []}), 403)],
)
def test_post_dadata_failed(
        mockserver, taxi_parks, dadata_response, dadata_code,
):
    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        request.get_data()
        return mockserver.make_response(dadata_response, dadata_code)

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '123', 'registration_number': '1'},
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 503, response.text


def test_not_russia(mockserver, taxi_parks):
    @mockserver.json_handler(DADATA_URL)
    def mock_callback(request):
        return {}

    response = taxi_parks.post(
        ENDPOINT_URL, params={'park_id': '124', 'registration_number': '1'},
    )

    assert mock_callback.times_called == 0
    assert response.status_code == 400, response.text
    assert response.json() == {
        'error': {
            'code': 'unsupported_country',
            'text': 'unsupported country',
        },
    }

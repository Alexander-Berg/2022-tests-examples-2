# coding=utf-8
import pytest

ENDPOINT_URL = '/texts'
NOT_FOUND_RESPONSE = {'error': {'text': 'text not found'}}


@pytest.mark.parametrize(
    'park_id,text_type,expected_message',
    [
        ('', 'terms', 'parameter park_id must be set'),
        ('777', '', 'parameter text_type must be set'),
        (
            '777',
            'unknown_text_type',
            'text_type unknown_text_type is not supported',
        ),
    ],
)
def test_invalid_args(taxi_parks, park_id, text_type, expected_message):
    response = taxi_parks.get(
        ENDPOINT_URL, params={'park_id': park_id, 'text_type': text_type},
    )

    assert response.status_code == 400
    assert response.json()['error']['text'] == expected_message


@pytest.mark.parametrize(
    'park_id, text_type, expected_code, ' 'expected_response',
    [
        (
            '999',
            'marketing_terms',
            200,
            {'text': 'Маркетинговые условия Москвы'},
        ),  # terms for city
        ('999', 'terms', 200, {'text': ''}),  # empty terms for city
        (
            '777',
            'terms',
            404,
            NOT_FOUND_RESPONSE,
        ),  # terms for city with empty page
        (
            '222333',
            'terms',
            404,
            NOT_FOUND_RESPONSE,
        ),  # terms for city not found
        (
            '999',
            'usage_consent',
            200,
            {'text': 'Условия использования РФ'},
        ),  # terms for country
        (
            '999',
            'driving_hiring',
            200,
            {
                'text': (
                    'Условия найма РФ. '
                    '02.03.2019 '
                    '10:20:10.5 20:30:20.5 30:40:30.5'
                ),
            },
        ),  # driving hiring, country template
        (
            '222333',
            'driving_hiring',
            200,
            {
                'text': (
                    'Общие условия найма. '
                    '02.03.2019 '
                    '10:20:10.5 -:-:- -:-:-'
                ),
            },
        ),  # driving_hiring, fallback to global template
        (
            '777',
            'driving_hiring',
            200,
            {'text': ''},
        ),  # driving_hiring, no driver_hiring rules for park
    ],
)
def test_text(
        taxi_parks, park_id, text_type, expected_code, expected_response,
):
    response = taxi_parks.get(
        ENDPOINT_URL, params={'park_id': park_id, 'text_type': text_type},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'park_id, text_type, expected_cache_control',
    [
        ('999', 'terms', 'max-age=3600, must-revalidate'),  # text found
        ('777', 'terms', 'max-age=600, must-revalidate'),  # text not found
    ],
)
def test_cache_control(taxi_parks, park_id, text_type, expected_cache_control):
    response = taxi_parks.get(
        ENDPOINT_URL, params={'park_id': park_id, 'text_type': text_type},
    )

    assert response.headers['Cache-Control'] == expected_cache_control

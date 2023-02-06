import json

import pytest


@pytest.mark.parametrize(
    'input,output,status_code',
    [
        (
            {'currency_from': 'USD', 'currency_to': 'EUR', 'value': 123},
            {'value': 61.5},
            200,
        ),
        (
            {'currency_from': 'RUB', 'currency_to': 'EUR', 'value': 123},
            {'value': 1.23},
            200,
        ),
        (
            {'currency_from': 'USD', 'currency_to': 'RUB', 'value': 11},
            {'value': 550},
            200,
        ),
        (
            {'currency_from': 'RUB', 'currency_to': 'RUB', 'value': 123},
            {'value': 123},
            200,
        ),
    ],
)
def test_convert_base(taxi_antifraud, input, output, status_code):
    response = taxi_antifraud.post('v1/currency/convert', json=input)
    assert response.status_code == status_code
    response_json = json.loads(response.text)
    assert response_json == output


@pytest.mark.parametrize(
    'input',
    [
        {'currency_from': 'ZERO', 'currency_to': 'EUR', 'value': 123},
        {'currency_from': 'RUB', 'currency_to': 'ZERO', 'value': 123},
        {'currency_from': 'NOT_EXISTS', 'currency_to': 'EUR', 'value': 123},
        {'currency_from': 'RUB', 'currency_to': 'NOT_EXISTS', 'value': 123},
    ],
)
def test_convert_fail(taxi_antifraud, input):
    response = taxi_antifraud.post('v1/currency/convert', json=input)
    assert response.status_code == 404

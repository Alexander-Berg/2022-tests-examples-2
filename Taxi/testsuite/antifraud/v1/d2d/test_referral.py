import json

import pytest


@pytest.mark.parametrize(
    'input,output,status_code',
    [
        (
            {'license': 'fraud_license1', 'date': '2019-10-01T03:00:00+03:00'},
            {'frauder': True},
            200,
        ),
        (
            {'license': 'fraud_license2', 'date': '2019-10-01T03:00:00+03:00'},
            {'frauder': True},
            200,
        ),
        (
            {
                'license': 'not_fraud_license',
                'date': '2019-10-01T03:00:00+03:00',
            },
            {'frauder': False},
            200,
        ),
        (
            {'license': 'fraud_license1', 'date': '2019-10-01T02:59:59+03:00'},
            {'frauder': False},
            200,
        ),
        (
            {'license': 'fraud_license1', 'date': '2019-11-01T00:00:00+00:00'},
            {'frauder': False},
            200,
        ),
    ],
)
def test_limit(taxi_antifraud, input, output, status_code):
    response = taxi_antifraud.post('v1/d2d/referral', json=input)
    assert response.status_code == status_code
    response_json = json.loads(response.text)
    assert response_json == output

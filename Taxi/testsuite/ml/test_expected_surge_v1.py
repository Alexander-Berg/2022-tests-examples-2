# from __future__ import print_function

import pytest


@pytest.mark.parametrize(
    'request_file', ['request.json', 'request_no_user_id.json'],
)
def test_response1(taxi_ml, load_json, request_file):
    request = load_json(request_file)

    tariffs = [ci['tariff_class'] for ci in request['classes_info']]

    response = taxi_ml.post('expected_surge/v1', json=request)
    assert response.status_code == 200

    result = response.json()

    assert len(result['expected_surge']) == len(tariffs)

    for item in result['expected_surge']:
        assert item['tariff_class'] in tariffs
        assert item['value'] > 0

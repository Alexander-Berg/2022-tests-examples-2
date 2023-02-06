import json

import pytest


def _make_input(input):
    return {'personal_phone_id': input[0], 'currency': input[1]}


def _make_output(output):
    return {'value': output}


def _make_not_found(input):
    return {
        'error': {
            'text': 'user not found, personal_phone_id: {}'.format(input[0]),
        },
    }


@pytest.mark.parametrize(
    'input,output,status_code',
    [
        (('100', 'USD'), 1472.02, 200),
        (('101', 'USD'), None, 404),
        (('100', 'EUR'), 0.0, 200),
        (('100', 'MDL'), 91363636363.64, 200),
        (('100', 'UAH'), 0.0, 200),
        (('100', 'KZT'), 544432.17, 200),
    ],
)
def test_sum_base(taxi_antifraud, mockserver, input, output, status_code):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_personal(request):
        request_json = json.loads(request.get_data())
        if request_json['id'] == '100':
            return {
                'id': '1fab75363700481a9adf5e31c3b6e673',
                'value': '+79031520355',
            }
        if request_json['id'] == '101':
            return {
                'id': '1fab75363700481a9adf5e31c3b6e674',
                'value': '+79031520356',
            }

        return mockserver.make_response({}, 404)

    response = taxi_antifraud.post('v1/overdraft/sum', json=_make_input(input))
    assert response.status_code == status_code
    assert status_code in (200, 404)
    response_json = json.loads(response.text)
    if status_code == 200:
        response_json['value'] = round(response_json['value'], 2)
        assert response_json == _make_output(output)
    else:
        assert response_json == _make_not_found(input)


@pytest.mark.parametrize(
    'input,output,status_code', [(('100', 'USD'), 0, 200)],
)
@pytest.mark.filldb(antifraud_currency_rates='not_enough_data')
def test_sum_not_enough_data(
        taxi_antifraud, mockserver, input, output, status_code,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_personal(request):
        request_json = json.loads(request.get_data())
        if request_json['id'] == '100':
            return {
                'id': '1fab75363700481a9adf5e31c3b6e673',
                'value': '+79031520355',
            }

        return mockserver.make_response({}, 404)

    response = taxi_antifraud.post('v1/overdraft/sum', json=_make_input(input))
    assert response.status_code == status_code
    assert status_code in (200, 404)
    response_json = json.loads(response.text)
    if status_code == 200:
        response_json['value'] = round(response_json['value'], 2)
        assert response_json == _make_output(output)
    else:
        assert response_json == _make_not_found(input)

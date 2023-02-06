import json

import pytest


def _make_input(input):
    def _make_debts(debts):
        return [{'currency': debt[0], 'value': debt[1]} for debt in debts]

    obj = {'personal_phone_id': input[0], 'currency': input[1]}
    if len(input) == 3 and input[2]:
        obj['debts'] = _make_debts(input[2])
    return obj


def _make_output(output):
    return {'value': output}


def _make_user_not_found(user):
    return {
        'error': {
            'text': 'user not found, personal_phone_id: {}'.format(user),
        },
    }


def _make_currency_not_found(currency, rate=None):
    msg = 'currency rate not found: {}'.format(currency)
    if rate:
        msg += ', {}'.format(rate)
    return {'error': {'text': msg}}


@pytest.mark.parametrize(
    'input,output,status_code',
    [
        (
            ('100', 'USD', (('AAA', 100), ('BBB', 134), ('CCC', 2589))),
            163.29,
            (200,),
        ),
        (
            ('100', 'RUB', (('AAA', 100), ('BBB', 134), ('CCC', 3894))),
            0.0,
            (200,),
        ),
        (('100', 'RUB', (('BBB', 134), ('CCC', 1894))), 35000.8, (200,)),
        (('101', 'RUB', (('BBB', 1344), ('CCC', 4891))), 15588.3, (200,)),
        (('101', 'RUB', (('EUR', 2000),)), 52953.8, (200,)),
        (('101', 'RUB', (('EUR', 2000), ('USD', 100))), 46126.43, (200,)),
        (
            ('101', 'RUB', (('EUR', 2000), ('USD', 100), ('UZS', 50))),
            46125.63,
            (200,),
        ),
        (('101', 'EUR', (('EUR', 2000), ('USD', 100))), 627.37, (200,)),
        (
            ('101', 'UZS', (('EUR', 2000), ('USD', 100), ('UZS', 50))),
            2878623.82,
            (200,),
        ),
        (('101', 'RUB'), 200000.0, (200,)),
        (('NOT_EXISTS', 'RUB'), None, (404, 'user')),
        (('101', 'NOT_EXISTS1'), None, (404, 'currency', 'NOT_EXISTS1')),
        (
            (
                '101',
                'RUB',
                (
                    ('AAA', 10047),
                    ('BBB', 13493),
                    ('NOT_EXISTS2', 100500),
                    ('CCC', 389429),
                ),
            ),
            None,
            (404, 'currency', 'NOT_EXISTS2'),
        ),
        (
            (
                '100',
                'TO_SMALL1',
                (('AAA', 10047), ('BBB', 13493), ('CCC', 389429)),
            ),
            None,
            (404, 'currency', 'TO_SMALL1'),
        ),
        (
            (
                '100',
                'RUB',
                (
                    ('AAA', 10047),
                    ('TO_SMALL2', 100500),
                    ('BBB', 13493),
                    ('CCC', 389429),
                ),
            ),
            None,
            (404, 'currency', 'TO_SMALL2'),
        ),
    ],
)
def test_limit_base(taxi_antifraud, mockserver, input, output, status_code):
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

    response = taxi_antifraud.post(
        'v1/overdraft/limit', json=_make_input(input),
    )
    assert response.status_code == status_code[0]
    assert status_code[0] in (200, 404)
    response_json = json.loads(response.text)
    if status_code[0] == 200:
        response_json['value'] = round(response_json['value'], 2)
        assert response_json == _make_output(output)
    elif status_code[0] == 404:
        if status_code[1] == 'user':
            assert response_json == _make_user_not_found(input[0])
        elif status_code[1] == 'currency':
            assert response_json == _make_currency_not_found(*status_code[2:])

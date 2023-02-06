import datetime
import json

import pytest


@pytest.mark.parametrize(
    'candidates_json, payment_type, status_code, combo_discount, '
    'alternatives, order_info, combo_info',
    [
        (
            'candidates.json',
            'card',
            200,
            0.4,
            ['combo_inner', 'combo_outer'],
            {'calc': {'alternative_type': 'combo_inner'}},
            {'need_free': True},
        ),
    ],
)
@pytest.mark.experiments3(filename='config3.json')
async def test_v1_pricing_info(
        mockserver,
        load_json,
        taxi_combo_contractors,
        candidates_json,
        payment_type,
        status_code,
        combo_discount,
        mocked_time,
        alternatives,
        order_info,
        combo_info,
        testpoint,
):
    @mockserver.json_handler('/candidates/order-search')
    def _candidates(request):
        request_json = json.loads(request.get_data())
        etalon_request = {
            'point': [37.62, 55.75],
            'destination': [37.62, 56.00],
            'zone_id': 'moscow',
            'allowed_classes': ['econom'],
            'payment_method': payment_type,
            'timeout': 200,
            'order': {
                'user_id': 'user_12345',
                'user_phone_id': 'user_phone_12345',
            },
            'order_id': 'combo_pricing/',
        }
        etalon_request['order'].update(order_info)
        if combo_info:
            etalon_request['combo'] = combo_info
        assert request_json == etalon_request

        return mockserver.make_response(
            json=load_json(candidates_json), status=status_code,
        )

    @mockserver.json_handler('/driver_scoring/v2/score-candidates')
    def _driver_scoring(request):
        request_json = json.loads(request.get_data())
        assert request_json['intent'] == 'combo-pricing-info'
        search = request_json['request']['search']
        assert search['order_id'] == 'combo_pricing/'
        assert search['order']['calc']['alternative_type'] == 'combo_inner'
        candidates = request_json['request']['candidates']
        candidates.sort(key=lambda x: x['id'])
        response = []
        for i, candidate in enumerate(candidates):
            response.append(
                {'id': candidate['id'], 'score': i * 1000, 'penalty': 0},
            )
        response_json = {'candidates': response}

        return mockserver.make_response(json=response_json, status=200)

    now_time = datetime.datetime(2019, 3, 18, 00, 00, 00)
    mocked_time.set(now_time)

    alternatives = ['combo_inner', 'combo_outer']
    tariff_classes = ['econom', 'comfort']

    request_json = {
        'alternatives': alternatives,
        'request_id': '12345',
        'user_id': 'user_12345',
        'user_phone_id': 'user_phone_12345',
        'route': [[37.62, 55.75], [37.62, 56.00]],
        'tariff_zone': 'moscow',
        'tariff_classes': tariff_classes,
        'payment_type': payment_type,
    }

    response_pricing_info = await taxi_combo_contractors.post(
        '/v1/pricing-info', json=request_json,
    )

    assert response_pricing_info.status_code == status_code
    if status_code != 200:
        return

    alternatives_info = response_pricing_info.json()['tariff_classes'][
        'econom'
    ]

    alt_discounts = {
        'combo_inner': {
            'a': 1.0,
            'b': 2.0,
            'c': 15.0,
            'd': 25.0,
            'discount_function': 'default_combo_inner',
            'saved_supply_minutes': 0.0,
        },
        'combo_outer': {
            'discount_function': 'default_combo_outer',
            'saved_supply_minutes': 0.0,
        },
    }

    for alt_name, alt in alternatives_info.items():
        assert alt_name in alternatives
        assert alt == alt_discounts[alt_name]

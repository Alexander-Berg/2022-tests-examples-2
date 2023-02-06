import json

import pytest

from taxi_tests.utils import ordered_object


PERSONAL_PHONES_DB = [
    {'id': f'p0000000000000000000000{d}', 'value': f'+790611122{d}{d}'}
    for d in range(10)
]


@pytest.fixture()
def test_fixtures(mockserver, load_binary, load_json):
    class Context:
        mock_driver_eta = None
        driver_eta_requests = []

    context = Context()

    @mockserver.json_handler('/maps-router/route_jams/')
    def _mock_yamaps_router(request):
        return mockserver.make_response(
            load_binary('yamaps_response_2.protobuf'),
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        request_json = json.loads(request.get_data())
        context.driver_eta_requests.append(request_json)
        return load_json('eta_response.json')

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def _mock_pin_storage_create_pin(request):
        assert 'tariff_zone' in json.loads(request.get_data()).get('pin')

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _mock_personal(request):
        request_json = json.loads(request.get_data())
        assert 'id' in request_json

        db_record = next(
            (
                record
                for record in PERSONAL_PHONES_DB
                if record['id'] == request_json['id']
            ),
            None,
        )
        return db_record or mockserver.make_response({}, 404)

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_phones_store(request):
        request_json = json.loads(request.get_data())
        new_row = {
            'id': f'p000000000000000000000{len(PERSONAL_PHONES_DB)}',
            'value': request_json['value'],
        }
        PERSONAL_PHONES_DB.append(new_row)
        return new_row

    context.mock_driver_eta = _mock_driver_eta

    return context


def check_response(
        response_body,
        db,
        user_id,
        offer_prices,
        price_modifiers,
        taxi_class,
        cost_breakdown,
        details_tariff,
        price,
        price_with_currency,
        time,
):
    assert response_body['user_id'] == user_id

    assert 'offer' in response_body
    db_offers_request = {
        '_id': response_body['offer'],
        'user_id': response_body['user_id'],
    }
    assert db.order_offers.count(db_offers_request) == 1
    offer = db.order_offers.find_one(db_offers_request)

    assert offer['prices'] == offer_prices
    if price_modifiers is not None:
        assert offer['price_modifiers'] == price_modifiers
    else:
        assert 'price_modifiers' not in offer

    assert response_body['is_fixed_price'] is True

    currency_rules = response_body['currency_rules']
    assert currency_rules['code'] == 'RUB'
    assert currency_rules['sign'] == ''
    assert currency_rules['template'] == '$VALUE$ $SIGN$$CURRENCY$'
    assert currency_rules['text'] == 'rub'

    service_levels = response_body['service_levels']
    assert service_levels[0]['class'] == taxi_class
    response_cost_breakdown = service_levels[0]['cost_message_details'][
        'cost_breakdown'
    ]
    ordered_object.assert_eq(cost_breakdown, response_cost_breakdown, [''])

    assert service_levels[0]['price'] == price_with_currency
    assert service_levels[0]['time'] == time
    assert service_levels[0]['estimated_waiting']['message'] == '14 min'
    assert service_levels[0]['estimated_waiting']['seconds'] == 839
    assert service_levels[0]['details_tariff'] == details_tariff

    prices = offer['prices'][0]
    assert prices['price'] == price

import bson
import pytest


PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
    'X-AppMetrica-DeviceId': 'DeviceId',
}


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=['top_level:proxy', 'top_level:full_auction'],
)
@pytest.mark.config(
    CURRENCY_ROUNDING_RULES={
        '__default__': {'__default__': 1},
        'RUB': {'__default__': 1, 'full_auction': 100},
    },
)
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'contains',
            'init': {
                'value': 'rida_econom',
                'arg_name': 'tariff_classes',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='full_auction',
    consumers=['uservices/routestats/full_auction'],
    default_value={
        'enabled': True,
        'passenger_bid_settings': {
            'price_settings': {
                'template_tk': 'auction_flow.templates.price',
                'step': 100.0,
                'min_ratio': 0.4,
                'max_ratio': 1.8,
            },
            'display_settings': {
                'conditions': [
                    {
                        'price_ratio_gte': 1.2,
                        'settings': {
                            'background_color': '#E1F7C3',
                            'comment_tk': 'auction_flow.comment.great_price',
                        },
                    },
                    {
                        'price_ratio_gte': 0.8,
                        'settings': {
                            'background_color': '#FFDAC1',
                            'comment_tk': 'auction_flow.comment.bad_price',
                        },
                    },
                ],
                'default_settings': {'background_color': '#FFEAB2'},
            },
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'auction_flow.templates.price': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'auction_flow.comment.great_price': {'ru': 'Great price!'},
        'auction_flow.comment.bad_price': {'ru': 'Not so great price!'},
    },
)
async def test_plugin(
        taxi_routestats, mockserver, load_json, taxi_config, experiments3,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_response = load_json('protocol_response.json')
        return protocol_response

    @mockserver.json_handler('/candidates/order-search')
    def _candidates(request):
        candidates_response = load_json('candidates_response.json')
        return candidates_response

    order_offers_requests = []

    @mockserver.handler('/order-offers/v1/save-offer')
    def _order_offers(request):
        order_offers_requests.append(request.get_data())
        return mockserver.make_response(
            bson.BSON.encode(
                {'document': {'_id': '8d4c7053cf27b8abc13b96b2f54a4dcb'}},
            ),
            status=200,
        )

    request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats', request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    response = response.json()
    expected_response = load_json('expected_response.json')
    assert response == expected_response

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
@pytest.mark.routestats_plugins(names=['top_level:proxy', 'top_level:combo'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='people_combo_order_inner',
    consumers=['uservices/routestats'],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(filename='exp_combo_order.json')
@pytest.mark.experiments3(
    filename='exp_people_combo_order_passengers_number_alert.json',
)
@pytest.mark.translations(
    client_messages={
        'people_combo_order.inner.tariff_name': {'ru': 'inner tariff name'},
        'people_combo_order.inner.order_button_title': {
            'ru': 'inner order button title',
        },
        'people_combo_order.inner.search.title': {'ru': 'inner search title'},
        'people_combo_order.inner.search.subtitle': {
            'ru': 'inner search subtitle',
        },
        'people_combo_order.inner.alert.text': {'ru': 'inner alert text'},
        'people_combo_order.inner.alert.title': {'ru': 'inner alert title'},
        'people_combo_order.inner.alert.subtitle': {
            'ru': 'inner alert subtitle',
        },
        'people_combo_order.inner.alert.lower_text': {
            'ru': 'inner alert lower text',
        },
        'people_combo_order.inner.alert.confirm_button_text': {
            'ru': 'inner alert confirm button text',
        },
        'people_combo_order.inner.alert.decline_button_text': {
            'ru': 'inner alert decline button text',
        },
        'people_combo_order.outer.tariff_name': {'ru': 'outer tariff name'},
        'people_combo_order.outer.order_button_title': {
            'ru': 'outer order button title',
        },
        'people_combo_order.outer.search.title': {'ru': 'outer search title'},
        'people_combo_order.outer.search.subtitle': {
            'ru': 'outer search subtitle',
        },
        'people_combo_order.outer.alert.text': {'ru': 'outer alert text'},
        'people_combo_order.outer.alert.title': {'ru': 'outer alert title'},
        'people_combo_order.outer.alert.subtitle': {
            'ru': 'outer alert subtitle',
        },
        'people_combo_order.outer.alert.lower_text': {
            'ru': 'outer alert lower text',
        },
        'people_combo_order.outer.alert.confirm_button_text': {
            'ru': 'outer alert confirm button text',
        },
        'people_combo_order.outer.alert.decline_button_text': {
            'ru': 'outer alert decline button text',
        },
        'people_combo_order.inner.alert.error_text_too_many_passengers': {
            'ru': 'inner alert error too crowded text',
        },
        'people_combo_order.outer.alert.error_text_too_many_passengers': {
            'ru': 'inner alert error too crowded text',
        },
        'people_combo_order.outer.alert.buffer_list_item.subtitle': {
            'ru': 'buffer list item subtitle',
        },
        'people_combo_order.outer.alert.buffer_list_item.title': {
            'ru': 'buffer list item title, eta: %(eta)s',
        },
        'people_combo_order.search_screen.subtitle': {
            'ru': 'search in %(eta_from)s - %(eta_to)s',
        },
    },
)
@pytest.mark.parametrize(
    'candidates, expected_response',
    [
        pytest.param(
            None, 'combo_outer_response.json', id='combo_outer_enabled',
        ),
        pytest.param(
            [1, 2, 3], 'combo_inner_response.json', id='combo_inner_enabled',
        ),
    ],
)
@pytest.mark.parametrize(
    'combo_tariff',
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='exp_people_combo_tariff.json',
                )
            ),
            id='combo_tariff',
        ),
        pytest.param(False, id='combo_alt'),
    ],
)
@pytest.mark.config(ROUTESTATS_COMBO_ALLOWED_REQUIREMENTS=['coupon'])
async def test_plugin_combo(
        candidates,
        expected_response,
        taxi_routestats,
        mockserver,
        load_json,
        taxi_config,
        experiments3,
        combo_tariff,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_response = load_json('protocol_response.json')
        if combo_tariff:
            protocol_response['service_levels'].append({'class': 'combo'})

        return protocol_response

    @mockserver.json_handler('/candidates/order-search')
    def _candidates(request):
        assert 'payment_method' in request.json
        assert request.json['payment_method'] == 'card'
        candidates_response = load_json('candidates_response.json')
        if candidates is not None:
            candidates_response['candidates'] = candidates
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

    def get_alternatives(x):
        return x.get('alternatives', {}).get('options', [])

    response_alternatives = [i['type'] for i in get_alternatives(response)]
    if combo_tariff:
        expected_response = load_json('tariff_' + expected_response)
    else:
        expected_response = load_json(expected_response)

    expected_alternatives = [
        i['type'] for i in get_alternatives(expected_response)
    ]
    assert response_alternatives == expected_alternatives
    assert response == expected_response

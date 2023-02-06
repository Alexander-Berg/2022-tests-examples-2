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


@pytest.fixture(name='mock_tariffs_promotions')
async def _mock_tariffs_promotions(mockserver, testpoint):
    @mockserver.json_handler('/tariffs-promotions/v1/offer-data')
    def post_order_data(request):
        assert request.method == 'POST'
        offers = request.json['offers']
        assert offers == [
            {
                'data': {
                    'categories': [
                        {
                            'final_price': '366',
                            'name': 'econom',
                            'estimated_seconds': 300,
                            'surge_value': '2',
                        },
                        {
                            'final_price': '541',
                            'name': 'business',
                            'estimated_seconds': 300,
                            'surge_value': '2',
                        },
                    ],
                    'currency': 'RUB',
                    'route_info': {
                        'distance': '21018',
                        'points': [
                            {'title': 'point_a_title', 'type': 'a'},
                            {'title': 'point_b_title', 'type': 'b'},
                        ],
                        'time': '1423',
                    },
                },
                'offer_id': '901809f10aeab348494ee08b2155e039',
            },
            {
                'data': {
                    'categories': [
                        {
                            'estimated_waiting': '2',
                            'final_price': '151',
                            'name': 'econom',
                        },
                    ],
                    'currency': 'RUB',
                    'price_delta': '4.2',
                },
                'offer_id': '8d4c7053cf27b8abc13b96b2f54a4dcb',
            },
        ]

        return {}

    @testpoint('post_offer_data')
    def data_posted(data):
        pass

    yield None

    await data_posted.wait_call()
    assert post_order_data.times_called == 1


@pytest.mark.experiments3(
    filename='perfect_chain_response_decoration_exp.json',
)
@pytest.mark.experiments3(
    filename='perfect_chain_routestats_eta_fallback_exp.json',
)
@pytest.mark.experiments3(filename='perfect_chain_display_settings_exp.json')
@pytest.mark.experiments3(
    filename='perfect_chain_routestats_offers_info_exp.json',
)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:hide_ride_price',
        'top_level:perfect_chain',
        'top_level:combo',
        'top_level:tariffs-promotions-hook',
    ],
)
async def test_routestats_with_perfect_chain(
        taxi_routestats,
        mockserver,
        load_json,
        experiments3,
        mock_tariffs_promotions,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        assert (
            'perfect_chain'
            in request.json['feature_flags']['prepare_altoffers']
        )
        return load_json('protocol_response.json')

    @mockserver.json_handler('/order-offers/v1/save-offer')
    def _mock_save_offer(_):
        return mockserver.make_response(
            bson.BSON.encode(
                {'document': {'_id': '8d4c7053cf27b8abc13b96b2f54a4dcb'}},
            ),
            200,
        )

    @mockserver.json_handler('/alt-offer-discount/v1/offers-info')
    def _mock_offers_info(request):
        assert request.json == {
            'request_id': 'request_id',
            'alternatives': [{'type': 'perfect_chain'}],
        }
        return {
            'offers_info': [
                {'alternative_type': 'perfect_chain', 'info': {'eta': 127}},
            ],
        }

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )

    def get_perfect_chain(options):
        for option in options:
            if option['type'] == 'perfect_chain':
                return option
        return False

    assert response.status_code == 200

    alternatives_option = response.json()['alternatives']['options']
    assert len(alternatives_option) == 2

    perfect_chain = get_perfect_chain(alternatives_option)
    assert perfect_chain['type'] == 'perfect_chain'

    service_level = perfect_chain['service_levels'][0]
    assert service_level['estimated_waiting']['seconds'] == 120
    assert service_level['estimated_waiting']['message'] == '2 мин'
    assert (
        service_level['selector']['tooltip']
        == 'ждать примерно 2 минут ИЛИ ждать примерно 2 минут'
    )
    assert service_level['paid_options'] is None

    icon = service_level['selector']['icon']
    assert icon['url'] == 'new_url'

    assert perfect_chain['show_in_tariff_selector'] is False
    assert perfect_chain['use_for_promos_on_summary'] is True

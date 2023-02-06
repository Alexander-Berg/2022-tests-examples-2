import json

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
@pytest.mark.parametrize(
    'resp_file', ['protocol_response.json', 'protocol_response_2.json'],
)
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'brandings:plus',
    ],
)
@pytest.mark.config(
    PLUS_SUMMARY_PROMOTION_SETTING={
        'rus': {
            'discount': 0.1,
            'min_price': 100,
            'categories': ['econom', 'business'],
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'routestats.brandings.plus_promo_v2.title': {
            'ru': 'Может быть начислено %(value)s баллов',
        },
    },
)
async def test_basic_protocol_extend_brandings(
        resp_file, taxi_routestats, mockserver, load_json,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_request = json.loads(request.get_data())
        protocol_supported = protocol_request.get('supported', [])
        service_supported = service_request.get('supported', [])
        assert len(protocol_supported) == len(service_supported)
        for i, service_supported in enumerate(service_supported):
            assert protocol_supported[i]['type'] == service_supported['type']

        return {
            'internal_data': load_json('internal_data.json'),
            **load_json(resp_file),
        }

    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _plus_wallet(request):
        return {
            'balances': {
                'balance': '4771.0000',
                'currency': 'RUB',
                'wallet_id': 'wallet_id',
            },
        }

    service_request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats', service_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    service_levels = response.json()['service_levels']
    econom = [x for x in service_levels if x['class'] == 'econom'][0]
    plus_promotion = [
        x for x in econom['brandings'] if x['type'] == 'plus_promotion'
    ][0]

    assert plus_promotion == {
        'title': 'Может быть начислено 141 баллов',
        'type': 'plus_promotion',
        'icon': 'plus_promo_big_cashback',
    }


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize('resp_file', ['protocol_response.json'])
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'brandings:plus',
    ],
)
@pytest.mark.config(
    PLUS_SUMMARY_PROMOTION_SETTING={
        'rus': {
            'discount': 0.1,
            'min_price': 100,
            'categories': ['econom', 'business'],
        },
    },
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2}},
)
@pytest.mark.translations(
    client_messages={
        'routestats.brandings.plus_promo_v2.title': {
            'ru': 'Может быть начислено %(value)s баллов',
        },
    },
)
async def test_brandings_rounding(
        taxi_routestats, mockserver, load_json, resp_file,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_request = json.loads(request.get_data())
        protocol_supported = protocol_request.get('supported', [])
        service_supported = service_request.get('supported', [])
        assert len(protocol_supported) == len(service_supported)
        for i, service_supported in enumerate(service_supported):
            assert protocol_supported[i]['type'] == service_supported['type']

        return {
            'internal_data': load_json('internal_data.json'),
            **load_json(resp_file),
        }

    @mockserver.json_handler('/plus-wallet/v1/balances')
    def _plus_wallet(request):
        return {
            'balances': {
                'balance': '4771.0000',
                'currency': 'RUB',
                'wallet_id': 'wallet_id',
            },
        }

    service_request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats', service_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    service_levels = response.json()['service_levels']
    econom = [x for x in service_levels if x['class'] == 'econom'][0]
    plus_promotion = [
        x for x in econom['brandings'] if x['type'] == 'plus_promotion'
    ][0]

    assert plus_promotion == {
        'title': 'Может быть начислено 141 баллов',
        'type': 'plus_promotion',
        'icon': 'plus_promo_big_cashback',
    }


@pytest.mark.experiments3(filename='exp3_cashback_brandings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=['top_level:brandings', 'brandings:cashbacks'],
)
@pytest.mark.config(
    PLUS_SUMMARY_PROMOTION_SETTING={
        'rus': {
            'discount': 0.1,
            'min_price': 100,
            'categories': ['econom', 'business'],
        },
    },
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2}},
)
@pytest.mark.translations(
    client_messages={
        'routestats.brandings.plus_promo_v2.title': {
            'ru': 'Может быть начислено %(value)s баллов',
        },
        'fintech_yandex_card_routestats.title': {'ru': '+5% кешбэка'},
        'fintech_yandex_card_routestats.subtitle': {
            'ru': 'От использования Яндекс.Карты',
        },
        'fintech_yandex_card_routestats.value': {'ru': '10%'},
    },
)
async def test_configure_brandings_by_marketing_sponsors(
        taxi_routestats, mockserver, load_json,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_request = json.loads(request.get_data())
        protocol_supported = protocol_request.get('supported', [])
        service_supported = service_request.get('supported', [])
        assert len(protocol_supported) == len(service_supported)
        for i, service_supported in enumerate(service_supported):
            assert protocol_supported[i]['type'] == service_supported['type']

        resp = {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_2.json'),
        }
        return resp

    service_request = load_json('request.json')
    response = await taxi_routestats.post(
        'v1/routestats', service_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200

    service_levels = response.json()['service_levels']
    econom = [level for level in service_levels if level['class'] == 'econom'][
        0
    ]

    comfortplus = [
        level for level in service_levels if level['class'] == 'comfortplus'
    ][0]

    econom_cashback_brandings = [
        branding
        for branding in econom['brandings']
        if branding['type'] == 'cashback'
    ]
    comfortplus_cashback_brandings = [
        branding
        for branding in comfortplus['brandings']
        if branding['type'] == 'cashback'
    ]

    assert (
        len(econom_cashback_brandings)
        == len(comfortplus_cashback_brandings)
        == 1
    )

    econom_branding = econom_cashback_brandings[0]
    comfortplus_branding = comfortplus_cashback_brandings[0]

    assert econom_branding == {
        'icon': 'plus_points_extra_gradient',
        'type': 'cashback',
        'extra': {'banner_id': 'fintech_banner_id'},
        'title': '+5% кешбэка',
        'subtitle': 'От использования Яндекс.Карты',
        'action': 'show_banner',
        'value': '+93',
        'tooltip': {'text': 'кэшбэк за поездку'},
    }

    assert comfortplus_branding == {
        'icon': 'plus_points_extra_gradient',
        'type': 'cashback',
        'extra': {'banner_id': 'fintech_banner_id'},
        'title': '+5% кешбэка',
        'subtitle': 'От использования Яндекс.Карты',
        'action': 'show_banner',
        'value': '10%',
        'tooltip': {'text': 'кэшбэк за поездку'},
    }

import pytest
import json
PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
}

TARIFF_KEYSET_FOR_ALTPINS_B = {
    'altpin_b.confirmation_screen.walk.walk_time': {'ru': '%(time)s'},
    'altpin_b.confirmation_screen.title': {'ru': 'Где заканачивается поездка'},
    'altpin_b.confirmation_screen.modal.title': {
        'ru': 'Дешевле на -%(price_delta)s',
    },
    'altpin_b.confirmation_screen.modal.description.badge.text': {
        'ru': '-%(price_delta)s',
    },
    'altpin_b.confirmation_screen.modal.description.title': {
        'ru': '%(altpin_address)s',
    },
    'altpin_b.confirmation_screen.modal.description.subtitle': {
        'ru': '%(time)s пешком',
    },
    'altpin_b.confirmation_screen.alternative_bubble.subtitle': {
        'ru': 'В %(arrival_local_time)s',
    },
    'altpin_b.confirmation_screen.destination_bubble.title': {
        'ru': '%(altpin_original_address)s',
    },
    'altpin_b.confirmation_screen.modal.buttons.close.text': {'ru': 'Нет'},
    'altpin_b.confirmation_screen.modal.buttons.confirm.text': {'ru': 'Да'},
}


@pytest.mark.translations(tariff=TARIFF_KEYSET_FOR_ALTPINS_B)
@pytest.mark.experiments3(filename='exps_for_altpins_b.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:sdc',
        'top_level:proxy',
        'top_level:brandings',
        'top_level:altpins_b',
        'brandings:proxy',
        'brandings:tariff_unavailable_branding',
        'top_level:brandings:tariff_unavailable_branding',
    ],
)
@pytest.mark.now('2022-02-18T10:10:00Z')
async def test_plugin_altpins_b(taxi_routestats, mockserver, load_json):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return load_json('protocol_response.json')

    @mockserver.json_handler('/order-core/v1/tc/active-orders')
    def _order_core(request):
        return {'orders': []}

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert len(response.json()['alternatives']['options']) == 1
    alternative = response.json()['alternatives']['options'][0]
    assert alternative == load_json('expected_alternative.json')

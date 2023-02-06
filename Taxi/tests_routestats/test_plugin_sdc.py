import pytest

PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
}


@pytest.mark.translations(
    client_messages={
        'routestats.sdc.tariff_unavailable.out_of_schedule.title': {
            'ru': 'Беспилотник не работает по расписанию',
        },
        'routestats.sdc.tariff_unavailable.out_of_schedule.subtitle': {
            'ru': '',
        },
        'sdc.summary_branding.tariff_unavailable.out_of_schedule.title': {
            'ru': 'Беспилотник не работает по расписанию',
        },
        'routestats.sdc.tariff_card.bullet.title': {
            'ru': 'Беспилотники самые лучшие',
        },
        'routestats.sdc.tariff_card.bullet.subtitle': {
            'ru': 'Довезут вас до дома',
        },
        'routestats.sdc.tariff_card.bullet.icon_tag': {'ru': 'Иконка_тег'},
    },
)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:sdc',
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'brandings:tariff_unavailable_branding',
        'top_level:brandings:tariff_unavailable_branding',
    ],
)
@pytest.mark.experiments3(filename='exp_sdc_routestats_summary_settings.json')
@pytest.mark.experiments3(
    filename='exp_routestats_tariff_unavailable_brandings.json',
)
@pytest.mark.experiments3(filename='exp_enable_sdc_2_out_of_schedule.json')
@pytest.mark.now('2022-02-18T02:00:00Z')
async def test_plugin_sdc(taxi_routestats, mockserver, load_json):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200

    sdc_level = next(
        (
            level
            for level in response.json().get('service_levels', [])
            if level['name'] == 'Беспилотник'
        ),
        None,
    )
    assert sdc_level == load_json('response_out_of_schedule.json')

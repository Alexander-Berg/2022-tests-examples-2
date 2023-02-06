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
@pytest.mark.translations(
    client_messages={
        'routestats.plugin.surge.order_button_title': {'ru': 'Поехали'},
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:proxy', 'top_level:surge'])
@pytest.mark.experiments3(filename='exp_surge_communications.json')
async def test_plugin_surge(taxi_routestats, mockserver, load_json):
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
    assert response.json() == load_json('response.json')


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.translations(
    client_messages={
        'routestats.plugin.surge.order_button_title': {'ru': 'Поехали'},
    },
)
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:proxy', 'top_level:surge'])
@pytest.mark.experiments3(filename='exp_surge_communications.json')
@pytest.mark.config(ROUTESTATS_HIDE_SURGE_FOR_ZERO_PRICE=True)
async def test_hide_surge_info(taxi_routestats, mockserver, load_json):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        resp = load_json('protocol_response.json')

        # set econom final_price to 0
        resp['internal_data']['service_levels_data'][0]['final_price'] = '0'

        return resp

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200

    expected_response = load_json('response.json')

    # delete econom paid_options
    del expected_response['service_levels'][0]['paid_options']
    del expected_response['service_levels'][0]['title']

    assert response.json() == expected_response


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:proxy', 'top_level:surge'])
@pytest.mark.experiments3(filename='exp_surge_communications.json')
async def test_disable_surge_info_for_sdc(
        taxi_routestats, mockserver, load_json,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        resp = load_json('protocol_response.json')

        # substitute all service levels for selfdriving
        resp['service_levels'] = [load_json('protocol_response_sdc_sl.json')]

        return resp

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )
    assert response.status_code == 200

    # check that sdc level is unchanged from protocol response
    expected_response = load_json('protocol_response_sdc_sl.json')
    assert response.json()['service_levels'][0] == expected_response

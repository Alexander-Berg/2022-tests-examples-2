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
@pytest.mark.routestats_plugins(names=['top_level:mock_eta'])
@pytest.mark.experiments3(filename='mock_eta_exp.json')
@pytest.mark.now('2022-04-12T14:00:00+00:00')
async def test_mock_eta(load_json, mockserver, testpoint, taxi_routestats):
    protocol_response = load_json('protocol_response.json')

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **protocol_response,
        }

    estimated_waiting = dict()

    @testpoint('approximation_eta')
    def _approximation_eta(data):
        nonlocal estimated_waiting
        estimated_waiting[data['level_class']] = data['mean']

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )

    assert response.status_code == 200
    assert estimated_waiting == {
        'econom': 1230.0,
        'business': 1300.0,
        'cargo': 1300.0,
        'child_tariff': 1300.0,
        'comfortplus': 1300.0,
        'courier': 1300.0,
        'express': 1300.0,
        'mkk_antifraud': 1300.0,
        'promo': 1300.0,
    }

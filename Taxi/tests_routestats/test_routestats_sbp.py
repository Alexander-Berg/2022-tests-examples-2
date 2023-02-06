from typing import Any
from typing import Dict

import pytest

MESSAGE_RU = 'Установите пункт назначения или смените метод оплаты'
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
TARIFF_UNAVAILABLE = 'tariff_unavailable'
BLACKLISTED_TARIFF = 'business'


def _get_disabled_tariffs(response) -> Dict[str, Any]:
    result: Dict[str, Any] = dict()
    for level in response['service_levels']:
        tariff_unavailable = level.get(TARIFF_UNAVAILABLE)
        if tariff_unavailable is not None:
            tariff = level['class']
            result[tariff] = tariff_unavailable
    return result


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(names=['top_level:sbp_tariff_unavailable'])
@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.need_point_b_for_sbp': {
            'ru': MESSAGE_RU,
        },
    },
)
@pytest.mark.config(
    SBP_TARIFF_UNAVAILABLE_BLACKLIST={'service_levels': [BLACKLISTED_TARIFF]},
)
async def test_sbp(load_json, mockserver, taxi_routestats):
    protocol_response = load_json('protocol_response.json')
    protocol_tariffs_unavailable = _get_disabled_tariffs(protocol_response)

    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **protocol_response,
        }

    response = await taxi_routestats.post(
        'v1/routestats', load_json('request.json'), headers=PA_HEADERS,
    )

    assert response.status_code == 200
    body = response.json()

    for level in body['service_levels']:
        tariff = level['class']
        if tariff in protocol_tariffs_unavailable:
            assert (
                level[TARIFF_UNAVAILABLE]
                == protocol_tariffs_unavailable[tariff]
            )
            continue
        if tariff == BLACKLISTED_TARIFF:
            assert TARIFF_UNAVAILABLE not in level
            continue
        tariff_unavailable = level[TARIFF_UNAVAILABLE]
        assert tariff_unavailable == {
            'code': 'sbp_not_available_without_point_b',
            'message': MESSAGE_RU,
        }

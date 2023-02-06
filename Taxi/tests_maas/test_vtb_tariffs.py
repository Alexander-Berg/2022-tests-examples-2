import pytest

import const


def _make_maas_tariffs():
    maas_tariff_settings_1 = const.MAAS_TARIFF_SETTINGS.copy()
    maas_tariff_settings_1.update(trips_count=5)

    maas_tariff_settings_2 = const.MAAS_TARIFF_SETTINGS.copy()
    maas_tariff_settings_2.update(sale_allowed=False)

    maas_tariff_settings_3 = const.MAAS_TARIFF_SETTINGS.copy()
    maas_tariff_settings_3.update(trips_count=20)

    return {
        'maas_tariff_1': maas_tariff_settings_1,
        'maas_tariff_2': maas_tariff_settings_2,
        'maas_tariff_3': maas_tariff_settings_3,
    }


def _check_response(response_body, expected_tariffs):
    assert 'tariffs' in response_body
    response_tariffs = {
        tariff['id']: tariff for tariff in response_body['tariffs']
    }
    assert response_tariffs == expected_tariffs


@pytest.mark.translations(
    client_messages={
        'maas.tariffs.maas_s.outer_description': {
            'ru': 'Описание такси тарифа для ВТБ',
            'en': 'MaaS tariff description for VTB',
        },
    },
)
@pytest.mark.config(MAAS_TARIFFS=_make_maas_tariffs())
async def test_simple(taxi_maas, load_json):
    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    response = await taxi_maas.post('/vtb/v1/tariffs', headers=headers)

    assert response.status == 200
    _check_response(response.json(), load_json('expected_tariffs.json'))

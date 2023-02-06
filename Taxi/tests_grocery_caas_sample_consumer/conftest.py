import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_caas_sample_consumer_plugins import *  # noqa: F403 F401


@pytest.fixture
def default_auth_headers():
    return {
        'X-YaTaxi-User': 'eats_user_id=12345',
        'X-YaTaxi-Session': 'taxi:taxi-user-id',
        'X-Yandex-UID': 'yandex-uid',
        'X-AppMetrica-DeviceId': 'AppMetricaDeviceId',
        'Accept-Language': 'ru-RU',
    }


@pytest.fixture(name='add_depots', autouse=True)
def mock_grocery_depots(mockserver, grocery_depots):
    grocery_depots.add_depot(
        depot_id='store11xx',
        depot_test_id=10,
        country_iso3='RUS',
        country_iso2='RU',
        region_id=223,
        timezone='Europe/Moscow',
        location=[10, 10],
        phone_number='+78007700461',
        currency='RUB',
        tin='123456',
        address='depot address 1',
        company_id='company-id',
        company_type='yandex',
    )

    grocery_depots.add_depot(
        depot_id='store22xx',
        depot_test_id=20,
        country_iso3='RUS',
        country_iso2='RU',
        region_id=223,
        timezone='Europe/Moscow',
        location=[11, 11],
        phone_number='+78007700462',
        currency='RUB',
        tin='223456',
        address='depot address',
        company_id='company-id',
        company_type='yandex',
    )

    grocery_depots.add_depot(
        depot_id='store33xx',
        depot_test_id=30,
        country_iso3='GBR',
        country_iso2='GB',
        region_id=334,
        timezone='Europe/London',
        location=[12, 12],
        phone_number='+448007700463',
        currency='GBP',
        tin='323456',
        address='depot address 2',
        company_id='company-id',
        company_type='yandex',
    )

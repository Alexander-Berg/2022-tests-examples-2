import os

# pylint: disable=import-error
from taximeter_emulator import settings


# BAKU = settings.City((49.794693, 40.309079), (49.943803, 40.435535))
TBILISI = settings.City((44.753057, 41.672947), (44.846078, 41.764157))
VILNIUS = settings.City((25.196992, 54.645855), (25.319493, 54.732625))
HUTORSKAY_STREET = settings.City((37.576, 55.802), (37.579, 55.804))
BUTOVO = settings.City((37.53, 55.54), (37.54, 55.55))


class IntegrationTestsSettings(settings.BaseSettings):
    def __init__(self):
        super().__init__()
        self.core_host = 'http://taximeter-core.taxi.yandex.net'
        self.utils_host = 'http://dev-utils.taxi.yandex.net'
        self.driver_protocol_host = 'http://driver-protocol.taxi.yandex.net'
        self.driver_login_host = 'http://driver-login.taxi.yandex.net'
        self.router_host = None
        self.gps_set_url = 'http://yagr.taxi.yandex.net/driver/position/store'
        self.driver_v1_position_store_url = (
            'http://yagr.taxi.yandex.net/driver/v1/position/store'
        )
        self.login_pool_size = 0
        self.parks = [
            settings.TaxiPark(
                HUTORSKAY_STREET,
                'f6d9f7e55a9144239f706f15525ff2bb',
                ['+79001110000', '+79001110001', '+79001110002'],
            ),
            settings.TaxiPark(
                settings.MOSCOW,
                'f6d9f7e55a9144239f706f15525ff2a9',
                ['+79001111%03d' % i for i in range(250)],
            ),
            settings.TaxiPark(
                BUTOVO,
                '1b0512eca97c4a1bbe53b50bdc0d5179',
                ['+79005555000', '+79005555001'],
            ),
            settings.TaxiPark(
                BUTOVO,
                '744b7ef014054c08b756c75cc64cf300',
                ['+79005555002', '+79005555003'],
            ),
            settings.TaxiPark(
                BUTOVO,
                '8fb027fe6dd14b5dae33d1d182978d69',
                ['+79005555004', '+79005555005'],
            ),
        ]
        self.driver_status_host = 'http://driver-status.taxi.yandex.net'
        self.taximeter_proxy_host = 'https://taximeter.yandex.rostaxi.org'
        self.pricing_url = 'http://pricing-data-preparer.taxi.yandex.net'
        if os.getenv('EATS_ENV'):
            self.parks = [
                settings.TaxiPark(
                    settings.MOSCOW_EATS,
                    'e3f66bc7ca3648e5a7c81ca01130d30c',
                    ['+79006666621'],
                    courier_type=settings.CourierType.EATS,
                    shift_type=settings.ShiftType.EDA,
                ),
            ]
            self.driver_profiles_host = (
                'http://driver-profiles.taxi.yandex.net'
            )
            self.eats_picker_orders_host = (
                'http://eats-picker-orders.eda.yandex.net'
            )
            self.driver_v1_position_store_url = (
                'http://yagr.taxi.yandex.net/driver/v1/position/store'
            )
            self.tinkoff_stub_host = (
                'https://secured-openapi.business.tinkoff.ru'
            )
            self.taximeter_proxy_host = 'http://taximeter.yandex.rostaxi.org'

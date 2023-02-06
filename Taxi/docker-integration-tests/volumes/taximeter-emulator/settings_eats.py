# pylint: disable=import-error
from taximeter_emulator import settings


class IntegrationTestsSettings(settings.BaseSettings):
    def __init__(self):
        super().__init__()
        self.core_host = 'http://taximeter-core.taxi.yandex.net'
        self.utils_host = 'http://dev-utils.taxi.yandex.net'
        self.driver_protocol_host = 'http://driver-protocol.taxi.yandex.net'
        self.driver_login_host = 'http://driver-login.taxi.yandex.net'
        self.router_host = None
        self.gps_set_url = 'http://yagr.taxi.yandex.net/driver/position/store'
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
        self.login_pool_size = 0
        self.parks = [
            settings.TaxiPark(
                settings.MOSCOW_EATS,
                'e3f66bc7ca3648e5a7c81ca01130d30c',
                ['+79006666621'],
                courier_type=settings.CourierType.EATS,
                shift_type=settings.ShiftType.EDA,
            ),
        ]
        self.driver_status_host = 'http://driver-status.taxi.yandex.net'
        self.taximeter_proxy_host = 'http://taximeter.yandex.rostaxi.org'
        self.pricing_url = 'http://pricing-data-preparer.taxi.yandex.net'

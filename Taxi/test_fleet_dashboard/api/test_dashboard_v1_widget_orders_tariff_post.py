import aiohttp.web
import pytest


ENDPOINT = '/dashboard/v1/widget/orders/tariff'


FLEET_DASHOARD_KEYSET = {
    'widget.orders_tariff.series.uber': {'ru': 'Убер'},
    'widget.orders_tariff.series.econom': {'ru': 'Эконом'},
    'widget.orders_tariff.series.comfort': {'ru': 'Комфорт'},
    'widget.orders_tariff.series.business': {'ru': 'Бизнесс'},
    'widget.orders_tariff.series.minivan': {'ru': 'Минивен'},
    'widget.orders_tariff.series.vip': {'ru': 'VIP'},
    'widget.orders_tariff.series.wagon': {'ru': 'Грузовое'},
    'widget.orders_tariff.series.comfort_plus': {'ru': 'Комфорт+'},
    'widget.orders_tariff.series.courier': {'ru': 'Курьер'},
    'widget.orders_tariff.series.express': {'ru': 'Експресс'},
    'widget.orders_tariff.series.pool': {'ru': 'Пул'},
    'widget.orders_tariff.series.start': {'ru': 'Старт'},
    'widget.orders_tariff.series.standard': {'ru': 'Стандарт'},
    'widget.orders_tariff.series.ultimate': {'ru': 'Ультима'},
    'widget.orders_tariff.series.maybach': {'ru': 'Майбах'},
    'widget.orders_tariff.series.premium_van': {'ru': 'Премиум_ван'},
    'widget.orders_tariff.series.premium_suv': {'ru': 'Премиум_сав'},
    'widget.orders_tariff.series.suv': {'ru': 'Сав'},
    'widget.orders_tariff.series.promo': {'ru': 'Промо'},
    'widget.orders_tariff.series.personal_driver': {
        'ru': 'Персональный водитель',
    },
    'widget.orders_tariff.series.cargo': {'ru': 'Доставка'},
}


FLEET_DASHBOARD_WIDGET_SERIES = {
    'widgets': [
        {
            'id': 'orders_tariff',
            'series': {
                'yandex_fleet': [
                    'successful_uber',
                    'successful_econom',
                    'successful_comfort',
                    'successful_business',
                    'successful_minivan',
                    'successful_vip',
                    'successful_wagon',
                    'successful_comfort_plus',
                    'successful_courier',
                    'successful_express',
                    'successful_pool',
                    'successful_start',
                    'successful_standard',
                    'successful_ultimate',
                    'successful_maybach',
                    'successful_premium_van',
                    'successful_premium_suv',
                    'successful_suv',
                    'successful_promo',
                    'successful_personal_driver',
                    'successful_cargo',
                ],
                'yango_fleet': ['successful_econom', 'successful_comfort'],
            },
        },
    ],
}


def build_headers(park_id) -> dict:
    return {
        'X-Ya-User-Ticket': 'user_ticket',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-Login': 'tarasalk',
        'X-Yandex-UID': '123',
        'X-Park-Id': park_id,
        'X-Real-IP': '127.0.0.1',
        'Accept-Language': 'ru',
    }


@pytest.mark.parametrize(
    'success_json, park_id',
    [
        ('success_saas.json', 'c5cdea22ad6b4e4da8f3fdbd4bddc2e7'),
        ('success.json', '7ad36bc7560449998acbe2c57a75c293'),
    ],
)
@pytest.mark.config(
    FLEET_DASHBOARD_WIDGET_SERIES=FLEET_DASHBOARD_WIDGET_SERIES,
)
@pytest.mark.translations(fleet_dashboard=FLEET_DASHOARD_KEYSET)
async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_driver_orders_metrics,
        load_json,
        success_json,
        park_id,
):
    stub = load_json(success_json)

    @mock_driver_orders_metrics('/v1/parks/orders/metrics-by-intervals')
    async def _orders_metrics_by_interval(request):
        assert request.json == stub['metrics']['request']
        return aiohttp.web.json_response(stub['metrics']['response'])

    response = await web_app_client.post(
        ENDPOINT,
        headers=build_headers(park_id=park_id),
        json=stub['service']['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service']['response']

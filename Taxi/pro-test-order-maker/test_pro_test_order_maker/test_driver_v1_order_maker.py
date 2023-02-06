import pytest


async def test_ok(web_app_client):
    res = await web_app_client.post(
        '/ptom/driver/v1/make-order',
        json={
            'payment_type': 'cash',
            'category': 'econom',
            'park_id': 'park_id',
            'driver_id': 'driver_id',
            'user_phone': '+70009325297',
            'route': [{'lat': 33.6, 'lon': 55.1}],
        },
    )

    assert res.status == 200


async def test_order_commit_price_changed(web_app_client, mockserver):
    @mockserver.json_handler('/yandex-int-api/v1/orders/commit')
    async def _(request):
        return mockserver.make_response(
            status=500, json={'status': 'PRICE_CHANGED'},
        )

    res = await web_app_client.post(
        '/ptom/driver/v1/make-order',
        json={
            'payment_type': 'cash',
            'category': 'econom',
            'park_id': 'park_id',
            'driver_id': 'driver_id',
            'user_phone': '+70009325297',
            'route': [{'lat': 33.6, 'lon': 55.1}],
        },
    )

    assert res.status == 410
    assert await res.json() == {
        'message': 'Ошибка order_commit: {\'status\': \'PRICE_CHANGED\'}',
        'status': 'fail',
    }


@pytest.mark.config(
    PRO_TEST_ORDER_MAKER_BLOCKING_REASONS_EXPLANATIONS={
        'infra/fetch_route_info': 'Не удалость построить маршрут',
    },
)
async def test_order_satisfy_blocking_resaons(web_app_client, mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    async def _(request):
        return {
            'candidates': [
                {'is_satisfied': False, 'reasons': ['infra/fetch_route_info']},
            ],
        }

    res = await web_app_client.post(
        '/ptom/driver/v1/make-order',
        json={
            'payment_type': 'cash',
            'category': 'econom',
            'park_id': 'park_id',
            'driver_id': 'driver_id',
            'user_phone': '+70009325297',
            'route': [{'lat': 33.6, 'lon': 55.1}],
        },
    )

    assert res.status == 410
    assert await res.json() == {
        'message': (
            'Не получилось назначить заказиз-за блокирующих фильтров: '
            '[\'infra/fetch_route_info'
            '(Не удалость построить маршрут)\']'
        ),
        'status': 'fail',
    }

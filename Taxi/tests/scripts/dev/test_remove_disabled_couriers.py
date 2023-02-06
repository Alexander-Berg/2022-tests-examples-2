import pytest

from stall.model.courier import Courier
from scripts.dev.remove_disabled_couriers import main


async def test_simple(tap, dataset):
    with tap.plan(5, 'Удаление курьера'):
        courier = await dataset.courier(
            status='disabled',
            first_name=None,
            delivery_type='foot',
        )
        courier_normal = await dataset.courier()

        tap.eq(courier.status, 'disabled', 'Курьер disabled')
        tap.eq(courier.first_name, None, 'Имя не установлено')
        tap.eq(courier.delivery_type, 'foot', 'Тип доставки установлен')

        await main()

        courier = await Courier.load(courier.courier_id)
        tap.eq(courier, None, 'Курьер удалён')

        courier_normal = await Courier.load(courier_normal.courier_id)
        tap.ok(courier_normal, 'Обычный курьер не удалён')


@pytest.mark.parametrize('params', [
    {'status': 'removed', 'first_name': None, 'delivery_type': 'foot'},
    {'status': 'active', 'first_name': None, 'delivery_type': 'car'},
    {'status': 'disabled', 'first_name': 'Alex', 'delivery_type': 'rover'},
    {'status': 'disabled', 'first_name': None, 'delivery_type': None},
    {'status': 'disabled', 'first_name': 'Alex', 'delivery_type': None},
    {},
])
async def test_normal(tap, dataset, params):
    with tap.plan(1, 'Обычные курьеры'):
        courier = await dataset.courier(**params)

        await main()

        courier = await Courier.load(courier.courier_id)
        tap.ok(courier, 'Курьер не удалён')

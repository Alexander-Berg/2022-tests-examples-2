import asyncio

import click

from taxi.robowarehouse.lib.concepts import orders
from taxi.robowarehouse.lib.concepts import package_places
from taxi.robowarehouse.lib.concepts import packages
from taxi.robowarehouse.lib.concepts import warehouse_zones
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.misc.coroutines import run_sync


@click.group()
def test_data():
    pass


@test_data.command()
@click.option('--count', type=int, default=5)
@run_sync
async def generate(count):
    async def __create():
        warehouse = await warehouses.factories.create()
        order = await orders.factories.create(warehouse_id=warehouse.warehouse_id)
        package = await packages.factories.create(order_id=order.order_id)

        await warehouse_zones.factories.create(warehouse_id=warehouse.warehouse_id)
        await package_places.factories.create(package_id=package.package_id, warehouse_id=warehouse.warehouse_id)
        await package_places.factories.create(warehouse_id=warehouse.warehouse_id)

    coros = []
    for _ in range(count):
        coros.append(__create())

    await asyncio.gather(*coros)

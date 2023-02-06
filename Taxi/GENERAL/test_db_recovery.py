import random

from stall.job import job
from stall.model.order import Order, job_save
from stall.model.product import Product
from stall.model.shelf import Shelf
from stall.model.stash import Stash
from stall.model.stock import Stock
from stall.model.store import Store
from stall.model.suggest import Suggest


def db_mode():
    return random.choice(['master', 'slave'])


async def job_dummy(stash_id: str):
    stash = await Stash.load(f'test_db_recovery.{stash_id}', by='name')

    if not stash:
        return

    stash.value['version'] = 0

    store = await Store.load(stash['store_id'], db={'mode': db_mode()})

    async for order in Order.ilist(
            by='look',
            conditions=('store_id', store.store_id),
            limit=random.choice([1, 2, 3]),
    ):
        await Suggest.list_by_order(order)
        await Stock.list_by_order(order)

        await job_save(order_id=order.order_id)

        stash.value['version'] += 1
        await stash.save()

    await stash.rm()


async def handle(request):
    req_id = request.params('json.req_id')
    req_type = random.choice(['r', 'rw', 'rw+'])

    cursor_str = None
    stocks = []

    for _ in range(random.choice([1, 2])):
        cursor = await Stock.list(
            by=random.choice(['replication', 'look']),
            cursor_str=cursor_str,
            direction='ASC',
            db={'mode': db_mode()},
        )

        cursor_str = cursor.cursor_str

        for s in cursor.list:
            stocks.append(s)

    stock = random.choice(stocks)

    if not stock:
        return 404

    await Store.load(stock.store_id, db={'mode': db_mode()})
    await Shelf.load(stock.shelf_id, db={'mode': db_mode()})
    await Product.load(stock.product_id, db={'mode': db_mode()})

    if req_type == 'r':
        return {
            'code': 'OK',
            'req_id': req_id,
            'req_type': req_type,
        }

    stash = await Stash.stash(
        name=f'test_db_recovery.{req_id}',
        expired=10,
        store_id=stock.store_id,
    )

    if req_type == 'rw':
        await stash.rm()
        return {
            'code': 'OK',
            'req_id': req_id,
            'req_type': req_type,
        }

    if req_type == 'rw+':
        await job.put(job_dummy, stash_id=stash.stash_id)
        return {
            'code': 'OK',
            'req_id': req_id,
            'req_type': req_type,
        }

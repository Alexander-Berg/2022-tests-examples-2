import datetime as dt

from libstall.util import now
from scripts.cron.clean_db import clean_db
from stall.model.order_log import OrderLog
from stall.model.suggest import Suggest


async def test_delete_old(dataset, tap, cfg):
    cfg.set('db_clean.max_age_days', 60)

    age = dt.timedelta(days=60, seconds=1)

    with tap.plan(9):
        order1 = await dataset.order(updated=now() - age,
                                     status='complete')
        order2 = await dataset.order(updated=now() - age,
                                     status='complete')
        order3 = await dataset.order(updated=now() - dt.timedelta(days=59),
                                     status='complete')

        await dataset.suggest(order1)
        await dataset.suggest(order1)

        await dataset.suggest(order2)
        await dataset.suggest(order2)

        await dataset.suggest(order3)
        await dataset.suggest(order3)

        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', [order1.order_id, order2.order_id]),
            sort=(),
        )
        tap.eq_ok(len(logs.list), 2, '2 log records')

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order1.order_id, order2.order_id]),
        )
        tap.eq_ok(len(suggests.list), 4, '4 suggests')

        await clean_db()

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order1.order_id, order2.order_id]),
        )
        tap.ok(not suggests.list, 'Old suggests deleted')

        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', [order1.order_id, order2.order_id]),
            sort=(),
        )
        tap.eq_ok(len(logs.list), 0, 'Old logs deleted')

        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', order3.order_id),
            sort=(),
        )
        tap.eq_ok(len(logs.list), 1, 'Recent logs were not deleted')

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', order3.order_id),
        )
        tap.eq_ok(len(suggests.list), 2, 'Recent suggests were not deleted')

        old_lsn1 = order1.lsn
        old_lsn2 = order2.lsn
        old_lsn3 = order3.lsn
        await order1.reload()
        await order2.reload()
        await order3.reload()
        tap.eq_ok(old_lsn1, order1.lsn, 'lsn did not change')
        tap.eq_ok(old_lsn2, order2.lsn, 'lsn did not change')
        tap.eq_ok(old_lsn3, order3.lsn, 'lsn did not change')


async def test_clean_order_once(dataset, tap, cfg):
    cfg.set('db_clean.max_age_days', 60)
    age = dt.timedelta(days=60, seconds=1)

    with tap.plan(8, 'Ensure that we do not process the same order twice'):
        order1 = await dataset.order(updated=now() - age,
                                     status='complete')
        order2 = await dataset.order(updated=now() - age,
                                     status='complete')

        await dataset.suggest(order1)
        await dataset.suggest(order1)
        await dataset.suggest(order2)
        await dataset.suggest(order2)

        await clean_db()

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order1.order_id, order2.order_id]),
        )
        tap.ok(not suggests.list, 'Suggests for orders 1 and 2 deleted')
        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', [order1.order_id, order2.order_id]),
            sort=(),
        )
        tap.ok(not logs.list, 'Logs for orders 1 and 2 deleted')

        order3 = await dataset.order(updated=now() - age,
                                     status='complete')
        await dataset.suggest(order1)
        await dataset.suggest(order1)
        await dataset.suggest(order2)
        await dataset.suggest(order2)
        await dataset.suggest(order3)
        await dataset.suggest(order3)

        await clean_db()

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', order3.order_id),
        )
        tap.ok(not suggests.list, 'Suggests for order3 deleted')
        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', order3.order_id),
            sort=(),
        )
        tap.ok(not logs.list, 'Logs for order3 deleted')

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order1.order_id, order2.order_id]),
        )
        tap.ok(suggests.list,
               'Suggests for already processed orders were not deleted')

        old_lsn1 = order1.lsn
        old_lsn2 = order2.lsn
        old_lsn3 = order3.lsn
        await order1.reload()
        await order2.reload()
        await order3.reload()
        tap.eq_ok(old_lsn1, order1.lsn, 'lsn did not change')
        tap.eq_ok(old_lsn2, order2.lsn, 'lsn did not change')
        tap.eq_ok(old_lsn3, order3.lsn, 'lsn did not change')


async def test_delete_same_order_id(dataset, tap, cfg, wait_order_status):
    cfg.set('db_clean.max_age_days', -1)

    with tap.plan(4):
        order1 = await dataset.order(type='stop_list',
                                     status='reserving')

        await order1.cancel()
        await wait_order_status(order1, ('canceled', 'done'))

        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', order1.order_id),
            sort=(),
        )
        tap.ok(len(logs.list) > 1, 'more than one log with the same order_id')

        await clean_db()

        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', order1.order_id),
            sort=(),
        )
        tap.ok(not logs.list, 'Old logs deleted')

        old_lsn1 = order1.lsn
        await order1.reload()
        tap.eq_ok(old_lsn1, order1.lsn, 'lsn did not change')


async def test_delete_old_closed(dataset, tap, cfg, monkeypatch):
    # pylint: disable=too-many-locals
    cfg.set('db_clean.max_age_days', 10)

    age_old = dt.timedelta(days=10, seconds=1)
    age_not_old = dt.timedelta(days=9)

    def patched_now():
        return now() + age_old

    with tap.plan(8):
        order1_delete = await dataset.order(updated=now() - age_old,
                                            status='complete')
        order2_preserve = await dataset.order(updated=now() - age_not_old,
                                              status='complete')
        order3_preserve = await dataset.order(updated=now() - age_old,
                                              status='processing')
        order4_delete = await dataset.order(updated=now() - age_old,
                                            status='complete')

        await dataset.suggest(order1_delete)
        await dataset.suggest(order2_preserve)

        await dataset.suggest(order3_preserve)
        await dataset.suggest(order4_delete)

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order1_delete.order_id,
                                     order2_preserve.order_id,
                                     order3_preserve.order_id,
                                     order4_delete.order_id]),
        )
        tap.eq_ok(len(suggests.list), 4, '4 suggests')

        await clean_db()

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order1_delete.order_id,
                                     order4_delete.order_id]),
        )
        tap.ok(not suggests.list, 'suggests deleted')

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order2_preserve.order_id,
                                     order3_preserve.order_id]),
        )
        tap.eq_ok(len(suggests.list), 2, 'suggests preserved')

        order3_preserve.status = 'complete'
        await order3_preserve.save()

        monkeypatch.setattr('scripts.cron.clean_db.now',
                            patched_now)
        await clean_db()

        suggests = await Suggest.list(
            by='full',
            conditions=('order_id', [order2_preserve.order_id,
                                     order3_preserve.order_id]),
        )
        tap.eq_ok(len(suggests.list), 0,
                  'previously preserved suggests deleted')

        old_lsn1 = order1_delete.lsn
        old_lsn2 = order2_preserve.lsn
        old_lsn3 = order3_preserve.lsn
        old_lsn4 = order4_delete.lsn
        await order1_delete.reload()
        await order2_preserve.reload()
        await order3_preserve.reload()
        await order4_delete.reload()
        tap.eq_ok(old_lsn1, order1_delete.lsn, 'lsn did not change')
        tap.eq_ok(old_lsn2, order2_preserve.lsn, 'lsn did not change')
        tap.eq_ok(old_lsn3, order3_preserve.lsn, 'lsn did not change')
        tap.eq_ok(old_lsn4, order4_delete.lsn, 'lsn did not change')


async def test_delete_many_logs(dataset, tap, cfg, wait_order_status):
    cfg.set('db_clean.max_age_days', -1)
    cfg.set('db_clean.order_logs_bunch_limit', 150)

    with tap.plan(4):
        order1 = await dataset.order(type='stop_list',
                                     status='reserving')

        for _ in range(300):
            user = await dataset.user(store_id=order1.store_id, role='admin')
            await order1.ack(user)
        await order1.cancel()
        await wait_order_status(order1, ('canceled', 'done'))

        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', order1.order_id),
            sort=(),
        )
        tap.ok(len(logs.list) > 300, 'many logs with the same order_id')

        await clean_db()

        logs = await OrderLog.list(
            by='full',
            conditions=('order_id', order1.order_id),
            sort=(),
        )
        tap.ok(not logs.list, 'Old logs deleted')

        old_lsn1 = order1.lsn
        await order1.reload()
        tap.eq_ok(old_lsn1, order1.lsn, 'lsn did not change')

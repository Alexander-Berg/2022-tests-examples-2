from datetime import date

from yt.wrapper import YPath

from libstall.util import time2time
from scripts.cron.sync_yt_revenue_tlog import YTSync, ErOrderNotFound
from stall.model.analytics.revenue_tlog import (
    RevenueTlog,
    REVENUE_TLOG_SOURCES,
)


async def test_get_tables(tap, monkeypatch):
    with tap.plan(4, 'даты по возрастанию'):
        class YTClientMock:
            def search(self, *args, **kwargs):
                # pylint: disable=unused-argument, no-self-use
                for d in ('2021-01-01', '1970-01-01', '2021-02-01'):
                    yield YPath(
                        f'//home/{d}',
                        attributes={
                            'row_count': 300,
                            'sorted_by': ['transaction_id'],
                        }
                    )

        yt_sync = YTSync(
            '//tmp',
            date(2021, 12, 21),
            date(2021, 12, 21),
            ['franchise'],
        )

        monkeypatch.setattr(yt_sync, 'yt_client', YTClientMock())

        tables = yt_sync.get_tables()

        tap.eq(len(tables), 3, 'три записи')
        tap.eq(tables[0]['date'], date(1970, 1, 1), 'первый')
        tap.eq(tables[1]['date'], date(2021, 1, 1), 'второй')
        tap.eq(tables[2]['date'], date(2021, 2, 1), 'последний')


async def test_need_sync_table(tap):
    with tap.plan(
            5, 'синкаем более новые таблицы и если кол-во строк не совпадает',
    ):
        yt_client = YTSync(
            '//tmp',
            date(2021, 12, 21),
            date(2021, 12, 31),
            ['franchise'],
        )

        tap.eq(
            yt_client.need_sync_table(
                {'date': date(1970, 1, 1), 'row_count': 300, 'path': ''},
                {'date': date(2021, 12, 21), 'row_count': 300, 'path': ''},
            ),
            False,
            'таблица < start_date -- не надо синкать',
        )

        tap.eq(
            yt_client.need_sync_table(
                {'date': date(2022, 1, 1), 'row_count': 300, 'path': ''},
                {'date': date(2021, 12, 31), 'row_count': 300, 'path': ''},
            ),
            False,
            'таблица > end_date -- не надо синкать',
        )

        tap.eq(
            yt_client.need_sync_table(
                {'date': date(2021, 12, 21), 'row_count': 300, 'path': ''},
                {'date': date(2021, 12, 22), 'row_count': 300, 'path': ''},
            ),
            False,
            'таблица < последней просинканной',
        )

        tap.eq(
            yt_client.need_sync_table(
                {'date': date(2021, 12, 21), 'row_count': 300, 'path': ''},
                {'date': date(2021, 12, 21), 'row_count': 300, 'path': ''},
            ),
            False,
            'даты и количество строк совпадают -- не надо синкать',
        )

        tap.eq(
            yt_client.need_sync_table(
                {'date': date(2021, 12, 21), 'row_count': 300, 'path': ''},
                {'date': date(2021, 12, 21), 'row_count': 299, 'path': ''},
            ),
            True,
            'даты совпадают, количество строк нет -- надо синкать',
        )


async def test_sync_table(tap, dataset, uuid, now, monkeypatch):
    with tap.plan(3, 'синк одной таблицы в два приседания'):
        store = await dataset.store(cost_center=uuid())
        order = await dataset.order(store=store)

        # pylint: disable=unused-argument,no-self-use
        class YQLClientMock:
            def __init__(self):
                self.res = ResultMock()

            def query(self, *args, **kwargs):
                return self

            def run(self, *args, **kwargs):
                return

            def get_results(self, *args, **kwargs):
                return [self.res]

        class ResultMock:
            @property
            def column_names(self):
                return [
                    'source',
                    'company_type',
                    'transaction_id',
                    'event_time',
                    'transaction_type',
                    'product',
                    'detailed_product',
                    'aggregation_sign',
                    'amount_with_vat',
                    'amount_without_vat',
                    'vat_amount',
                    'vat_rate',
                    'order_id',
                    'oebs_depot_id',
                    'item_id',
                    'quantity',
                ]

            def get_iterator(self, *args, **kwargs):
                # pylint: disable=unused-argument, no-self-use
                for i in range(2):
                    row = {
                        'source': 'grocery_revenues',
                        'company_type': 'franchise',
                        'transaction_id': int(
                            now().timestamp() * 1000_000 + i
                        ),
                        'event_time': now().isoformat(),
                        'transaction_type': 'payment',
                        'product': 'smth',
                        'detailed_product': 'smth',
                        'aggregation_sign': 1,
                        'amount_with_vat': '300',
                        'amount_without_vat': '300',
                        'vat_amount': '0',
                        'vat_rate': '0',
                        'order_id': order.external_id,
                        'oebs_depot_id': store.cost_center,
                        'item_id': uuid(),
                        'quantity': 300,
                    }
                    yield list(row.values())

        yt_sync = YTSync(
            f'//{uuid()}',
            date(1970, 1, 1),
            date(1970, 1, 1),
            ['franchise'],
        )

        monkeypatch.setattr(yt_sync, 'yql_client', YQLClientMock())

        r = await yt_sync.sync_table(
            {'date': date(1970, 1, 1), 'row_count': 2, 'path': '//home'},
        )

        tap.eq(r, (0, 2), 'вставили две записи')

        r = await yt_sync.sync_table(
            {'date': date(1970, 1, 1), 'row_count': 4, 'path': '//home'},
        )

        tap.eq(r, (0, 2), 'вставили еще две записи')

        revenues = await RevenueTlog.list(
            by='full',
            conditions=('company_id', store.company_id),
        )
        tap.eq(len(revenues.list), 4, 'все записи есть в базе')


async def test_state(tap, uuid):
    with tap.plan(8, 'управление стейтом'):
        yt_sync = YTSync(
            f'//{uuid()}',
            date(1970, 1, 1),
            date(1970, 1, 1),
            ['franchise'],
        )

        tap.ok(yt_sync.stash is None, 'нет стейта')

        state = await yt_sync.get_state()

        tap.ok(yt_sync.stash, 'есть стейта')
        tap.ok(yt_sync.stash.stash_id, 'сохранили в бд')
        tap.eq(yt_sync.stash.name, yt_sync.base_dir, 'имя стеша')

        tap.eq(state['date'], date(1970, 1, 1), 'date')
        tap.eq(state['row_count'], 0, 'row_count')

        state = await yt_sync.set_state(date(1970, 1, 2), 300)

        tap.eq(state['date'], date(1970, 1, 2), 'date')
        tap.eq(state['row_count'], 300, 'row_count')


async def test_get_last_transaction_id(tap, uuid, now):
    with tap.plan(6):
        yt_sync = YTSync(
            f'//{uuid()}',
            date(1970, 1, 1),
            date(1970, 1, 1),
            ['franchise'],
        )

        for i in range(3):
            last = await yt_sync.get_last_transaction_id()

            rows = [
                {
                    'company_id': uuid(),
                    'store_id': uuid(),
                    'order_id': uuid(),
                    'source': REVENUE_TLOG_SOURCES[0],
                    'transaction_id': int(now().timestamp() * 1000_000 + i),
                    'transaction_dttm': now(),
                    'raw_data': {
                        'transaction_type': 'payment',
                        'transaction_product': 'smth',
                        'transaction_detailed_product': 'smth',
                        'aggregation_sign': 1,
                        'product_id': uuid(),
                        'quantity': '300',
                        'amount_with_vat': '300',
                        'amount_without_vat': '300',
                        'vat_amount': '0',
                        'vat_rate': '0',
                    }
                }
            ]
            tap.ok(await RevenueTlog.insert_batch(rows), 'вставили пачечку')

            new_last = await yt_sync.get_last_transaction_id()

            tap.ok(last < new_last, 'есть надежда, что последний больше')


async def test_get_order(tap, dataset, uuid):
    with tap.plan(2, 'поиск заказа без дублей'):
        yt_sync = YTSync(
            f'//{uuid()}',
            date(1970, 1, 1),
            date(1970, 1, 1),
            ['franchise'],
        )

        store = await dataset.store(cost_center=uuid())
        order = await dataset.order(store=store)

        same_order = await yt_sync.get_order(order.external_id, None)

        tap.eq(
            order.order_id,
            same_order.order_id,
            'достали заказ по внешнему ид',
        )

        same_order = await yt_sync.get_order(
            order.external_id,
            store.cost_center,
        )

        tap.eq(
            order.order_id,
            same_order.order_id,
            'достали заказ по внешнему ид и oebs id',
        )


async def test_get_order_dupl(tap, dataset, uuid):
    with tap.plan(3, 'поиск заказа с дублями'):
        yt_sync = YTSync(
            f'//{uuid()}',
            date(1970, 1, 1),
            date(1970, 1, 1),
            ['franchise'],
        )

        store = await dataset.store(cost_center=uuid())
        order = await dataset.order(store=store)

        store2 = await dataset.store(cost_center=uuid())
        order2 = await dataset.order(
            external_id=order.external_id,
            store=store2,
        )
        tap.eq(order.external_id, order2.external_id, 'дубль идентификатора')

        same_order2 = await yt_sync.get_order(order2.external_id, None)
        tap.ok(same_order2 is None, 'не можем точно найти заказ')

        same_order2 = await yt_sync.get_order(
            order2.external_id,
            store2.cost_center,
        )
        tap.eq(
            order2.order_id,
            same_order2.order_id,
            'c oebs id находим нормально',
        )


async def test_prepare_row(tap, dataset, uuid, now):
    with tap.plan(2, 'строчка из ытя в наше родное'):
        yt_sync = YTSync(
            f'//{uuid()}',
            date(1970, 1, 1),
            date(1970, 1, 1),
            ['franchise'],
        )

        store = await dataset.store(cost_center=uuid())
        order = await dataset.order(store=store)

        row = {
            'source': 'grocery_revenues',
            'transaction_id': int(now().timestamp() * 1000_000),
            'event_time': now().isoformat(),
            'transaction_type': 'payment',
            'product': 'smth',
            'detailed_product': 'smth',
            'aggregation_sign': -1,
            'amount_with_vat': '300',
            'amount_without_vat': '300',
            'vat_amount': '0',
            'vat_rate': '0',
            'order_id': uuid(),
            'oebs_depot_id': uuid(),
            'item_id': uuid(),
            'quantity': 300,
        }

        with tap.raises(ErOrderNotFound, 'не нашли ордер'):
            await yt_sync.prepare_row(row)

        row['order_id'] = order.external_id

        prepared = await yt_sync.prepare_row(row)

        tap.eq(
            prepared,
            {
                'company_id': store.company_id,
                'store_id': store.store_id,
                'order_id': order.order_id,
                'source': REVENUE_TLOG_SOURCES[0],
                'transaction_id': row['transaction_id'],
                'transaction_dttm': time2time(row['event_time']),
                'raw_data': {
                    'transaction_type': 'payment',
                    'transaction_product': 'smth',
                    'transaction_detailed_product': 'smth',
                    'aggregation_sign': -1,
                    'product_id': row['item_id'],
                    'quantity': '300',
                    'amount_with_vat': '300',
                    'amount_without_vat': '300',
                    'vat_amount': '0',
                    'vat_rate': '0',
                    'courier_id': None,
                },
            },
            'подготовили данные',
        )

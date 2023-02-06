import datetime
from yt.wrapper.ypath import YPath

import tests.dataset as dt

from stall.model.analytics.writeoff_limit import WriteoffLimit
from stall.model.analytics.md_audit import MDAudit
from scripts.cron.sync_yt_analytics import (
    fetch_date_from_path,
    filter_tables,
    sync_md_audit,
    sync_writeoff_limits,
)


async def test_fetch_date_from_path(tap):
    monday = fetch_date_from_path('2021-01', 'year-week')
    tap.eq_ok(monday, datetime.date(2021, 1, 4),
              'Не считаем неделю с началом в прошлом году')

    monday = fetch_date_from_path('//some_path/2022-03', 'year-week')
    tap.eq_ok(monday, datetime.date(2022, 1, 17), 'Начало 3-й недели')

    first_day = fetch_date_from_path('//some_path/2022-09', 'year-month')
    tap.eq_ok(first_day, datetime.date(2022, 9, 1), 'Сентябрь')


    monday = fetch_date_from_path('//some_path/wrong_path', 'year-week')
    tap.eq_ok(monday, None, 'Строка не содержит год и неделю')

    monday = fetch_date_from_path('', 'year-week')
    tap.eq_ok(monday, None, 'Пустая строа')

    monday = fetch_date_from_path(None, 'year-week')
    tap.eq_ok(monday, None, 'None')


async def test_filter_tables(tap, now):
    filtered = filter_tables(
        iter([
            YPath(
                '//2021-1',
                attributes={
                    'modification_time': now() + datetime.timedelta(hours=1)
                }
            ),
            YPath(
                '//2021-02',
                attributes={'modification_time': now()}
            )
        ]),
        None,
    )
    tap.eq_ok(
        [str(it) for it in filtered],
        ['//2021-02', '//2021-1'],
        'Пустой last_date не фильтрует'
    )

    filtered = filter_tables(
        iter([
            YPath(
                '//wrong-table-name',
                attributes={'modification_time': now()}
            )
        ]),
        None,
    )

    tap.eq_ok(
        [str(it) for it in filtered],
        [],
        'Игнорируем пути, которые не подходят под YYYY-MM'
    )

    filtered = filter_tables(
        iter([
            YPath(
                '//2021-1',
                attributes={
                    'modification_time': now() - datetime.timedelta(hours=4)
                }
            ),
            YPath(
                '//2021-02',
                attributes={'modification_time': now()}
            )
        ]),
        now() - datetime.timedelta(hours=2),
    )
    tap.eq_ok(
        [str(it) for it in filtered],
        ['//2021-02'],
        'modification_time фильтруется'
    )


async def test_sync_md_audit(tap, dataset, uuid, now):
    store = await dataset.store(external_id=uuid())
    today = now().date()
    monday = today - datetime.timedelta(days=today.weekday())
    yaer, week, _ = monday.isocalendar()

    class YTClientMock:
        def search(self, path, **kwargs):
            # pylint: disable=unused-argument, no-self-use
            return [
                YPath(
                    f'//{yaer}-{week}',
                    attributes={'modification_time': now()}
                )
            ]

        def read_table(self, path):
            # pylint: disable=unused-argument, no-self-use
            yield {
                'store_external_id': store.external_id,
                'value': '87.2'
            }

    cursor = await MDAudit.list(
        by='full',
        conditions=('store_id', store.store_id)
    )
    tap.eq_ok(len(cursor.list), 0, 'Данных по аудиту нет')

    await sync_md_audit(YTClientMock())

    cursor = await MDAudit.list(
        by='full',
        conditions=('store_id', store.store_id)
    )
    tap.eq_ok(len(cursor.list), 1, 'Данные по аудиту')
    with cursor.list[0] as md_audit:
        tap.eq_ok(md_audit.date, monday, 'Записали на понедельник')
        tap.eq_ok(md_audit.store_id, store.store_id, 'Лавка верная')
        tap.eq_ok(md_audit.value, 87.2, 'Значение аудита верное')


async def test_sync_md_audit_wrong(tap, dataset, uuid, now):
    store = await dataset.store(external_id=uuid())
    today = now().date()
    monday = today - datetime.timedelta(days=today.weekday())
    yaer, week, _ = monday.isocalendar()

    class YTClientMock:
        def search(self, path, **kwargs):
            # pylint: disable=unused-argument, no-self-use
            return [
                YPath(
                    f'//{yaer}-{week}',
                    attributes={'modification_time': now()}
                )
            ]

        def read_table(self, path):
            # pylint: disable=unused-argument, no-self-use
            yield {
                'store_external_id': store.external_id,
                'value': 'Wrong data'
            }
            yield {
                'store_external_id': store.external_id,
                'value': ''
            }
            yield {
                'store_external_id': store.external_id,
                'value': None
            }

    cursor = await MDAudit.list(
        by='full',
        conditions=('store_id', store.store_id)
    )
    tap.eq_ok(len(cursor.list), 0, 'Данных по аудиту нет')

    await sync_md_audit(YTClientMock())

    cursor = await MDAudit.list(
        by='full',
        conditions=('store_id', store.store_id)
    )
    tap.eq_ok(len(cursor.list), 0, 'Данных по аудиту нет')


async def test_sync_writeoff_limits(tap, dataset: dt, uuid, now):
    cluster_title = uuid()
    cluster = await dataset.cluster(title=cluster_title)
    today = now().date()
    yaer, month = today.year, today.month

    class YTClientMock:
        def search(self, path, **kwargs):
            # pylint: disable=unused-argument, no-self-use
            return [
                YPath(
                    f'//{yaer}-{month}',
                    attributes={'modification_time': now()}
                )
            ]

        def read_table(self, path):
            # pylint: disable=unused-argument, no-self-use
            yield {
                'city': cluster_title,
                'factor': 3,
                'check_valid_max': 21.85,
                'damage_max': 3.01,
                'refund_max': 0.05,
                'recount_min': -0.45,
                'recount_max': 0.45,
                'blind_acceptance_max': 0.52,
            }

    cursor = await WriteoffLimit.list(
        by='full',
        conditions=('cluster_id', cluster.cluster_id)
    )
    tap.eq_ok(len(cursor.list), 0, 'Лимиты списания не заданы')

    await sync_writeoff_limits(YTClientMock())

    cursor = await WriteoffLimit.list(
        by='full',
        conditions=('cluster_id', cluster.cluster_id)
    )
    tap.eq_ok(len(cursor.list), 1, 'Лимиты списания сохранены')
    with cursor.list[0] as wo_limit:
        tap.eq_ok(wo_limit.date, datetime.date(yaer, month, 1),
                  'Первый день месяца')
        tap.eq_ok(wo_limit.cluster_id, cluster.cluster_id, 'Кластер найден')
        tap.eq_ok(wo_limit.factor, 3, 'Фактор')
        tap.eq_ok(wo_limit.check_valid_max, 21.85, 'Лимит КСГ верхний')
        tap.eq_ok(wo_limit.damage_max, 3.01, 'Лимит брака верхний')
        tap.eq_ok(wo_limit.refund_max, 0.05, 'Лимит возвратов верхний')
        tap.eq_ok(wo_limit.recount_min, -0.45, 'Лимит пересчета нижний')
        tap.eq_ok(wo_limit.recount_max, 0.45, 'Лимит пересчёта верхний')
        tap.eq_ok(wo_limit.blind_acceptance_max, 0.52,
                  'Лимит доверительной приёмки верхний')

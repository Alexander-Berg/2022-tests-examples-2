# pylint: disable=too-many-locals,too-many-statements
import argparse
from datetime import timedelta
from io import StringIO

import pytest

from stall.model.courier_shift_tag import TAG_BEGINNER
from scripts.dev.set_beginner_tags import main, THE_GREAT_MIGRATION


@pytest.mark.parametrize('tags', (
    [],              # никаких тегов нет
    [TAG_BEGINNER],  # числился новичком
))
async def test_versed_courier(tap, dataset, unique_int, tags):
    with tap.plan(2, 'Курьер с завершенной сменой не должен получить тег'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=tags,
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
        )
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=None,
            cluster_id=cluster.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [], 'тега Новичок нет')


@pytest.mark.parametrize('status', (
        'waiting', 'processing', 'leave', 'cancelled', 'absent',
))
async def test_beginner_from_eda(tap, dataset, unique_int, now, tzone, status):
    with tap.plan(3, f'Новичок из Еды без завершенных смен (status={status})'):
        eda_id = str(unique_int())

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': eda_id,
                },
            },
        )

        _now = now(tz=tzone('Europe/Moscow')).replace(microsecond=0)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=_now + timedelta(hours=1),
            closes_at=_now + timedelta(hours=2),
        )
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
            started_at=_now + timedelta(hours=10),
            closes_at=_now + timedelta(hours=12),
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=StringIO(f'["{eda_id}"]'),
            cluster_id=cluster.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'выдан тег новичок')

        with await shift.reload():
            tap.eq(shift.tags, [TAG_BEGINNER], 'выдан тег новичок')


@pytest.mark.parametrize('tags', (
    [],              # никаких тегов нет
    [TAG_BEGINNER],  # числился новичком
))
async def test_versed_from_eda(tap, dataset, unique_int, tags):
    with tap.plan(2, 'Новичок Еды с complete-сменой не должен получить тег'):
        eda_id = str(unique_int())

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            tags=tags,
            vars={
                'external_ids': {
                    'eats': eda_id,
                },
            },
        )

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=StringIO(f'["{eda_id}"]'),
            cluster_id=cluster.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [], 'тега Новичок нет')


async def test_versed_from_eda_2(tap, dataset, unique_int):
    with tap.plan(2, 'Опытный курьер не должен потерять тег, кроме Новичка'):
        eda_id = str(unique_int())

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        required_tag = await dataset.courier_shift_tag()
        courier = await dataset.courier(
            cluster=cluster,
            tags=[required_tag.title, TAG_BEGINNER],
            vars={
                'external_ids': {
                    'eats': eda_id,
                },
            },
        )
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='complete',
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=StringIO(f'["{eda_id}"]'),
            cluster_id=cluster.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [required_tag.title], 'тег не потерялся')


async def test_versed_prev_profile(tap, dataset, unique_int):
    with tap.plan(2, 'Опытный курьер потерять тег, из-за старого профиля'):
        eda_id = str(unique_int())

        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        required_tag = await dataset.courier_shift_tag()
        courier_old = await dataset.courier(
            cluster=cluster,
            status='disabled',
            vars={
                'external_ids': {
                    'eats': eda_id,
                },
            },
        )
        await dataset.courier_shift(
            store=store,
            courier=courier_old,
            status='complete',
        )
        courier_new = await dataset.courier(
            cluster=cluster,
            status='active',
            tags=[required_tag.title, TAG_BEGINNER],
            vars={
                'external_ids': {
                    'eats': eda_id,
                },
            },
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=StringIO(f'["{eda_id}"]'),
            cluster_id=cluster.cluster_id,
            tags_store=None,
            only_active=False,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier_new.reload():
            tap.eq(courier_new.tags, [required_tag.title], 'тег не потерялся')


@pytest.mark.parametrize('tags', (
    [],              # никаких тегов нет
    [TAG_BEGINNER],  # числился новичком
))
async def test_beginner_after_migration(
        tap, dataset, unique_int, tags,
):
    with tap.plan(2, 'Курьер, пришедший после миграции из ЕДЫ и без смен'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
            tags=tags,
            # пришел после миграции
            created=THE_GREAT_MIGRATION + timedelta(minutes=1),
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=None,
            cluster_id=cluster.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'тег Новичок в наличии')


async def test_versed_before_migration(
        tap, dataset, unique_int
):
    with tap.plan(2, 'Курьер, пришедший ДО миграции и в списке Еды его нет'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
            # пришел ДО миграции
            created=THE_GREAT_MIGRATION - timedelta(minutes=1),
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=None,
            cluster_id=cluster.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [], 'новых тегов нет')


async def test_filter_cluster_id(tap, dataset, unique_int):
    with tap.plan(3, 'Фильтрация по кластеру'):
        courier_1 = await dataset.courier(
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
            # пришел после миграции
            created=THE_GREAT_MIGRATION + timedelta(minutes=1),
        )
        courier_2 = await dataset.courier(
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
            # пришел после миграции
            created=THE_GREAT_MIGRATION + timedelta(minutes=1),
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=None,
            cluster_id=courier_1.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier_1.reload():
            tap.eq(courier_1.tags, [TAG_BEGINNER], 'тег Новичок выдан')

        with await courier_2.reload():
            tap.eq(courier_2.tags, [], 'тег не выдан')


async def test_filter_tags_store(tap, dataset, unique_int):
    with tap.plan(3, 'Фильтрация по привязке лавки'):
        store_1 = await dataset.store()
        store_2 = await dataset.store()
        courier_1 = await dataset.courier(
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
            tags_store=[store_1.store_id],
            # пришел после миграции
            created=THE_GREAT_MIGRATION + timedelta(minutes=1),
        )
        courier_2 = await dataset.courier(
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
            tags_store=[store_2.store_id],
            # пришел после миграции
            created=THE_GREAT_MIGRATION + timedelta(minutes=1),
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=None,
            cluster_id=None,
            tags_store=[store_1.store_id],
            only_active=True,
            apply=True,
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier_1.reload():
            tap.eq(courier_1.tags, [TAG_BEGINNER], 'тег Новичок выдан')

        with await courier_2.reload():
            tap.eq(courier_2.tags, [], 'тег не выдан')


async def test_not_apply(tap, dataset, unique_int):
    with tap.plan(4, 'Запуск в режиме теста'):
        courier = await dataset.courier(
            vars={
                'external_ids': {
                    'eats': str(unique_int()),
                },
            },
            # пришел после миграции
            created=THE_GREAT_MIGRATION + timedelta(minutes=1),
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=None,
            cluster_id=courier.cluster_id,
            tags_store=None,
            only_active=True,
            apply=False,        # только показываем
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [], 'тег не выдан')

        # Выполняем скрипт
        args = argparse.Namespace(
            eda_beginners=None,
            cluster_id=courier.cluster_id,
            tags_store=None,
            only_active=True,
            apply=True,        # покупаем
        )
        tap.eq(await main(args), True, 'Скрипт выполнился успешно')

        with await courier.reload():
            tap.eq(courier.tags, [TAG_BEGINNER], 'тег Новичок выдан')

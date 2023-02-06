import argparse
import pytest

from scripts.dev.cluster_set import main


@pytest.mark.parametrize('params', [
    {'setup': 'slot_start_range', 'value': 300},
    {'setup': 'shift_close_disable', 'value': True},
    {'setup': 'slot_min_size', 'value': 0},
])
async def test_simple(tap, dataset, params):
    with tap.plan(5, 'Проставление настройки'):
        cluster = await dataset.cluster(
            courier_shift_setup={'pause_duration': 100},
        )

        tap.eq(
            cluster.courier_shift_setup.pause_duration,
            100,
            'Настройки кластера установлены'
        )
        tap.eq(
            cluster.courier_shift_setup[params['setup']],
            None,
            f"Настройка {params['setup']} не установлена"
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            cluster=cluster.cluster_id,
            setup=params['setup'],
            value=str(params['value']),
            apply=True,
        )
        tap.eq(await main(args), None, 'Скрипт выполнился')

        await cluster.reload()
        tap.eq(
            cluster.courier_shift_setup.pause_duration,
            100,
            'Настройки кластера сохранились'
        )
        tap.eq(
            cluster.courier_shift_setup[params['setup']],
            params['value'],
            f"Настройка {params['setup']} обновлена",
        )

async def test_all(tap, dataset):
    with tap.plan(3, 'Проставление настроек всем кластерам'):
        cluster = await dataset.cluster()

        tap.eq(
            cluster.courier_shift_setup.slot_start_range,
            None,
            'Настройка не установлена'
        )

        # Выполняем скрипт
        args = argparse.Namespace(
            cluster=None,
            setup='slot_start_range',
            value='300',
            apply=True,
        )
        tap.eq(await main(args), None, 'Скрипт выполнился')

        await cluster.reload()
        tap.eq(
            cluster.courier_shift_setup.slot_start_range,
            300,
            'Настройка обновлена',
        )

async def test_wrong_cluster(tap, uuid):
    with tap.plan(1, 'Неверный кластер'):
        # Выполняем скрипт
        args = argparse.Namespace(
            cluster=uuid(),
            setup='shift_close_time',
            value='11:30:55',
        )
        tap.eq(await main(args), 2, 'Скрипт выполнился с ошибкой')

async def test_wrong_setup(tap, uuid):
    with tap.plan(1, 'Неверная настройка'):
        # Выполняем скрипт
        args = argparse.Namespace(
            cluster=uuid(),
            setup='undefined_setup',
            value='123',
        )
        tap.eq(await main(args), 2, 'Скрипт выполнился с ошибкой')

async def test_wrong_value(tap, uuid):
    with tap.plan(1, 'Неверное значение'):
        # Выполняем скрипт
        args = argparse.Namespace(
            cluster=uuid(),
            setup='slot_start_range',
            value='asd',
        )
        tap.eq(await main(args), 2, 'Скрипт выполнился с ошибкой')

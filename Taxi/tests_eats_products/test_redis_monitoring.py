import pytest


PERIODIC_NAME = 'redis-monitoring'
MOCK_NOW = '2021-02-18T20:00:00+00:00'


@pytest.mark.config(
    EATS_PRODUCTS_REDIS_MONITORING={'enabled': False, 'period_in_sec': 10},
)
@pytest.mark.now(MOCK_NOW)
async def test_redis_monitoring_disabled(
        taxi_eats_products, testpoint, redis_store,
):
    """Проверяем что мониторинг не запускается выключенным."""

    @testpoint(f'eats_products::{PERIODIC_NAME}-finished')
    def periodic_tp(arg):
        pass

    for i in range(3):
        items = [0.01, 'item_id_1']
        redis_store.zadd(f'scores:top:table_1:{i}:{i}', *items)

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    assert periodic_tp.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_redis_monitoring_simple(
        taxi_eats_products, taxi_eats_products_monitor, redis_store,
):
    """Простейший тест, проверяем что мониторинг вызывается и считает тотал."""

    for i in range(3):
        items = [0.01, 'item_id_1']
        redis_store.zadd(f'scores:top:table_1:{i}:{i}', *items)

    for i in range(2):
        # Проверяем, что метрики не суммируются
        await taxi_eats_products.run_distlock_task(PERIODIC_NAME)

        metrics = await taxi_eats_products_monitor.get_metric(
            'redis_statistics',
        )

        assert metrics['total_keys'] == 3


@pytest.mark.now(MOCK_NOW)
async def test_redis_monitoring_default_categories_carousels_count(
        taxi_eats_products, taxi_eats_products_monitor, redis_store,
):
    """Проверяем подсчет перцентилей количества каруселей в каждом плейсе.
    Для этого создаем 10 плейсов, каждый содержит от 1 до 10 категорий,
    с одним товаром (в этом тесте кол-во товаров не важно). И проверяем
    перцентили."""
    categories_sizes = [i + 1 for i in range(10)]
    place_id = 1

    for category_size in categories_sizes:
        items = [0.01, 'item_id_1']
        for category_id in range(category_size):
            redis_store.zadd(
                f'scores:top:table_1:{place_id}:{category_id}', *items,
            )
        place_id += 1

    for _ in range(2):
        # Проверяем, что метрики не суммируются
        await taxi_eats_products.run_distlock_task(PERIODIC_NAME)

        metrics = (
            await taxi_eats_products_monitor.get_metric('redis_statistics')
        )['table_1']['default_categories']

        assert metrics['carousels_count'] == {
            'p00': 1,
            'p10': 2,
            'p20': 3,
            'p30': 4,
            'p40': 5,
            'p50': 6,
            'p60': 7,
            'p70': 8,
            'p80': 9,
            'p90': 10,
            'p100': 10,
        }
        assert metrics['places_count'] == len(categories_sizes)


@pytest.mark.now(MOCK_NOW)
async def test_redis_monitoring_default_categories_products_count(
        taxi_eats_products, taxi_eats_products_monitor, redis_store,
):
    """Проверяем, что считаются перцентили товаров для дефолтных категорий.
    Для этого создаем 10 плейсов, в каждом из которых одна карусель,
    содержащая от 1 до 10 товаров."""
    items_id_counter = 1
    items_count = 1
    place_id = 1
    places_count = 10

    for i in range(places_count):
        items = []
        # Prepare items
        for _ in range(i + 1):
            items.append(0.01)
            items.append(f'item_id_{items_id_counter}')
            items_id_counter += 1
        items_count += 1

        redis_store.zadd(f'scores:top:table_1:{place_id}:{i}', *items)
        place_id += 1

    for _ in range(2):
        # Проверяем, что метрики не суммируются
        await taxi_eats_products.run_distlock_task(PERIODIC_NAME)

        metrics = (
            await taxi_eats_products_monitor.get_metric('redis_statistics')
        )['table_1']['default_categories']

        assert metrics['products_count'] == {
            'p00': 1,
            'p10': 2,
            'p20': 3,
            'p30': 4,
            'p40': 5,
            'p50': 6,
            'p60': 7,
            'p70': 8,
            'p80': 9,
            'p90': 10,
            'p100': 10,
        }
        assert metrics['places_count'] == places_count


@pytest.mark.now(MOCK_NOW)
async def test_redis_monitoring_dynamic_categories(
        taxi_eats_products, taxi_eats_products_monitor, redis_store,
):
    """Для каждой динамической категории, проверяем что считаются перцентили
    товаров, и не считаются перцентили количества каруселей на плейс."""
    for dynamic_category_name, dynamic_category_id in zip(
            ('repeat_categories', 'discount_categories', 'popular_categories'),
            (44004, 44008, 44012),
    ):
        items_id_counter = 1
        items_count = 1
        place_id = 1
        places_count = 10

        for i in range(places_count):
            items = []
            # Prepare items
            for _ in range(i + 1):
                items.append(0.01)
                items.append(f'item_id_{items_id_counter}')
                items_id_counter += 1
            items_count += 1

            redis_store.zadd(
                f'scores:top:table_1:{place_id}:{dynamic_category_id}', *items,
            )
            place_id += 1

        for _ in range(2):
            # Проверяем, что метрики не суммируются
            await taxi_eats_products.run_distlock_task(PERIODIC_NAME)

            metrics = (
                await taxi_eats_products_monitor.get_metric('redis_statistics')
            )['table_1'][dynamic_category_name]

            assert metrics['products_count'] == {
                'p00': 1,
                'p10': 2,
                'p20': 3,
                'p30': 4,
                'p40': 5,
                'p50': 6,
                'p60': 7,
                'p70': 8,
                'p80': 9,
                'p90': 10,
                'p100': 10,
            }
            assert 'carousels_count' not in metrics
            assert metrics['places_count'] == places_count


@pytest.mark.config(
    EATS_PRODUCTS_REDIS_MONITORING={
        'enabled': True,
        'percentiles': [0, 100],
        'period_in_sec': 10,
        'sampling_rate': 2,
    },
)
@pytest.mark.now(MOCK_NOW)
async def test_redis_monitoring_default_categories_sampling_rate(
        taxi_eats_products, taxi_eats_products_monitor, redis_store,
):
    """Проверяем, что при sampling_rate=2 (то есть берем число товаров из
    каждого второго ключа), и двух ключах, 0 и 100 перцентиль совпадут -
    то есть, значение возьмется из одного какого-то ключа."""

    items_id_counter = 1
    place_id = 1
    places_count = 2

    for i in range(places_count):
        items = []
        # Prepare items
        for _ in range(i + 1):
            items.append(0.01)
            items.append(f'item_id_{items_id_counter}')
            items_id_counter += 1

        redis_store.zadd(f'scores:top:table_1:{place_id}:{i}', *items)
        place_id += 1

    for _ in range(2):
        # Проверяем, что метрики не суммируются
        await taxi_eats_products.run_distlock_task(PERIODIC_NAME)

        metrics = (
            await taxi_eats_products_monitor.get_metric('redis_statistics')
        )['table_1']['default_categories']

        assert (
            metrics['products_count']['p00']
            == metrics['products_count']['p100']
        )
        assert metrics['places_count'] == places_count

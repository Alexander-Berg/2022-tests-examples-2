import pytest

from . import conftest

PERIODIC_NAME = 'metrics-per-brand'


@pytest.mark.config(
    EATS_NOMENCLATURE_COLLECTOR_PERIODICS={
        PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 300},
    },
)
async def test_per_brand_metrics(
        taxi_eats_nomenclature_collector,
        taxi_eats_nomenclature_collector_monitor,
        testpoint,
        fill_db,
):
    @testpoint(f'eats_nomenclature_collector::{PERIODIC_NAME}')
    def handle_finished(arg):
        pass

    brands, place_groups, places = _generate_data()
    fill_db(brands, place_groups, [], places)

    await taxi_eats_nomenclature_collector.run_periodic_task(
        f'eats-nomenclature-collector_{PERIODIC_NAME}',
    )
    handle_finished.next_call()

    metrics = await taxi_eats_nomenclature_collector_monitor.get_metrics()
    assert metrics[PERIODIC_NAME] == _get_expected_metrics()


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(
        f'eats-nomenclature-collector_{PERIODIC_NAME}', is_distlock=False,
    )


def _generate_data():
    brands = [
        conftest.create_brand(1, 'brand_1'),
        conftest.create_brand(2, 'brand_2'),
        conftest.create_brand(3, 'brand_3', False),
    ]
    place_groups = [
        conftest.create_place_group(1, '1111111', '8:00,15:00'),
        conftest.create_place_group(2, '1111111', '8:00,15:00'),
        conftest.create_place_group(3, '1111111', '8:00,15:00'),
    ]
    places = [
        conftest.create_place(1, 1, 1),
        conftest.create_place(2, 1, 1, False),
        conftest.create_place(3, 1, 1),
        conftest.create_place(4, 2, 2, False),
        conftest.create_place(5, 2, 2),
        conftest.create_place(6, 3, 3),
        conftest.create_place(7, 3, 3),
    ]
    return brands, place_groups, places


def _get_expected_metrics():
    return {
        '$meta': {'solomon_children_labels': 'brand'},
        'brand_1': {'enabled_places_count': 2},
        'brand_2': {'enabled_places_count': 1},
    }

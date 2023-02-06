from dateutil import parser
import pytest

from eats_catalog import storage
from . import search_utils


@pytest.mark.now('2021-07-05T14:14:00+03:00')
async def test_predicate_filtration(
        mockserver, catalog_for_full_text_search, eats_catalog_storage,
):
    """
    Проверяем что фильтрация по предикатам работает.
    Запрашиваем предикат вида brand_id in set(1)
    И проверяем, что в выдаче есть только заведение с
    brand_id == 1
    """

    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    expected_slug = 'slug_1'
    unexpected_slug = 'slug_2'

    eats_catalog_storage.add_place(
        storage.Place(
            slug=expected_slug, place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=open_schedule),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug=unexpected_slug, place_id=2, brand=storage.Brand(brand_id=2),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=2, place_id=2, working_intervals=open_schedule),
    )

    block_id = 'predicate'

    response = await catalog_for_full_text_search(
        blocks=[
            {
                'id': block_id,
                'type': 'any',
                'condition': {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'brand_id',
                        'set_elem_type': 'int',
                        'set': [1],
                    },
                },
            },
        ],
    )

    assert response.status == 200
    data = response.json()

    block = search_utils.find_block(block_id, data)
    place = search_utils.find_place_by_slug(expected_slug, block)
    assert place['brand']['id'] == 1
    search_utils.assert_no_slug(unexpected_slug, block)


@pytest.mark.now('2021-07-05T14:14:00+03:00')
async def test_many_blocks(
        mockserver, catalog_for_full_text_search, eats_catalog_storage,
):
    """
    Проверяем, что каталог возвращает больше одного блока.
    """

    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            slug='slug_1', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=open_schedule),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            slug='slug_2', place_id=2, brand=storage.Brand(brand_id=2),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=2, place_id=2, working_intervals=open_schedule),
    )

    response = await catalog_for_full_text_search(
        blocks=[
            {
                'id': 'first',
                'type': 'any',
                'condition': {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'brand_id',
                        'set_elem_type': 'int',
                        'set': [2],
                    },
                },
            },
            {
                'id': 'second',
                'type': 'any',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'int',
                        'value': 1,
                    },
                },
            },
        ],
    )

    assert response.status == 200
    data = response.json()

    block = search_utils.find_block('first', data)
    place = search_utils.find_place_by_slug('slug_2', block)
    assert place['brand']['id'] == 2

    block = search_utils.find_block('second', data)
    place = search_utils.find_place_by_slug('slug_1', block)
    assert place['brand']['id'] == 1


@pytest.mark.now('2021-07-05T14:14:00+03:00')
async def test_empty_block(
        mockserver, catalog_for_full_text_search, eats_catalog_storage,
):
    """
    Проверяем, что блок возвращается пустым, если нет заведений,
    которые подходят под условия фильтрации.
    """

    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-05T10:00:00+03:00'),
            end=parser.parse('2021-07-05T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            slug='slug_1', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=open_schedule),
    )

    block_id = 'block_id'

    response = await catalog_for_full_text_search(
        blocks=[
            {
                'id': block_id,
                'type': 'any',
                'condition': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'brand_id',
                        'arg_type': 'int',
                        'value': 2,
                    },
                },
            },
        ],
    )

    assert response.status == 200
    data = response.json()

    search_utils.assert_no_block_or_empty(block_id, data)

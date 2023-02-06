from dateutil import parser
import pytest

from eats_catalog import storage
from . import layout_utils


SCHEDULE = [
    storage.WorkingInterval(
        start=parser.parse('2021-04-07T10:00:00+00:00'),
        end=parser.parse('2021-04-07T22:00:00+00:00'),
    ),
]

PLACES: list = [
    storage.Place(place_id=1, brand=storage.Brand(brand_id=1), slug='1'),
    storage.Place(place_id=2, brand=storage.Brand(brand_id=2), slug='2'),
    storage.Place(place_id=3, brand=storage.Brand(brand_id=3), slug='3'),
    storage.Place(
        place_id=4,
        brand=storage.Brand(brand_id=4),
        slug='4',
        place_type=storage.PlaceType.Marketplace,
    ),
]

# Время доставки, которое вренет umlaas-eats
PLACE_TIMING = [
    {'place_id': 1, 'min': 10, 'max': 10},
    {'place_id': 2, 'min': 25, 'max': 30},
    {'place_id': 3, 'min': 30, 'max': 45},
    {'place_id': 4, 'min': 15, 'max': 15},
]

ZONES: list = [
    storage.Zone(
        place_id=1,
        couriers_type=storage.CouriersType.YandexTaxi,
        working_intervals=SCHEDULE,
    ),
    storage.Zone(
        place_id=2,
        couriers_type=storage.CouriersType.Pedestrian,
        working_intervals=SCHEDULE,
    ),
    storage.Zone(
        place_id=3,
        couriers_type=storage.CouriersType.YandexRover,
        working_intervals=SCHEDULE,
    ),
]


@pytest.mark.now('2021-04-07T12:00:00+00:00')
async def test_promo_type_predicate(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """EDACAT-676: тест проверяет, что в блоке присутствуют только те рестораны,
    которые попадают под условие предиката по типу промо-акции."""

    slugs: list = ['2', '3']
    for place in PLACES:
        eats_catalog_storage.add_place(place)

    for zone in ZONES:
        eats_catalog_storage.add_zone(zone)

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _promo_active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': '1',
                    'type': {
                        'id': 1,
                        'name': '1',
                        'picture': 'pic',
                        'detailed_picture': 'pic',
                    },
                    'places': [
                        {'id': 1, 'disabled_by_surge': False},
                        {'id': 2, 'disabled_by_surge': False},
                        {'id': 3, 'disabled_by_surge': False},
                    ],
                },
                {
                    'id': 2,
                    'name': '2',
                    'type': {
                        'id': 2,
                        'name': '2',
                        'picture': 'pic',
                        'detailed_picture': 'pic',
                    },
                    'places': [{'id': 2, 'disabled_by_surge': False}],
                },
                {
                    'id': 3,
                    'name': '3',
                    'type': {
                        'id': 3,
                        'name': '3',
                        'picture': 'pic',
                        'detailed_picture': 'pic',
                    },
                    'places': [{'id': 3, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'condition': {
                    'type': 'intersects',
                    'init': {
                        'arg_name': 'promo_type',
                        'set_elem_type': 'int',
                        'set': [2, 3],
                    },
                },
            },
        ],
    )
    assert response.status_code == 200

    data: dict = response.json()
    block: dict = layout_utils.find_block('open', data)
    for slug in slugs:
        layout_utils.find_place_by_slug(slug, block)


@pytest.mark.now('2021-04-07T12:00:00+00:00')
async def test_courier_type_predicate(
        catalog_for_layout, eats_catalog_storage,
):
    """EDACAT-676: тест проверяет, что в блоке присутствуют только те рестораны,
    которые попадают под условие предиката по типу курьерской доставки."""

    slugs: list = ['1', '3']
    for place in PLACES:
        eats_catalog_storage.add_place(place)

    for zone in ZONES:
        eats_catalog_storage.add_zone(zone)

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'condition': {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'courier_type',
                        'set_elem_type': 'string',
                        'set': ['yandex_rover', 'yandex_taxi'],
                    },
                },
            },
        ],
    )
    assert response.status_code == 200

    data: dict = response.json()
    block: dict = layout_utils.find_block('open', data)
    for slug in slugs:
        layout_utils.find_place_by_slug(slug, block)


@pytest.mark.now('2021-04-07T12:00:00+00:00')
@pytest.mark.parametrize(
    'arg_name,predicate_type,expected_slugs',
    (
        pytest.param('delivery_time_max', 'lt', ['1'], id='max less 30'),
        pytest.param(
            'delivery_time_max', 'lte', ['1', '2'], id='max less or equal 30',
        ),
        pytest.param('delivery_time_min', 'lt', ['1', '2'], id='min less 30'),
        pytest.param(
            'delivery_time_min',
            'lte',
            ['1', '2', '3'],
            id='min less or equal 30',
        ),
    ),
)
async def test_delivery_time_predicate(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        predicate_type,
        arg_name,
        expected_slugs,
):
    """
    Тест проверяет, что в блоке присутствуют только те рестораны,
    которые попадают под условие предиката по типу времени доставки.
    """

    all_slugs = set()
    for place in PLACES:
        all_slugs.add(place['slug'])
        eats_catalog_storage.add_place(place)

    for zone in ZONES:
        eats_catalog_storage.add_zone(zone)

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        result: list = []
        for place in PLACE_TIMING:
            place_id = place['place_id']
            result.append(
                dict(
                    id=place_id,
                    relevance=float(place_id),
                    type='ranking',
                    predicted_times=dict(min=place['min'], max=place['max']),
                    blocks=[],
                ),
            )
        return dict(
            exp_list=[],
            request_id='',
            provider='',
            available_blocks=[],
            result=result,
        )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'condition': {
                    'type': 'all_of',
                    'predicates': [
                        {
                            'type': predicate_type,
                            'init': {
                                'arg_name': arg_name,
                                'arg_type': 'int',
                                'value': 30,
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'delivery_type',
                                'arg_type': 'string',
                                'value': 'native',
                            },
                        },
                    ],
                },
            },
        ],
    )
    assert response.status_code == 200

    assert umlaas_eats.times_called == 1

    data: dict = response.json()
    block: list = layout_utils.find_block('open', data)
    for slug in expected_slugs:
        layout_utils.find_place_by_slug(slug, block)
    unexpected_slugs = all_slugs - set(expected_slugs)
    for slug in unexpected_slugs:
        layout_utils.assert_no_slug(slug, block)


@pytest.mark.now('2021-08-24T12:00:00+00:00')
@pytest.mark.parametrize(
    'predicate, expected_place_ids',
    [
        pytest.param(
            {
                'type': 'eq',
                'init': {
                    'arg_name': 'place_id',
                    'arg_type': 'int',
                    'value': 1,
                },
            },
            [5, 4, 3, 2],
            id='not (place_id eq 1)',
        ),
        pytest.param(
            {
                'type': 'in_set',
                'init': {
                    'arg_name': 'place_id',
                    'set_elem_type': 'int',
                    'set': [2, 3, 4, 5],
                },
            },
            [1],
            id='not (place_id in set (2, 3, 4, 5))',
        ),
    ],
)
async def test_not_predicate(
        catalog_for_layout,
        eats_catalog_storage,
        predicate,
        expected_place_ids,
):
    """
    EDACAT-1579: проверяет предикат типа Not
    """

    ids: list = [1, 2, 3, 4, 5]
    for pid in ids:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=pid,
                brand=storage.Brand(brand_id=pid),
                slug='place_{}'.format(pid),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=pid,
                place_id=pid,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-08-24T08:00:00+00:00'),
                        end=parser.parse('2021-08-24T23:00:00+00:00'),
                    ),
                ],
            ),
        )

    block_id: str = 'open'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'condition': {'type': 'not', 'predicates': [predicate]},
            },
        ],
    )
    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())
    assert len(block) == len(expected_place_ids)

    for place, expected_pid in zip(block, expected_place_ids):
        assert place['meta']['place_id'] == expected_pid


@pytest.mark.now('2021-08-24T12:00:00+00:00')
@pytest.mark.parametrize(
    'predicate, expected_place_ids',
    [
        pytest.param(
            {
                'type': 'contains',
                'init': {
                    'arg_name': 'category_id',
                    'arg_type': 'int',
                    'value': 10,
                },
            },
            [],
            id='category in not match anything',
        ),
        pytest.param(
            {
                'type': 'any_of',
                'predicates': [
                    {
                        'type': 'contains',
                        'init': {
                            'arg_name': 'category_id',
                            'arg_type': 'int',
                            'value': 5,
                        },
                    },
                    {
                        'type': 'contains',
                        'init': {
                            'arg_name': 'category_id',
                            'arg_type': 'int',
                            'value': 4,
                        },
                    },
                ],
            },
            [5, 4],
            id='category in (4, 5)',
        ),
        pytest.param(
            {
                'type': 'contains',
                'init': {
                    'arg_name': 'category_id',
                    'arg_type': 'int',
                    'value': 1,
                },
            },
            [5, 4, 3, 2, 1],
            id='category_id contains (1)',
        ),
    ],
)
async def test_category_id_predicate(
        catalog_for_layout,
        eats_catalog_storage,
        predicate,
        expected_place_ids,
):
    """
    EDACAT-1579: проверяет предикат на соответсвие категории набору категорий
    ресторанов.
    """
    ids: list = [1, 2, 3, 4, 5]
    for pid in ids:
        categories: list = []
        for cid in ids[:pid]:
            categories.append(
                storage.Category(
                    category_id=cid, name='category_{}'.format(cid),
                ),
            )

        eats_catalog_storage.add_place(
            storage.Place(
                place_id=pid,
                brand=storage.Brand(brand_id=pid),
                slug='place_{}'.format(pid),
                categories=categories,
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=pid,
                place_id=pid,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-08-24T08:00:00+00:00'),
                        end=parser.parse('2021-08-24T23:00:00+00:00'),
                    ),
                ],
            ),
        )

    block_id: str = 'open'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'condition': predicate,
            },
        ],
    )
    assert response.status_code == 200

    if not expected_place_ids:
        layout_utils.assert_no_block_or_empty(block_id, response.json())
        return

    block = layout_utils.find_block(block_id, response.json())
    assert len(block) == len(expected_place_ids)

    for place, expected_pid in zip(block, expected_place_ids):
        assert place['meta']['place_id'] == expected_pid

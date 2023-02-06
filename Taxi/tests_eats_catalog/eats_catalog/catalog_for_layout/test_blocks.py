# pylint: disable=too-many-lines

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils


def create_place(
        eats_catalog_storage, place_id: int, place_slug: str, closed: bool,
):

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T22:00:00+00:00'),
    )
    if closed:
        schedule = storage.WorkingInterval(
            start=parser.parse('2021-03-16T10:00:00+00:00'),
            end=parser.parse('2021-03-16T22:00:00+00:00'),
        )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            brand=storage.Brand(brand_id=place_id),
            slug=place_slug,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=place_id, place_id=place_id, working_intervals=[schedule],
        ),
    )


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_block(catalog_for_layout, eats_catalog_storage):

    open_places = []
    closed_places = []

    for place_id in range(10):
        slug = 'open_{}'.format(place_id)
        open_places.append(slug)
        create_place(eats_catalog_storage, place_id, slug, False)

    for place_id in range(11, 20):
        slug = 'closed_{}'.format(place_id)
        closed_places.append(slug)
        create_place(eats_catalog_storage, place_id, slug, True)

    response = await catalog_for_layout(
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
            {'id': 'any', 'type': 'any', 'disable_filters': False},
        ],
    )

    assert response.status_code == 200

    data = response.json()

    open_block = layout_utils.find_block('open', data)
    for slug in open_places:
        layout_utils.find_place_by_slug(slug, open_block)
    for slug in closed_places:
        layout_utils.assert_no_slug(slug, open_block)

    closed_block = layout_utils.find_block('closed', data)
    for slug in closed_places:
        layout_utils.find_place_by_slug(slug, closed_block)
    for slug in open_places:
        layout_utils.assert_no_slug(slug, closed_block)

    any_block = layout_utils.find_block('any', data)
    for slug in closed_places:
        layout_utils.find_place_by_slug(slug, any_block)
    for slug in open_places:
        layout_utils.find_place_by_slug(slug, any_block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.config(
    EATS_CATALOG_PLACE_STORAGE_SETTINGS={
        'consider_new_for': 2,
        'min_preparation_minutes': 5,
        'min_delivery_minutes': 5,
    },
)
async def test_block_new(catalog_for_layout, eats_catalog_storage):
    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T22:00:00+00:00'),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='new',
            launched_at=parser.parse('2021-03-14T15:00:00+00:00'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=[schedule]),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=4,
            brand=storage.Brand(brand_id=4),
            slug='new_but_closed',
            launched_at=parser.parse('2021-03-14T15:00:00+00:00'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=4,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T14:00:00+00:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='old',
            launched_at=parser.parse('2021-03-01T0:00:00+00:00'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=2, place_id=2, working_intervals=[schedule]),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            slug='barely_new',
            launched_at=parser.parse('2021-03-13T15:1:00+00:00'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=3, place_id=3, working_intervals=[schedule]),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'new', 'type': 'new', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()
    new_block = layout_utils.find_block('new', data)

    layout_utils.find_place_by_slug('new', new_block)
    layout_utils.find_place_by_slug('barely_new', new_block)
    layout_utils.assert_no_slug('old', new_block)
    layout_utils.assert_no_slug('new_but_closed', new_block)

    assert len(new_block) == 2


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.config(
    EATS_CATALOG_UMLAAS_CATALOG={'limit': 1000, 'sort_only_blocks': ['promo']},
)
async def test_block_promo(
        catalog_for_layout, eats_catalog_storage, surge, mockserver,
):

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T22:00:00+00:00'),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='with_promo_disabled_by_surge',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=[schedule]),
    )

    surge.set_place_info(
        place_id=1,
        surge={
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2, brand=storage.Brand(brand_id=2), slug='with_promo',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=2, place_id=2, working_intervals=[schedule]),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3, brand=storage.Brand(brand_id=3), slug='without_promo',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=3, place_id=3, working_intervals=[schedule]),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=4,
            brand=storage.Brand(brand_id=4),
            slug='with_promo_closed',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=4,
            place_id=4,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T14:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold/{w}x{h}',
                        'detailed_picture': 'http://istock/pepe/{w}x{h}',
                    },
                    'places': [{'id': 2, 'disabled_by_surge': False}],
                },
                {
                    'id': 2,
                    'name': 'Бесплатные тесты 2',
                    'description': 'При написании фичи, тесты в подарок 2',
                    'type': {
                        'id': 2,
                        'name': 'Тесты в подарок 2',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': True}],
                },
                {
                    'id': 3,
                    'name': 'Бесплатные тесты 3',
                    'description': 'При написании фичи, тесты в подарок 3',
                    'type': {
                        'id': 3,
                        'name': 'Тесты в подарок 3',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 18, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[{'id': 'promo', 'type': 'promo', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()
    promo_block = layout_utils.find_block('promo', data)

    assert len(promo_block) == 1

    layout_utils.find_place_by_slug('with_promo', promo_block)
    layout_utils.assert_no_slug('with_promo_disabled_by_surge', promo_block)
    layout_utils.assert_no_slug('without_promo', promo_block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_block_taxi_delivery(catalog_for_layout, eats_catalog_storage):
    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T22:00:00+00:00'),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug='taxi_delivery',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[schedule],
            couriers_type=storage.CouriersType.YandexTaxi,
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2, brand=storage.Brand(brand_id=2), slug='pedestrian',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[schedule],
            couriers_type=storage.CouriersType.Pedestrian,
        ),
    )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'taxi_delivery',
                'type': 'taxi-delivery',
                'disable_filters': False,
            },
        ],
    )

    assert response.status_code == 200

    data = response.json()
    taxi_block = layout_utils.find_block('taxi_delivery', data)

    assert len(taxi_block) == 1

    layout_utils.find_place_by_slug('taxi_delivery', taxi_block)
    layout_utils.assert_no_slug('pedestrian', taxi_block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_block_pickup(catalog_for_layout, eats_catalog_storage):
    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T22:00:00+00:00'),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='pickup_and_delivery',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Delivery,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Pickup,
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3, brand=storage.Brand(brand_id=3), slug='pickup_only',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=3,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Pickup,
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=6, brand=storage.Brand(brand_id=6), slug='delivery',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=6,
            place_id=6,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Delivery,
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'pickup', 'type': 'pickup', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()
    pickup_block = layout_utils.find_block('pickup', data)

    assert len(pickup_block) == 2

    layout_utils.find_place_by_slug('pickup_and_delivery', pickup_block)
    layout_utils.find_place_by_slug('pickup_only', pickup_block)
    layout_utils.assert_no_slug('delivery', pickup_block)


@pytest.mark.now('2021-03-15T21:00:00+00:00')
async def test_block_open_delivery_or_pickup(
        catalog_for_layout, eats_catalog_storage,
):
    """
        Тест на фильтр open-delivery-or-pickup
    """
    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T22:00:00+00:00'),
    )
    early_schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-15T10:00:00+00:00'),
        end=parser.parse('2021-03-15T20:00:00+00:00'),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='pickup_and_delivery',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Pickup,
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3, brand=storage.Brand(brand_id=3), slug='pickup_only',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=3,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Pickup,
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=6, brand=storage.Brand(brand_id=6), slug='delivery',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=6,
            place_id=6,
            working_intervals=[schedule],
            shipping_type=storage.ShippingType.Delivery,
        ),
    )
    # в результат выдачи попасть не должен т.к. к закрывается раньше
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=4, brand=storage.Brand(brand_id=4), slug='early_pickup',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=4,
            place_id=4,
            working_intervals=[early_schedule],
            shipping_type=storage.ShippingType.Pickup,
        ),
    )
    # в результат выдачи попасть не должен т.к. к закрывается раньше
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=5, brand=storage.Brand(brand_id=5), slug='early_delivery',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=5,
            place_id=5,
            working_intervals=[early_schedule],
            shipping_type=storage.ShippingType.Delivery,
        ),
    )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open-delivery-or-pickup',
                'type': 'open-delivery-or-pickup',
                'disable_filters': False,
            },
        ],
    )

    assert response.status_code == 200

    open_delivery_or_pickup = layout_utils.find_block(
        'open-delivery-or-pickup', response.json(),
    )

    assert len(open_delivery_or_pickup) == 3

    place = layout_utils.find_place_by_slug(
        'pickup_and_delivery', open_delivery_or_pickup,
    )
    payload = place['payload']
    assert payload['availability']['is_available']
    assert payload['data']['features']['delivery']['text'] == '1.1 км'

    place = layout_utils.find_place_by_slug(
        'pickup_only', open_delivery_or_pickup,
    )
    payload = place['payload']
    assert payload['availability']['is_available']
    assert payload['data']['features']['delivery']['text'] == '1.1 км'

    place = layout_utils.find_place_by_slug(
        'delivery', open_delivery_or_pickup,
    )
    payload = place['payload']
    assert payload['availability']['is_available']
    assert payload['data']['features']['delivery']['text'] == '25 – 35 мин'

    layout_utils.assert_no_slug('early_pickup', open_delivery_or_pickup)
    layout_utils.assert_no_slug('early_delivery', open_delivery_or_pickup)


@pytest.mark.now('2021-04-07T17:00:00+00:00')
@pytest.mark.parametrize(
    'filters, open_place_slugs, close_place_slugs',
    [
        pytest.param([], ['place_1'], ['place_3'], id='delivery places'),
        pytest.param(
            [{'type': 'pickup', 'slug': 'pickup'}],
            ['place_2'],
            ['place_4'],
            id='pickup places',
        ),
    ],
)
async def test_open_closed_blocks(
        catalog_for_layout,
        eats_catalog_storage,
        filters,
        open_place_slugs,
        close_place_slugs,
):
    """EDACAT-829: Тест проверяет, что pickup-only ресторан не попадает в
    блок закрытых на доставку ресторанов."""

    def add_zone(eats_catalog_storage, place_id, schedule):
        shipping_type = storage.ShippingType.Delivery
        if place_id % 2 == 0:
            shipping_type = storage.ShippingType.Pickup

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                shipping_type=shipping_type,
                working_intervals=schedule,
            ),
        )

    for zone_id in [1, 2]:
        add_zone(
            eats_catalog_storage,
            zone_id,
            [
                storage.WorkingInterval(
                    start=parser.parse('2021-04-07T10:00:00+00:00'),
                    end=parser.parse('2021-04-07T22:00:00+00:00'),
                ),
            ],
        )

    for zone_id in [3, 4]:
        add_zone(
            eats_catalog_storage,
            zone_id,
            [
                storage.WorkingInterval(
                    start=parser.parse('2021-04-08T10:00:00+00:00'),
                    end=parser.parse('2021-04-08T22:00:00+00:00'),
                ),
            ],
        )

    for place_id in [1, 2, 3, 4]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug='place_{}'.format(place_id),
            ),
        )

    request: dict = {
        'blocks': [
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
        ],
    }
    if filters:
        request['filters'] = filters

    response = await catalog_for_layout(**request)
    assert response.status_code == 200

    data = response.json()
    layout_utils.assert_no_block_or_empty('close', data)

    open_block = layout_utils.find_block('open', data)
    assert len(open_block) == len(open_place_slugs)
    for slug in open_place_slugs:
        layout_utils.find_place_by_slug(slug, open_block)

    close_block = layout_utils.find_block('closed', data)
    assert len(close_block) == len(close_place_slugs)
    for slug in close_place_slugs:
        layout_utils.find_place_by_slug(slug, close_block)


@pytest.mark.now('2021-04-07T17:00:00+00:00')
async def test_pickup_block(catalog_for_layout, eats_catalog_storage):
    """EDACAT-829: тест проверяет, что рестораны правильно сортируются в блоке
    самовывозных ресторанов."""

    place_ids: list = [1, 2, 3]
    points: list = [
        storage.Location(lon=47.601, lat=55.810),
        storage.Location(lon=37.601, lat=55.810),
        storage.Location(lon=77.601, lat=55.810),
    ]
    expected_order_ids = [2, 1, 3]
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-04-07T10:00:00+00:00'),
            end=parser.parse('2021-04-07T22:00:00+00:00'),
        ),
    ]

    for place_id, point in zip(place_ids, points):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug='place_{}'.format(place_id),
                location=point,
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                working_intervals=schedule,
                shipping_type=storage.ShippingType.Pickup,
            ),
        )

    response = await catalog_for_layout(
        blocks=[{'id': 'pickup', 'type': 'pickup', 'disable_filters': False}],
    )
    assert response.status_code == 200

    block = layout_utils.find_block('pickup', response.json())
    assert len(block) == len(expected_order_ids)
    for place, expected_id in zip(block, expected_order_ids):
        assert place['meta']['place_id'] == expected_id


@pytest.mark.now('2021-04-07T17:00:00+00:00')
async def test_distance_predicate(catalog_for_layout, eats_catalog_storage):
    """
    EDACAT-1637: проверяем фильтрацию плейсов в блоке
    по растоянию до них
    """

    expected_ids = {1, 2}
    points: tuple = (
        storage.Location(lon=37.6001, lat=55.810),  # 940 m
        storage.Location(lon=37.6003, lat=55.810),  # 950 m
        storage.Location(lon=37.6007, lat=55.810),  # 960 m
    )
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-04-07T10:00:00+00:00'),
            end=parser.parse('2021-04-07T22:00:00+00:00'),
        ),
    ]
    for place_id, point in enumerate(points, 1):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug='place_{}'.format(place_id),
                location=point,
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                working_intervals=schedule,
                shipping_type=storage.ShippingType.Pickup,
            ),
        )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'pickup',
                'type': 'pickup',
                'disable_filters': False,
                'condition': {
                    'type': 'lte',
                    'init': {
                        'arg_name': 'distance_m',
                        'arg_type': 'int',
                        'value': 959,
                    },
                },
            },
        ],
    )

    assert response.status_code == 200
    block = layout_utils.find_block('pickup', response.json())
    response_ids = set()
    for place in block:
        response_ids.add(place['meta']['place_id'])
    assert response_ids == expected_ids


EATS_CUSTOMER_SLOTS = (
    '/eats-customer-slots/api/v1/places/calculate-delivery-time'
)


@experiments.USE_DELIVERY_SLOTS
@pytest.mark.now('2021-05-09T17:36:00+03:00')
async def test_deliver_slots_open(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    EDACAT-957: проверяет, что opеn стратегия фильтрации учитывает слоты
    доставки для магазинов
    """
    open_place = [
        storage.WorkingInterval(
            start=parser.parse('2021-05-09T15:00:00+03:00'),
            end=parser.parse('2021-05-09T20:00:00+03:00'),
        ),
    ]
    closed_place = [
        storage.WorkingInterval(
            start=parser.parse('2021-05-09T15:00:00+03:00'),
            end=parser.parse('2021-05-09T17:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='open',
            business=storage.Business.Shop,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.OurPicking,
            ),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(place_id=1, zone_id=1, working_intervals=open_place),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='closed',
            business=storage.Business.Shop,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.OurPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=2, zone_id=2, working_intervals=closed_place),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            slug='no_slots',
            business=storage.Business.Shop,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.OurPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=3, zone_id=3, working_intervals=open_place),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=4,
            brand=storage.Brand(brand_id=4),
            slug='native_assembly',
            business=storage.Business.Shop,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.ShopPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=4, zone_id=4, working_intervals=open_place),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(request):
        assert {
            'places': [
                {'place_id': 1, 'estimated_delivery_duration': 1380},
                {'place_id': 2, 'estimated_delivery_duration': 1380},
                {'place_id': 3, 'estimated_delivery_duration': 1380},
                {'place_id': 4, 'estimated_delivery_duration': 1380},
            ],
            'delivery_point': {'lat': 55.802998, 'lon': 37.591503},
            'delivery_time': {
                'time': '2021-05-09T17:36:00',
                'zone': 'Europe/Moscow',
            },
            'device_id': 'testsuite',
            'source': 'layout',
        } == request.json

        return {
            'places': [
                {
                    'place_id': '1',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': False,
                },
                {
                    'place_id': '2',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': False,
                },
                {
                    'place_id': '3',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 4200,
                    'slots_availability': False,
                    'asap_availability': False,
                },
            ],
        }

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'testsuite',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert eats_customer_slots.times_called == 1
    assert response.status == 200

    block = layout_utils.find_block('open', response.json())

    layout_utils.find_place_by_slug('open', block)
    layout_utils.find_place_by_slug('closed', block)
    layout_utils.find_place_by_slug('native_assembly', block)
    layout_utils.assert_no_slug('no_slots', block)

    assert len(block) == 3


@pytest.mark.parametrize('is_place_open', [True, False])
@pytest.mark.parametrize(
    'flag_to_test,expected_meta',
    [
        pytest.param(
            'with_extra_delivery_meta',
            {
                'brand_id': 0,
                'delivery_time_max': 35,
                'delivery_time_min': 25,
                'is_available_now': True,
                'place_id': 0,
                'surge_level': 0,
                'is_ultima': False,
                'categories': ['Завтраки'],
            },
            id='with_extra_delivery_meta',
        ),
        pytest.param(
            'with_delivery_conditions',
            {
                'brand_id': 0,
                'delivery_conditions': [
                    {'delivery_cost': '139', 'order_price': '0'},
                    {'delivery_cost': '89', 'order_price': '500'},
                    {'delivery_cost': '0', 'order_price': '2000'},
                ],
                'is_available_now': True,
                'place_id': 0,
                'surge_level': 0,
                'is_ultima': False,
                'categories': ['Завтраки'],
            },
            id='with_delivery_conditions',
        ),
    ],
)
@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_block_additional_info(
        catalog_for_layout,
        eats_catalog_storage,
        flag_to_test,
        expected_meta,
        is_place_open,
):
    place = 'place_slug'
    create_place(eats_catalog_storage, 0, place, not is_place_open)

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'any',
                'type': 'any',
                'disable_filters': False,
                flag_to_test: True,
            },
        ],
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data['blocks']) == 1
    block = data['blocks'][0]
    assert len(block['list']) == 1
    meta = block['list'][0]['meta']

    if not is_place_open:
        expected_meta['is_available_now'] = False
        if flag_to_test == 'with_extra_delivery_meta':
            expected_meta['opening_datetime'] = '2021-03-16T11:00:00+00:00'

    assert meta == expected_meta


@pytest.mark.now('2022-02-16T14:50:00+03:00')
@pytest.mark.parametrize(
    [],
    [
        pytest.param(id='preorder enabled'),
        pytest.param(
            marks=experiments.DISABLE_PREORDER, id='preorder disabled',
        ),
    ],
)
async def test_shipping_type_for_preorder(
        catalog_for_layout, eats_catalog_storage,
):
    """
    Проверяет, что при отключенном предзаказе фильтрация блока по
    типам доставки будет работать как и при включенном предзаказе
    """
    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-02-16T12:00:00+03:00'),
                    end=parser.parse('2022-02-16T18:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        [
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'condition': {
                    'init': {
                        'arg_name': 'shipping_types',
                        'set': ['delivery', 'pickup'],
                        'set_elem_type': 'string',
                    },
                    'type': 'intersects',
                },
            },
        ],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('open', response.json())
    layout_utils.find_place_by_slug('place', block)

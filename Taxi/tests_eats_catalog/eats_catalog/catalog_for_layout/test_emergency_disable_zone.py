from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils


EATS_CUSTOMER_SLOTS = (
    '/eats-customer-slots/api/v1/places/calculate-delivery-time'
)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.parametrize(
    'expected_open,expected_closed',
    (
        pytest.param(
            ['slug_taxi', 'slug_auto'],
            ['slug_pedestrian'],
            marks=experiments.emergency_disable_zone(disable_pedestrian=True),
            id='disable_pedestrian',
        ),
        pytest.param(
            ['slug_pedestrian', 'slug_auto'],
            ['slug_taxi'],
            marks=experiments.emergency_disable_zone(disable_taxi=True),
            id='disable_taxi',
        ),
        pytest.param(
            ['slug_taxi', 'slug_pedestrian'],
            ['slug_auto'],
            marks=experiments.emergency_disable_zone(disable_auto=True),
            id='disable_auto',
        ),
        pytest.param(
            [],
            ['slug_pedestrian', 'slug_taxi', 'slug_auto'],
            marks=experiments.emergency_disable_zone(
                disable_pedestrian=True, disable_taxi=True, disable_auto=True,
            ),
            id='disable_all',
        ),
    ),
)
async def test_emergency_disable_zone(
        catalog_for_layout,
        eats_catalog_storage,
        expected_open,
        expected_closed,
):
    """
    Проверяет, что конфигом eats_catalog_emergency_disable_zone
    можно отключать типы зон
    """

    params = (
        (1, 'slug_pedestrian', storage.CouriersType.Pedestrian),
        (2, 'slug_taxi', storage.CouriersType.YandexTaxi),
        (3, 'slug_auto', storage.CouriersType.Vehicle),
    )

    for idx, slug, courier in params:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx, brand=storage.Brand(brand_id=idx), slug=slug,
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=idx,
                place_id=idx,
                couriers_type=courier,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-15T10:00:00+03:00'),
                        end=parser.parse('2021-03-15T22:00:00+03:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_layout(
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
        ],
    )

    assert response.status_code == 200
    data = response.json()

    if expected_open:
        open_block = layout_utils.find_block('open', data)
        for slug in expected_open:
            layout_utils.find_place_by_slug(slug, open_block)

    if expected_closed:
        closed_block = layout_utils.find_block('closed', data)
        for slug in expected_closed:
            layout_utils.find_place_by_slug(slug, closed_block)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@experiments.emergency_disable_zone(
    disable_pedestrian=True, disable_taxi=True, disable_auto=True,
)
async def test_emergency_disable_zone_pickup(
        catalog_for_layout, eats_catalog_storage,
):
    """
    Проверяет, что конфиг eats_catalog_emergency_disable_zone
    Не влияет на самовывоз
    """

    slug = 'slug_pickup'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug=slug,
            quick_filters=storage.QuickFilters(
                general=[storage.QuickFilter(quick_filter_id=1)],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
        filters_v2={
            'groups': [
                {
                    'type': 'and',
                    'filters': [{'slug': 'pickup', 'type': 'pickup'}],
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    open_block = layout_utils.find_block('open', data)
    layout_utils.find_place_by_slug(slug, open_block)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@experiments.USE_DELIVERY_SLOTS
@experiments.emergency_disable_zone(
    disable_pedestrian=True, disable_taxi=True, disable_auto=True,
)
async def test_emergency_disable_zone_shop(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    Проверяет, что конфиг eats_catalog_emergency_disable_zone
    Отключает запрос в слоты
    """

    slug = 'slug_slot'

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug=slug, business=storage.Business.Shop),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(_):
        return {
            'places': [
                {
                    'place_id': '1',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': True,
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
        ],
    )

    assert eats_customer_slots.times_called == 0

    assert response.status_code == 200
    data = response.json()

    layout_utils.assert_no_block_or_empty('open', data)

    closed_block = layout_utils.find_block('closed', data)
    layout_utils.find_place_by_slug(slug, closed_block)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@experiments.emergency_disable_zone(
    disable_pedestrian=True, disable_taxi=True, disable_auto=True,
)
@pytest.mark.parametrize(
    'delivery_type,business',
    (
        pytest.param(
            storage.PlaceType.Marketplace,
            storage.Business.Restaurant,
            id='marketplace',
        ),
        pytest.param(
            storage.PlaceType.Native, storage.Business.Store, id='lavka',
        ),
    ),
)
async def test_emergency_disable_non_native(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        delivery_type,
        business,
):
    """
    Проверяет, что конфиг eats_catalog_emergency_disable_zone
    Не влияет на МП и Лавку
    """

    slug = 'bureaucrat'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug=slug, place_type=delivery_type, business=business,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(_):
        return {
            'places': [
                {
                    'place_id': '1',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': True,
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
        ],
    )

    assert eats_customer_slots.times_called == 0

    assert response.status_code == 200
    data = response.json()

    layout_utils.assert_no_block_or_empty('closed', data)

    open_block = layout_utils.find_block('open', data)
    layout_utils.find_place_by_slug(slug, open_block)

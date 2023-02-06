from dateutil import parser
import pytest

from eats_catalog import storage
from . import layout_utils


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_pickup_deduplication(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    Проверяем, что независимо от типа сортировки
    дедупликацию выигрывает один и тот же плейс
    """

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def _eats_plus(_):
        return {'cashback': []}

    expected_slug = 'close'
    unexpected_slug = 'far'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug=unexpected_slug,
            location=storage.Location(lon=37.5916, lat=55.8129),
            new_rating=storage.NewRating(rating=5),
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
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=1),
            slug=expected_slug,
            location=storage.Location(lon=37.591503, lat=55.802998),
            new_rating=storage.NewRating(rating=4),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    async def request(sort):
        return await catalog_for_layout(
            blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
            sort=sort,
            filters_v2={
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'type': 'pickup', 'slug': 'pickup'}],
                    },
                ],
            },
        )

    response = await request('default')
    assert response.status_code == 200
    data = response.json()
    block = layout_utils.find_block('any', data)
    layout_utils.find_place_by_slug(expected_slug, block)
    layout_utils.assert_no_slug(unexpected_slug, block)

    response = await request('high_rating')
    assert response.status_code == 200
    data = response.json()
    block = layout_utils.find_block('any', data)
    layout_utils.find_place_by_slug(expected_slug, block)
    layout_utils.assert_no_slug(unexpected_slug, block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
async def test_pickup_native_mp_deduplication(
        catalog_for_layout, eats_catalog_storage,
):
    """
    Проверяем, что если растояние до рестов одинаковое,
    дедупликацию выигрывает натив
    """

    for idx, delivery_type in (
            (1, storage.PlaceType.Native),
            (2, storage.PlaceType.Marketplace),
    ):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                brand=storage.Brand(brand_id=1),
                slug=f'slug_{idx}',
                location=storage.Location(lon=37.5916, lat=55.8129),
                place_type=delivery_type,
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=idx,
                place_id=idx,
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
                    'filters': [{'type': 'pickup', 'slug': 'pickup'}],
                },
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()

    block = layout_utils.find_block('open', data)
    layout_utils.find_place_by_slug('slug_1', block)
    layout_utils.assert_no_slug('slug_2', block)

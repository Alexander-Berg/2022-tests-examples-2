from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils
from . import search_utils


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@experiments.eats_surge_planned(interval=120)
@configs.eats_catalog_delivery_feature(
    taxi_delivery_icon_url='test://taxi_delivery',
    disable_by_surge_for_minutes=180,  # 3 часа
    radius_surge_can_keep_automobile_zones=True,
)
@pytest.mark.parametrize(
    'show_radius, expect_delivery_disabled, preorder',
    [
        pytest.param(
            1000.0,
            True,
            False,
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius surge applied',
        ),
        pytest.param(
            1000.0,
            True,
            True,
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius surge applied preorder',
        ),
        pytest.param(
            1000.0,
            True,
            'can-not-deliver',
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius surge applied preorder can not deliver',
        ),
        pytest.param(
            1000.0,
            False,
            False,
            marks=experiments.eats_catalog_surge_radius(),
            id='radius surge applied keep taxi',
        ),
        pytest.param(
            2000.0,
            False,
            False,
            marks=experiments.eats_catalog_surge_radius(),
            id='radius too big',
        ),
        pytest.param(1000.0, False, False, id='no experiment'),
    ],
)
async def test_delivery_disabled_by_radius_surge(
        catalog_for_full_text_search,
        eats_catalog_storage,
        surge_resolver,
        surge,
        show_radius,
        expect_delivery_disabled,
        preorder,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='place_slug',
            location=storage.Location(lon=37.5916, lat=55.8129),
        ),
    )

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-25T10:00:00+03:00'),
            end=parser.parse('2021-07-25T20:00:00+03:00'),
        ),
    ]
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=working_intervals,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            couriers_type=storage.CouriersType.YandexTaxi,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=working_intervals,
        ),
    )

    surge.set_place_info(
        place_id=1,
        surge={
            'nativeInfo': {
                'surgeLevel': 0,
                'loadLevel': 0,
                'deliveryFee': 0.0,
                'show_radius': show_radius,
            },
        },
    )
    surge_resolver.place_radius = {
        1: surge_utils.SurgeRadius(pedestrian=show_radius),
    }

    response = await catalog_for_full_text_search(
        longitude=37.6,
        latitude=55.8,
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
        ],
        delivery_time='2021-07-25T15:30:00+03:00'
        if preorder == 'can-not-deliver'
        else '2021-07-25T16:00:00+03:00'
        if preorder
        else None,
    )

    if expect_delivery_disabled:
        search_utils.assert_no_block_or_empty('open', response.json())
        block = search_utils.find_block('closed', response.json())
        expect_delivery_text = 'Сегодня 19:00'
    else:
        search_utils.assert_no_block_or_empty('closed', response.json())
        block = search_utils.find_block('open', response.json())
        expect_delivery_text = '35\u2009–\u200945 мин'
    place = search_utils.find_place_by_slug('place_slug', block)
    assert place['delivery']['text'] == expect_delivery_text
    assert place['availability']['is_available'] == (
        not expect_delivery_disabled
    )

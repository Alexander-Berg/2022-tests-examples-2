from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils


@pytest.mark.now('2021-08-17T14:00:00+03:00')
async def test_invisible_preorder(catalog_for_layout, eats_catalog_storage):
    eats_catalog_storage.add_place_from_file('447453_place.json')
    eats_catalog_storage.add_zones_from_file('447453_zones.json')

    eats_catalog_storage.add_place_from_file('447468_place.json')
    eats_catalog_storage.add_zones_from_file('447468_zones.json')

    response = await catalog_for_layout(
        location={'latitude': 48.715794, 'longitude': 44.488175},
        blocks=[{'id': 'closed', 'type': 'closed', 'disable_filters': False}],
        delivery_time={'time': '2021-08-18T04:00:00+03:00', 'zone': 10800},
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('closed', data)
    layout_utils.find_place_by_slug('obedy_angarskij', block)


@pytest.mark.now('2021-12-23T15:13:00+03:00')
@pytest.mark.parametrize(
    'delivery_time, no_block, timepicker, business, disable_on_place',
    [
        pytest.param(
            '2021-12-23T15:13:00+03:00',
            False,
            [
                [
                    '2021-12-23T15:30:00+03:00',
                    '2021-12-23T16:00:00+03:00',
                    '2021-12-23T16:30:00+03:00',
                    '2021-12-23T17:00:00+03:00',
                    '2021-12-23T17:30:00+03:00',
                    '2021-12-23T18:00:00+03:00',
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                ],
                [],
            ],
            storage.Business.Shop,
            False,
            id='ASAP, preorder enabled',
        ),
        pytest.param(
            '2021-12-23T15:13:00+03:00',
            False,
            [[], []],
            storage.Business.Shop,
            False,
            marks=experiments.DISABLE_PREORDER,
            id='ASAP, preorder disabled',
        ),
        pytest.param(
            '2021-12-23T18:13:00+03:00',
            False,
            [
                [
                    '2021-12-23T15:30:00+03:00',
                    '2021-12-23T16:00:00+03:00',
                    '2021-12-23T16:30:00+03:00',
                    '2021-12-23T17:00:00+03:00',
                    '2021-12-23T17:30:00+03:00',
                    '2021-12-23T18:00:00+03:00',
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                ],
                [],
            ],
            storage.Business.Restaurant,
            False,
            id='Preorder, preorder enabled',
        ),
        pytest.param(
            '2021-12-23T18:13:00+03:00',
            True,
            [[], []],
            storage.Business.Restaurant,
            False,
            marks=experiments.DISABLE_PREORDER,
            id='Preoreder, preorder disabled',
        ),
        pytest.param(
            '2021-12-23T15:13:00+03:00',
            False,
            [
                [
                    '2021-12-23T15:30:00+03:00',
                    '2021-12-23T16:00:00+03:00',
                    '2021-12-23T16:30:00+03:00',
                    '2021-12-23T17:00:00+03:00',
                    '2021-12-23T17:30:00+03:00',
                    '2021-12-23T18:00:00+03:00',
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                ],
                [],
            ],
            storage.Business.Shop,
            False,
            marks=experiments.DISABLE_PREORDER_FOR_RESTAURANTS,
            id='ASAP + shop, preorder disabled for restaurants',
        ),
        pytest.param(
            '2021-12-23T15:13:00+03:00',
            False,
            [[], []],
            storage.Business.Shop,
            False,
            marks=experiments.DISABLE_PREORDER_FOR_SHOPS_ONLY,
            id='ASAP + shop, preorder disabled for shops',
        ),
        pytest.param(
            '2021-12-23T16:00:00+03:00',
            True,
            [[], []],
            storage.Business.Shop,
            False,
            marks=experiments.DISABLE_PREORDER_FOR_SHOPS_ONLY,
            id='Preorder + shop, preorder disabled for shops',
        ),
        pytest.param(
            '2021-12-23T16:00:00+03:00',
            False,
            [
                [
                    '2021-12-23T15:30:00+03:00',
                    '2021-12-23T16:00:00+03:00',
                    '2021-12-23T16:30:00+03:00',
                    '2021-12-23T17:00:00+03:00',
                    '2021-12-23T17:30:00+03:00',
                    '2021-12-23T18:00:00+03:00',
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                ],
                [],
            ],
            storage.Business.Restaurant,
            False,
            marks=experiments.DISABLE_PREORDER_FOR_SHOPS_ONLY,
            id='Preorder + restaurant, preorder disabled for shops',
        ),
        pytest.param(
            '2021-12-23T16:00:00+03:00',
            True,
            [[], []],
            storage.Business.Shop,
            True,
            id='Disable preorder by place',
        ),
        pytest.param(
            '2021-12-23T16:00:00+03:00',
            True,
            [[], []],
            storage.Business.Restaurant,
            True,
            id='Disable preorder by place',
        ),
    ],
)
async def test_preorder_disable(
        catalog_for_layout,
        eats_catalog_storage,
        delivery_time,
        no_block,
        timepicker,
        business,
        disable_on_place,
):

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-12-23T12:00:00+03:00'),
            end=parser.parse('2021-12-23T19:00:00+03:00'),
        ),
    ]

    for i in range(1, 11):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=i,
                slug=f'place_{i}',
                brand=storage.Brand(brand_id=i),
                business=business,
                features=storage.Features(
                    supports_preordering=not disable_on_place,
                ),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(zone_id=i, place_id=i, working_intervals=schedule),
        )

    response = await catalog_for_layout(
        location={'longitude': 37.591503, 'latitude': 55.802998},
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
            {
                'id': 'open-delivery-or-pickup',
                'type': 'open-delivery-or-pickup',
                'disable_filters': False,
            },
        ],
        delivery_time={'time': delivery_time, 'zone': 10800},
    )

    assert response.status_code == 200

    data = response.json()
    assert data['timepicker'] == timepicker

    if no_block:
        layout_utils.assert_no_block_or_empty('open', data)
        layout_utils.assert_no_block_or_empty('open-delivery-or-pickup', data)
        layout_utils.find_block('closed', data)
    else:
        layout_utils.assert_no_block_or_empty('closed', data)
        layout_utils.find_block('open', data)
        layout_utils.find_block('open-delivery-or-pickup', data)

from dateutil import parser
import pytest

from eats_catalog import storage
from . import layout_utils


def create_places(eats_catalog_storage):

    for i in range(0, 20):
        eats_catalog_storage.add_place(
            storage.Place(
                slug='place_{}'.format(i),
                place_id=i,
                brand=storage.Brand(brand_id=i),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-06-29T12:47:00+03:00'),
                        end=parser.parse('2021-06-29T20:30:00+03:00'),
                    ),
                ],
            ),
        )


@pytest.mark.now('2021-06-29T18:47:00+03:00')
@pytest.mark.parametrize(
    'low, first_slug, count',
    [
        pytest.param(None, 'place_19', 20, id='no start offset'),
        pytest.param(10, 'place_9', 10, id='start offset = 10'),
        pytest.param(13, 'place_6', 7, id='start offset = 13'),
        pytest.param(0, 'place_19', 20, id='start offset = 0'),
        pytest.param(100, '', 0, id='start offset = 100'),
    ],
)
async def test_start_offset(
        catalog_for_layout, eats_catalog_storage, low, first_slug, count,
):
    create_places(eats_catalog_storage)

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'low': low,
            },
        ],
    )

    assert response.status_code == 200
    if count == 0:
        layout_utils.assert_no_block_or_empty('open', response.json())
    else:
        block = layout_utils.find_block('open', response.json())

        assert len(block) == count
        assert block[0]['payload']['slug'] == first_slug
        assert block[len(block) - 1]['payload']['slug'] == 'place_0'


@pytest.mark.now('2021-06-29T18:47:00+03:00')
@pytest.mark.parametrize(
    'limit, last_slug, count',
    [
        pytest.param(None, 'place_0', 20, id='no limit'),
        pytest.param(10, 'place_10', 10, id='limit = 10'),
        pytest.param(7, 'place_13', 7, id='limit = 13'),
        pytest.param(0, '', 0, id='limit = 0'),
        pytest.param(100, 'place_0', 20, id='limit = 100'),
    ],
)
async def test_start_limit(
        catalog_for_layout, eats_catalog_storage, limit, last_slug, count,
):
    create_places(eats_catalog_storage)

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'limit': limit,
            },
        ],
    )

    assert response.status_code == 200
    if count == 0:
        layout_utils.assert_no_block_or_empty('open', response.json())
    else:
        block = layout_utils.find_block('open', response.json())

        assert len(block) == count
        assert block[len(block) - 1]['payload']['slug'] == last_slug
        assert block[0]['payload']['slug'] == 'place_19'


@pytest.mark.now('2021-06-29T18:47:00+03:00')
@pytest.mark.parametrize(
    'low, limit, first_slug, last_slug, count',
    [
        pytest.param(
            None, None, 'place_19', 'place_0', 20, id='no offset limit',
        ),
        pytest.param(
            2, 10, 'place_17', 'place_8', 10, id='offset = 2, limit = 10',
        ),
        pytest.param(
            15, 7, 'place_4', 'place_0', 5, id='offset = 15, limit = 7',
        ),
        pytest.param(0, 0, '', '', 0, id='offset = 0, limit = 0'),
        pytest.param(20, 30, '', '', 0, id='offset = 20, limit = 30'),
        pytest.param(
            0, 100, 'place_19', 'place_0', 20, id='offset = 0, limit = 100',
        ),
    ],
)
async def test_start_limit_with_offset(
        catalog_for_layout,
        eats_catalog_storage,
        low,
        limit,
        first_slug,
        last_slug,
        count,
):
    create_places(eats_catalog_storage)

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'low': low,
                'limit': limit,
            },
        ],
    )

    assert response.status_code == 200
    if count == 0:
        layout_utils.assert_no_block_or_empty('open', response.json())
    else:
        block = layout_utils.find_block('open', response.json())

        assert len(block) == count
        assert block[0]['payload']['slug'] == first_slug
        assert block[len(block) - 1]['payload']['slug'] == last_slug


@pytest.mark.now('2021-06-29T18:47:00+03:00')
@pytest.mark.parametrize(
    'min_count, is_block_expected',
    [
        pytest.param(10, True, id='min_count = 10'),
        pytest.param(30, False, id='min_count = 30'),
        pytest.param(None, True, id='min_count = None'),
    ],
)
async def test_min_count(
        catalog_for_layout, eats_catalog_storage, min_count, is_block_expected,
):
    create_places(eats_catalog_storage)

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'open',
                'type': 'open',
                'disable_filters': False,
                'min_count': min_count,
            },
        ],
    )

    assert response.status_code == 200
    if not is_block_expected:
        layout_utils.assert_no_block_or_empty('open', response.json())
    else:
        layout_utils.find_block('open', response.json())

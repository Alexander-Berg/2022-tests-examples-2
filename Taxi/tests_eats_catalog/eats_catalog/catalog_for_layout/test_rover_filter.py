from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils


@pytest.mark.now('2021-07-26T12:10:00+03:00')
@experiments.eda_yandex_rover_courier(place_ids=[2], weekday=1, hour=12)
@pytest.mark.config(
    EATS_CATALOG_ROVER_FILTER={
        'filter_name': '_',
        'filter_icon': 'rover_icon',
        'filter_picture': 'rover_picture',
    },
)
@pytest.mark.translations(
    **{
        'eats-catalog': {
            'c4l.filters.rover.name': {'ru': 'Ровер'},
            'c4l.filters.rover.description': {'ru': 'Киберпанк!'},
        },
    },
)
@pytest.mark.parametrize(
    'request_filters,response_filters,expected_slugs',
    (
        pytest.param(
            {'groups': []},
            [
                {
                    'slug': 'rover',
                    'type': 'quickfilter',
                    'payload': {
                        'state': 'enabled',
                        'name': 'Ровер',
                        'description': 'Киберпанк!',
                        'icon_url': 'rover_icon',
                        'picture_url': 'rover_picture',
                    },
                },
            ],
            frozenset(['slug_1', 'slug_2']),
            id='empty request',
        ),
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'slug': 'rover', 'type': 'quickfilter'}],
                    },
                ],
            },
            [
                {
                    'slug': 'rover',
                    'type': 'quickfilter',
                    'payload': {
                        'state': 'selected',
                        'name': 'Ровер',
                        'description': 'Киберпанк!',
                        'icon_url': 'rover_icon',
                        'picture_url': 'rover_picture',
                    },
                },
            ],
            frozenset(['slug_2']),
            id='filter applied',
        ),
    ),
)
async def test_rover_filter(
        catalog_for_layout,
        eats_catalog_storage,
        request_filters,
        response_filters,
        expected_slugs,
):
    """
    Проверяем логику работы фильтра доставкой ровером
    """

    all_slugs = []
    for idx in range(1, 3):
        slug = f'slug_{idx}'
        all_slugs.append(slug)
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                brand=storage.Brand(brand_id=idx),
                slug=slug,
                quick_filters=storage.QuickFilters(general=[]),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=idx,
                place_id=idx,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-15T10:00:00+00:00'),
                        end=parser.parse('2021-03-15T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters_v2=request_filters,
    )

    assert response.status_code == 200

    filters: slice = response.json()['filters_v2']['list']
    assert filters == response_filters

    block = layout_utils.find_block('any', response.json())
    for slug in all_slugs:
        if slug in expected_slugs:
            layout_utils.find_place_by_slug(slug, block)
        else:
            layout_utils.assert_no_slug(slug, block)

import pytest

from . import utils


def create_places(count: int, is_open: bool):
    places = []
    for i in range(count):
        place = {
            'meta': {'place_id': i, 'brand_id': i},
            'payload': {
                'availability': {'is_available': is_open},
                'id': f'id_{i}',
                'name': f'name{i}',
            },
        }
        places.append(place)

    return places


def create_advert_places(count: int, is_open: bool, last_index=0):
    places = []
    for i in range(last_index, last_index + count):
        place = {
            'meta': {'place_id': i, 'brand_id': i},
            'payload': {
                'availability': {'is_available': is_open},
                'id': f'id_{i}',
                'name': f'name{i}',
                'data': {
                    'features': {
                        'advertisement': {
                            'view_url': 'https://yandex.ru/view',
                            'click_url': 'https://yandex.ru/count',
                        },
                    },
                    'meta': [
                        {
                            'id': 'ca99959abe9e49099c89b5b3f6851093',
                            'type': 'advertisements',
                            'payload': {
                                'text': {
                                    'color': [
                                        {'theme': 'light', 'value': '#999588'},
                                        {'theme': 'dark', 'value': '#999588'},
                                    ],
                                    'text': 'Реклама',
                                },
                                'background': [
                                    {'theme': 'light', 'value': '#EBE7DA'},
                                    {'theme': 'dark', 'value': '#56544D'},
                                ],
                            },
                        },
                    ],
                },
            },
        }
        places.append(place)
    return places


@pytest.mark.layout(
    autouse=True,
    slug='popup_layout',
    widgets=[
        utils.Widget(
            type='places_collection',
            name='first',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
        utils.Widget(
            type='places_collection',
            name='closed',
            meta={'place_filter_type': 'closed', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
        utils.Widget(
            type='places_collection',
            name='first repeat',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
        ),
    ],
)
@pytest.mark.parametrize(
    'location, count_per_block, stat_name, count',
    [
        pytest.param(
            {'latitude': 55.750028, 'longitude': 37.534397},
            20,
            'places.open.213',
            40,
            id='moscow',
        ),
        pytest.param(
            {'latitude': 53.892707, 'longitude': 27.551402},
            3,
            'places.open.157',
            6,
            id='minsk',
        ),
    ],
)
async def test_open_count(
        taxi_eats_layout_constructor,
        layout_constructor,
        statistics,
        mockserver,
        location,
        count_per_block,
        stat_name,
        count,
):
    """
    Проверяет, что количество открытых заведений, в выдаче пишется в сервис
    статистики.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        assert len(request.json['blocks']) == 2

        blocks = []

        for block in request.json['blocks']:
            is_open = 'open' in block['id']

            blocks.append(
                {
                    'id': block['id'],
                    'list': create_places(count_per_block, is_open),
                },
            )

        return {'filters': {}, 'sort': {}, 'timepicker': [], 'blocks': blocks}

    async with statistics.capture(taxi_eats_layout_constructor) as capture:
        response = await layout_constructor.post(location=location)

        assert response.status_code == 200
        assert eats_catalog.times_called == 1

    assert stat_name in capture.statistics, capture.statistics.keys()
    assert capture.statistics[stat_name] == count


CAROUSEL_WIDGET = utils.Widget(
    type='places_carousel',
    name='first',
    meta={'carousel': 'advertisements'},
    payload={},
    payload_schema={},
)

COLLECTION_WIDGET = utils.Widget(
    type='places_collection',
    name='first repeat',
    meta={
        'place_filter_type': 'advertisements',
        'output_type': 'list',
        'advert_settings': {},
    },
    payload={},
    payload_schema={},
)


@pytest.mark.parametrize(
    'location, count_per_block,expected_count, is_open',
    [
        pytest.param(
            {'latitude': 55.750028, 'longitude': 37.534397},
            20,
            20,
            True,
            id='carousel_widget',
            marks=[
                pytest.mark.layout(
                    autouse=True,
                    slug='popup_layout',
                    widgets=[CAROUSEL_WIDGET],
                ),
            ],
        ),
        pytest.param(
            {'latitude': 55.750028, 'longitude': 37.534397},
            3,
            3,
            True,
            id='collection_widget',
            marks=[
                pytest.mark.layout(
                    autouse=True,
                    slug='popup_layout',
                    widgets=[COLLECTION_WIDGET],
                ),
            ],
        ),
        pytest.param(
            {'latitude': 55.750028, 'longitude': 37.534397},
            3,
            6,
            True,
            id='collection_and_carousel_widget_with_opened',
            marks=[
                pytest.mark.layout(
                    autouse=True,
                    slug='popup_layout',
                    widgets=[COLLECTION_WIDGET, CAROUSEL_WIDGET],
                ),
            ],
        ),
        pytest.param(
            {'latitude': 55.750028, 'longitude': 37.534397},
            5,
            0,
            False,
            id='collection_and_carousel_widget_with_closed',
            marks=[
                pytest.mark.layout(
                    autouse=True,
                    slug='popup_layout',
                    widgets=[COLLECTION_WIDGET, CAROUSEL_WIDGET],
                ),
            ],
        ),
    ],
)
async def test_adverts_open_count(
        taxi_eats_layout_constructor,
        layout_constructor,
        statistics,
        mockserver,
        location,
        count_per_block,
        expected_count,
        is_open,
):
    """
    EDACAT-2883: Проверяет, что количество открытых рекламных заведений,
    в выдаче пишется в сервис статистики.
    """

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def eats_catalog(request):
        print(request.json['blocks'])
        assert len(request.json['blocks']) == 1

        blocks = []

        for block in request.json['blocks']:
            blocks.append(
                {
                    'id': block['id'],
                    'list': (
                        create_places(count_per_block, is_open)
                        + create_advert_places(
                            count_per_block, is_open, count_per_block,
                        )
                    ),
                },
            )

        return {'filters': {}, 'sort': {}, 'timepicker': [], 'blocks': blocks}

    async with statistics.capture(taxi_eats_layout_constructor) as capture:
        response = await layout_constructor.post(
            location=location, region_id=42,
        )

    assert response.status_code == 200
    assert eats_catalog.times_called == 1

    zero_metric = 'zero.advert-places.open.213'
    non_zero_metric = 'non-zero.advert-places.open.213'

    print(capture.statistics, capture.statistics.keys())

    assert zero_metric in capture.statistics, capture.statistics.keys()
    assert capture.statistics[zero_metric] == expected_count

    if is_open:
        assert non_zero_metric in capture.statistics, capture.statistics.keys()
        assert capture.statistics[non_zero_metric] == expected_count
    else:
        assert (
            non_zero_metric not in capture.statistics
        ), capture.statistics.keys()

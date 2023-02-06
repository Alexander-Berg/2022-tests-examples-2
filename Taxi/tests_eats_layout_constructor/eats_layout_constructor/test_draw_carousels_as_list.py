import pytest

from testsuite.utils import matching


def get_places(count):
    return list(
        [
            {
                'meta': {'place_id': i, 'brand_id': i},
                'payload': {'id': f'id_{i}', 'name': f'name{i}'},
            }
            for i in range(count)
        ],
    )


@pytest.mark.now('2020-05-07T11:30:00+0300')
@pytest.mark.experiments3(filename='eats_layout_places_carousels.json')
@pytest.mark.parametrize(
    'carousels,layout',
    [
        (
            {
                'promo': {
                    'count': 2,
                    'in_response': True,
                    'id': '1_places_carousel',
                    'title': 'Акции и новинки',
                },
                'new': {
                    'count': 2,
                    'in_response': True,
                    'id': '1_places_carousel',
                    'title': 'Акции и новинки',
                },
            },
            {
                'layout': [
                    {
                        'id': '1_places_carousel',
                        'payload': {'title': 'Акции и новинки'},
                        'type': 'places_carousel',
                    },
                ],
                'data': {
                    'places_carousels': [
                        {
                            'id': '1_places_carousel',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'places': [
                                    {
                                        'id': 'id_0',
                                        'name': 'name0',
                                        'context': matching.any_string,
                                    },
                                    {
                                        'id': 'id_1',
                                        'name': 'name1',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        ),
        (
            {
                'promo': {
                    'count': 1,
                    'in_response': True,
                    'id': '1_places_carousel',
                    'title': 'Акции и новинки',
                },
                'new': {
                    'count': 2,
                    'in_response': True,
                    'id': '1_places_carousel',
                    'title': 'Акции и новинки',
                },
            },
            {
                'layout': [
                    {
                        'id': '1_places_carousel',
                        'payload': {'title': 'Акции и новинки'},
                        'type': 'places_list',
                    },
                ],
                'data': {
                    'places_lists': [
                        {
                            'id': '1_places_carousel',
                            'template_name': 'Widget template 1',
                            'payload': {
                                'places': [
                                    {
                                        'id': 'id_0',
                                        'name': 'name0',
                                        'context': matching.any_string,
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        ),
    ],
)
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
async def test_draw_carousel_as_list(
        taxi_eats_layout_constructor, mockserver, carousels, layout,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):

        catalog_response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [],
        }
        for block in request.json['blocks']:
            carousel = block['type']

            catalog_response['blocks'].append(
                {
                    'id': block['id'],
                    'type': carousel,
                    'list': get_places(carousels[carousel]['count']),
                },
            )
        return catalog_response

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 0.0, 'longitude': 0.0}},
    )

    assert response.status_code == 200
    assert response.json() == layout

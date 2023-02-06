import pytest

from testsuite.utils import matching


def get_place_payload(num, with_context: bool = False):
    return {
        'id': f'id_{num}',
        'name': f'name_{num}',
        'context': matching.any_string if with_context else None,
    }


def get_places(place_count):
    return list(
        [
            {
                'meta': {'place_id': place, 'brand_id': place},
                'payload': get_place_payload(place),
            }
            for place in range(place_count)
        ],
    )


@pytest.mark.now('2020-05-07T11:30:00+0300')
@pytest.mark.experiments3(filename='eats_layout_places_carousels.json')
@pytest.mark.config(
    EATS_LAYOUT_CONSTRUCTOR_EXPERIMENT_SETTINGS={
        'check_experiment': True,
        'refresh_period_ms': 1000,
        'experiment_name': 'eats_layout_template',
    },
)
async def test_empty_color(taxi_eats_layout_constructor, mockserver):
    places_count = 2

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _catalog(request):
        catalog_response = {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [],
        }
        for block in request.json['blocks']:
            catalog_response['blocks'].append(
                {
                    'id': block['id'],
                    'type': block['type'],
                    'list': get_places(places_count),
                },
            )
        return catalog_response

    expected_layout = {
        'layout': [
            {
                'id': '1_places_carousel',
                'payload': {
                    'title': 'Карусель',
                    'background_color_dark': '#FFFFFF',
                },
                'type': 'places_carousel',
            },
            {
                'id': '2_places_list',
                'payload': {
                    'title': 'Список',
                    # in static/test_empty_color it is empty string
                    'background_color_dark': None,
                },
                'type': 'places_list',
            },
        ],
        'data': {
            'places_carousels': [
                {
                    'id': '1_places_carousel',
                    'template_name': 'Widget template 1',
                    'payload': {
                        'places': [
                            get_place_payload(place, True)
                            for place in range(places_count)
                        ],
                    },
                },
            ],
            'places_lists': [
                {
                    'id': '2_places_list',
                    'template_name': 'Widget template 2',
                    'payload': {
                        'places': [
                            get_place_payload(place, True)
                            for place in range(places_count)
                        ],
                    },
                },
            ],
        },
    }

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
    assert response.json() == expected_layout

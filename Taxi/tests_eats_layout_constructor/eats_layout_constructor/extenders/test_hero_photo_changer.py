import pytest


from eats_layout_constructor import configs
from eats_layout_constructor import experiments
from eats_layout_constructor import utils


@pytest.mark.layout(
    slug='places',
    widgets=[
        utils.Widget(
            name='places',
            type='places_collection',
            meta={'place_filter_type': 'open', 'output_type': 'list'},
            payload={},
            payload_schema={},
            meta_widget=utils.MetaWidget(
                type='place_layout',
                slug='meta_widget_for_extender',
                name='meta_widget_for_extender',
                settings={
                    'hero_photo': {'limit': 0},
                    'order': [],
                    'action_extenders': [],
                    'meta_extenders': [],
                },
            ),
        ),
    ],
)
@experiments.layout('places')
@configs.layout_experiment_name()
@configs.brands_photo(
    {'1': {'breakfast': 'http://second', 'something': 'http://third'}},
)
@pytest.mark.parametrize(
    'expected_urls',
    [
        pytest.param(['http://first', 'http://second'], id='no tag'),
        pytest.param(
            ['http://second', 'http://first'],
            marks=(experiments.brand_photo_tag('breakfast')),
            id='second first',
        ),
        pytest.param(
            ['http://third', 'http://first', 'http://second'],
            marks=(experiments.brand_photo_tag('something')),
            id='new image',
        ),
    ],
)
async def test_hero_photo_changer(
        taxi_eats_layout_constructor, mockserver, expected_urls,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog(_):
        return {
            'filters': {},
            'sort': {},
            'timepicker': [],
            'blocks': [
                {
                    'id': 'open',
                    'list': [
                        {
                            'meta': {'place_id': 1, 'brand_id': 1},
                            'payload': {
                                'brand': {'slug': 'brand'},
                                'media': {
                                    'photos': [
                                        {'uri': 'http://first'},
                                        {'uri': 'http://second'},
                                    ],
                                },
                                'layout': [{'layout': [], 'type': 'meta'}],
                                'data': {'features': {}, 'meta': []},
                            },
                        },
                    ],
                },
            ],
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
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
    assert catalog.times_called == 1

    data = response.json()

    places_lists = data['data']['places_lists']
    assert len(places_lists) == 1

    places = places_lists[0]['payload']['places']
    assert len(places) == 1

    place = places_lists[0]['payload']['places'][0]

    # NOTE(EDACAT-2454): Проверяем, что махинации экстендера не уничтожили
    # другие данные в плейсе
    expected_fields = [
        'analytics',
        'brand',
        'context',
        'data',
        'media',
        'layout',
    ]
    for field in expected_fields:
        assert field in place, f'missing place field {field}'

    assert expected_urls == [
        photo['uri'] for photo in place['media']['photos']
    ]

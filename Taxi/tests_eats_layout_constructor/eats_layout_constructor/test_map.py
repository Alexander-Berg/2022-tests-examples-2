import pytest

from . import configs
from . import experiments


@pytest.fixture(name='mock_catalog_for_map')
def _mock_catalog_for_map(mockserver, load_json):
    class CatalogForMap:
        clusters = []
        catalog = None

        def set_clusters(self, clusters):
            self.clusters = clusters

    catalog = CatalogForMap()

    @mockserver.json_handler('/eats-catalog-map/internal/v1/catalog-for-map')
    def _catalog(request):
        assert request.json['bounding_box'] == [1.1, 2.2, 3.3, 4.4]
        assert request.json['zoom'] == 4.4
        assert request.json['location'] == {'latitude': 0.0, 'longitude': 0.0}
        return {
            'places': load_json('catalog_map_places.json'),
            'filters': {
                'list': [
                    {
                        'active': False,
                        'group': 'pickup',
                        'name': 'pickup',
                        'slug': 'pickup',
                        'type': 'pickup',
                    },
                ],
            },
            'filters_v2': {
                'list': [
                    {
                        'payload': {'name': 'pickup', 'state': 'enabled'},
                        'slug': 'pickup',
                        'type': 'pickup',
                    },
                    {
                        'payload': {'name': 'pizza', 'state': 'selected'},
                        'slug': 'pizza',
                        'type': 'quickfilter',
                    },
                ],
                'meta': {'selected_count': 1},
            },
            'bounding_box': [1.1, 2.2, 3.3, 4.4],
            'zoom_range': {'min': 4, 'max': 6},
            'timepicker': [
                ['2020-05-15T18:30:00+05:00', '2020-05-15T19:00:00+05:00'],
                [
                    '2020-05-16T09:30:00+05:00',
                    '2020-05-16T10:00:00+05:00',
                    '2020-05-16T10:30:00+05:00',
                ],
            ],
            'clusters': catalog.clusters,
        }

    catalog.catalog = _catalog
    return catalog


@configs.layout_experiment_name(map_name='eats_layout_template')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='layout_by_exp',
            marks=pytest.mark.experiments3(
                filename='eats_layout_map_layout.json',
            ),
        ),
        pytest.param(
            id='default_layout',
            marks=pytest.mark.config(
                EATS_LAYOUT_CONSTRUCTOR_FALLBACK_LAYOUT={
                    'fallback_enabled': True,
                    'layout_slug': 'any_value',
                    'collection_layout_slug': 'any_value',
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'filters_version',
    [
        pytest.param(
            'v1',
            id='filters_v1',
            marks=pytest.mark.experiments3(
                filename='eats_layout_disable_filters_v2.json',
            ),
        ),
        pytest.param(
            'v2',
            id='filers_v2',
            marks=pytest.mark.experiments3(
                filename='eats_layout_enable_filters_v2.json',
            ),
        ),
    ],
)
@pytest.mark.now('2020-05-08T00:00:00.000Z')
async def test_map_layout(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        filters_version,
        mock_catalog_for_map,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog_for_layout(request):
        return {}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/map',
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
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'bbox': [1.1, 2.2, 3.3, 4.4],
            'zoom_level': 4.4,
        },
    )

    assert mock_catalog_for_map.catalog.times_called == 1
    assert catalog_for_layout.times_called == 0

    assert response.status_code == 200

    expected = load_json('eats-layout-constructor-response.json')
    if filters_version == 'v1':
        expected['data']['filters'] = load_json('filters.json')
        expected['layout'][0]['id'] = expected['data']['filters'][0]['id']
    if filters_version == 'v2':
        expected['data']['filters_v2s'] = load_json('filters_v2s.json')
        expected['layout'][0]['id'] = expected['data']['filters_v2s'][0]['id']
        expected['layout'][0]['type'] = 'filters_v2'
    assert response.json() == expected


@pytest.mark.now('2020-05-08T00:00:00.000Z')
@configs.layout_experiment_name(map_name='eats_layout_template')
@pytest.mark.experiments3(filename='eats_layout_enable_filters_v2.json')
@pytest.mark.experiments3(filename='eats_layout_map_layout.json')
async def test_map_layout_cluster(
        taxi_eats_layout_constructor,
        mockserver,
        load_json,
        mock_catalog_for_map,
):

    mock_catalog_for_map.set_clusters(
        [
            {
                'map_pin': {'cluster_some_extra': 'cluster_data'},
                'place_slugs': ['first', 'second'],
                'title': 'cluster_title',
                'subtitle': 'cluster_subtitle',
            },
        ],
    )

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog_for_layout(request):
        return {}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/map',
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
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'bbox': [1.1, 2.2, 3.3, 4.4],
            'zoom_level': 4.4,
        },
    )

    assert mock_catalog_for_map.catalog.times_called == 1
    assert catalog_for_layout.times_called == 0

    assert response.status_code == 200

    expected = load_json('eats-layout-constructor-cluster-response.json')

    assert response.json() == expected


@pytest.mark.now('2020-05-08T00:00:00.000Z')
@pytest.mark.experiments3(filename='eats_layout_map_layout.json')
@configs.layout_experiment_name(map_name='eats_layout_template')
@experiments.filter_source_response(place_ids=[1])
async def test_map_filter_source_response(
        taxi_eats_layout_constructor,
        mockserver,
        mock_catalog_for_map,
        load_json,
):
    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def catalog_for_layout(_):
        return {}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/map',
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
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'bbox': [1.1, 2.2, 3.3, 4.4],
            'zoom_level': 4.4,
        },
    )

    assert mock_catalog_for_map.catalog.times_called == 1
    assert catalog_for_layout.times_called == 0

    assert response.status_code == 200

    data = response.json()

    expected = load_json('eats-layout-constructor-filtered-response.json')
    assert (
        data['data']['pickup_places_lists']
        == expected['data']['pickup_places_lists']
    )


async def test_map_request_no_device_id(taxi_eats_layout_constructor):
    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/map',
        headers={
            'x-platform': 'android_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'bbox': [1.1, 2.2, 3.3, 4.4],
            'zoom_level': 4.4,
        },
    )
    assert response.status_code == 400

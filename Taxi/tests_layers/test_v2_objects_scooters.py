import operator
import time

import pytest

from . import consts
from . import utils

URL = '/4.0/layers/v2/objects'


SHOW_NAVIGATION_OPTION = {
    'actions': [
        {
            'type': 'show_navigation',
            'attributed_text': {
                'items': [{'text': 'Построить маршрут?', 'type': 'text'}],
            },
            'buttons': [
                {
                    'attributed_text': {
                        'items': [{'text': 'Да', 'type': 'text'}],
                    },
                    'type': 'confirm',
                },
                {
                    'attributed_text': {
                        'items': [{'text': 'Нет', 'type': 'text'}],
                    },
                    'type': 'reject',
                },
            ],
        },
    ],
    'on': 'tap',
}


def build_base_request(mode, screen):
    return {
        'state': {
            'bbox': [37.5, 55.7, 37.6, 55.8],
            'location': [37.51, 55.72],
            'mode': mode,
            'screen': screen,
            'pin': [37.5366, 55.7508],
            'zoom': 19.0,
            'scooters': {'autoselect': True},
        },
    }


def get_scooter_parking_bubble(selected: bool = False):
    component = {'type': 'text', 'value': 'Едем сюда'}
    style = {
        'bg_color': '#ffffff',
        'text_color': '#000000',
        'hide_chevron': True,
    }
    bubble = {
        'hide_after_tap': True,
        'supports_multiline': True,
        'id': 'scooters_parking_bubble',
        'zooms': [17.0, 21.0],
        'components': [],  # required field
    }
    if selected:
        bubble['selected_components'] = [component]
        bubble['selected_style'] = style
    else:
        bubble['components'] = [component]
        bubble['style'] = style
    return bubble


def assert_metrics(actual_metrics, expected_metrics):
    def _assert_metrics(actual, expected):
        # print('!!', actual, expected)
        for key, val in actual.items():
            if key == '$meta':
                continue
            if isinstance(val, dict):
                _assert_metrics(val, expected[key])
            elif (
                (not expected[key](val))
                if callable(expected[key])
                else (expected[key] != val)
            ):
                print('Metrics:', actual_metrics)  # `assert` shrinks the json
                assert not actual_metrics

    _assert_metrics(actual_metrics, expected_metrics)


EXPECTED_PERCENTILES = ['p99', 'p95', 'p75']
ALMOST_IMMEDIATE = {p: lambda v: v < 5 for p in EXPECTED_PERCENTILES}


@pytest.fixture(autouse=True)
def mock_car_list(request, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/car/list')
    def _handler(request):
        print('!!', request.args)
        assert request.args == {'limit': '2147483647'}
        return load_json('car_list_response.json')


@pytest.mark.parametrize(
    'carlist_cache',
    [
        pytest.param(False, id='nocache'),
        pytest.param(
            True,
            marks=(
                pytest.mark.config(
                    LAYERS_CARLIST_CACHE={
                        'providers': {
                            'scooters': {
                                'enabled': True,
                                'uid': 'layers_cache_filler',
                            },
                        },
                    },
                )
            ),
            id='cache',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_enable_drive_clusters.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_discovery_scooters(
        taxi_layers,
        taxi_layers_monitor,
        mockserver,
        mocked_time,
        load_json,
        carlist_cache,
):
    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        assert (
            request.args == {'limit': '2147483647'}
            if carlist_cache
            else {
                'limit': '1000',
                'bbox': '37.45 55.6 37.7 55.9',
                'lang': 'ru',
                'no_selected': '1',
            }
        )  # depends on no_selected_mode
        time.sleep(0.1)
        return load_json('car_list_response.json')

    request = build_base_request(screen='discovery', mode='scooters')
    if carlist_cache:
        await taxi_layers.post(
            URL, request, headers=consts.AUTHORIZED_HEADERS,
        )  # fill the cache
        assert _mock_car_list.times_called == 1

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1

    assert utils.sort_features(response.json()) == utils.sort_features(
        load_json('expected_response_discovery_scooters.json'),
    )

    mocked_time.sleep(10)  # idea copied from userver-sample/*/test_metrix.py
    await taxi_layers.tests_control(invalidate_caches=False)
    metrics = await taxi_layers_monitor.get_metric('layers_metrics')
    assert_metrics(
        metrics,
        {
            'provider_features_count': {
                'scooters': {
                    'polygon': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
                    'polyline': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
                    'point': {'p50': 3, 'p75': 3, 'p95': 3, 'p99': 3},
                },
            },
            'provider_status_count': {
                'scooters': {'success': 2 if carlist_cache else 1},
            },
            'provider_request_features_time': {
                'scooters': (
                    ALMOST_IMMEDIATE
                    if carlist_cache
                    else {p: lambda v: v >= 100 for p in EXPECTED_PERCENTILES}
                ),
            },
            'provider_move_to_collection_time': {'scooters': ALMOST_IMMEDIATE},
        },
    )


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_enable_drive_clusters.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.tariffs(filename='tariffs_moscow.json')
async def test_discovery_clusters(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        return load_json('car_list_scooter_in_cluster_response.json')

    request = build_base_request(screen='discovery', mode='scooters')
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1

    cluster = response.json()['features'][0]
    assert cluster['properties']['type'] == 'scooters_parking'

    # check that cluster has 2 overlays for selected and unselected states
    overlays = cluster['properties']['overlays']
    assert len(overlays) == 2
    assert overlays[0]['show_states'] == ['unselected']
    assert overlays[1]['show_states'] == ['selected']


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_enable_drive_clusters.json')
@pytest.mark.layers_scooters_areas(filename='scooters_areas.json')
async def test_multiorder_normal(taxi_layers, mockserver, load_json):
    sessions_current_response = load_json(
        'sessions_current_multi_order_response.json',
    )

    @mockserver.json_handler('/scooter-backend/sessions/current')
    def _mock_sessions_current(request):
        assert request.query.get('multi_sessions') == 'true'
        return sessions_current_response

    car_list_response = load_json('car_list_response.json')

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        return car_list_response

    request = build_base_request(screen='multiorder', mode='normal')
    request['state']['known_orders'] = ['scooters:123:1', 'scooters:124:1']
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_sessions_current.times_called == 1
    assert _mock_car_list.times_called == 1

    features = response.json()['features']

    scooter_features = [
        f for f in features if f['properties']['type'] == 'scooter'
    ]
    # check that all scooters from /sessions/current exist in response
    assert {
        f'scooters__{session["segment"]["car_number"]}'
        for session in sessions_current_response['sessions']
    } == {f['id'] for f in scooter_features}

    cluster_features = [
        f for f in features if f['properties']['type'] == 'scooters_parking'
    ]
    # check that all parkings from /car/list exist in response
    assert {
        f'scooters__cluster__{cluster["id"]}'
        for cluster in car_list_response['clusters']
    } == {f['id'] for f in cluster_features}
    for feature in cluster_features:
        assert 'options' not in feature['properties']
        assert 'overlays' not in feature['properties']

    area_centroid_features = [
        f for f in features if f['properties']['type'] == 'scooters_area_label'
    ]
    assert (
        sorted(area_centroid_features, key=operator.itemgetter('id'))
        == sorted(
            load_json('scooters_area_centroid_features.json'),
            key=operator.itemgetter('id'),
        )
    )

    assert response.json()['status_view'] == load_json(
        'expected_multiorder_status_view.json',
    )


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.parametrize(
    ['overlay_text'],
    [
        pytest.param(
            '91%',
            marks=pytest.mark.experiments3(
                filename='experiments3_display_settings_scooters.json',
            ),
        ),
        pytest.param(
            '1',
            marks=pytest.mark.experiments3(
                filename='experiments3_display_settings_scooters'
                '_single_scooter_overlay.json',
            ),
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_discovery_scooters_selected_scooter(
        taxi_layers, mockserver, load_json, overlay_text,
):
    number = '123'

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        assert request.args['car_number'] == number
        car_list_response = load_json('car_list_response.json')
        # leave only one scooter
        car_list_response['cars'] = [car_list_response['cars'][0]]
        car_list_response['cars'][0]['number'] = number
        return car_list_response

    request = build_base_request(screen='discovery', mode='scooters')
    request['state']['scooters'] = {'selected_scooter_number': number}
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1
    data = response.json()

    assert data['selected_object_id'] == f'scooters__{number}'
    assert len(data['features']) == 1

    selected_scooter_feature = data['features'][0]

    properties = selected_scooter_feature['properties']

    assert properties['type'] == 'scooter'
    assert properties['options'] == [
        {
            'actions': [
                {'car_number': '123', 'type': 'pick_scooter'},
                {
                    'dst': {'position': [37.53320058, 55.7502463]},
                    'type': 'walk_route',
                },
            ],
            'on': 'tap',
        },
    ]
    assert properties['overlays'] == [
        {
            'anchor': [0.5, 0.88],
            'attributed_text': {
                'items': [
                    {
                        'color': '#FFFFFF',
                        'font_size': 13,
                        'text': overlay_text,
                        'type': 'text',
                    },
                ],
            },
            'background': {'color': '#00ca50'},
            'shape': 'rounded_rectangle',
            'show_states': ['unselected'],
            'zooms': [19.91, 21.0],
        },
    ]


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_enable_drive_clusters.json')
@pytest.mark.parametrize('car_found', [True, False])
@pytest.mark.parametrize('has_destination', [True, False])
async def test_discovery_scooters_selected_scooter_from_cluster(
        taxi_layers, mockserver, load_json, car_found, has_destination,
):
    number = '120'

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        assert request.args['car_number'] == number
        mock_response = load_json('car_list_scooter_in_cluster_response.json')
        if not car_found:
            # remove the car from car/list mock
            mock_response['cars'] = [
                car for car in mock_response['cars'] if car['number'] != number
            ]
        return mock_response

    request = build_base_request(screen='discovery', mode='scooters')
    request['state']['scooters'] = {'selected_scooter_number': number}
    if has_destination:
        request['state']['scooters']['destination'] = [33.6, 55.76]
    # selected scooter must be retrieved even if it is out of bbox
    request['state']['bbox'] = [7.5, 5.7, 7.6, 5.8]
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1
    data = response.json()

    expected_selected_object_id = (
        'scooters__cluster__39091' if car_found else None
    )
    assert data.get('selected_object_id') == expected_selected_object_id

    if car_found:
        selected_object = next(
            (
                f
                for f in data['features']
                if f['id'] == expected_selected_object_id
            ),
            None,
        )
        assert selected_object is not None
        if has_destination:
            options = selected_object['properties']['options']
            option = next((opt for opt in options if opt['on'] == 'tap'), None)
            pick_scooter_action = next(
                (
                    a
                    for a in option['actions']
                    if a['type'] == 'pick_scooter_parking'
                ),
                None,
            )
            assert pick_scooter_action is not None
            assert pick_scooter_action['destination'] == [33.6, 55.76]


@pytest.mark.config(
    LAYERS_CARLIST_CACHE={
        'providers': {
            'scooters': {'enabled': True, 'uid': 'layers_cache_filler'},
        },
    },
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.parametrize(
    'scooters_enabled_on_main, scooters_enabled',
    [(True, True), (True, False), (False, True), (False, False)],
)
async def test_main_normal(
        taxi_layers,
        taxi_layers_monitor,
        mockserver,
        mocked_time,
        experiments3,
        load_json,
        scooters_enabled_on_main,
        scooters_enabled,
):
    if scooters_enabled_on_main:
        experiments3.add_experiments_json(
            load_json('experiments3_scooters_enabled.json'),
        )

    if scooters_enabled:
        experiments3.add_experiments_json(
            load_json('experiments3_scooters.json'),
        )

    scooters_enabled_and_on_main = (
        scooters_enabled and scooters_enabled_on_main
    )

    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/promos-on-map',
    )
    def _mock_promos_on_map(request):
        time.sleep(0.05)
        return {'objects': []}

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        assert request.query == {'limit': '2147483647'}
        assert request.headers['X-Uid'] == 'layers_cache_filler'
        time.sleep(0.1)
        return (
            load_json('car_list_scooter_on_main_response.json')
            if scooters_enabled_and_on_main
            else load_json('car_list_scooter_in_cluster_response.json')
        )

    request = build_base_request(screen='main', mode='normal')
    await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )  # fetch cache
    assert _mock_car_list.times_called == 1
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )  # use cache
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1
    if scooters_enabled_and_on_main:
        assert response.json()['features']

    mocked_time.sleep(10)  # idea copied from userver-sample/*/test_metrix.py
    await taxi_layers.tests_control(invalidate_caches=False)
    metrics = await taxi_layers_monitor.get_metric('layers_metrics')
    expected_provider_status_count = {'success': 2}  # 2 post-s
    expected_metrics = {
        'provider_features_count': {
            'promo': {
                'polygon': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
                'polyline': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
                'point': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
            },
            'static_objects': {
                'polygon': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
                'polyline': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
                'point': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
            },
        },
        'provider_status_count': {
            'promo': expected_provider_status_count,
            'static_objects': expected_provider_status_count,
        },
        'provider_request_features_time': {
            'promo': {p: lambda v: v >= 50 for p in EXPECTED_PERCENTILES},
            'static_objects': ALMOST_IMMEDIATE,
        },
        'provider_move_to_collection_time': {
            'promo': ALMOST_IMMEDIATE,
            'static_objects': ALMOST_IMMEDIATE,
        },
    }
    if scooters_enabled_and_on_main:
        expected_metrics['provider_features_count']['scooters'] = {
            'polygon': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
            'polyline': {'p50': 0, 'p75': 0, 'p95': 0, 'p99': 0},
            'point': {'p50': 1, 'p75': 1, 'p95': 1, 'p99': 1},
        }
        expected_metrics['provider_status_count'][
            'scooters'
        ] = expected_provider_status_count
        expected_metrics['provider_request_features_time'][
            'scooters'
        ] = ALMOST_IMMEDIATE  # cached
        expected_metrics['provider_move_to_collection_time'][
            'scooters'
        ] = ALMOST_IMMEDIATE
    assert_metrics(metrics, expected_metrics)


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_enable_drive_clusters.json')
@pytest.mark.parametrize('selected_scooter_number', [None, '120', '121'])
@pytest.mark.parametrize('send_destination', [True, False])
async def test_choose_b_scooters(
        taxi_layers,
        mockserver,
        load_json,
        selected_scooter_number,
        send_destination,
):
    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        car_list_response = load_json('car_list_scooter_on_choose_b.json')
        return car_list_response

    request = build_base_request(screen='choose_b', mode='scooters')
    request['state']['scooters'] = (
        {'destination': [37.54624078, 55.74097094]} if send_destination else {}
    )

    if selected_scooter_number:
        request['state']['scooters'][
            'selected_scooter_number'
        ] = selected_scooter_number
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1

    data = response.json()

    if not send_destination:
        assert 'selected_object_id' not in data
    else:
        nearest_parking_id = 'scooters__cluster__3851'

        # assert that nearest parking is selected
        assert data['selected_object_id'] == nearest_parking_id

        nearest_parking = [
            f for f in data['features'] if f['id'] == nearest_parking_id
        ][0]

        assert nearest_parking['properties'][
            'bubble'
        ] == get_scooter_parking_bubble(selected=True)

    for feature in data['features']:
        properties = feature['properties']
        if properties['type'] == 'scooter':
            assert feature['id'] == f'scooters__{selected_scooter_number}'
            continue
        # assert that desired action is present
        assert properties['options'][0]['actions'] == [
            {'type': 'select_as_destination'},
        ]
        # assert that there are only parkings in response
        assert properties['type'] == 'scooters_parking'

    scooters = [
        f for f in data['features'] if f['properties']['type'] == 'scooter'
    ]
    if selected_scooter_number:
        assert _mock_car_list.times_called == 1
        assert len(scooters) == 1

        if selected_scooter_number == '120':
            cluster_ids = set(feature['id'] for feature in data['features'])
            # assert there are no selected_scooter's cluster in response
            assert 'scooters__cluster__390120' not in cluster_ids
    else:
        assert not scooters


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_enable_drive_clusters.json')
@pytest.mark.parametrize(
    'send_destination, expect_parking_bubble',
    [
        pytest.param(True, True, id='expect parking bubble'),
        pytest.param(False, False, id='destination not sent'),
        pytest.param(True, False, id='parking is too far from destination'),
    ],
)
@pytest.mark.parametrize(
    'navigation_enabled',
    [
        pytest.param(False, id='navigation off'),
        pytest.param(True, id='navigation on'),
    ],
)
async def test_totw_scooters(
        taxi_layers,
        mockserver,
        load_json,
        send_destination,
        expect_parking_bubble,
        navigation_enabled,
):
    car_list_response = load_json('car_list_response.json')

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        return car_list_response

    @mockserver.json_handler('/scooter-backend/sessions/current')
    def _mock_sessions_current(request):
        assert request.query.get('session_id') == 'SESSION_ID'
        return load_json('sessions_current_single_order_response.json')

    destination = None
    if send_destination:
        location = car_list_response['clusters'][0]['location']
        destination = [location['lon'], location['lat']]
        if not expect_parking_bubble:
            destination = [
                i + 1.0 for i in destination
            ]  # destination is far from parking

    request = build_base_request(screen='totw', mode='scooters')
    request['state']['known_orders'] = ['scooters:123:1']
    request['state']['scooters'] = {'session_id': 'SESSION_ID'}
    if destination:
        request['state']['scooters']['destination'] = destination
    if navigation_enabled:
        request['state']['scooters']['navigation'] = {'enabled': True}

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1
    assert _mock_sessions_current.times_called == (
        0 if navigation_enabled else 1
    )

    data = response.json()

    # assert that no selected object
    assert data.get('selected_object_id') is None

    for feature in data['features']:
        if feature['properties']['type'] == 'scooters_parking':
            assert feature['properties']['options'] == [SHOW_NAVIGATION_OPTION]

    if navigation_enabled:
        scooters = [
            f for f in data['features'] if f['properties']['type'] == 'scooter'
        ]
        assert not scooters  # no scooters in reponse

    if expect_parking_bubble:
        fix_offer_parking = [
            f
            for f in data['features']
            if f['geometry']['coordinates'] == destination
        ][0]

        assert (
            fix_offer_parking['properties']['style']['image']['name']
            == 'destination_parking_image'
        )
        assert (
            fix_offer_parking['properties']['style']['selected_image']['name']
            == 'destination_parking_image'
        )
        assert (
            fix_offer_parking['properties']['display_settings']['z_index']
            == 101
        )
        assert fix_offer_parking['properties']['display_settings'][
            'zooms'
        ] == [0, 21]
        assert fix_offer_parking['properties'][
            'bubble'
        ] == get_scooter_parking_bubble(selected=False)


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_enable_drive_clusters.json')
@pytest.mark.layers_scooters_areas(filename='forbidden_areas.json')
async def test_parkings_in_forbidden_zone(taxi_layers, mockserver, load_json):
    """
    cluster 3 is in forbidden area,
    check visualization: https://nda.ya.ru/t/hHOMRY8F4nptL7
    """

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_car_list(request):
        clusters = [
            {'count': 0, 'id': 1, 'location': {'lat': 55.72, 'lon': 37.52}},
            {'count': 0, 'id': 2, 'location': {'lat': 55.74, 'lon': 37.54}},
            {'count': 0, 'id': 3, 'location': {'lat': 55.78, 'lon': 37.58}},
        ]
        return {'cars': [], 'views': [], 'clusters': clusters}

    request = build_base_request(screen='discovery', mode='scooters')
    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert _mock_car_list.times_called == 1

    feature_ids = {f['id'] for f in response.json()['features']}
    assert feature_ids == {'scooters__cluster__1', 'scooters__cluster__2'}

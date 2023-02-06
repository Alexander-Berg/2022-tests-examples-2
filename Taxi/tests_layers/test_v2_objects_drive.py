import copy
import hashlib

import pytest

from . import consts
from . import utils

URL = '/4.0/layers/v2/objects'


BASE_REQUEST = {
    'state': {
        'bbox': [37.5, 55.7, 37.6, 55.8],
        'location': [37.51, 55.72],
        'mode': 'normal',
        'screen': 'main',
        'pin': [37.5466, 55.7108],
        'zoom': 19.0,
    },
}


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_multiorder(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/yandex-drive/sessions/current')
    def _mock_yandex_drive(request):
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'400000000').hexdigest()
        )
        assert request.headers['Lon'] == '37.510000'
        assert request.headers['Lat'] == '55.720000'
        return mockserver.make_response(
            json=load_json('response_yandex_drive_sessions_current.json'),
            headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'normal'
    request['state']['screen'] = 'multiorder'
    request['state']['known_orders'] = ['drive:123:1']

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'drive_multiorder_expected_response.json',
    )


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(
    filename='experiments3_add_invisible_totw_object.json',
)
async def test_v2_objects_totw_invisible(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/yandex-drive/sessions/current')
    def _mock_yandex_drive(request):
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        raise mockserver.TimeoutError()

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'totw'

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'totw_invisible_expected_response.json',
    )


@pytest.mark.parametrize(
    'drive_response,expected_response',
    [
        (
            'response_yandex_drive_car_list.json',
            'drive_discovery_expected_response.json',
        ),
        (
            'response_yandex_drive_car_list_no_location.json',
            'drive_discovery_expected_response_no_location.json',
        ),
        (
            'response_yandex_drive_car_list_empty.json',
            'drive_discovery_no_objects_expected_response.json',
        ),
        (
            'response_yandex_drive_car_list_no_cars.json',
            'drive_discovery_no_objects_expected_response.json',
        ),
        (
            'response_yandex_drive_car_list_out_of_bbox.json',
            'drive_discovery_out_of_bbox_expected_response.json',
        ),
        pytest.param(
            'response_yandex_drive_car_list.json',
            'drive_discovery_expected_response_with_clusters.json',
            marks=pytest.mark.experiments3(
                filename='experiments3_enable_drive_clusters.json',
            ),
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_drive_discovery(
        taxi_layers, mockserver, load_json, drive_response, expected_response,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'discovery'

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['Lon'] == '37.510000'
        assert request.headers['Lat'] == '55.720000'
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['UUID'] == 'UUID'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert request.headers['X-YaTaxi-UserId'] == consts.USER_ID
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'400000000').hexdigest()
        )
        assert request.args == {
            'bbox': '37.45 55.6 37.7 55.9',
            'limit': '1000',
            'lang': 'ru',
        }
        return mockserver.make_response(
            json=load_json(drive_response), headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert utils.sort_features(response.json()) == utils.sort_features(
        load_json(expected_response),
    )


@pytest.mark.parametrize(
    'filters, drive_response, expected_response',
    [
        pytest.param(
            [],
            'drive_response_with_filters.json',
            'drive_discovery_expected_filtered_response.json',
            id='filtered',
        ),
        pytest.param(
            [],
            'response_yandex_drive_car_list.json',
            'drive_discovery_expected_response_empty_filters.json',
            id='no_filters_id_drive_response',
        ),
        pytest.param(
            [],
            'drive_response_unknown_filter.json',
            'drive_discovery_expected_response_empty_filters.json',
            id='unknown_filters',
        ),
        pytest.param(
            ['filter_model_renault_kaptur'],
            'drive_response_unknown_filter.json',
            'drive_discovery_expected_response_only_known_filters.json',
            id='only_known_filters',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_drive_filters(
        taxi_layers,
        mockserver,
        load_json,
        filters,
        drive_response,
        expected_response,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'discovery'
    request['state']['drive'] = {
        'filters': {
            'version': 'v1',
            'conditions': [
                ['filter_model_hyundai_creta', 'filter_yaauto'],
                ['filter_model_vw_polo', 'filter_yaauto'],
            ],
        },
    }
    if filters:
        request['state']['drive']['filters']['conditions'].append(filters)

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        return mockserver.make_response(
            json=load_json(drive_response), headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert utils.sort_features(response.json()) == utils.sort_features(
        load_json(expected_response),
    )


@pytest.mark.parametrize(
    'drive_response,expected_response',
    [
        (
            'response_yandex_drive_car_list.json',
            'drive_discovery_demo_expected_response.json',
        ),
        (
            'response_yandex_drive_car_list_empty.json',
            'drive_discovery_demo_no_objects_expected_response.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_drive_discovery_demo(
        taxi_layers, mockserver, load_json, drive_response, expected_response,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'discovery'
    request['state']['drive'] = {'demo_mode': True}

    @mockserver.json_handler('/yandex-drive/static/list')
    def _mock_yandex_drive(request):
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['Lon'] == '37.510000'
        assert request.headers['Lat'] == '55.720000'
        assert request.headers['UUID'] == 'UUID'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'DeviceId').hexdigest()
        )
        return mockserver.make_response(
            json={'options': {'user_app_car_list': load_json(drive_response)}},
            headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(
        URL, request, headers=consts.NOT_AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.experiments3(filename='experiments3_hide_drive_totw_action.json')
async def test_v2_objects_mode_drive_totw(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/yandex-drive/sessions/current')
    def _mock_yandex_drive(request):
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'400000000').hexdigest()
        )
        assert request.headers['Lon'] == '37.510000'
        assert request.headers['Lat'] == '55.720000'
        return mockserver.make_response(
            json=load_json('response_yandex_drive_sessions_current.json'),
            headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'totw'

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('drive_totw_expected_response.json')


MARKS_DRIVE_IMAGE_BY_SIZE_HINT = pytest.mark.config(
    YANDEX_DRIVE_CAR_SIDE_IMAGE_SETTINGS={
        'rules': [
            {
                'type': 'drive_car_side_image_from_meta_by_size_hint',
                'by_app_name': {
                    'iphone': [
                        {'size_hint': 500, 'image_size': '1_5x'},
                        # skipped rule: no such image
                        {'size_hint': 1337, 'image_size': '4x'},
                        # should choose this, 1500 is closer to 1337, than 500
                        {'size_hint': 1500, 'image_size': '2x'},
                    ],
                    # no rules for android, should fall back to large image
                    'android': [],
                },
            },
        ],
    },
)


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.parametrize(
    ['context', 'drive_response', 'expected_response'],
    [
        (
            {'base': 'fixpoint_offers_context_drive_summary_noreg.json'},
            None,  # drive_response
            'drive_fixpoint_offers_summary_noreg_expected_response.json',
        ),
        (
            {'size_hint': 1337},
            'response_yandex_drive_fixpoint.json',
            'drive_fixpoint_offers_expected_response.json',
        ),
        (
            {'size_hint': 1337},
            'response_yandex_drive_no_offers.json',
            'drive_no_objects_expected_response.json',
        ),
        (
            {'summary_tariff_class': 'drive', 'size_hint': 1337},
            'response_yandex_drive_fixpoint.json',
            'drive_fixpoint_offers_summary_expected_response.json',
        ),
        pytest.param(
            {'summary_tariff_class': 'drive', 'size_hint': 1337},
            'response_yandex_drive_fixpoint.json',
            'drive_fixpoint_offers_summary_expected_response_with_2x.json',
            marks=MARKS_DRIVE_IMAGE_BY_SIZE_HINT,
        ),
        pytest.param(
            {'size_hint': 1337},
            'response_yandex_drive_fixpoint.json',
            'drive_fixpoint_offers_expected_response_with_2x.json',
            marks=MARKS_DRIVE_IMAGE_BY_SIZE_HINT,
        ),
    ],
)
async def test_v2_objects_drive_fixpoint_offers(
        taxi_layers,
        mockserver,
        load_json,
        context,
        drive_response,
        expected_response,
):
    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['Lon'] == '37.510000'
        assert request.headers['Lat'] == '55.720000'
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['UUID'] == 'UUID'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert request.headers['X-YaTaxi-UserId'] == consts.USER_ID
        assert request.args == {
            'src': '37.1 55.2',
            'dst': '37.2 55.3',
            'destination_name': 'Дом',
            'lang': 'ru',
            'bbox': '-180 -90 180 90',
            'offer_count_limit': '3',
            'encode_deeplink': '1',
        }
        assert request.json == {'previous_offer_ids': ['offer_1', 'offer_2']}
        return mockserver.make_response(
            json=load_json(drive_response), headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['screen'] = 'summary'
    request['state']['mode'] = 'drive'
    request['context'] = (
        {
            'type': 'drive_fixpoint_offers',
            'src': [37.1, 55.2],
            'dst': [37.2, 55.3],
            'offer_count_limit': 3,
            'destination_name': 'Дом',
            'preferred_car_number': 'н587ху750',
            'previous_offer_ids': ['offer_1', 'offer_2'],
        }
        if 'base' not in context
        else load_json(context['base'])
    )
    if 'summary_tariff_class' in context:
        request['context']['summary_tariff_class'] = context[
            'summary_tariff_class'
        ]
    if 'size_hint' in context:
        request['context']['size_hint'] = context['size_hint']

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)

    if 'drive_response' in request['context']:
        assert _mock_yandex_drive.times_called == 0


@pytest.mark.parametrize(
    ['expected_cache_zooms', 'expected_cache_bbox', 'expected_features_zooms'],
    [
        pytest.param(
            [18, 20],
            [37.45, 55.5, 37.71, 56],
            [10, 7, 4, 4, 4],
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_layers_object_filtering_drive'
                    '_simple.json',
                ),
                pytest.mark.experiments3(
                    filename='experiments3_layers_providers_drive_filtering'
                    '.json',
                ),
            ],
        ),
        pytest.param(
            [1.337, 21],
            [37.45, 55.6, 37.7, 55.9],
            [4, 4, 4, 4, 4],
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_layers_object_filtering_drive'
                    '_with_all_visible_zoom.json',
                ),
                pytest.mark.experiments3(
                    filename='experiments3_layers_providers_drive_filtering'
                    '.json',
                ),
            ],
        ),
    ],
)
@pytest.mark.experiments3(
    filename='experiments3_display_settings_drive_filtering.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
async def test_v2_objects_drive_discovery_filtering(
        taxi_layers,
        mockserver,
        load_json,
        expected_cache_zooms,
        expected_cache_bbox,
        expected_features_zooms,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'discovery'

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return mockserver.make_response(
            json=load_json('response_yandex_drive_car_list_filtering.json'),
            headers={'X-Req-Id': '123'},
        )

    expected_response = load_json(
        'drive_discovery_expected_response_filtering.json',
    )
    expected_response['zooms'] = expected_cache_zooms
    expected_response['bbox'] = pytest.approx(expected_cache_bbox)

    assert len(expected_features_zooms) == len(expected_response['features'])
    for zoom, feature in zip(
            expected_features_zooms, expected_response['features'],
    ):
        feature['properties']['display_settings']['zooms'][0] = zoom

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='experiments3_scooters.json')
@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(
    filename='experiments3_display_settings_scooters.json',
)
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
@pytest.mark.parametrize('mode', ['drive', 'city'])
@pytest.mark.parametrize(
    ['drive_resp_code', 'scooters_resp_code'],
    (
        ['timeout', 'timeout'],
        [500, 500],
        [401, 401],
        [400, 400],
        ['timeout', 401],
        ['timeout', 400],
        [500, 401],
        [500, 400],
    ),
)
async def test_v2_objects_drive_and_scooters_errors(
        taxi_layers,
        mockserver,
        load_json,
        drive_resp_code,
        scooters_resp_code,
        mode,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = mode
    request['state']['screen'] = 'discovery'

    @mockserver.json_handler('/scooter-backend/car/list')
    def _mock_yandex_scooters(request):
        if scooters_resp_code == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(
            status=scooters_resp_code, headers={'X-Req-Id': '123'},
        )

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        if drive_resp_code == 'timeout':
            raise mockserver.TimeoutError()
        return mockserver.make_response(
            status=drive_resp_code, headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )

    drive_failed = drive_resp_code in (500, 'timeout')
    scooters_failed = scooters_resp_code in (500, 'timeout')
    layers_500 = False
    if mode != 'city' and drive_failed:
        layers_500 = True
    if mode == 'city' and drive_failed and scooters_failed:
        layers_500 = True
    if layers_500:
        assert response.status_code == 500
        msg = 'Provider {} features request failed'.format(
            'all' if mode == 'city' else 'drive',
        )
        assert response.json() == {
            'code': 'provider_request_failed',
            'message': msg,
        }
    else:
        assert response.status_code == 200
        assert response.json() == load_json(
            'drive_discovery_expected_response_empty.json',
        )


@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_cache_v2.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_drive_selected_car(
        taxi_layers, mockserver, load_json,
):
    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'choose_b'
    request['state']['drive'] = {'selected_car_number': 'н587ху750'}

    @mockserver.json_handler('/yandex-drive/car/list')
    def _mock_yandex_drive(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['Lon'] == '37.510000'
        assert request.headers['Lat'] == '55.720000'
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['UUID'] == 'UUID'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert request.headers['X-YaTaxi-UserId'] == consts.USER_ID
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'400000000').hexdigest()
        )
        assert request.args == {
            'car_number': 'н587ху750',
            'limit': '1000',
            'lang': 'ru',
        }
        return mockserver.make_response(
            json=load_json('response_yandex_drive_car_number.json'),
            headers={'X-Req-Id': '123'},
        )

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'drive_car_number_expected_response.json',
    )


@pytest.mark.experiments3(
    filename='experiments3_layers_cache_v2_config_kwargs.json',
)
@pytest.mark.experiments3(filename='experiments3_display_settings_drive.json')
@pytest.mark.experiments3(filename='experiments3_layers_providers.json')
async def test_v2_objects_config_kwargs(taxi_layers, mockserver, load_json):
    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return mockserver.make_response(
            json=load_json('response_yandex_drive_no_offers.json'),
            headers={'X-Req-Id': '123'},
        )

    request = copy.deepcopy(BASE_REQUEST)
    request['state']['mode'] = 'drive'
    request['state']['screen'] = 'main'
    request['context'] = {
        'type': 'drive_fixpoint_offers',
        'src': [37.1, 55.2],
        'dst': [37.2, 55.3],
        'offer_count_limit': 3,
        'destination_name': 'Дом',
        'preferred_car_number': 'н587ху750',
        'previous_offer_ids': ['offer_1', 'offer_2'],
    }

    response = await taxi_layers.post(
        URL, request, headers=consts.AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response_layers_cache_v2_config_kwargs.json',
    )

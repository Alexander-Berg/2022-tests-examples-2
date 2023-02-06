import pytest

URL = 'umlaas-geo/v1/finalsuggest'
USER_ID = 'user_id'

PA_HEADERS = {
    'X-YaTaxi-UserId': USER_ID,
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_brand=yango,app_name=yango_android',
}

PA_HEADERS_NO_AUTH = {
    'X-YaTaxi-UserId': USER_ID,
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
}


@pytest.mark.experiments3(filename='exp_auto_position_without_ml.json')
@pytest.mark.experiments3(filename='exp_nearest_position_params.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
async def test_w_stick(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_w_stick.json')


@pytest.mark.experiments3(filename='exp_auto_position_without_ml.json')
@pytest.mark.experiments3(filename='exp_nearest_position_params_small.json')
@pytest.mark.experiments3(
    filename='exp_pickup_points_recommeder_params_small.json',
)
async def test_wo_stick(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_wo_stick.json')


@pytest.mark.experiments3(filename='exp_auto_position_without_ml.json')
@pytest.mark.experiments3(
    filename='exp_nearest_position_params_userplaces.json',
)
async def test_userplace_stick(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    request['actions'] = ['stick']
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_userplace_stick.json',
    )


@pytest.mark.experiments3(
    filename='exp_pickup_points_recommeder_params_exp_resource.json',
)
async def test_exp_resource(taxi_umlaas_geo, load_json, mockserver):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        return {'results': []}

    @mockserver.json_handler('/pickup-points-manager/v1/points/')
    def _mock_pickup_points_manager(request):
        assert 'X-Request-Language' in request.headers
        return {'points': [], 'num_points': 0}

    request = load_json('request.json')
    request['actions'] = ['points']
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_exp_resource.json')


@pytest.mark.experiments3(filename='exp_auto_position_without_ml.json')
@pytest.mark.experiments3(filename='exp_nearest_position_params.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
async def test_unauthorized(
        taxi_umlaas_geo,
        load_json,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
):

    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(
        URL, request, headers=PA_HEADERS_NO_AUTH,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_unauthorized.json')


@pytest.mark.experiments3(filename='exp_auto_position_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
async def test_ml_auto_position(
        taxi_umlaas_geo,
        load_json,
        mockserver,
        _mock_userplaces,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        for header, value in PA_HEADERS.items():
            if header == 'X-Request-Application':
                # Compare ignoring key-value pair order
                assert set(request.headers[header].split(',')) == set(
                    value.split(','),
                )
            elif header != 'X-Ya-User-Ticket':
                assert request.headers[header] == value
        return load_json('routehistory_get_response.json')

    request = load_json('request.json')
    request['actions'] = ['stick']
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_auto_position.json')


@pytest.mark.experiments3(filename='exp_auto_position_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
async def test_ml_auto_position_routehistory(
        taxi_umlaas_geo,
        load_json,
        mockserver,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        for header, value in PA_HEADERS.items():
            if header == 'X-Request-Application':
                # Compare ignoring key-value pair order
                assert set(request.headers[header].split(',')) == set(
                    value.split(','),
                )
            elif header != 'X-Ya-User-Ticket':
                assert request.headers[header] == value
        return load_json('routehistory_get_response_extra.json')

    @mockserver.json_handler('/userplaces/userplaces/list')
    def _get_response(request):
        return {}

    request = load_json('request.json')
    request['actions'] = ['stick']
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_auto_position_extra.json',
    )


@pytest.mark.experiments3(
    filename='exp_auto_position_recommeder_params_explore.json',
)
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
async def test_ml_auto_position_explore(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert 'stick_result' in response.json()


@pytest.mark.config(UMLAAS_GEO_ROUTEHISTORY_GROCERY_ENABLED=False)
@pytest.mark.experiments3(filename='exp_auto_position_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_foodtech_auto_position_params.json')
async def test_ml_auto_position_foodtech_mode(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
        _mock_eats_ordershistory,
):
    request = load_json('request.json')
    request['state']['current_mode'] = 'grocery'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert _mock_eats_ordershistory.has_calls
    assert 'stick_result' in response.json()
    stick_result = response.json()['stick_result']
    assert stick_result['method'] == 'eats_ordershistory.delivery_location'


@pytest.mark.experiments3(filename='exp_auto_position_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(
    filename='exp_foodtech_auto_position_grocery_get_params.json',
)
async def test_ml_auto_position_foodtech_mode_grocery(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_routehistory_grocery,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
        _mock_eats_ordershistory,
):
    request = load_json('request.json')
    request['state']['current_mode'] = 'grocery'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert _mock_eats_ordershistory.has_calls
    assert _mock_routehistory_grocery.has_calls
    assert 'stick_result' in response.json()
    stick_result = response.json()['stick_result']
    assert stick_result['method'] == 'routehistory_grocery.position'


@pytest.mark.experiments3(filename='exp_zero_lat.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_auto_position_recommeder_params.json')
async def test_zero_lat(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    request['position'][1] = 0
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == load_json(
        'expected_response_w_stick_zero_lat.json',
    )


@pytest.mark.experiments3(filename='exp_base_coordinate_hit.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_auto_dual_to_base.json')
async def test_base_coordinate_hit(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    expected_response = load_json(
        'expected_response_corrected_bad_location.json',
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='exp_base_coordinate_miss.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_auto_dual_to_base.json')
async def test_base_coordinate_miss(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    expected_response = load_json('expected_response_w_stick.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='exp_base_coordinate_position_stick.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_auto_dual_to_base.json')
async def test_base_coordinate_position_stick(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    expected_response = load_json(
        'expected_response_corrected_bad_location.json',
    )
    expected_response['stick_result'], expected_response['alternatives'][0] = (
        expected_response['alternatives'][0],
        expected_response['stick_result'],
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='exp_base_coordinate_heuristic_only.json')
@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_auto_dual_to_base.json')
@pytest.mark.now('2020-09-09T18:18:19.000000Z')
async def test_base_coordinate_heuristic_only(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    request = load_json('request.json')
    request['position'] = [37.345403, 55.662874]  # Mesherskiy park
    request['state']['accuracy'] = 12000
    PA_HEADERS['X-Request-Application'] = 'app_brand=aboba,app_name=iphone'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    expected_response = load_json(
        'expected_response_triangle_heuristic_only.json',
    )
    assert response.status_code == 200
    assert response.json() == expected_response

    PA_HEADERS['X-Request-Application'] = 'app_brand=yandex,app_name=iphone'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.experiments3(filename='exp_pickup_points_recommeder_params.json')
@pytest.mark.experiments3(filename='exp_auto_position_recommeder_params.json')
async def test_do_stick(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_yaga_adjust,
        _mock_searchhistory,
):
    # old clients without `geo_tap` field
    request = load_json('request.json')
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    expected_response = load_json('expected_response_geo_tap_w_stick.json')
    assert response.status_code == 200
    assert response.json() == expected_response

    # modern clients, request at launch
    request['geo_tap'] = False
    PA_HEADERS['X-Request-Application'] = 'app_brand=yandex,app_name=iphone'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    expected_response = load_json('expected_response_geo_tap_w_stick.json')
    assert response.status_code == 200
    assert response.json() == expected_response

    # modern clients, request at tap on geolocation button
    request['geo_tap'] = True
    PA_HEADERS['X-Request-Application'] = 'app_brand=yandex,app_name=iphone'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    expected_response = load_json('expected_response_geo_tap_wo_stick.json')
    assert response.status_code == 200
    assert 'points' in response.json()
    assert 'stick_result' in response.json()
    assert response.json() == expected_response


@pytest.mark.experiments3(
    filename='exp_auto_position_only_position_resource.json',
)
@pytest.mark.experiments3(filename='exp_push_out_of_building_params.json')
@pytest.mark.config(UMLAAS_GEO_BUILDINGS_RADIUS=100000)
async def test_framing_building_search(
        taxi_umlaas_geo,
        load_json,
        _mock_yaga_adjust,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_searchhistory,
        testpoint,
):
    @testpoint('finalsuggest_framing_building')
    def success_message_testpoint(success_message):
        pass

    await taxi_umlaas_geo.enable_testpoints()
    successful_request = load_json('request.json')
    response = await taxi_umlaas_geo.post(
        URL, successful_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert success_message_testpoint.times_called == 1
    assert response.json()['stick_result']['push_out_of_building_method'] in [
        'building_entrance',
        'building_edge',
        'building_pickup_point',
    ]

    await taxi_umlaas_geo.enable_testpoints()
    unsuccessful_request = load_json('request.json')
    unsuccessful_request['position'] = [38.642736, 56.734385]
    response = await taxi_umlaas_geo.post(
        URL, unsuccessful_request, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert success_message_testpoint.times_called == 1


@pytest.mark.experiments3(
    filename='exp_auto_position_only_position_resource.json',
)
@pytest.mark.experiments3(filename='exp_push_out_of_building_params.json')
@pytest.mark.config(UMLAAS_GEO_BUILDINGS_RADIUS=100000)
async def test_framing_building_exploration_edges_and_pp(
        taxi_umlaas_geo,
        load_json,
        _mock_yaga_adjust,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_searchhistory,
):
    request = load_json('request.json')
    request['position'] = [37.0, 55.0]
    pushed_to_pickup_point = 'no result'
    pushed_to_edge = 'no result'
    counter = 0
    while (
            pushed_to_pickup_point == 'no result'
            or pushed_to_edge == 'no result'
    ):
        counter += 1
        response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
        assert response.status_code == 200
        if (
                response.json()['stick_result']['push_out_of_building_method']
                == 'building_edge'
        ):
            pushed_to_edge = response.json()['stick_result']
        if (
                response.json()['stick_result']['push_out_of_building_method']
                == 'building_pickup_point'
        ):
            pushed_to_pickup_point = response.json()['stick_result']
        assert counter < 100
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_yaga_adjust.has_calls
    assert _mock_pickup_points_manager.has_calls
    assert _mock_searchhistory.has_calls
    assert pushed_to_pickup_point['position'] == [37.00001, 55.00001]
    assert pushed_to_edge['position'] in [
        [37.0, 55.5],
        [37.5, 56.0],
        [38.0, 55.5],
        [37.5, 55.0],
    ]


@pytest.mark.experiments3(
    filename='exp_auto_position_only_position_resource.json',
)
@pytest.mark.experiments3(filename='exp_push_out_of_building_params.json')
@pytest.mark.config(UMLAAS_GEO_BUILDINGS_RADIUS=100000)
async def test_framing_building_exploration_entrances(
        taxi_umlaas_geo,
        load_json,
        _mock_yaga_adjust,
        _mock_userplaces,
        _mock_routehistory,
        _mock_pickup_points_manager,
        _mock_searchhistory,
):
    request = load_json('request.json')
    request['position'] = [37.5, 53.5]
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    counter = 0
    entrances = {
        frozenset([37.3, 53.0]): False,
        frozenset([37.6, 53.0]): False,
    }
    while False in entrances.values():
        counter += 1
        response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
        assert response.status_code == 200
        if (
                response.json()['stick_result']['push_out_of_building_method']
                == 'building_entrance'
        ):
            pushed_to_entrance = frozenset(
                response.json()['stick_result']['position'],
            )
            entrances[pushed_to_entrance] = True
        assert counter < 100

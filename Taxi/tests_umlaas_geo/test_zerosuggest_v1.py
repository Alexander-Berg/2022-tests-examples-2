import pytest


URL = 'umlaas-geo/v1/zerosuggest'
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


@pytest.mark.experiments3(filename='exp_fallback_to_popular_locations.json')
@pytest.mark.config(UMLAAS_GEO_ZEROSUGGEST_FALLBACK_ENABLED=True)
async def test_fallback_to_popular_locations(
        taxi_umlaas_geo, mockserver, load_json,
):
    @mockserver.json_handler('/userplaces/userplaces/list')
    def _mock_userplaces(request):
        return []

    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        return []

    @mockserver.json_handler('/pickup-points-manager/v1/points/')
    def _mock_pickup_points_manager(request):
        return []

    @mockserver.json_handler('/routehistory/routehistory/search-get')
    def _mock_searchhistory(request):
        return []

    request = load_json('request.json')
    request['type'] = 'b'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert _mock_pickup_points_manager.has_calls
    assert response.json()['results']


@pytest.mark.experiments3(filename='exp_recommender_params_source.json')
@pytest.mark.experiments3(filename='exp_personal_geosuggest.json')
@pytest.mark.config(UMLAAS_GEO_ZEROSUGGESTGEO_ENABLED=True)
async def test_source(
        taxi_umlaas_geo,
        mockserver,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_pickup_points_manager,
):
    @mockserver.json_handler('/yamaps-suggest-geo/zero-suggest')
    def _mock_yamaps_zerosuggest(request):
        request_args = dict(request.args)
        assert 'client_reqid' in request_args
        assert request_args['client_reqid']
        request_args.pop('client_reqid')
        assert request_args == load_json('zerosuggest_geo_request.json')
        user_ticket = PA_HEADERS['X-Ya-User-Ticket']
        assert request.headers['X-Ya-User-Ticket'] == user_ticket
        return load_json('yamaps_suggest_geo_zerosuggest_response.json')

    request = load_json('request.json')
    request['type'] = 'a'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_yamaps_zerosuggest.has_calls
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert _mock_pickup_points_manager.has_calls
    assert response.json() == load_json('expected_response_source.json')


@pytest.mark.experiments3(filename='exp_recommender_params_destination.json')
@pytest.mark.experiments3(filename='cfg3_umlaas_geo_zerosuggest_max_size.json')
async def test_request_source_config(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_searchhistory,
        _mock_pickup_points_manager,
        mockserver,
):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        return load_json('routehistory_get_response_several.json')

    request = load_json('request.json')
    request['type'] = 'b'
    request['source'] = 'shortcuts'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert _mock_pickup_points_manager.has_calls
    assert not response.json()['results']


@pytest.mark.experiments3(filename='exp_recommender_params_shortcuts.json')
async def test_request_source(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_pickup_points_manager,
):

    request = load_json('request.json')
    request['source'] = 'shortcuts'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert len(response.json()['results']) == 1


@pytest.mark.experiments3(filename='exp_foodtech_params.json')
async def test_foodtech_mode(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_eats_ordershistory,
):

    request = load_json('request.json')
    request['type'] = 'a'
    request['state']['current_mode'] = 'grocery'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_eats_ordershistory.has_calls
    assert len(response.json()['results']) == 1


@pytest.mark.experiments3(filename='exp_shuttle_params.json')
@pytest.mark.config(
    UMLAAS_GEO_SHUTTLE_ORDERHISTORY_ENABLED=True,
    UMLAAS_GEO_SHUTTLE_ORDERHISTORY_SETTINGS={
        'max_size': 10,
        'endpoints': {'__default__': {'enabled': True, 'max_size': 10}},
    },
    UMLAAS_GEO_ROUTEHISTORY_ENABLED=False,
    UMLAAS_GEO_USERPLACES_ENABLED=False,
    UMLAAS_GEO_ROUTEHISTORY_SEARCH_ENABLED=False,
)
async def test_shuttle_mode(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_shuttlehistory,
):

    request = load_json('request.json')
    request['type'] = 'a'
    request['state']['current_mode'] = 'shuttle'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert not _mock_userplaces.has_calls
    assert not _mock_routehistory.has_calls
    assert not _mock_searchhistory.has_calls
    assert _mock_shuttlehistory.has_calls
    assert len(response.json()['results']) == 1
    assert response.json() == {
        'results': [
            {
                'method': 'phone_history.source',
                'position': [37.618822, 55.751626],
                'tags': [],
                'taxi_order_id': 'order_id_1',
                'text': 'Full text 1',
                'uri': 'URI_1',
            },
        ],
    }


@pytest.mark.experiments3(filename='exp_other_modes_params.json')
async def test_other_modes(
        taxi_umlaas_geo,
        mockserver,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_eats_ordershistory,
):

    request = load_json('request.json')
    request['type'] = 'a'
    request['state']['current_mode'] = 'delivery'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert not _mock_eats_ordershistory.has_calls
    assert len(response.json()['results']) == 1


@pytest.mark.experiments3(filename='exp_manual_points_params.json')
async def test_manual_points(
        taxi_umlaas_geo,
        mockserver,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
):
    @mockserver.json_handler('/pickup-points-manager/v1/points/')
    def _mock_pp_manager(request):
        return load_json('pickup_points_manager_poi_response.json')

    request = load_json('request.json')
    request['type'] = 'b'
    request['position'] = [10.766080160346776, 59.92668656710592]
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_pp_manager.has_calls
    assert len(response.json()['results']) == 8
    assert response.json()['results'][5]['method'] == 'manual_poi'
    assert response.json()['results'][5]['uri'] == 'ytpp://id=1'
    assert response.json()['results'][6]['method'] == 'manual_poi'
    assert response.json()['results'][6]['uri'] == 'ytpp://id=3'
    assert response.json()['results'][7]['method'] == 'manual_poi'
    assert response.json()['results'][7]['uri'] == 'ytpp://id=2'


@pytest.mark.experiments3(
    filename='exp_manual_points_params_skip_blender.json',
)
async def test_manual_points_skip_blender(
        taxi_umlaas_geo,
        mockserver,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
):
    @mockserver.json_handler('/pickup-points-manager/v1/points/')
    def _mock_pp_manager(request):
        return load_json('pickup_points_manager_poi_response.json')

    request = load_json('request.json')
    request['type'] = 'b'
    request['position'] = [10.766080160346776, 59.92668656710592]
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_pp_manager.has_calls
    assert len(response.json()['results']) == 8
    assert response.json()['results'][5]['method'] == 'manual_poi'
    assert response.json()['results'][5]['uri'] == 'ytpp://id=1'
    assert response.json()['results'][6]['method'] == 'manual_poi'
    assert response.json()['results'][6]['uri'] == 'ytpp://id=3'
    assert response.json()['results'][7]['method'] == 'manual_poi'
    assert response.json()['results'][7]['uri'] == 'ytpp://id=2'


@pytest.mark.experiments3(filename='exp_fallback_to_popular_locations.json')
async def test_separate_resources(
        taxi_umlaas_geo,
        mockserver,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
):
    @mockserver.json_handler('/pickup-points-manager/v1/points/')
    def _mock_pp_manager(request):
        return load_json('pickup_points_manager_poi_response.json')

    request = load_json('request.json')
    request['type'] = 'b'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert _mock_pp_manager.has_calls
    assert len(response.json()['results']) == 6


@pytest.mark.experiments3(filename='exp_ml_yt_logger_all_kwargs.json')
async def test_ml_yt_logger_kwargs(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        testpoint,
):
    @testpoint('zerosuggest_log_ml_request_v1')
    def success_message_testpoint(success_message):
        pass

    await taxi_umlaas_geo.enable_testpoints()
    successful_request = load_json('request.json')
    successful_request['state']['current_mode'] = 'robot_call_center'
    response = await taxi_umlaas_geo.post(
        URL, successful_request, headers=PA_HEADERS,
    )
    assert success_message_testpoint.times_called == 1
    assert response.status_code == 200

    await taxi_umlaas_geo.enable_testpoints()
    unsuccessful_request = load_json('request.json')
    unsuccessful_request['state']['current_mode'] = 'not_robot_call_center'
    response = await taxi_umlaas_geo.post(
        URL, unsuccessful_request, headers=PA_HEADERS,
    )
    assert success_message_testpoint.times_called == 1
    assert response.status_code == 200


@pytest.mark.now('2020-09-10T17:18:19.000000Z')
@pytest.mark.experiments3(filename='exp_suggest_userplaces.json')
async def test_suggest_userplaces(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_pickup_points_manager,
):
    request = load_json('request.json')
    request['type'] = 'b'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert (
        response.json()['results'][0]['method']
        == 'phone_history.completion_point'
    )
    assert response.json()['results'][0]['additional_point_info']
    additional_info = response.json()['results'][0]['additional_point_info']
    assert additional_info['userplace_suggestion']
    userplace_suggestion = additional_info['userplace_suggestion']
    assert userplace_suggestion['available_types']
    assert userplace_suggestion['count'] == 1
    assert userplace_suggestion['datetime'] == '2020-09-09T17:18:19+00:00'


@pytest.mark.now('2020-09-10T17:18:19.000000Z')
@pytest.mark.experiments3(filename='exp_reveal_relevance.json')
async def test_reveal_relevance(
        taxi_umlaas_geo,
        load_json,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_pickup_points_manager,
):
    request = load_json('request.json')
    request['type'] = 'b'
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls
    assert (
        response.json()['results'][0]['additional_point_info']['relevance']
        == 0.5
    )


@pytest.mark.parametrize(
    ['tag'],
    [
        pytest.param(
            'keklol',
            marks=(
                pytest.mark.experiments3(
                    filename='exp_recommender_params_no_tag_rules.json',
                )
            ),
        ),
        pytest.param(
            'uber_high_relevance',
            marks=(
                pytest.mark.experiments3(
                    filename='exp_recommender_params_destination.json',
                )
            ),
        ),
    ],
)
async def test_tag_rules(
        taxi_umlaas_geo,
        load_json,
        tag,
        _mock_userplaces,
        _mock_routehistory,
        _mock_searchhistory,
        _mock_pickup_points_manager,
):
    request = load_json('request.json')
    request['type'] = 'b'
    request['tag_rules'] = [
        {
            'methods': [
                'userplace',
                'phone_history.destination',
                'phone_history.intermediate',
                'phone_history.source',
                'search_routes.destination',
                'search_routes.intermediate',
                'search_routes.source',
            ],
            'min_relevance': 0.1,
            'name': 'keklol',
        },
    ]
    response = await taxi_umlaas_geo.post(URL, request, headers=PA_HEADERS)
    assert response.json()['results'][0]['tags'][0] == tag
    assert response.status_code == 200
    assert _mock_userplaces.has_calls
    assert _mock_routehistory.has_calls
    assert _mock_searchhistory.has_calls

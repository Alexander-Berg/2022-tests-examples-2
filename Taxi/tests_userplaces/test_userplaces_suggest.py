import pytest

USER_ID = '12345678901234567890123456789012'
DEFAULT_PHONE_ID = '02aaaaaaaaaaaaaaaaaaaa01'
DEFAULT_UID = '400000000'

YAMAPS_ADDRESS = {
    'geocoder': {
        'address': {
            'formatted_address': 'Russia, Moscow, Petrovskiy alley, 21',
            'country': 'Russia',
            'locality': 'Moscow',
        },
        'id': '1',
    },
    'uri': 'ymapsbm1://URI_1_1',
    'name': 'Petrovskiy alley, 21',
    'description': 'Russia, Moscow',
    'geometry': [37.586634, 55.736716],
}

PLACE = [
    {
        'info': {
            'timeinfo': {
                'full_text': 'Вы были здесь уже 3 раз',
                'short_text': '3 раз за 2 недели',
            },
            'available_types': ['home', 'other'],
        },
        'point': {
            'coordinates': [37.586634, 55.736716],
            'subtitle': 'Petrovskiy alley, 21',
            'title': 'Russia, Moscow, Petrovskiy alley, 21',
            'uri': 'ymapsbm1://URI_1_1',
        },
    },
]

SUGGEST_PARAMS = {
    'match': {'predicate': {'type': 'true'}, 'enabled': True},
    'name': 'userplaces_suggest_params',
    'consumers': ['userplaces/userplaces'],
    'clauses': [],
    'is_config': True,
}


@pytest.mark.translations(
    client_messages={
        'userplaces.suggest.short_text_rides_count': {
            'ru': '%(rides_count)s раз',
        },
        'userplaces.suggest.short_text_weeks_count': {
            'ru': ' за %(weeks_count)s недели',
        },
        'userplaces.suggest.full_text': {
            'ru': 'Вы были здесь уже %(rides_count)s раз',
        },
    },
)
@pytest.mark.parametrize(
    'status_code,max_results,response_place',
    [
        pytest.param(
            200,
            80,
            PLACE,
            marks=pytest.mark.experiments3(
                **SUGGEST_PARAMS,
                default_value={
                    'routehistory_max_size': 80,
                    'min_dist_from_userplace': 200,
                    'min_dist_from_completion_point': 2000,
                    'min_near_points_size': 3,
                    'max_weeks_count_from_ride': 12,
                },
            ),
        ),
        pytest.param(
            500,
            30,
            [],
            marks=pytest.mark.experiments3(
                **SUGGEST_PARAMS,
                default_value={
                    'routehistory_max_size': 30,
                    'min_dist_from_userplace': 200,
                    'min_dist_from_completion_point': 2000,
                    'min_near_points_size': 3,
                    'max_weeks_count_from_ride': 12,
                },
            ),
        ),
        pytest.param(
            200,
            80,
            [],
            marks=pytest.mark.experiments3(
                **SUGGEST_PARAMS,
                default_value={
                    'routehistory_max_size': 80,
                    'min_dist_from_userplace': 20000,
                    'min_dist_from_completion_point': 2000,
                    'min_near_points_size': 3,
                    'max_weeks_count_from_ride': 12,
                },
            ),
        ),
        pytest.param(
            200,
            80,
            [],
            marks=pytest.mark.experiments3(
                **SUGGEST_PARAMS,
                default_value={
                    'routehistory_max_size': 80,
                    'min_dist_from_userplace': 200,
                    'min_dist_from_completion_point': 2000,
                    'min_near_points_size': 4,
                    'max_weeks_count_from_ride': 12,
                },
            ),
        ),
        pytest.param(
            200,
            80,
            [],
            marks=pytest.mark.experiments3(
                **SUGGEST_PARAMS,
                default_value={
                    'routehistory_max_size': 80,
                    'min_dist_from_userplace': 200,
                    'min_dist_from_completion_point': 200,
                    'min_near_points_size': 3,
                    'max_weeks_count_from_ride': 12,
                },
            ),
        ),
        pytest.param(
            200,
            80,
            [],
            marks=pytest.mark.experiments3(
                **SUGGEST_PARAMS,
                default_value={
                    'routehistory_max_size': 80,
                    'min_dist_from_userplace': 200,
                    'min_dist_from_completion_point': 200,
                    'min_near_points_size': 3,
                    'max_weeks_count_from_ride': 1,
                },
            ),
        ),
    ],
    ids=[
        'simple_suggest_userplace',
        'routehistory_error',
        'close_to_userplace',
        'min_points_count',
        'min_distance_to_completion_point',
        'max_weeks_count',
    ],
)
@pytest.mark.now('2022-05-12T17:38:12.955+0000')
async def test_suggest_userplace(
        taxi_userplaces,
        load_json,
        mockserver,
        status_code,
        max_results,
        yamaps,
        response_place,
):
    @mockserver.json_handler('/routehistory/routehistory/get')
    def _mock_routehistory(request):
        assert request.json['max_results'] == max_results
        if status_code == 500:
            return mockserver.make_response(status=500)
        return load_json('routehistory_response.json')

    yamaps.add_fmt_geo_object(YAMAPS_ADDRESS)

    response = await taxi_userplaces.post(
        '4.0/userplaces/suggested-points',
        headers={
            'X-YaTaxi-UserId': USER_ID,
            'X-YaTaxi-PhoneId': DEFAULT_PHONE_ID,
            'Accept-Language': 'ru',
            'X-Yandex-UID': DEFAULT_UID,
            'X-Request-Application': 'app_name=yango_android',
        },
        json={'coordinates': [37.586634, 55.736716]},
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()['places'] == response_place

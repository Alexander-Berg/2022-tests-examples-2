import copy

from aiohttp import web
import pytest

from supportai_actions.action_types import get_objects_nearby
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as params_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    (
        'organization_name',
        'num_objects',
        'response_language_param',
        'language_core_feature',
        'get_position_from',
        'geo_object_type',
    ),
    [
        ('Широкую на широкую', 1, None, None, 'coordinates_feature', 'org'),
        ('Широкую на широкую', 1, 'ru', None, 'lon_lat_features', 'org'),
        ('Широкую на широкую', 1, 'ru', 'en', 'lon_lat_features', 'org'),
        ('Широкую на широкую', None, 'en', 'ru', 'user_message', 'org'),
        (None, None, None, 'en', 'user_message', 'geo'),
    ],
)
async def test_get_objects_nearby(
        web_context,
        mockserver,
        organization_name,
        num_objects,
        response_language_param,
        language_core_feature,
        get_position_from,
        geo_object_type,
):
    expected_language = (
        response_language_param
        if response_language_param
        else language_core_feature
        if language_core_feature
        else 'ru'
    )
    longitude = 1.000
    latitude = 2.01201
    user_message = 'some user message'
    state = state_module.State(
        feature_module.Features(
            [
                {'key': 'longitude', 'value': longitude},
                {'key': 'latitude', 'value': latitude},
            ]
            if get_position_from == 'lon_lat_features'
            else [{'key': 'coordinates', 'value': [longitude, latitude]}]
            if get_position_from == 'coordinates_feature'
            else [{'key': 'last_user_message', 'value': user_message}],
        ),
    )
    if language_core_feature:
        state.features['language'] = language_core_feature

    num_response_objects = num_objects or 2

    res_coordinates = [37.636122, 55.761575]

    action_params = {
        'category': 'бар',
        'get_position_from': (
            {'latitude_feature': 'latitude', 'longitude_feature': 'longitude'}
            if get_position_from == 'lon_lat_features'
            else {'coordinates_feature': 'coordinates'}
            if get_position_from == 'coordinates_feature'
            else {'user_message_feature': 'last_user_message'}
        ),
    }
    if organization_name is not None:
        action_params['organization_name'] = organization_name
    if num_objects is not None:
        action_params['num_objects'] = num_objects
    if response_language_param is not None:
        action_params['response_language'] = response_language_param

    action = get_objects_nearby.GetObjectsNearby(
        'text',
        'get_objects_nearby',
        '1',
        [params_module.ActionParam(action_params)],
    )

    yamaps_addresses = [
        {
            'Components': [
                {'kind': 'locality', 'name': 'Москва'},
                {'kind': 'street', 'name': 'Кривоколенный переулок'},
                {'kind': 'house', 'name': f'10, стр. {str(idx)}'},
            ],
            'country_code': '',
            'formatted': '',
            'postal_code': '',
        }
        for idx in range(num_response_objects)
    ]

    yamaps_response_json = {
        'features': [
            {
                'geometry': {'coordinates': res_coordinates, 'type': 'Point'},
                'properties': (
                    {
                        'CompanyMetaData': (
                            {
                                'Address': yamaps_address,
                                'Categories': [
                                    {'class': 'some', 'name': 'бар, паб'},
                                ],
                                'name': 'Широкую на широкую',
                            }
                        ),
                    }
                    if geo_object_type == 'org'
                    else {'GeocoderMetaData': {'Address': yamaps_address}}
                ),
            }
            for yamaps_address in yamaps_addresses
        ],
    }

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(request):
        assert request.query.get('lang') == expected_language
        if request.query.get('ll') is None:
            assert request.query['text'] == user_message
            assert request.query['results'] == '1'
            user_position_response = copy.deepcopy(yamaps_response_json)
            user_position_response['features'][0]['geometry'][
                'coordinates'
            ] = [longitude, latitude]
            return web.json_response(data=user_position_response)

        expected_text_query = (
            f'бар {organization_name}'
            if organization_name is not None
            else 'rubric:(бар)'
        )
        assert request.query['text'] == expected_text_query
        assert (
            request.query['results'] == str(num_objects * 2)
            if num_objects is not None
            else '10'
        )
        assert request.query['ll'] == f'{longitude},{latitude}'
        return web.json_response(data=yamaps_response_json)

    new_state = await action(web_context, state)

    expected_addresses = [
        f'Москва, Кривоколенный переулок, 10, стр. {str(idx)}'
        for idx in range(num_response_objects)
    ]
    user_point_address = 'Москва, Кривоколенный переулок, 10, стр. 0'
    user_point_title = 'бар, паб Широкую на широкую'
    expected_titles = [user_point_title] * num_response_objects

    assert new_state.features.get('configuration_error') is None

    if get_position_from == 'user_message':
        assert new_state.features['user_point_coordinates'] == [
            longitude,
            latitude,
        ]
        assert new_state.features['user_point_address'] == user_point_address
        if organization_name:
            assert new_state.features['user_point_title'] == user_point_title

    assert new_state.features[f'objects_addresses'] == expected_addresses
    assert (
        new_state.features[f'objects_coordinates']
        == res_coordinates * num_response_objects
    )
    if organization_name:
        assert new_state.features[f'objects_titles'] == expected_titles


async def test_keep_unique_and_sort_by_distance(web_context, mockserver):
    state = state_module.State(
        feature_module.Features(
            [
                {'key': 'longitude', 'value': 0.0},
                {'key': 'latitude', 'value': 0.0},
            ],
        ),
    )

    action_params = {
        'category': 'something',
        'num_objects': 3,
        'get_position_from': {
            'latitude_feature': 'latitude',
            'longitude_feature': 'longitude',
        },
    }

    action = get_objects_nearby.GetObjectsNearby(
        'text',
        'get_objects_nearby',
        '1',
        [params_module.ActionParam(action_params)],
    )

    latitudes = [4.0] * 4 + [3.0] * 3 + [2.0] * 2 + [1.0] * 1

    houses = [1] * 4 + [2] * 3 + [3] * 2 + [4] * 1
    yamaps_addresses = [
        {
            'Components': [
                {'kind': 'locality', 'name': 'Москва'},
                {'kind': 'house', 'name': str(house)},
            ],
            'country_code': '',
            'formatted': '',
            'postal_code': '',
        }
        for house in houses
    ]

    yamaps_response_json = {
        'features': [
            {
                'geometry': {'coordinates': [latitude, 0.0], 'type': 'Point'},
                'properties': (
                    {'GeocoderMetaData': {'Address': yamaps_address}}
                ),
            }
            for latitude, yamaps_address in zip(latitudes, yamaps_addresses)
        ],
    }

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(request):
        assert request.query['results'] == '6'
        return web.json_response(data=yamaps_response_json)

    new_state = await action(web_context, state)

    expected_addresses = ['Москва, 4', 'Москва, 3', 'Москва, 2']
    assert new_state.features['objects_addresses'] == expected_addresses


@pytest.mark.parametrize('no_category', [True, False])
@pytest.mark.parametrize(
    (
        'no_get_position_from',
        'extra_in_get_position_from',
        'both_position_options',
        'no_properties_in_get_position',
    ),
    [
        (True, False, False, False),
        (False, True, False, False),
        (False, False, True, False),
        (False, False, False, True),
    ],
)
@pytest.mark.parametrize('extra_in_params', [True, False])
async def test_wrong_action_params_schema(
        web_context,
        mockserver,
        no_category,
        no_get_position_from,
        extra_in_get_position_from,
        both_position_options,
        no_properties_in_get_position,
        extra_in_params,
):
    state = state_module.State(features=feature_module.Features([]))

    valid_params = {
        'category': 'some',
        'get_position_from': {
            'latitude_feature': 'some',
            'longitude_feature': 'some',
        },
    }

    if no_category:
        valid_params.pop('category')
    if no_get_position_from:
        valid_params.pop('get_position_from')
    if extra_in_get_position_from:
        valid_params['get_position_from']['extra_param'] = 'some'
    if both_position_options:
        valid_params['get_position_from']['coordinates_feature'] = 'some'
    if no_properties_in_get_position:
        valid_params['get_position_from'].clear()
    if extra_in_params:
        valid_params['extra_param'] = 'some'

    action = get_objects_nearby.GetObjectsNearby(
        'text',
        'get_objects_nearby',
        '1',
        [params_module.ActionParam(valid_params)],
    )

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        assert False

    new_state = await action(web_context, state)
    assert new_state.features.get('configuration_error') is not None

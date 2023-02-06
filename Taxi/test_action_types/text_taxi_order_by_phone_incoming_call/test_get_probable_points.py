# flake8: noqa: I100
# pylint: disable=broad-except
import copy

import pytest
from aiohttp import web

from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.taxi_order_by_phone_incoming_call import (
    get_probable_points,
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
            '+799976543321': {
                'geo_zone_coords': {'lat': 55.744319908, 'lon': 37.6175675721},
                'application': 'call_center',
            },
        },
        TVM_RULES=[{'src': 'supportai-actions', 'dst': 'personal'}],
    ),
]


@pytest.mark.config(
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'zerosuggest_current_mode': 'some_current_mode',
        'zerosuggest_use_location_parameter': True,
    },
)
@pytest.mark.parametrize(
    ('has_points', 'address_is_parsed'),
    [(True, False), (True, True), (False, None)],
)
@pytest.mark.parametrize(
    ('is_organization', 'is_metro', 'is_airport', 'entrance'),
    [
        (True, False, False, None),
        (True, True, False, None),
        (True, False, True, None),
        (False, False, False, None),
        (False, False, False, '1'),
    ],
)
@pytest.mark.parametrize('city', ['Москва', None])
async def test_get_probable_points(
        web_context,
        mockserver,
        has_points,
        mock_user_api,
        address_is_parsed,
        is_organization,
        is_metro,
        is_airport,
        entrance,
        city,
):
    sentinel = 'SENTINEL'

    street = 'Улица Охотный ряд'
    house = '2'
    unparsed_address = 'Совсем другой результат!'
    organization_name = (
        'Кафе Дырка от бублика'
        if not is_metro and not is_airport
        else 'станция метро Кучеряево'
        if is_metro
        else 'аэропорт Пубертатово'
    )

    position = [37.6169653333, 55.7563438333]
    callcenter_position = [37.6175675721, 55.744319908]

    state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'callcenter_number', 'value': '+799976543321'},
                {'key': 'abonent_number', 'value': '+79991234567'},
            ],
        ),
    )

    action = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', [],
    )

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _(request):
        assert request.json['position'] == callcenter_position
        assert request.json['state']['location'] == callcenter_position
        assert request.json['state']['current_mode'] == 'some_current_mode'
        result = {
            'lang': '',
            'log': 'log',
            'method': 'phone_history.source',
            'position': [37.6169653333, 55.7563438333],
            'subtitle': {'text': 'Москва, Россия', 'hl': []},
            'text': unparsed_address,
            'title': {'text': organization_name, 'hl': []},
            'uri': 'uri',
            'type': 'organization' if is_organization else 'address',
            'image_tag': 'custom_suggest_default_tag',
            'city': city,
            'tags': [],
            'postal_code': '103265',
        }
        if address_is_parsed:
            result['street'] = street
            result['house'] = house
        if entrance:
            result['entrance'] = entrance
        return web.json_response(
            data={'results': [result] if has_points else []},
        )

    new_state = await action(web_context, state)

    assert new_state.features.get('application_name') == 'call_center'
    assert new_state.features.get('yandex_uid') is not None
    assert new_state.features.get('callcenter_position') is not None

    expected_address = (
        f'{city}, {street}, {house}'
        if address_is_parsed and city is not None
        else unparsed_address
    )
    if entrance and address_is_parsed and city is not None:
        expected_address += f', подъезд {entrance}'
    if is_organization:
        if not is_metro and not is_airport:
            expected_address = f'{organization_name}, {expected_address}'
        else:
            expected_address = organization_name

    expected_obj_types = ['organization'] if is_organization else ['address']

    for point_type in ['a', 'b']:
        obj_types_feature = f'probable_points_{point_type}_obj_types'
        points_feature = f'probable_points_{point_type}'
        titles_feature = f'probable_points_{point_type}_titles'
        cities_feature = f'probable_points_{point_type}_cities'
        subtitles_feature = f'probable_points_{point_type}_subtitles'
        positions_feature = f'probable_points_{point_type}_pos'
        call_center_ok_feature = f'probable_points_{point_type}_call_center_ok'
        avg_position_feature = f'probable_points_{point_type}_avg_position'

        points_obj_types = new_state.features.get(obj_types_feature, sentinel)
        points = new_state.features.get(points_feature, sentinel)
        points_titles = new_state.features.get(titles_feature, sentinel)
        points_subtitles = new_state.features.get(subtitles_feature, sentinel)
        points_cities = new_state.features.get(cities_feature, sentinel)
        points_pos = new_state.features.get(positions_feature, sentinel)
        call_center_ok = new_state.features.get(
            call_center_ok_feature, sentinel,
        )
        avg_position = new_state.features.get(avg_position_feature, sentinel)

        if has_points:
            assert points_obj_types == expected_obj_types
            assert points == [expected_address]
            assert points_titles == [organization_name]
            assert points_subtitles == ['Москва, Россия']
            assert points_pos == position
            assert call_center_ok is False
            assert avg_position == [37.6169653333, 55.7563438333]
            assert points_cities == ([city] if city is not None else [''])
        else:
            assert points_obj_types is None
            assert points is None
            assert points_titles is None
            assert points_subtitles is None
            assert points_pos is None
            assert call_center_ok is None
            assert avg_position is None


@pytest.mark.config(
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'zerosuggest_current_mode': 'some_current_mode',
        'zerosuggest_use_location_parameter': True,
    },
)
async def test_get_probable_points_call_center_ok(
        web_context, mockserver, mock_user_api, default_state,
):
    action = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', [],
    )

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _(_):
        return web.json_response(
            data={
                'results': [
                    {
                        'lang': '',
                        'log': 'log',
                        'method': 'phone_history.source',
                        'position': [0.0, 0.0],
                        'subtitle': {'text': '', 'hl': []},
                        'text': '',
                        'title': {'text': '', 'hl': []},
                        'uri': 'uri',
                        'image_tag': 'custom_suggest_default_tag',
                        'tags': ['call_center_ok'],
                    },
                ],
            },
        )

    new_state = await action.call(web_context, default_state)
    for point_type in ['a', 'b']:
        assert (
            new_state.features.get(f'probable_points_{point_type}') is not None
        )
        assert (
            new_state.features.get(
                f'probable_points_{point_type}_call_center_ok',
            )
            is True
        )


@pytest.mark.config(
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'zerosuggest_current_mode': 'some_current_mode',
        'zerosuggest_use_location_parameter': True,
    },
)
@pytest.mark.parametrize(
    ('use_point_a_position', 'point_a_position'),
    [(True, [11.00, 11.00]), (True, None), (False, [11.00, 11.00])],
)
async def test_using_point_a_position_in_zerosuggest(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        use_point_a_position,
        point_a_position,
):
    callcenter_position = [37.6175675721, 55.744319908]
    action_params = (
        [param_module.ActionParam({'use_point_a_position': True})]
        if use_point_a_position
        else []
    )

    if point_a_position:
        default_state.features['recognized_point_a_pos'] = point_a_position

    action = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', action_params,
    )

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _(request):
        expected_position = (
            point_a_position
            if use_point_a_position and point_a_position
            else callcenter_position
        )
        assert request.json['position'] == expected_position
        assert request.json['state']['location'] == expected_position
        return web.json_response(data={'results': []})

    await action.call(web_context, default_state)


@pytest.mark.config(
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'zerosuggest_current_mode': 'some_current_mode',
    },
)
async def test_no_using_location_in_zerosuggest(
        web_context, mockserver, mock_user_api, default_state,
):
    callcenter_position = [37.6175675721, 55.744319908]
    action = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', [],
    )

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _(request):
        assert request.json['position'] == callcenter_position
        assert request.json['state'].get('location') is None
        return web.json_response(data={'results': []})

    await action.call(web_context, default_state)


@pytest.mark.config(
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'zerosuggest_current_mode': 'some_current_mode',
    },
)
async def test_current_mode_when_sandbox(
        web_context, mockserver, mock_user_api, default_state,
):
    action = get_probable_points.GetProbablePoints(
        'test',
        'get_probable_points',
        '0',
        [param_module.ActionParam({'is_sandbox': True})],
    )

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _(request):
        assert (
            request.json['state']['current_mode']
            == 'some_current_mode_sandbox'
        )
        return web.json_response(data={'results': []})

    await action.call(web_context, default_state)


@pytest.mark.config(
    SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
        'country_names_to_exclude': ['Россия', 'Российская империя'],
    },
)
@pytest.mark.parametrize('with_magadan', [True, False])
async def test_truncating_country(
        web_context, mockserver, mock_user_api, default_state, with_magadan,
):
    if with_magadan:
        web_context.config.SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG[
            'country_names_to_exclude'
        ].append('Магаданская республика')

    full_address = ''

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _(_):
        return web.json_response(
            data={
                'results': [
                    {
                        'lang': '',
                        'log': 'log',
                        'method': 'search',
                        'position': [0.0, 0.0],
                        'subtitle': {'text': '', 'hl': []},
                        'text': full_address,
                        'title': {'text': '', 'hl': []},
                        'uri': 'uri',
                    },
                ],
            },
        )

    action = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', [param_module.ActionParam({})],
    )

    truncated_address = 'Город, Улица, 7'

    cases = [
        # country, should_be_truncated
        ('Россия', True),
        ('Российская империя', True),
        ('Магаданская республика', with_magadan),
    ]

    for country, should_be_truncated in cases:
        full_address = f'{country}, {truncated_address}'
        state = copy.copy(default_state)
        new_state = await action(web_context, state)
        expected_address = (
            truncated_address if should_be_truncated else full_address
        )

        assert new_state.features['probable_points_a'] == [expected_address]

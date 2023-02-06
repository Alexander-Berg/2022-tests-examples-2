# flake8: noqa: I100
# pylint: disable=broad-except
# pylint: disable=too-many-lines
import copy
import random
import pytest
from aiohttp import web

from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.taxi_order_by_phone_incoming_call import (
    extract_point,
)
from supportai_actions.action_types.taxi_order_by_phone_incoming_call import (
    get_probable_points,
)
from supportai_actions.action_types.taxi_order_by_phone_incoming_call.taxi_order_utils import (
    constants,
)

MAX_CALLCENTER_TO_A_DISTANCE = 500
MAX_A_TO_B_DISTANCE = 100
MIN_ZEROSUGGEST_POINT_ML_SCORE = 0.7
MIN_ZEROSUGGEST_POINT_ML_SCORE_SANDBOX = 0.9
MIN_USER_MESSAGE_RELEVANCE = 0.075
MIN_USER_MESSAGE_RELEVANCE_EXTRA = 0.15

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
            '+799976543321': {
                'geo_zone_coords': {'lat': 55.744319908, 'lon': 37.6175675721},
                'application': 'call_center',
            },
        },
        SUPPORTAI_ACTIONS_TAXI_ORDER_CONFIG={
            'callcenter_specific_settings': {},
            'default_tariff': 'econom',
            'heuristics_min_score': 4,
            'max_callcenter_to_point_a_distance_km': (
                MAX_CALLCENTER_TO_A_DISTANCE
            ),
            'max_levenstein_distance': 2,
            'max_point_a_to_point_b_distance_km': MAX_A_TO_B_DISTANCE,
            'ml_min_zerosuggest_point_relevance': (
                MIN_ZEROSUGGEST_POINT_ML_SCORE
            ),
            'ml_min_zerosuggest_point_relevance_sandbox': (
                MIN_ZEROSUGGEST_POINT_ML_SCORE_SANDBOX
            ),
            'ml_min_user_message_relevance': MIN_USER_MESSAGE_RELEVANCE,
            'ml_min_user_message_relevance_sandbox': (
                MIN_USER_MESSAGE_RELEVANCE
            ),
            'ml_min_user_message_relevance_extra': (
                MIN_USER_MESSAGE_RELEVANCE_EXTRA
            ),
            'region_names_to_keep': [
                'Московская область',
                'Ленинградская область',
            ],
            'words_to_exclude': ['здравствуйте'],
            'words_to_ignore_extra_persuggest': ['арара'],
        },
        TVM_RULES=[{'src': 'supportai-actions', 'dst': 'personal'}],
    ),
]


@pytest.fixture(name='separator')
def _get_separator():
    return constants.ORGANIZATION_SUBTITLE_SEPARATOR


def _get_prefilled_persuggest_res():
    return {
        'results': [
            {
                'lang': 'rus',
                'log': 'log',
                'method': 'geosuggest',
                'position': [37.617115, 55.75713],
                'subtitle': {'text': 'default subtitle', 'hl': []},
                'text': 'default text',
                'title': {'text': 'default title', 'hl': []},
                'uri': '',
                'distance': {'text': '', 'value': 0.0},
                'image_tag': 'custom_suggest_default_tag',
                'action': 'search',
                'tags': [],
            },
        ],
        'part': '',
        'suggest_reqid': 'id',
    }


def _get_wizard_response(address=None, org=None):
    rules = {}
    if address:
        rules['GeoAddr'] = {'NormalizedText': address}
    if org:
        rules['Wares'] = {
            'CatsFlat': [
                f'org\t{org}\t0.680\t0.046\t1\t2\t'
                f'0.978\t0.000\t0.680\t0.069\tunknown\t0.000',
            ],
        }
    return web.json_response(data={'rules': rules})


@pytest.mark.parametrize('wizard_address', ['Охотный ряд 2', None])
@pytest.mark.parametrize('entrance_number', ['3', None])
async def test_extract_point(
        web_context,
        mockserver,
        wizard_address,
        entrance_number,
        mock_user_api,
):
    user_message = 'Охотный ряд 2, пожалуйста'
    state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'callcenter_number', 'value': '+799976543321'},
                {'key': 'abonent_number', 'value': '+79991234567'},
                {'key': 'last_user_message', 'value': user_message},
            ],
        ),
    )

    _call_param = [param_module.ActionParam({'point_type': 'a'})]

    action = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address=wizard_address)

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(request):
        if wizard_address:
            assert request.json['part'] == wizard_address
        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['subtitle']['text'] = 'Москва, Россия'
        result['text'] = (
            'Россия, Москва, улица Охотный Ряд, 2'
            if wizard_address is not None
            else 'Россия, Москва, улица Охотный Ряд'
        )
        result['title']['text'] = 'улица Охотный Ряд, 2'
        if entrance_number is not None:
            result['entrance'] = entrance_number
        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    new_state = await action(web_context, state)

    assert new_state.features.get('application_name') == 'call_center'

    assert 'recognized_point_a' in new_state.features
    expected_address = 'Москва, улица Охотный Ряд'
    if wizard_address:
        expected_address += ', 2'
    if entrance_number:
        expected_address += f', подъезд {entrance_number}'

    assert new_state.features['recognized_point_a'] == expected_address
    assert 'yandex_uid' in new_state.features
    assert 'callcenter_position' in new_state.features


async def test_extract_point_using_avg_zs_pos(
        web_context, mockserver, mock_user_api,
):
    user_message = 'Охотный ряд 2, пожалуйста'
    state = state_module.State(
        features=feature_module.Features(
            features=[
                {'key': 'callcenter_number', 'value': '+799976543321'},
                {'key': 'abonent_number', 'value': '+79991234567'},
                {'key': 'last_user_message', 'value': user_message},
                {'key': 'probable_points_a_avg_position', 'value': [1.2, 3.4]},
            ],
        ),
    )

    _call_param = [
        param_module.ActionParam(
            {'point_type': 'a', 'use_avg_zs_position': True},
        ),
    ]

    action = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address='Охотный ряд 2')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(request):
        assert request.json['state']['location'] == [1.2, 3.4]

        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['subtitle']['text'] = 'Москва, Россия'
        result['text'] = 'Россия, Москва, улица Охотный Ряд, 2'
        result['title']['text'] = 'улица Охотный Ряд, 2'
        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    new_state = await action(web_context, state)

    assert 'recognized_point_a' in new_state.features


@pytest.mark.parametrize('wizard_address', ['some_response', None])
async def test_extract_no_point(
        web_context, mockserver, wizard_address, mock_user_api, default_state,
):
    state = default_state

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address=wizard_address)

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        return {'results': [], 'part': '', 'suggest_reqid': 'id'}

    for point_type in ('a', 'b'):
        _call_param = [param_module.ActionParam({'point_type': point_type})]

        action = extract_point.ExtractPoint(
            'test', 'extract_point', '0', _call_param,
        )

        state = await action.call(web_context, state)

        assert f'recognized_point_{point_type}' in state.features
        assert state.features[f'recognized_point_{point_type}'] is None
        assert f'point_{point_type}_is_from_zerosuggest' not in state.features
        assert f'point_{point_type}_is_from_persuggest' not in state.features
        assert (
            state.features.get(
                f'point_{point_type}_persuggest_is_from_wizard_response',
            )
            is False
        )
        assert (
            state.features.get(
                f'point_{point_type}_persuggest_is_from_raw_user_message',
            )
            is False
        )


async def test_using_point_a_position_when_extracting_point_b(
        web_context, mockserver, mock_user_api, default_state,
):
    callcenter_position = [37.6175675721, 55.744319908]
    point_a_position = [11.00, 11.00]

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response()

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(request):
        if request.json['type'] == 'a':
            assert request.json['state']['location'] == callcenter_position
        else:
            assert request.json['state']['location'] == point_a_position

        response = _get_prefilled_persuggest_res()
        response['results'][0]['position'] = point_a_position
        return response

    for point_type in ('a', 'b'):
        _call_param = [param_module.ActionParam({'point_type': point_type})]
        action = extract_point.ExtractPoint(
            'test', 'extract_point', '0', _call_param,
        )
        default_state = await action.call(web_context, default_state)


@pytest.mark.parametrize('distance_limit_exceeded', [True, False])
async def test_different_truncating_by_distance_for_a_and_b(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        distance_limit_exceeded,
):
    max_callcenter_to_a_m = MAX_CALLCENTER_TO_A_DISTANCE * 1000
    max_a_to_b_m = MAX_A_TO_B_DISTANCE * 1000
    deviation = 100 if distance_limit_exceeded else -100

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response()

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(request):
        response = _get_prefilled_persuggest_res()
        if request.json['type'] == 'a':
            distance = max_callcenter_to_a_m + deviation
        else:
            distance = max_a_to_b_m + deviation
        response['results'][0]['distance']['value'] = float(distance)
        return response

    for point_type in ('a', 'b'):
        _call_param = [param_module.ActionParam({'point_type': point_type})]
        action = extract_point.ExtractPoint(
            'test', 'extract_point', '0', _call_param,
        )
        default_state = await action.call(web_context, default_state)

    if distance_limit_exceeded:
        assert default_state.features.get('recognized_point_a') is None
        assert default_state.features.get('recognized_point_b') is None
    else:
        assert default_state.features.get('recognized_point_a') is not None
        assert default_state.features.get('recognized_point_b') is not None


@pytest.mark.parametrize('wizard_address', ['Улица Новаторов 2', None])
async def test_extract_organization_address(
        web_context,
        mockserver,
        mock_user_api,
        wizard_address,
        default_state,
        separator,
):
    _call_param = [param_module.ActionParam({'point_type': 'a'})]

    action = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address=wizard_address, org='SUPERNOVA')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(request):
        search_request = request.json['part']
        org_name, *address = search_request.split(', ')
        assert org_name == 'SUPERNOVA'
        if wizard_address:
            assert address
            assert address[0] == 'Улица Новаторов 2'

        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['text'] = 'SUPERNOVA'

        if wizard_address:
            subtitle_text = (
                f'Ночной клуб {separator} Зеленоярск, улица Новаторов, 2с1'
            )
        else:
            subtitle_text = (
                f'Дом престарелых {separator} Зеленоярск, улица Тоски, 0'
            )
        result['subtitle']['text'] = subtitle_text
        result['uri'] = 'something//org?something'
        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    new_state = await action(web_context, default_state)

    assert (
        new_state.features.get('recognized_point_a_obj_type') == 'organization'
    )

    recognized_point_a = new_state.features.get('recognized_point_a')
    expected_point = (
        'Ночной клуб SUPERNOVA, Зеленоярск, улица Новаторов, 2с1'
        if wizard_address
        else 'Дом престарелых SUPERNOVA, Зеленоярск, улица Тоски, 0'
    )
    assert recognized_point_a == expected_point

    if wizard_address:
        assert 'yandex_uid' in new_state.features
        assert 'callcenter_position' in new_state.features


@pytest.mark.parametrize(
    ('is_metro', 'is_airport'), [(False, False), (True, False), (False, True)],
)
async def test_extract_metro_station_and_airport(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        separator,
        is_metro,
        is_airport,
):
    _call_param = [param_module.ActionParam({'point_type': 'a'})]

    action = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    org_type = 'Тип организации'
    org_name = 'Имя организации'
    address = 'Город, дом, улица'

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address=None, org='Метро Лубянка')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['text'] = org_name
        result['subtitle']['text'] = f'{org_type} {separator} {address}'
        result['uri'] = 'something//org?something'
        result['tags'] = (
            ['metro'] if is_metro else ['airports'] if is_airport else []
        )
        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    new_state = await action(web_context, default_state)

    expected_point = (
        f'{org_type} {org_name}'
        if is_metro
        else org_name
        if is_airport
        else f'{org_type} {org_name}, {address}'
    )

    assert 'recognized_point_a' in new_state.features
    assert new_state.features['recognized_point_a'] == expected_point


@pytest.mark.parametrize('truncate_by_distance', [True, False])
async def test_passing_raw_user_message_to_persuggest_when_no_result(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        separator,
        truncate_by_distance,
):
    _call_param = [param_module.ActionParam({'point_type': 'a'})]

    action = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    bad_address = 'some weird address'
    good_address = 'some good address'
    default_state.features['last_user_message'] = good_address
    max_distance_m = MAX_CALLCENTER_TO_A_DISTANCE * 1000

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address=bad_address)

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(request):
        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['uri'] = 'something//geo?something'
        result['distance'] = {'value': max_distance_m, 'text': 'RAR'}

        query = request.json['part']
        if query == bad_address:
            if not truncate_by_distance:
                json_response['results'] = []
                return json_response
            result[
                'text'
            ] = 'Плохая страна, Плохой город, Плохая улица, Плохой дом'
            result['distance']['value'] += 1
        elif query == good_address:
            result[
                'text'
            ] = 'Хорошая страна, Хороший город, Хорошая улица, Хороший дом'
            result['distance']['value'] -= 1
        else:
            assert False, 'такого быть не должно...'

        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    new_state = await action(web_context, default_state)

    assert new_state.features.get('point_a_persuggest_query') == bad_address
    assert (
        new_state.features.get('point_a_persuggest_is_from_wizard_response')
        is False
    )
    assert (
        new_state.features.get('point_a_persuggest_is_from_raw_user_message')
        is True
    )
    assert (
        new_state.features.get('recognized_point_a')
        == 'Хороший город, Хорошая улица, Хороший дом'
    )


async def test_truncating_region_name(
        web_context, mockserver, mock_user_api, default_state, separator,
):
    address = ''

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response()

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['uri'] = 'something//geo?something'
        result['distance'] = {'value': 0, 'text': 'RAR'}
        result['text'] = address
        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    _call_param = [param_module.ActionParam({'point_type': 'a'})]

    action = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    reduced_address = 'Какой-то город, Какая-то улица, дом некий'
    region_names = [
        'МосКоВскАя обЛастЬ',
        'Ленинградская область',
        'КраЙ МОЙ ДАЛЕКИЙ',
        'моя любимая республика',
        'Округ Белого Мотылька',
        'Паховая область',
    ]

    for idx, region_name in enumerate(region_names):
        address_with_no_country = f'{region_name}, {reduced_address}'
        address = f'Россия, {address_with_no_country}'
        initial_state = copy.deepcopy(default_state)
        new_state = await action(web_context, initial_state)

        recognized_address = new_state.features.get('recognized_point_a')

        if idx <= 1:
            assert recognized_address == address_with_no_country
        else:
            assert recognized_address == reduced_address


@pytest.mark.parametrize('is_sandbox', [True, False])
@pytest.mark.parametrize('user_message_is_irrelevant', [True, False])
async def test_ranging_zerosuggest_addresses(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        separator,
        user_message_is_irrelevant,
        is_sandbox,
):
    wizard_address = 'некая улица дом 1/1'
    user_message = 'ааааа ббббб ввввв'
    suggest_address = 'рандом рандом рандом'

    threshold = (
        MIN_ZEROSUGGEST_POINT_ML_SCORE
        if not is_sandbox
        else MIN_ZEROSUGGEST_POINT_ML_SCORE_SANDBOX
    )
    scored_zerosuggest_addresses = [
        ('Адрес не будет выбран', threshold * 0.9),
        ('Адрес будет выбран вторым', threshold * 1.02),
        ('Адрес будет выбран первым', threshold * 1.05),
    ]

    default_state.features['use_zerosuggest'] = True
    default_state.features['last_user_message'] = user_message

    call_params = {'point_type': 'a'}
    if is_sandbox:
        call_params['is_sandbox'] = True
    _call_param = [param_module.ActionParam(call_params)]

    action_zerosuggest = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', _call_param,
    )
    action = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(wizard_address)

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['uri'] = 'something//geo?something'
        result['distance'] = {'value': 0, 'text': 'ROAR'}
        result['text'] = f'Россия, {suggest_address}'

        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    while scored_zerosuggest_addresses:
        initial_state = copy.deepcopy(default_state)
        shuffled_zerosuggest_addresses = copy.deepcopy(
            scored_zerosuggest_addresses,
        )
        random.shuffle(shuffled_zerosuggest_addresses)

        @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
        async def _(request):
            def _create_result(address):
                return {
                    'uri': 'something//geo?something',
                    'distance': {'value': 0, 'text': 'ROAR'},
                    'text': f'Россия, {address}',
                    'position': [0.0, 0.0],
                    'lang': 'rus',
                    'log': 'log',
                    'method': '',
                    'title': {'text': 'something', 'hl': []},
                    'subtitle': {'text': 'subsomething', 'hl': []},
                }

            if request.json['type'] == 'a':
                results = [
                    _create_result(address[0])
                    for address in shuffled_zerosuggest_addresses
                ]
            else:
                results = []

            json_response = _get_prefilled_persuggest_res()
            json_response['results'] = results
            return json_response

        @mockserver.json_handler(
            'plotva-ml/taxi_order_by_phone/match_address/v1',
        )
        async def _(request):
            assert request.json['user_message'] == user_message
            assert request.json['mode'] == (
                'sandbox_robot_call_center'
                if is_sandbox
                else 'robot_call_center'
            )
            scored_zerosuggest_items = [
                {
                    'zerosuggest_item': {
                        'title': zerosuggest_item['title'],
                        'subtitle': zerosuggest_item['subtitle'],
                        'index': zerosuggest_item['index'],
                    },
                    'score': shuffled_zerosuggest_addresses[
                        zerosuggest_item['index']
                    ][1],
                }
                for zerosuggest_item in request.json['zerosuggest_items']
            ]
            relevance = (
                MIN_USER_MESSAGE_RELEVANCE + 0.01
                if not user_message_is_irrelevant
                else MIN_USER_MESSAGE_RELEVANCE - 0.01
            )

            return {
                'scored_zerosuggest_items': scored_zerosuggest_items,
                'relevance': relevance,
            }

        new_state = await action_zerosuggest(web_context, initial_state)
        new_state = await action(web_context, new_state)

        if user_message_is_irrelevant:
            assert new_state.features['recognized_point_a'] is None
            assert 'point_a_is_from_zerosuggest' not in new_state.features
            assert 'point_a_is_from_persuggest' not in new_state.features
            assert (
                new_state.features.get('point_a_user_message_is_irrelevant')
                is True
            )
            return

        assert 'point_a_user_message_is_irrelevant' not in new_state.features

        if len(scored_zerosuggest_addresses) <= 1:
            assert new_state.features['recognized_point_a'] == suggest_address
            assert (
                new_state.features.get('point_a_is_from_zerosuggest') is False
            )
            assert new_state.features.get('point_a_is_from_persuggest') is True
        else:
            assert (
                new_state.features['recognized_point_a']
                == scored_zerosuggest_addresses[-1][0]
            )
            assert (
                new_state.features.get('point_a_is_from_zerosuggest') is True
            )
            assert (
                new_state.features.get('point_a_is_from_persuggest') is False
            )

        scored_zerosuggest_addresses.pop(-1)


@pytest.mark.parametrize(
    ('zs_has_additional', 'zs_probabilities'),
    [
        ([False, False], [None, None]),
        ([False, True], [None, 0.4]),
        ([True, True], [0.4, None]),
    ],
)
async def test_extract_point_call_center_ok_and_probability(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        zs_has_additional,
        zs_probabilities,
):
    default_state.features['use_zerosuggest'] = True
    default_state.features['last_user_message'] = 'first address'

    action_zerosuggest = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', [],
    )
    action_extract_point = extract_point.ExtractPoint(
        'test', 'extract_point', '0', [],
    )

    addresses = ['first address', 'second address']

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response()

    @mockserver.json_handler('plotva-ml/taxi_order_by_phone/match_address/v1')
    async def _(_):
        scored_zerosuggest_items = [
            {
                'zerosuggest_item': {
                    'title': '',
                    'subtitle': '',
                    'index': idx,
                },
                'score': 1.0 - float(idx),
            }
            for idx in range(2)
        ]
        relevance = 1.0

        return {
            'scored_zerosuggest_items': scored_zerosuggest_items,
            'relevance': relevance,
        }

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        assert False

    for call_center_ok_idx in range(-1, 2):

        @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
        async def _(_):
            def _create_result(
                    address, is_call_center_ok, has_additional, relevance,
            ):
                result = {
                    'uri': 'something//geo?something',
                    'distance': {'value': 0, 'text': 'do not repeat yourself'},
                    'text': f'Россия, {address}',
                    'position': [0.0, 0.0],
                    'lang': 'rus',
                    'log': 'log',
                    'method': '',
                    'title': {'text': 'something', 'hl': []},
                    'subtitle': {'text': 'subsomething', 'hl': []},
                    'tags': ['call_center_ok'] if is_call_center_ok else [],
                }
                if has_additional:
                    additional_info = {}
                    if relevance is not None:
                        additional_info['relevance'] = relevance
                    result['additional_point_info'] = additional_info
                return result

            results = [
                _create_result(
                    address,
                    idx == call_center_ok_idx,
                    has_additional,
                    relevance,
                )
                for idx, (address, has_additional, relevance) in enumerate(
                    zip(addresses, zs_has_additional, zs_probabilities),
                )
            ]

            json_response = _get_prefilled_persuggest_res()
            json_response['results'] = results
            return json_response

        initial_state = copy.deepcopy(default_state)
        new_state = await action_zerosuggest(web_context, initial_state)
        new_state = await action_extract_point(web_context, new_state)

        assert new_state.features.get('probable_points_a_call_center_ok') is (
            call_center_ok_idx > -1
        )
        assert new_state.features.get('probable_points_a_probabilities') == [
            probability or -1.0 for probability in zs_probabilities
        ]

        assert new_state.features.get('recognized_point_a') == 'first address'
        assert new_state.features.get('point_a_call_center_ok') is (
            call_center_ok_idx == 0
        )
        assert new_state.features.get('point_a_zerosuggest_probability') == (
            zs_probabilities[0] or -1.0
        )


async def test_joining_zerosuggest_addresses(
        web_context, mockserver, mock_user_api, default_state, patch,
):
    default_state.features['use_zerosuggest'] = True
    default_state.features['last_user_message'] = 'first address'

    _call_param = [
        param_module.ActionParam(
            {'point_type': 'a', 'ml_zerosuggest_scoring': True},
        ),
    ]

    action_zerosuggest = get_probable_points.GetProbablePoints(
        'test', 'get_probable_points', '0', [],
    )
    action_extract_point = extract_point.ExtractPoint(
        'test', 'extract_point', '0', _call_param,
    )

    title_a = 'title_a'
    title_b = 'title_b'

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response()

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/zerosuggest')
    async def _(request):
        json_response = _get_prefilled_persuggest_res()
        if request.json['type'] == 'a':
            json_response['results'][0]['title'] = title_a
        else:
            json_response['results'][0]['title'] = title_b
        return json_response

    @mockserver.json_handler('plotva-ml/taxi_order_by_phone/match_address/v1')
    async def _(request):
        zerosuggest_items = request.json['zerosuggest_items']
        titles = [item['title'] for item in zerosuggest_items]
        assert set(titles) == {title_a, title_b}
        scored_zerosuggest_items = [
            {
                'zerosuggest_item': {
                    'title': zerosuggest_item['title'],
                    'subtitle': zerosuggest_item['subtitle'],
                    'index': zerosuggest_item['index'],
                },
                'score': 1.0,
            }
            for zerosuggest_item in request.json['zerosuggest_items']
        ]
        relevance = 1.0

        return {
            'scored_zerosuggest_items': scored_zerosuggest_items,
            'relevance': relevance,
        }

    initial_state = copy.deepcopy(default_state)
    new_state = await action_zerosuggest(web_context, initial_state)
    await action_extract_point(web_context, new_state)


@pytest.mark.parametrize(
    ('moscow_region', 'with_house', 'with_entrance'),
    [
        (True, True, True),
        (True, True, False),
        (False, True, False),
        (False, False, False),
    ],
)
async def test_extract_geo_address_from_yamaps(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        moscow_region,
        with_house,
        with_entrance,
):
    action_extract_point = extract_point.ExtractPoint(
        'test', 'extract_point', '0', [],
    )

    yamaps_response_json = {
        'features': [
            {
                'geometry': {
                    'coordinates': [37.428881, 55.889341],
                    'type': 'Point',
                },
                'properties': {
                    'GeocoderMetaData': {
                        'Address': {
                            'Components': [
                                {'kind': 'country', 'name': 'Россия'},
                                {
                                    'kind': 'province',
                                    'name': 'Центральный федеральный округ',
                                },
                                {
                                    'kind': 'province',
                                    'name': (
                                        'Московская область'
                                        if moscow_region
                                        else 'Некая иная область'
                                    ),
                                },
                                {
                                    'kind': 'area',
                                    'name': 'городской округ Химки',
                                },
                                {'kind': 'locality', 'name': 'Химки'},
                                {'kind': 'street', 'name': 'улица 9 Мая'},
                            ],
                            'formatted': '',
                        },
                    },
                },
            },
        ],
    }
    if with_house:
        yamaps_response_json['features'][0]['properties']['GeocoderMetaData'][
            'Address'
        ]['Components'].append({'kind': 'house', 'name': '1'})
    if with_entrance:
        yamaps_response_json['features'][0]['properties']['GeocoderMetaData'][
            'Address'
        ]['Components'].append({'kind': 'entrance', 'name': 'подъезд 3'})

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address='anything')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['uri'] = 'something//geo?something'
        result['distance'] = {'value': 0, 'text': 'ROAR'}
        result['text'] = f'does not matter at all'

        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def yamaps_handle(_):
        return web.json_response(data=yamaps_response_json)

    new_state = await action_extract_point(web_context, default_state)

    assert new_state.features['recognized_point_a'] == (
        'Московская область, Химки, улица 9 Мая, 1, подъезд 3'
        if moscow_region and with_house and with_entrance
        else 'Московская область, Химки, улица 9 Мая, 1'
        if moscow_region and with_house
        else 'Химки, улица 9 Мая, 1'
        if with_house
        else None
    )

    assert yamaps_handle.times_called == 1


@pytest.mark.parametrize('class_', ['metro', 'airports', 'landmark', 'bar'])
async def test_extract_organization_address_from_yamaps(
        web_context, mockserver, mock_user_api, default_state, class_,
):
    action_extract_point = extract_point.ExtractPoint(
        'test', 'extract_point', '0', [],
    )

    yamaps_response_json = {
        'features': [
            {
                'geometry': {
                    'coordinates': [37.636122, 55.761575],
                    'type': 'Point',
                },
                'properties': {
                    'CompanyMetaData': {
                        'Address': {
                            'Components': [
                                {'kind': 'country', 'name': 'Россия'},
                                {
                                    'kind': 'province',
                                    'name': 'Центральный федеральный округ',
                                },
                                {'kind': 'province', 'name': 'Москва'},
                                {'kind': 'locality', 'name': 'Москва'},
                                {
                                    'kind': 'street',
                                    'name': 'Кривоколенный переулок',
                                },
                                {'kind': 'house', 'name': '10, стр. 5'},
                            ],
                            'country_code': '',
                            'formatted': '',
                            'postal_code': '',
                        },
                        'Categories': [
                            {'class': class_, 'name': 'Бар, паб'},
                            {'class': 'cafe', 'name': 'Кафе'},
                        ],
                        'name': 'Широкую на широкую',
                    },
                },
            },
        ],
    }

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response('anything')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['uri'] = 'something//org?something'
        result['distance'] = {'value': 0, 'text': 'ROAR'}
        result['text'] = f'does not matter at all'

        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data=yamaps_response_json)

    new_state = await action_extract_point(web_context, default_state)

    class_to_expected_address = {
        'metro': 'Бар, паб Широкую на широкую',
        'airports': 'Широкую на широкую',
        'landmark': 'Широкую на широкую',
        'bar': (
            'Бар, паб Широкую на широкую, '
            'Москва, Кривоколенный переулок, 10, стр. 5'
        ),
    }

    recognized_point = new_state.features['recognized_point_a']
    assert recognized_point == class_to_expected_address[class_]


@pytest.mark.parametrize('point_type', ['a', 'b'])
@pytest.mark.parametrize('too_far_point', [True, False])
async def test_using_yamaps(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        point_type,
        too_far_point,
):
    callcenter_pos = [37.617115, 55.75713]
    persuggest_pos = [0.0, 0.0]
    if point_type == 'b':
        default_state.features['recognized_point_a_pos'] = callcenter_pos

    user_address = 'УлИЦа 9 МАЯ'
    user_text = f'здРаВстВуйтЕ----++++,...,,,{user_address}'
    default_state.features['last_user_message'] = user_text

    yamaps_res_coords = copy.copy(callcenter_pos)
    if too_far_point:
        deviation = 10.0 if point_type == 'a' else 2.0
        yamaps_res_coords[0] += deviation

    yamaps_response_json = {
        'features': [
            {
                'geometry': {
                    'coordinates': yamaps_res_coords,
                    'type': 'Point',
                },
                'properties': {
                    'GeocoderMetaData': {
                        'Address': {
                            'Components': [
                                {'kind': 'locality', 'name': 'Химки'},
                                {'kind': 'street', 'name': 'улица 9 Мая'},
                                {'kind': 'house', 'name': '1'},
                            ],
                            'formatted': '',
                        },
                    },
                },
            },
        ],
    }

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address='some address', org='some org')

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        if not too_far_point:
            assert False

        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['position'] = persuggest_pos
        result['uri'] = 'something//org?something'
        result['distance'] = {'value': 0, 'text': 'ROAR'}
        result['text'] = f'does not matter at all'

        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def yamaps_handler(request):
        if request.query.get('text') is not None:
            assert request.query['text'] == user_address
        else:
            assert (
                request.query['ll']
                == f'{persuggest_pos[0]},{persuggest_pos[1]}'
            )
        return web.json_response(data=yamaps_response_json)

    action_params = {
        'use_yamaps_cases': [['addr', 'org']],
        'point_type': point_type,
    }

    action_extract_point = extract_point.ExtractPoint(
        'test',
        'extract_point',
        '0',
        [param_module.ActionParam(action_params)],
    )

    new_state = await action_extract_point(web_context, default_state)

    expected_position = callcenter_pos if not too_far_point else persuggest_pos

    assert (
        new_state.features[f'point_{point_type}_yamaps_query'] == user_address
    )

    assert new_state.features[f'point_{point_type}_query_has_address'] is True
    assert (
        new_state.features[f'point_{point_type}_query_has_organization']
        is True
    )

    assert (
        new_state.features[f'recognized_point_{point_type}_pos']
        == expected_position
    )

    assert yamaps_handler.times_called == (1 if not too_far_point else 2)


@pytest.mark.parametrize('wizard_address_part', ['some_address', None])
@pytest.mark.parametrize('wizard_org_part', ['some_org', None])
@pytest.mark.parametrize(
    ('use_yamaps_cases', 'no_point_when_non_relevant'),
    [
        ([['no_addr', 'org'], ['no_addr', 'no_org']], True),
        ([['no_addr', 'org'], ['no_addr', 'no_org']], False),
        ([['no_addr', 'org'], ['no_addr', 'no_org'], ['addr', 'org']], False),
        ([['addr', 'org']], False),
    ],
)
async def test_use_yamaps_cases_and_point_relevance(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        wizard_org_part,
        wizard_address_part,
        use_yamaps_cases,
        no_point_when_non_relevant,
):
    should_use_yamaps = any(
        [
            all(
                [
                    (wizard_address_part is None) is ('no' in part)
                    if 'addr' in part
                    else (wizard_org_part is None) is ('no' in part)
                    for part in case
                ],
            )
            for case in use_yamaps_cases
        ],
    )

    yamaps_pos = [37.617115, 55.75713]
    persuggest_pos = [0.0, 0.0]

    user_address = 'УлИЦа 9 МАЯ'
    default_state.features['last_user_message'] = user_address

    yamaps_response_json = {
        'features': [
            {
                'geometry': {'coordinates': yamaps_pos, 'type': 'Point'},
                'properties': {
                    'GeocoderMetaData': {
                        'Address': {
                            'Components': [
                                {'kind': 'locality', 'name': 'Город'},
                                {'kind': 'street', 'name': 'улица'},
                                {'kind': 'house', 'name': 'дом'},
                            ],
                            'formatted': '',
                        },
                    },
                },
            },
        ],
    }

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(
            address=wizard_address_part, org=wizard_org_part,
        )

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def _(_):
        if should_use_yamaps:
            assert False

        json_response = _get_prefilled_persuggest_res()
        result = json_response['results'][0]
        result['position'] = persuggest_pos
        result['uri'] = 'something//org?something'
        result['distance'] = {'value': 0, 'text': 'ROAR'}
        result['text'] = 'какой-то адрес'

        return json_response

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(request):
        if request.query.get('text') is not None:
            if not should_use_yamaps:
                assert False
            assert request.query['text'] == user_address
        else:
            if should_use_yamaps:
                assert False
            assert (
                request.query['ll']
                == f'{persuggest_pos[0]},{persuggest_pos[1]}'
            )
        return web.json_response(data=yamaps_response_json)

    action_params = {'use_yamaps_cases': use_yamaps_cases, 'point_type': 'a'}

    if no_point_when_non_relevant:
        action_params['no_point_when_non_relevant_query'] = True

    action_extract_point = extract_point.ExtractPoint(
        'test',
        'extract_point',
        '0',
        [param_module.ActionParam(action_params)],
    )

    new_state = await action_extract_point(web_context, default_state)

    expected_position = yamaps_pos if should_use_yamaps else persuggest_pos

    if (
            no_point_when_non_relevant
            and wizard_address_part is None
            and wizard_org_part is None
    ):
        assert new_state.features[f'recognized_point_a'] is None
        return

    if should_use_yamaps:
        assert new_state.features[f'point_a_yamaps_query'] == user_address
    else:
        assert f'point_a_yamaps_query' not in new_state.features

    assert new_state.features[f'point_a_query_has_address'] is (
        wizard_address_part is not None
    )
    assert new_state.features[f'point_a_query_has_organization'] is (
        wizard_org_part is not None
    )

    assert new_state.features[f'recognized_point_a_pos'] == expected_position


async def test_splitting_house_number(
        web_context, mockserver, mock_user_api, default_state,
):
    user_text_cases = [
        ('Улица 71 подЪезд', 'Улица 70 подЪезд 1', True),
        ('Улица 11 подъезд', 'Улица 11 подъезд', False),
        ('Улица 171 подъезд', 'Улица 170 подъезд 1', True),
        ('Улица 111 подъезд', 'Улица 100 подъезд 11', True),
        ('Улица 71 подъезд 3', 'Улица 71 подъезд 3', False),
        ('Улица 71 подъезд ном 3', 'Улица 71 подъезд ном 3', False),
        ('Улица 71 подъезд ном ном 3', 'Улица 70 подъезд 1 ном ном 3', True),
        ('подъезд 33 подъезд', 'подъезд 33 подъезд', False),
    ]

    yamaps_response_json = {
        'features': [
            {
                'geometry': {
                    'coordinates': [37.617568, 55.74432],
                    'type': 'Point',
                },
                'properties': {
                    'GeocoderMetaData': {
                        'Address': {
                            'Components': [
                                {'kind': 'locality', 'name': 'Москва'},
                                {'kind': 'street', 'name': 'Московская'},
                                {'kind': 'house', 'name': '12321'},
                            ],
                            'formatted': '',
                        },
                    },
                },
            },
        ],
    }

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response()

    action_extract_point = extract_point.ExtractPoint(
        'test',
        'extract_point',
        '0',
        [
            param_module.ActionParam(
                {
                    'use_yamaps_cases': [['no_addr', 'no_org']],
                    'point_type': 'a',
                },
            ),
        ],
    )

    for user_text, modified_user_text, house_splitted in user_text_cases:

        @mockserver.json_handler('yamaps/yandsearch')
        # pylint: disable=cell-var-from-loop
        async def _(request):
            assert request.query.get('text') == modified_user_text
            return web.json_response(data=yamaps_response_json)

        state = copy.deepcopy(default_state)
        state.features['last_user_message'] = user_text

        new_state = await action_extract_point(web_context, state)
        assert new_state.features['point_a_yamaps_query'] == modified_user_text
        assert (
            new_state.features['point_a_house_number_splitted']
            is house_splitted
        )


@pytest.mark.parametrize(
    (
        'wizard_address',
        'user_message_relevance',
        'user_message',
        'address_extracted',
        'extra_mode',
    ),
    [
        ('some address', None, 'Здравствуйте Володарская 6', True, False),
        (
            None,
            MIN_USER_MESSAGE_RELEVANCE_EXTRA * 0.5,
            'Здравствуйте Володарская 6',
            False,
            False,
        ),
        (
            None,
            MIN_USER_MESSAGE_RELEVANCE_EXTRA * 2.0,
            'Здравствуйте Володарская 6',
            True,
            True,
        ),
        (
            None,
            MIN_USER_MESSAGE_RELEVANCE_EXTRA * 2.0,
            'Здравствуйте арара 6 аб',
            False,
            False,
        ),
        (
            None,
            MIN_USER_MESSAGE_RELEVANCE_EXTRA * 2.0,
            'Здравствуйте барара 6 аб',
            True,
            True,
        ),
    ],
)
async def test_using_extra_persuggest(
        web_context,
        mockserver,
        mock_user_api,
        default_state,
        wizard_address,
        user_message_relevance,
        user_message,
        address_extracted,
        extra_mode,
):
    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        return _get_wizard_response(address=wizard_address)

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        return web.json_response(data={'features': []})

    default_state.features['last_user_message'] = user_message

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def persuggest_handler(request):
        expected_query = (
            'some address'
            if not extra_mode
            else 'Володарская 6'
            if 'барара' not in user_message
            else 'барара 6 аб'
        )
        assert request.json['part'] == expected_query
        return _get_prefilled_persuggest_res()

    @mockserver.json_handler('plotva-ml/taxi_order_by_phone/match_address/v1')
    async def plotva_handler(_):
        return {
            'scored_zerosuggest_items': [],
            'relevance': user_message_relevance,
        }

    action_extract_point = extract_point.ExtractPoint(
        'test',
        'extract_point',
        '0',
        [
            param_module.ActionParam(
                {'use_extra_persuggest': True, 'point_type': 'a'},
            ),
        ],
    )

    new_state = await action_extract_point(web_context, default_state)

    check_plotva = (
        wizard_address is None and user_message != 'Здравствуйте арара 6 аб'
    )

    assert plotva_handler.times_called == int(check_plotva)
    assert persuggest_handler.times_called == int(address_extracted)

    if not address_extracted:
        assert new_state.features['recognized_point_a'] is None
        assert 'point_a_is_from_persuggest' not in new_state.features
        assert 'point_a_is_from_extra_persuggest' not in new_state.features
    else:
        assert new_state.features['recognized_point_a'] == 'default text'
        if extra_mode:
            assert new_state.features['point_a_is_from_persuggest'] is False
            assert (
                new_state.features['point_a_is_from_extra_persuggest'] is True
            )
        else:
            assert new_state.features['point_a_is_from_persuggest'] is True
            assert (
                new_state.features['point_a_is_from_extra_persuggest'] is False
            )


async def test_correct_address(
        web_context, mockserver, mock_user_api, default_state,
):
    previous_point = '17-я улица, дом 36к3'
    default_state.features['recognized_point_a'] = previous_point

    corrected_address = '17-я улица, дом 40 подъезд 1'
    cases = [('41 подъезд', corrected_address), ('37 38 39', None)]

    @mockserver.json_handler('/wizard/wizard')
    async def _(_):
        assert False

    @mockserver.json_handler('yamaps/yandsearch')
    async def _(_):
        assert False

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/suggest')
    async def persuggest_handler(request):
        assert request.json['part'] == corrected_address
        return _get_prefilled_persuggest_res()

    @mockserver.json_handler('plotva-ml/taxi_order_by_phone/match_address/v1')
    async def _(_):
        assert False

    action_extract_point = extract_point.ExtractPoint(
        'test',
        'extract_point',
        '0',
        [
            param_module.ActionParam(
                {'point_type': 'a', 'try_correct_address': True},
            ),
        ],
    )

    for user_correction, correction_result in cases:
        state = copy.deepcopy(default_state)
        state.features['last_user_message'] = user_correction
        new_state = await action_extract_point(web_context, state)
        assert new_state.features['point_a_is_from_zerosuggest'] is False
        assert new_state.features['point_a_is_from_persuggest'] is False
        assert new_state.features['point_a_is_from_yamaps'] is False
        assert new_state.features['point_a_is_from_extra_persuggest'] is False
        assert new_state.features[
            'point_a_is_corrected_from_persuggest'
        ] is bool(correction_result)
        if correction_result:
            assert new_state.features['recognized_point_a'] is not None
            assert new_state.features['point_a_address_corrected'] is True
            assert (
                new_state.features['point_a_corrected_address_query']
                == corrected_address
            )
        else:
            assert new_state.features['recognized_point_a'] is None
            assert 'point_a_address_corrected' not in new_state.features
            assert 'point_a_corrected_address_query' not in new_state.features

    assert persuggest_handler.times_called == 1

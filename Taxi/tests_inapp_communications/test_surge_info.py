import copy

import pytest

DEFAULT_HEADERS = {
    'X-Yandex-UID': '1234567890',
    'X-YaTaxi-UserId': 'test_user_id',
    'X-YaTaxi-PhoneId': 'test_phone_id',
    'User-Agent': (
        'yandex-taxi/3.107.0.dev_sergu_b18dbfd* Android/6.0.1 (LGE; Nexus 5)'
    ),
    'X-Request-Application': (
        'app_name=android,app_brand=yataxi,app_ver1=1,app_ver2=2,app_ver3=3'
    ),
    'X-Request-Language': 'ru',
}

DEFAULT_DATA = {
    'selected_classes': ['econom'],
    'payload': {'surge_color': '#FFC618', 'balance': 45},
    'state': {},
}


def find_content_section_by_type(main_section, section_type):
    for item in main_section['items']:
        if item.get('type', '') == section_type:
            return item['content']
    return None


def find_all_sections_by_type(main_section, section_type):
    result = []

    for item in main_section['items']:
        if item.get('type', '') == section_type:
            result.append(item['content'])

    return result


@pytest.mark.parametrize(
    'expected_status_code',
    [
        pytest.param(
            200,
            marks=pytest.mark.experiments3(filename='exp_surge_info.json'),
            id='exp enabled',
        ),
        pytest.param(500, marks=[], id='exp disabled'),
    ],
)
@pytest.mark.translations(
    client_messages={
        'balance_title': {'ru': 'заголовок баланса', 'en': 'balance title'},
        'surge_info_title': {
            'ru': 'заголовок модалки',
            'en': 'surge info title',
        },
        'surge_info_description': {
            'ru': 'описание модалки',
            'en': 'surge info description',
        },
        'details_title': {'ru': 'подробнее', 'en': 'details title'},
        'surge_info_button': {'ru': 'понятно', 'en': 'surge info button'},
    },
)
async def test_surge_common(
        taxi_inapp_communications, mockserver, load_json, expected_status_code,
):
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/surge/info',
        json=DEFAULT_DATA,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == expected_status_code

    if expected_status_code != 200:
        return

    body = response.json()
    assert body['details'] == {
        'title': 'подробнее',
        'deeplink': 'yandextaxi://story?id=xxx',
    }

    content = body['content']
    assert content['title'] == {
        'items': [{'type': 'text', 'text': 'заголовок модалки'}],
    }
    assert content['description'] == {
        'items': [{'type': 'text', 'text': 'описание модалки'}],
    }
    assert content['button'] == {'text': 'понятно'}
    assert content['icon'] == 'widget_info_icon'
    assert content['icon_color'] == '#FFC618'
    assert content['accessibility_info'] == {
        'label': 'заголовок модалки',
        'value': 'описание модалки',
        'hint': 'подробнее',
    }
    assert content['main_section']['style'] == 'list'
    assert content['bottom_section']['style'] == 'promoblocks'


def balance_section(balance, text, color, text_color=None):
    return {
        'balance': balance,
        'color': color,
        'leading_icon': 'balance_lead_icon',
        'text': text,
        'text_color': text_color or color,
        'trail_icon': 'balance_trail_icon',
        'value_icon': 'balance_value_icon',
    }


@pytest.mark.parametrize(
    'request_payload, expected_status, expected_section',
    [
        pytest.param(
            {'surge_color': '#FFC618', 'balance': 45},
            200,
            balance_section(45, 'заголовок баланса', '#FFC618'),
            id='exp enabled, good payload',
            marks=pytest.mark.experiments3(filename='exp_surge_info.json'),
        ),
        pytest.param(
            {'surge_color': '#FFC618'},
            200,
            None,
            id='no balance in payload',
            marks=pytest.mark.experiments3(filename='exp_surge_info.json'),
        ),
        pytest.param(
            {'balance': 45},
            200,
            balance_section(
                45,
                'заголовок баланса',
                # default color if no in payload
                '#E0DEDA',
            ),
            id='no color in payload',
            marks=pytest.mark.experiments3(filename='exp_surge_info.json'),
        ),
        pytest.param(
            {'surge_color': '#FFC618', 'balance': 45},
            200,
            balance_section(
                45,
                'заголовок баланса',
                '#FFC618',
                # text color from exp
                '#012345',
            ),
            id='text color from exp',
            marks=pytest.mark.experiments3(
                filename='exp_surge_info_full.json',
            ),
        ),
        pytest.param(
            {'surge_color': '#FFC618', 'balance': 45},
            200,
            balance_section(45, '', '#FFC618'),
            id='exp enabled, bad translations',
            marks=pytest.mark.experiments3(
                filename='exp_surge_info_bad_translations.json',
            ),
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'balance_title': {'ru': 'заголовок баланса', 'en': 'balance title'},
    },
)
async def test_surge_info_balance_section(
        taxi_inapp_communications,
        request_payload,
        expected_status,
        expected_section,
):

    request = copy.deepcopy(DEFAULT_DATA)
    request['payload'] = request_payload

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/surge/info',
        json=request,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    body = response.json()
    section = find_content_section_by_type(
        body['content']['main_section'], 'balance',
    )
    assert section == expected_section


def separator_section(text):
    return {'items': [{'text': text, 'type': 'text'}]}


@pytest.mark.parametrize(
    'expected_status, expected_section',
    [
        pytest.param(
            200,
            None,
            id='exp enabled, no key',
            marks=pytest.mark.experiments3(filename='exp_surge_info.json'),
        ),
        pytest.param(
            200,
            separator_section('заголовок секции'),
            id='exp enabled, good key',
            marks=pytest.mark.experiments3(
                filename='exp_surge_info_full.json',
            ),
        ),
        pytest.param(
            200,
            None,
            id='exp enabled, bad key',
            marks=pytest.mark.experiments3(
                filename='exp_surge_info_bad_translations.json',
            ),
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'section_name': {
            'ru': 'заголовок секции',
            'en': 'separator section title',
        },
    },
)
async def test_surge_info_separator(
        taxi_inapp_communications, expected_status, expected_section,
):
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/surge/info',
        json=DEFAULT_DATA,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    body = response.json()
    section = find_content_section_by_type(
        body['content']['main_section'], 'separator',
    )
    assert section == expected_section


def textblock_section(title, subtitle, icon, icon_type=None):
    icon = {'tag': icon}
    if icon_type:
        icon['type'] = icon_type

    content = {
        'icon': icon,
        'title': {'items': [{'type': 'text', 'text': title}]},
    }

    if subtitle:
        content['subtitle'] = {'items': [{'type': 'text', 'text': subtitle}]}

    return content


@pytest.mark.parametrize(
    'expected_status, expected_blocks',
    [
        pytest.param(
            200,
            [],
            id='exp enabled, no key',
            marks=pytest.mark.experiments3(filename='exp_surge_info.json'),
        ),
        pytest.param(
            200,
            [],
            id='exp enabled, bad key',
            marks=pytest.mark.experiments3(
                filename='exp_surge_info_bad_translations.json',
            ),
        ),
        pytest.param(
            200,
            # priority: 'weather', 'traffic', 'trend'
            [
                textblock_section(
                    'заголовок погоды', 'заголовок подпогоды', 'weather_icon',
                ),
                textblock_section('заголовок трафика', None, 'traffic_icon'),
                textblock_section(
                    'заголовок тренда',
                    'заголовок подтренда',
                    'trend_icon',
                    'rotate',
                ),
            ],
            id='exp enabled, good key',
            marks=pytest.mark.experiments3(
                filename='exp_surge_info_full.json',
            ),
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'trend_title': {'ru': 'заголовок тренда', 'en': 'trend title'},
        'trend_subtitle': {
            'ru': 'заголовок подтренда',
            'en': 'trend subtitle',
        },
        'weather_title': {'ru': 'заголовок погоды', 'en': 'weather title'},
        'weather_subtitle': {
            'ru': 'заголовок подпогоды',
            'en': 'weather subtitle',
        },
        'traffic_title': {'ru': 'заголовок трафика', 'en': 'traffic title'},
    },
)
async def test_surge_info_text_blocks(
        taxi_inapp_communications, expected_status, expected_blocks,
):

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/surge/info',
        json=DEFAULT_DATA,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    body = response.json()
    sections = find_all_sections_by_type(
        body['content']['main_section'], 'textblock',
    )
    assert sections == expected_blocks


@pytest.mark.now('2017-12-08T23:40:00Z')
@pytest.mark.experiments3(filename='exp_surge_info_trend_only.json')
@pytest.mark.parametrize(
    'request_payload, request_location, expected_status, expected_blocks',
    [
        pytest.param(
            None,
            [37.5724505, 55.74383601869103],
            200,
            [],
            id='no trend seconds',
        ),
        pytest.param(
            {'trend_time_delta_sec': 600}, None, 200, [], id='no location',
        ),
        pytest.param(
            {'trend_time_delta_sec': 600},
            [37.5724505, 55.74383601869103],
            200,
            [
                textblock_section(
                    'заголовок тренда: снижение к 02:50',
                    'заголовок подтренда: снижение к 02:50',
                    'trend_icon',
                    'rotate',
                ),
            ],
            id='Moscow location +3',
        ),
        pytest.param(
            {'trend_time_delta_sec': 1260},
            [37.5724505, 55.74383601869103],
            200,
            [
                textblock_section(
                    'заголовок тренда: снижение к 03:01',
                    'заголовок подтренда: снижение к 03:01',
                    'trend_icon',
                    'rotate',
                ),
            ],
            id='Moscow location +3, minutes starts with 0',
        ),
        pytest.param(
            {'trend_time_delta_sec': 600},
            [-82.37342834472656, 23.1132069804176],
            200,
            [
                textblock_section(
                    'заголовок тренда: снижение к 18:50',
                    'заголовок подтренда: снижение к 18:50',
                    'trend_icon',
                    'rotate',
                ),
            ],
            id='Havana location -5',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'trend_title': {
            'ru': 'заголовок тренда: снижение к %(moment)s',
            'en': 'trend title: снижение к %(moment)s',
        },
        'trend_subtitle': {
            'ru': 'заголовок подтренда: снижение к %(moment)s',
            'en': 'trend subtitle: снижение к %(moment)s',
        },
    },
)
async def test_surge_info_text_blocks_trend_templated(
        taxi_inapp_communications,
        request_payload,
        request_location,
        expected_status,
        expected_blocks,
):
    request = copy.deepcopy(DEFAULT_DATA)
    if request_payload:
        request['payload'] = request_payload
    if request_location:
        request['state']['location'] = request_location

    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/surge/info',
        json=request,
        headers=DEFAULT_HEADERS,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    body = response.json()
    sections = find_all_sections_by_type(
        body['content']['main_section'], 'textblock',
    )
    assert sections == expected_blocks

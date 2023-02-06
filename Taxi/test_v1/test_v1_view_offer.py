# pylint: disable=C0302
import copy
import datetime
import json

import pytest

from tests_driver_fix import common


_CONFIG_BY_ROLE1 = {
    'offer_card': {
        'title': 'role_offer_card.title',
        'description': 'role_offer_card.description',
    },
    'offer_screen': [
        {
            'type': 'caption',
            'title': 'role_offer_screen.title',
            'description': 'role_offer_screen.description',
        },
        {
            'type': 'driver_fix_tariffication',
            'title': 'role_offer_screen.tariffication',
            'caption': 'role_offer_screen.tariffication_select_date',
        },
        {
            'type': 'driver_fix_requirements',
            'title': 'role_offer_screen.requirements',
            'items': [{'type': 'default_constraints'}],
        },
        {
            'type': 'detail_button',
            'text': 'role_offer_screen.full_description_button_text',
            'payload_url': 'https://driver.yandex.role',
            'payload_title': 'role_offer_screen.title',
        },
    ],
    'memo_screen': [
        {'type': 'header', 'caption': 'role_memo_screen.header'},
        {'type': 'multy_paragraph_text', 'text': 'role_memo_screen.text'},
        {'type': 'image', 'image_url': 'memo_image.png.role'},
    ],
}

_CONFIG_BY_ROLE2 = {
    'offer_card': {
        'title': 'role2_offer_card.title',
        'description': 'role2_offer_card.description',
    },
    'offer_screen': [
        {
            'type': 'caption',
            'title': 'role2_offer_screen.title',
            'description': 'role2_offer_screen.description',
        },
        {
            'type': 'driver_fix_tariffication',
            'title': 'role2_offer_screen.tariffication',
            'caption': 'role2_offer_screen.tariffication_select_date',
        },
        {
            'type': 'driver_fix_requirements',
            'title': 'role2_offer_screen.requirements',
            'items': [{'type': 'default_constraints'}],
        },
        {
            'type': 'detail_button',
            'text': 'role2_offer_screen.full_description_button_text',
            'payload_url': 'https://driver.yandex.role2',
            'payload_title': 'role2_offer_screen.title',
        },
    ],
    'memo_screen': [
        {'type': 'header', 'caption': 'role2_memo_screen.header'},
        {'type': 'multy_paragraph_text', 'text': 'role2_memo_screen.text'},
        {'type': 'image', 'image_url': 'memo_image.png.role2'},
    ],
}

use_role_config = pytest.mark.config(  # pylint: disable=C0103
    DRIVER_FIX_OFFER_SCREENS_BY_ROLE_V2={
        '__default__': common.DEFAULT_OFFER_CONFIG_V2,
        'role': _CONFIG_BY_ROLE1,
        'role2': _CONFIG_BY_ROLE2,
    },
)


def _get_body_with_roles(roles=None) -> dict:
    body: dict = {'driver_profile_id': 'uuid', 'park_id': 'dbid'}
    if roles is not None:
        body['roles'] = [{'name': role} for role in roles]
    return body


def _get_params(time_zone: None) -> dict:
    params: dict = {}
    if time_zone:
        params['tz'] = time_zone
    return params


def _get_time_zone(client_time_zone, rule_time_zone) -> dict:
    return client_time_zone if client_time_zone else rule_time_zone


def _check_offers_count(roles, response, expected_offers_count=1) -> None:
    if roles:
        roles_set = {role for role in roles}
        assert (
            len(response['offers']) == len(roles_set) * expected_offers_count
        )
    else:
        assert len(response['offers']) == expected_offers_count


def _get_role_ending(text: str, roles, expected_roles: set) -> str:
    role_ending = ''
    for role in expected_roles:
        if text.endswith(role):
            role_ending = ' ' + role
            assert role in roles
            expected_roles.remove(role)
            break
    return role_ending


AVAILABLE_TILL_SUBTITLE_EXACT_TIMES = {
    'Europe/Moscow': 'Доступен до 23:59 10 января',
    'Asia/Vladivostok': 'Доступен до 06:59 11 января',
}

WAS_AVAILABLE_SUBTITLE_EXACT_TIMES = {
    'Europe/Moscow': 'Был доступен до 23:59 10 января',
    'Asia/Vladivostok': 'Был доступен до 06:59 11 января',
}
WAS_AVAILABLE_DISABLE_REASONS = {
    'Europe/Moscow': 'Режим был доступен до 10 января',
    'Asia/Vladivostok': 'Режим был доступен до 11 января',
}

WILL_BE_AVAILABLE_SUBTITLE_EXACT_TIMES = {
    'Europe/Moscow': 'Будет доступен с 01:05 1 января',
    'Asia/Vladivostok': 'Будет доступен с 08:05 1 января',
}
WILL_BE_AVAILABLE_DISABLE_REASONS = {
    'Europe/Moscow': 'Режим будет доступен с 1 января',
    'Asia/Vladivostok': 'Режим будет доступен с 1 января',
}


@pytest.mark.parametrize(
    'rule_time_zone',
    (
        {'id': 'Europe/Moscow', 'offset': '+03:00'},
        {'id': 'Asia/Vladivostok', 'offset': '+10:00'},
    ),
)
@pytest.mark.parametrize(
    'client_time_zone', (None, 'Europe/Moscow', 'Asia/Vladivostok'),
)
@use_role_config
@pytest.mark.parametrize(
    'expected_subtitle_exact_times, expected_disable_reasons, '
    'expected_is_enabled, roles',
    [
        pytest.param(
            AVAILABLE_TILL_SUBTITLE_EXACT_TIMES,
            None,
            True,
            None,
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
            id='AvailableTill',
        ),
        pytest.param(
            WAS_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WAS_AVAILABLE_DISABLE_REASONS,
            False,
            None,
            marks=[pytest.mark.now('2019-01-12T12:00:00+0300')],
            id='WasAvailable',
        ),
        pytest.param(
            WILL_BE_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WILL_BE_AVAILABLE_DISABLE_REASONS,
            False,
            None,
            marks=[pytest.mark.now('2018-12-31T12:00:00+0300')],
            id='WillBeAvailable',
        ),
        pytest.param(
            AVAILABLE_TILL_SUBTITLE_EXACT_TIMES,
            None,
            True,
            ['missing_role'],
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
            id='AvailableTill_missing_role',
        ),
        pytest.param(
            WAS_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WAS_AVAILABLE_DISABLE_REASONS,
            False,
            ['missing_role'],
            marks=[pytest.mark.now('2019-01-12T12:00:00+0300')],
            id='WasAvailable_missing_role',
        ),
        pytest.param(
            WILL_BE_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WILL_BE_AVAILABLE_DISABLE_REASONS,
            False,
            ['missing_role'],
            marks=[pytest.mark.now('2018-12-31T12:00:00+0300')],
            id='WillBeAvailable_missing_role',
        ),
        pytest.param(
            AVAILABLE_TILL_SUBTITLE_EXACT_TIMES,
            None,
            True,
            ['role'],
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
            id='AvailableTill_role',
        ),
        pytest.param(
            WAS_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WAS_AVAILABLE_DISABLE_REASONS,
            False,
            ['role'],
            marks=[pytest.mark.now('2019-01-12T12:00:00+0300')],
            id='WasAvailable_role',
        ),
        pytest.param(
            WILL_BE_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WILL_BE_AVAILABLE_DISABLE_REASONS,
            False,
            ['role'],
            marks=[pytest.mark.now('2018-12-31T12:00:00+0300')],
            id='WillBeAvailable_role',
        ),
        pytest.param(
            AVAILABLE_TILL_SUBTITLE_EXACT_TIMES,
            None,
            True,
            ['role', 'role'],
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
            id='AvailableTill_role_duplicate',
        ),
        pytest.param(
            WAS_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WAS_AVAILABLE_DISABLE_REASONS,
            False,
            ['role', 'role'],
            marks=[pytest.mark.now('2019-01-12T12:00:00+0300')],
            id='WasAvailable_role_duplicate',
        ),
        pytest.param(
            WILL_BE_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WILL_BE_AVAILABLE_DISABLE_REASONS,
            False,
            ['role', 'role'],
            marks=[pytest.mark.now('2018-12-31T12:00:00+0300')],
            id='WillBeAvailable_role_duplicate',
        ),
        pytest.param(
            AVAILABLE_TILL_SUBTITLE_EXACT_TIMES,
            None,
            True,
            ['role', 'missing_role'],
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
            id='AvailableTill_role_and_missing_role',
        ),
        pytest.param(
            WAS_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WAS_AVAILABLE_DISABLE_REASONS,
            False,
            ['role', 'missing_role'],
            marks=[pytest.mark.now('2019-01-12T12:00:00+0300')],
            id='WasAvailable_role_and_missing_role',
        ),
        pytest.param(
            WILL_BE_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WILL_BE_AVAILABLE_DISABLE_REASONS,
            False,
            ['role', 'missing_role'],
            marks=[pytest.mark.now('2018-12-31T12:00:00+0300')],
            id='WillBeAvailable_role_and_missing_role',
        ),
        pytest.param(
            AVAILABLE_TILL_SUBTITLE_EXACT_TIMES,
            None,
            True,
            ['role', 'role2'],
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
            id='AvailableTill_role_and_role2',
        ),
        pytest.param(
            WAS_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WAS_AVAILABLE_DISABLE_REASONS,
            False,
            ['role', 'role2'],
            marks=[pytest.mark.now('2019-01-12T12:00:00+0300')],
            id='WasAvailable_role_and_role2',
        ),
        pytest.param(
            WILL_BE_AVAILABLE_SUBTITLE_EXACT_TIMES,
            WILL_BE_AVAILABLE_DISABLE_REASONS,
            False,
            ['role', 'role2'],
            marks=[pytest.mark.now('2018-12-31T12:00:00+0300')],
            id='WillBeAvailable_role_and_role2',
        ),
    ],
)
async def test_offer_card(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        taxi_config,
        expected_subtitle_exact_times,
        expected_disable_reasons,
        expected_is_enabled,
        roles,
        rule_time_zone,
        client_time_zone,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.rules_select_value['time_zone'] = rule_time_zone

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        params=_get_params(client_time_zone),
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()

    _check_offers_count(roles, doc)

    expected_roles = {'role', 'role2'}

    time_zone = _get_time_zone(client_time_zone, rule_time_zone['id'])
    expected_subtitle_exact_time = expected_subtitle_exact_times[time_zone]
    expected_disable_reason = ''
    if expected_disable_reasons:
        expected_disable_reason = expected_disable_reasons[time_zone]

    for offer in doc['offers']:
        card = offer['offer_card']
        role_ending = _get_role_ending(card['title'], roles, expected_roles)

        assert card['title'] == 'За время' + role_ending
        assert card['subtitle'] == expected_subtitle_exact_time
        assert (
            card['description']
            == 'Заработок зависит от времени работы.' + role_ending
        )
        assert card['enabled'] == expected_is_enabled

        if expected_disable_reason:
            assert card['disable_reason'] == expected_disable_reason
        else:
            assert 'disable_reason' not in card


@pytest.mark.config(
    DRIVER_FIX_OFFER_DAYS_NEW=1,
    DRIVER_FIX_VIEW_OFFER_SETTINGS={
        'rules_select_limit': 10000,
        'days_backward': 3,
        'days_forward': 3,
    },
)
@use_role_config
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.parametrize(
    'expected_is_new',
    [
        pytest.param(
            True, marks=[pytest.mark.now('2018-12-31T12:00:00+0300')],
        ),
        pytest.param(
            True, marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
        ),
        pytest.param(
            False, marks=[pytest.mark.now('2019-01-02T12:00:00+0300')],
        ),
    ],
)
async def test_is_new(
        taxi_driver_fix,
        taxi_config,
        mock_offer_requirements,
        expected_is_new,
        roles,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc)

    for offer in doc['offers']:
        assert 'offer_card' in offer
        card = offer['offer_card']
        assert card['is_new'] == expected_is_new


@use_role_config
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.servicetest
async def test_offers_order(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        mock_offer_requirements,
        roles,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    # 1. all ended rules are sorted by descending of rule end;
    # 2. all started but not ended rules are sorted by ascending of rule end;
    # 3. all future rules sorted by ascending of rule begin;
    # 4. for unavailable rules all future rules are before all past rules.

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        rule1 = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
        rule1['start'] = '2018-12-28T00:00:00.000000+03:00'
        rule1['end'] = '2018-12-31T00:00:00.000000+03:00'
        rule1['subvention_rule_id'] = 'id_rule_past1'

        rule2 = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
        rule2['start'] = '2018-12-28T00:00:00.000000+03:00'
        rule2['end'] = '2018-12-30T00:00:00.000000+03:00'
        rule2['subvention_rule_id'] = 'id_rule_past2'

        rule3 = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
        rule3['start'] = '2018-01-31T00:00:00.000000+03:00'
        rule3['end'] = '2019-01-05T00:00:00.000000+03:00'
        rule3['subvention_rule_id'] = 'id_rule_present1'

        rule4 = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
        rule4['start'] = '2018-12-30T00:00:00.000000+03:00'
        rule4['end'] = '2019-01-07T00:00:00.000000+03:00'
        rule4['subvention_rule_id'] = 'id_rule_present2'

        rule5 = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
        rule5['start'] = '2019-01-03T00:00:00.000000+03:00'
        rule5['end'] = '2019-01-07T00:00:00.000000+03:00'
        rule5['subvention_rule_id'] = 'id_rule_future1'

        rule6 = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
        rule6['start'] = '2019-01-04T00:00:00.000000+03:00'
        rule6['end'] = '2019-01-05T00:00:00.000000+03:00'
        rule6['subvention_rule_id'] = 'id_rule_future2'

        return {'subventions': [rule4, rule6, rule1, rule2, rule3, rule5]}

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc, 6)
    order = [i['settings']['rule_id'] for i in doc['offers']]
    expected_order = [
        'id_rule_present1',
        'id_rule_present2',
        'id_rule_future1',
        'id_rule_future2',
        'id_rule_past1',
        'id_rule_past2',
    ]
    count = 1
    if roles:
        count = len({role for role in roles})

    order_it = 0
    for expected in expected_order:
        for _ in range(count):
            assert order[order_it] == expected
            order_it += 1


@pytest.mark.parametrize(
    'rule_time_zone',
    (
        {'id': 'Europe/Moscow', 'offset': '+03:00'},
        {'id': 'Asia/Vladivostok', 'offset': '+10:00'},
    ),
)
@pytest.mark.parametrize(
    'client_time_zone', (None, 'Europe/Moscow', 'Asia/Vladivostok'),
)
@use_role_config
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.parametrize(
    'expected_sct',
    [
        pytest.param(
            '01:00:00',
            marks=[
                pytest.mark.config(
                    DRIVER_FIX_DEFAULT_SHIFT_CLOSE_TIME='01:00:00',
                ),
            ],
        ),
        pytest.param(
            '20:30:00',
            marks=[
                pytest.mark.config(
                    DRIVER_FIX_DEFAULT_SHIFT_CLOSE_TIME='20:30:00',
                ),
            ],
        ),
    ],
)
@pytest.mark.servicetest
async def test_settings(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        mock_offer_requirements,
        expected_sct,
        roles,
        rule_time_zone,
        client_time_zone,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.rules_select_value['time_zone'] = rule_time_zone

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        params=_get_params(client_time_zone),
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc)

    time_zone_suffixes = {
        'Europe/Moscow': '+03:00',
        'Asia/Vladivostok': '+10:00',
    }
    time_zone_suffix = time_zone_suffixes[
        _get_time_zone(client_time_zone, rule_time_zone['id'])
    ]

    for offer in doc['offers']:
        assert offer['settings']['rule_id'] == 'subvention_rule_id'
        assert 'shift_close_time' in offer['settings']
        assert offer['settings']['shift_close_time'] == (
            expected_sct + time_zone_suffix
        )


DEFAULT_REF_CTORS = {
    'default': 'expected_offer_screen.json',
    'moscow': 'expected_offer_screen_moscow_in_vladivostok_tz.json',
    'vladivostok': 'expected_offer_screen_vladivostok_in_moscow_tz.json',
}
ROLE_REF_CTORS = {
    'default': 'expected_role_offer_screen.json',
    'moscow': 'expected_role_offer_screen_moscow_in_vladivostok_tz.json',
    'vladivostok': 'expected_role_offer_screen_vladivostok_in_moscow_tz.json',
}
ROLE2_REF_CTORS = {
    'default': 'expected_role2_offer_screen.json',
    'moscow': 'expected_role2_offer_screen_moscow_in_vladivostok_tz.json',
    'vladivostok': 'expected_role2_offer_screen_vladivostok_in_moscow_tz.json',
}


@pytest.mark.parametrize(
    'rule_time_zone',
    (
        pytest.param(
            {'id': 'Europe/Moscow', 'offset': '+03:00'},
            marks=[pytest.mark.now('2019-01-02T23:00:00+0300')],  # wednesday
        ),
        pytest.param(
            {'id': 'Asia/Vladivostok', 'offset': '+10:00'},
            marks=[pytest.mark.now('2019-01-02T23:00:00+1000')],  # wednesday
        ),
    ),
)
@pytest.mark.parametrize(
    'client_time_zone', (None, 'Europe/Moscow', 'Asia/Vladivostok'),
)
@use_role_config
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid', tags=common.TAGS_DEFAULT_VALUE,
)
@pytest.mark.match_tags(
    entity_type='dbid_uuid',
    entity_value='dbid_uuid',
    entity_tags=common.TAGS_DEFAULT_VALUE,
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.servicetest
async def test_offer_screen_common(
        taxi_driver_fix,
        mock_offer_requirements,
        driver_tags_mocks,
        load_json,
        taxi_config,
        roles,
        rule_time_zone,
        client_time_zone,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.rules_select_value['time_zone'] = rule_time_zone

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        params=_get_params(client_time_zone),
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    doc = mock_offer_requirements.rules_select_call_params[0]
    assert 'profile_tags' in doc
    assert sorted(doc['profile_tags']) == sorted(common.TAGS_DEFAULT_VALUE)
    assert 'tariff_zone' in doc
    assert doc['tariff_zone'] == common.NEARESTZONE_DEFAULT_VALUE
    assert 'types' in doc
    assert doc['types'] == ['driver_fix']

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc)

    time_zone = _get_time_zone(client_time_zone, rule_time_zone['id'])
    ctor_key = 'default'
    if time_zone != rule_time_zone['id']:
        if time_zone == 'Europe/Moscow':
            ctor_key = 'moscow'
        else:
            ctor_key = 'vladivostok'
    default_ref_ctor = load_json(DEFAULT_REF_CTORS[ctor_key])
    role_ref_ctor = load_json(ROLE_REF_CTORS[ctor_key])
    role2_ref_ctor = load_json(ROLE2_REF_CTORS[ctor_key])

    expected_roles = {'role', 'role2'}
    for offer in doc['offers']:
        test_ctor = offer['offer_screen']

        ref_ctor = default_ref_ctor
        subtitle = test_ctor['items'][0]['subtitle']
        role_ending = _get_role_ending(subtitle, roles, expected_roles)
        if role_ending == ' role':
            ref_ctor = role_ref_ctor
        elif role_ending == ' role2':
            ref_ctor = role2_ref_ctor

        assert test_ctor == ref_ctor

    assert driver_tags_mocks.has_calls()


@pytest.mark.parametrize(
    'rule_time_zone',
    (
        {'id': 'Europe/Moscow', 'offset': '+03:00'},
        {'id': 'Asia/Vladivostok', 'offset': '+10:00'},
    ),
)
@pytest.mark.parametrize(
    'client_time_zone', (None, 'Europe/Moscow', 'Asia/Vladivostok'),
)
@pytest.mark.now('2019-01-02T12:00:00+0300')
@pytest.mark.config(
    DRIVER_FIX_IMAGE_SETTINGS={
        'enabled': True,
        'memo_screen_image': {'enabled': True, 'image_url': 'memo_image.png'},
    },
)
@use_role_config
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.servicetest
async def test_memo_screen(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        mock_offer_requirements,
        load_json,
        roles,
        rule_time_zone,
        client_time_zone,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        params=_get_params(client_time_zone),
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc)

    default_ref_ctor = load_json('expected_memo_screen.json')
    role_ref_ctor = load_json('expected_role_memo_screen.json')
    role2_ref_ctor = load_json('expected_role2_memo_screen.json')

    expected_roles = {'role', 'role2'}
    for offer in doc['offers']:
        assert 'memo_screen' in offer
        test_ctor = offer['memo_screen']

        ref_ctor = default_ref_ctor
        subtitle = test_ctor['items'][0]['subtitle']
        role_ending = _get_role_ending(subtitle, roles, expected_roles)
        if role_ending == ' role':
            ref_ctor = role_ref_ctor
        elif role_ending == ' role2':
            ref_ctor = role2_ref_ctor

        assert test_ctor == ref_ctor


@use_role_config
@pytest.mark.now('2019-01-02T23:00:00+0300')
@pytest.mark.experiments3(filename='exp3_use_table_instead_chart.json')
async def test_tariffication_table(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        load_json,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(None),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200
    doc = response.json()

    expected_value = load_json('expected_tariffication_table.json')

    for offer in doc['offers']:
        ctor_items = offer['offer_screen']['items']
        charts = [item for item in ctor_items if item['type'] == 'selector']
        assert len(charts) == 1
        assert charts[0] == expected_value


@use_role_config
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    'fetch_payment_type_from_candidates',
    [
        pytest.param(
            True,
            id='candidates',
            marks=[
                pytest.mark.config(
                    DRIVER_FIX_FETCH_PAYMENT_TYPE_FROM='candidates',
                ),
            ],
        ),
        pytest.param(
            False,
            id='DPT',
            marks=[
                pytest.mark.config(
                    DRIVER_FIX_FETCH_PAYMENT_TYPE_FROM='driver-payment-types',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'profile_payment_type, bs_payment_type,'
    'expected_check_val, expected_is_enabled',
    [
        ('none', 'none', (True, 'Принимать любой способ оплаты'), True),
        ('none', 'online', (True, 'Принимать заказы по карте'), True),
        ('none', 'cash', (True, 'Принимать заказы с наличной оплатой'), True),
        ('none', 'any', None, True),
        ('online', 'none', (False, 'Принимать любой способ оплаты'), True),
        ('online', 'online', (True, 'Принимать заказы по карте'), True),
        (
            'online',
            'cash',
            (False, 'Принимать заказы с наличной оплатой'),
            True,
        ),
        ('online', 'any', None, True),
        ('cash', 'none', (False, 'Принимать любой способ оплаты'), True),
        ('cash', 'online', (False, 'Принимать заказы по карте'), True),
        ('cash', 'cash', (True, 'Принимать заказы с наличной оплатой'), True),
        ('cash', 'any', None, True),
    ],
)
async def test_payment_type(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        taxi_config,
        profile_payment_type,
        bs_payment_type,
        expected_check_val,
        expected_is_enabled,
        roles,
        fetch_payment_type_from_candidates,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    if fetch_payment_type_from_candidates:
        mock_offer_requirements.set_candidates_payment_type(
            profile_payment_type,
        )
    else:
        payment_types = mock_offer_requirements.payment_types_values[0][
            'payment_types'
        ]
        for payment_type in payment_types:
            payment_type['active'] = (
                payment_type['payment_type'] == profile_payment_type
            )

    mock_offer_requirements.rules_select_value[
        'profile_payment_type_restrictions'
    ] = bs_payment_type

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc)

    expected_roles = {'role', 'role2'}
    for offer in doc['offers']:
        ctor = offer['offer_screen']

        check_val = common.extract_check_value(ctor, 'Принимать')

        expected = expected_check_val
        if check_val:
            expected = (
                expected[0],
                expected[1]
                + _get_role_ending(check_val[1], roles, expected_roles),
            )

        assert check_val == expected

        is_enabled = offer['offer_card']['enabled']
        assert is_enabled == expected_is_enabled


@use_role_config
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    'driver_classes, billing_classes, expected_check_val, expected_is_enabled',
    [
        ([], ['econom'], (False, 'Включите класс Эконом'), True),
        (
            ['econom', 'business'],
            ['econom'],
            (True, 'Включите класс Эконом'),
            True,
        ),
        (
            ['econom', 'business'],
            ['econom'],
            (True, 'Включите класс Эконом'),
            True,
        ),
        (
            ['econom'],
            ['econom', 'business'],
            (False, 'Включите классы Эконом, Комфорт'),
            True,
        ),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
async def test_classes(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        taxi_config,
        driver_classes,
        billing_classes,
        expected_check_val,
        expected_is_enabled,
        roles,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    mock_offer_requirements.profiles_value['classes'] = driver_classes
    mock_offer_requirements.rules_select_value[
        'profile_tariff_classes'
    ] = billing_classes

    driver_profile_id = 'uuid'
    park_id = 'dbid'
    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    doc = response.json()
    _check_offers_count(roles, doc)
    expected_roles = {'role', 'role2'}
    for offer in doc['offers']:
        ctor = offer['offer_screen']
        check_val = common.extract_check_value(ctor, 'Включите класс')

        expected = expected_check_val
        if check_val:
            expected = (
                expected[0],
                expected[1]
                + _get_role_ending(check_val[1], roles, expected_roles),
            )

        assert check_val == expected

        is_enabled = offer['offer_card']['enabled']
        assert is_enabled == expected_is_enabled

    candidates_req = json.loads(
        mock_offer_requirements.profiles.next_call()['request'].get_data(),
    )
    assert candidates_req['driver_ids'] == [
        {'dbid': park_id, 'uuid': driver_profile_id},
    ]


@pytest.mark.parametrize('tariff_zone_from_geoareas', (None, True, False))
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
@use_role_config
async def test_use_taximeter_coordinate_as_fallback(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        roles,
        tariff_zone_from_geoareas,
):
    if tariff_zone_from_geoareas is not None:
        taxi_config.set_values(
            dict(
                DRIVER_FIX_FETCH_TARIFF_ZONE_FROM_GEOAREAS=(
                    tariff_zone_from_geoareas
                ),
            ),
        )

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    mock_offer_requirements.set_position_fallback([37.5, 55.7])

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        doc = request.json
        assert doc['point'] == [37.5, 55.7]
        return {'nearest_zone': 'moscow'}

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        params={'lon': 37.5, 'lat': 55.7},
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('tariff_zone_from_geoareas', (None, True, False))
async def test_no_taximeter_fallback_no_tariff_zone(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        tariff_zone_from_geoareas,
):
    if tariff_zone_from_geoareas is not None:
        taxi_config.set_values(
            dict(
                DRIVER_FIX_FETCH_TARIFF_ZONE_FROM_GEOAREAS=(
                    tariff_zone_from_geoareas
                ),
            ),
        )

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    mock_offer_requirements.set_position_fallback([22.88, 14.88])

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        doc = request.json
        assert 'point' in doc
        assert doc['point'] == [22.88, 14.88]
        return mockserver.make_response(
            json={'error': {'message': 'No zone found'}}, status=404,
        )

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(None),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'candidates_response',
    [
        pytest.param(
            {
                'drivers': [
                    {
                        'classes': ['econom', 'business'],
                        'dbid': '7ad36bc7560449998acbe2c57a75c293',
                        'position': [0, 0],  # bad coordinate
                        'uuid': 'c5673ab7870c45b3adc42fec699a252c',
                    },
                ],
            },
            id='bad coordinate',
        ),
        pytest.param({'drivers': []}, id='no_driver'),
    ],
)
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
async def test_driver_not_found(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        candidates_response,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    @mockserver.json_handler('/candidates/profiles')
    def _candidates(request):
        return candidates_response

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 404


@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
@use_role_config
@pytest.mark.parametrize(
    'driver_position, expected_check_val',
    [
        ([37.63361316, 55.75419758], (True, 'Находиться в городе Москва')),
        ([37.60418263, 55.75293071], (True, 'Находиться в городе Москва')),
        ([30.00000000, 50.00000000], (False, 'Находиться в городе Москва')),
        (
            [37.64899583, 55.76904453],  # close to but outside zone
            (False, 'Находиться в городе Москва'),
        ),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
async def test_driver_position(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        driver_position,
        expected_check_val,
        roles,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = driver_position

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc)
    expected_roles = {'role', 'role2'}
    for offer in doc['offers']:
        ctor = offer['offer_screen']
        check_val = common.extract_check_value(ctor, 'Находиться в')
        expected = expected_check_val
        if check_val:
            expected = (
                expected[0],
                expected[1]
                + _get_role_ending(check_val[1], roles, expected_roles),
            )

        assert check_val == expected


@pytest.mark.parametrize('tariff_zone_from_geoareas', (None, True, False))
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
@use_role_config
@pytest.mark.parametrize(
    'current_rule_id,expected_response_rule_ids,expected_bs_times_called',
    [
        ('id_rule_msk', ['id_rule_tver', 'id_rule_msk'], 2),
        ('id_rule_tver', ['id_rule_tver'], 1),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
async def test_current_mode_when_driver_is_outside_tariff_zone(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        current_rule_id,
        expected_response_rule_ids,
        expected_bs_times_called,
        roles,
        tariff_zone_from_geoareas,
):
    if tariff_zone_from_geoareas is not None:
        taxi_config.set_values(
            dict(
                DRIVER_FIX_FETCH_TARIFF_ZONE_FROM_GEOAREAS=(
                    tariff_zone_from_geoareas
                ),
            ),
        )

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = [47.5, 65.7]

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        return {'nearest_zone': 'tver'}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        doc = request.json
        if 'cursor' in doc and doc['cursor'] == 'end':
            return {'subventions': []}
        if 'rule_ids' in doc:
            assert len(doc['rule_ids']) == 1
            assert doc['rule_ids'][0] == 'id_rule_msk'
            rule = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
            rule['tariff_zone'] = 'msk'
            rule['subvention_rule_id'] = 'id_rule_msk'
            rule['cursor'] = 'end'
            return {'subventions': [rule]}
        if 'tariff_zone' in doc:
            assert doc['tariff_zone'] == 'tver'
            rule = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
            rule['tariff_zone'] = 'tver'
            rule['subvention_rule_id'] = 'id_rule_tver'
            return {'subventions': [rule]}
        return {'subventions': []}

    body = _get_body_with_roles(roles)
    body['current_mode_settings'] = {
        'rule_id': current_rule_id,
        'shift_close_time': '00:00:00+03:00',
    }
    response = await taxi_driver_fix.post(
        '/v1/view/offer', json=body, headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc, len(expected_response_rule_ids))
    ctor = doc['offers']
    count = 1
    if roles:
        count = len({role for role in roles})

    ctor_it = 0
    for expected_id in expected_response_rule_ids:
        for _ in range(count):
            assert ctor[ctor_it]['settings']['rule_id'] == expected_id
            ctor_it += 1

    assert _bs.times_called == expected_bs_times_called


@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
@use_role_config
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid', tags=common.TAGS_DEFAULT_VALUE,
)
@pytest.mark.match_tags(
    entity_type='dbid_uuid',
    entity_value='dbid_uuid',
    entity_tags=common.TAGS_DEFAULT_VALUE,
)
@pytest.mark.now('2019-01-02T12:00:00+0300')  # wednesday
@pytest.mark.servicetest
async def test_show_description_button(
        taxi_driver_fix, mock_offer_requirements, taxi_config, roles,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    _check_offers_count(roles, doc)

    expected_roles = {'role', 'role2'}
    for offer in doc['offers']:
        fix_offer_screen_items = offer['offer_screen']['items']
        assert fix_offer_screen_items[-1]['type'] == 'detail'

        title = fix_offer_screen_items[-1]['title']
        expected_title = 'Полное описание' + _get_role_ending(
            title, roles, expected_roles,
        )

        assert title == expected_title


@pytest.mark.parametrize('tariff_zone_from_geoareas', (None, True, False))
@pytest.mark.parametrize('roles', (None, ['role'], ['role', 'role2']))
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
@use_role_config
@pytest.mark.parametrize('has_current_mode', (True, False))
async def test_handling_of_404_from_nearest_zone(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        has_current_mode,
        roles,
        tariff_zone_from_geoareas,
):
    if tariff_zone_from_geoareas is not None:
        taxi_config.set_values(
            dict(
                DRIVER_FIX_FETCH_TARIFF_ZONE_FROM_GEOAREAS=(
                    tariff_zone_from_geoareas
                ),
            ),
        )

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    mock_offer_requirements.set_position_fallback([22.88, 14.88])

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        return mockserver.make_response(
            json={'error': {'message': 'No zone found'}}, status=404,
        )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        doc = request.json
        if 'rule_ids' not in doc and 'tariff_zone' in doc:
            assert (
                doc['tariff_zone'] is not None
            ), 'rules/select requested with empty tariff zone'
        if 'rule_ids' in doc and 'tariff_zone' not in doc:
            assert len(doc['rule_ids']) == 1
            assert doc['rule_ids'][0] == 'id_rule_msk'
            rule = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
            rule['tariff_zone'] = 'msk'
            rule['subvention_rule_id'] = 'id_rule_msk'
            rule['cursor'] = 'end'
            return {'subventions': [rule]}
        return {'subventions': []}

    request_json = _get_body_with_roles(roles)
    if has_current_mode:
        request_json['current_mode_settings'] = {
            'rule_id': 'id_rule_msk',
            'shift_close_time': '00:00:00+03:00',
        }

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        params={'lon': 22.88, 'lat': 14.88},
        json=request_json,
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()
    if not has_current_mode:
        assert not doc['offers']
    else:
        _check_offers_count(roles, doc)
        for offer in doc['offers']:
            assert offer['settings']['rule_id'] == 'id_rule_msk'
        assert _bs.times_called == 1


@pytest.mark.parametrize('match_roles_for_tags', (True, False))
@pytest.mark.parametrize('use_roles_as_tags', (True, False))
@pytest.mark.parametrize(
    'roles, expected_rule_id',
    [
        (['car', 'car_other'], '_id/1'),
        (['pedestrian', 'pedestrian_other'], '_id/2'),
        (['some_other_role'], None),
        (None, None),
    ],
)
@pytest.mark.parametrize('current_rule_id', [None, '_id/1', '_id/2'])
@pytest.mark.now('2020-01-01T12:00:00+0300')
async def test_match_roles_for_offers(
        taxi_driver_fix,
        mock_offer_requirements,
        mockserver,
        roles,
        expected_rule_id,
        current_rule_id,
        match_roles_for_tags,
        taxi_config,
        use_roles_as_tags,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    taxi_config.set_values(
        dict(
            DRIVER_FIX_OFFER_USE_ROLES_AS_TAGS=use_roles_as_tags,
            DRIVER_FIX_MATCH_ROLES_FOR_OFFERS={
                'driver_fix': match_roles_for_tags,
                'geo_booking': False,
            },
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        def _create_rule(rule_id, tag):
            rule = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
            rule['subvention_rule_id'] = rule_id
            rule['tags'] = [tag]
            return rule

        return {
            'subventions': [
                _create_rule('_id/1', 'car'),
                _create_rule('_id/2', 'pedestrian'),
                _create_rule('_id/3', 'smth_else'),
            ],
        }

    roles_settings = [{'name': role} for role in roles] if roles else []
    body = {'driver_profile_id': 'uuid', 'park_id': 'dbid'}
    if roles_settings:
        body['roles'] = roles_settings

    if current_rule_id is not None:
        body['current_mode_settings'] = {
            'rule_id': current_rule_id,
            'shift_close_time': '00:00:00+03:00',
        }

    response = await taxi_driver_fix.post(
        '/v1/view/offer', json=body, headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    expected_rules = []
    if expected_rule_id is not None:
        expected_rules.append(expected_rule_id)
    if current_rule_id is not None and current_rule_id != expected_rule_id:
        expected_rules.append(current_rule_id)
    if not match_roles_for_tags or not use_roles_as_tags:
        roles_length = len(roles) if roles else 1
        expected_rules = ['_id/1', '_id/2', '_id/3'] * roles_length

    offers = response.json()['offers']
    got_rules = [offer['settings']['rule_id'] for offer in offers]

    assert sorted(expected_rules) == sorted(got_rules)


@pytest.mark.parametrize('use_roles', (True, False))
@pytest.mark.parametrize('roles', (['role1', 'role2'], None))
@pytest.mark.driver_tags_match(
    dbid='dbid', uuid='uuid', tags=common.TAGS_DEFAULT_VALUE,
)
async def test_use_roles(
        taxi_driver_fix,
        mock_offer_requirements,
        mockserver,
        taxi_config,
        use_roles,
        roles,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    taxi_config.set(DRIVER_FIX_OFFER_USE_ROLES_AS_TAGS=use_roles)

    roles = [{'name': role} for role in roles] if roles else []

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        if not roles and use_roles:
            assert 'profile_tags' not in request.json
            return {'subventions': []}

        tags = request.json['profile_tags']
        if use_roles:
            assert tags == [role['name'] for role in roles]
        else:
            assert tags == common.TAGS_DEFAULT_VALUE
        return {'subventions': []}

    body = {'driver_profile_id': 'uuid', 'park_id': 'dbid'}
    if roles:
        body['roles'] = roles

    response = await taxi_driver_fix.post(
        '/v1/view/offer', json=body, headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200


async def _setup_and_perform_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        restriction_name,
        violate_if,
        apply_if,
        driver_tags,
        show_in_offer_screen,
        use_ttl=None,
        driver_tags_info=None,
        apply_always_when_role=None,
        roles=None,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    driver_tags_mocks.set_tags_info(
        'dbid',
        'uuid',
        tags=list(driver_tags) if driver_tags_info is None else None,
        tags_info=driver_tags_info,
    )

    taxi_config.set(
        DRIVER_FIX_CONSTRAINTS_ON_TAGS=(
            common.build_constraint_on_tags_config(
                restriction_name,
                violate_if=violate_if,
                apply_if=apply_if,
                show_in_offer_screen=show_in_offer_screen,
                use_ttl=use_ttl,
                apply_always_when_role=apply_always_when_role,
            )
        ),
    )

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    return response


@use_role_config
@pytest.mark.parametrize('show_in_offer_screen', [None, False, True])
@pytest.mark.parametrize(
    'driver_tags', [{'violate_tag'}, {'apply_tag', 'vioate_tag'}],
)
@pytest.mark.parametrize('apply_if', [None, {'apply_tag'}, set()])
@pytest.mark.parametrize(
    'apply_always_when_role', [None, 'role1', ['role3', 'role2', 'role1'], []],
)
@pytest.mark.parametrize('violate_if', [{'violate_tag'}, set()])
@pytest.mark.now('2019-01-01T12:00:00+0300')
async def test_restriction_on_tags(
        taxi_driver_fix,
        driver_tags_mocks,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        violate_if,
        apply_always_when_role,
        apply_if,
        driver_tags,
        show_in_offer_screen,
):
    driver_role = 'role1'

    response = await _setup_and_perform_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        restriction_name='test_restriction_on_tags',
        taxi_config=taxi_config,
        violate_if=list(violate_if),
        apply_if=list(apply_if) if apply_if else None,
        driver_tags=driver_tags,
        show_in_offer_screen=show_in_offer_screen,
        apply_always_when_role=apply_always_when_role,
        roles=[driver_role],
    )

    should_be_applied_by_tag = apply_if is None or apply_if.issubset(
        driver_tags,
    )
    should_be_applied_by_role = (
        apply_always_when_role and driver_role in apply_always_when_role
    )
    should_be_violated = violate_if.issubset(driver_tags)

    for offer in response.json()['offers']:
        ctor = offer['offer_screen']
        check_val = common.extract_check_value(
            ctor, 'test_restriction_on_tags_title',
        )

        if not show_in_offer_screen or (
                not should_be_applied_by_tag and not should_be_applied_by_role
        ):
            assert check_val is None
        else:
            is_checked, _ = check_val
            assert is_checked == (not should_be_violated)


@use_role_config
@pytest.mark.parametrize(
    'now,tags_info,expected_title,expected_is_checked',
    [
        ('2019-01-01T12:00:00', {}, 'Вы заблокированы (без TTL)', True),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-01T13:23:15+0000'}},
            'Вы заблокированы до 16:23, осталось 1:23',
            False,
        ),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-01T13:00:15+0000'}},
            'Вы заблокированы до 16:00, осталось 1',
            False,
        ),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-03T13:11:15+0000'}},
            'Вы заблокированы до 3 января 16:11, осталось 49:11',
            False,
        ),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-01T10:00:00+0000'}},
            'Вы заблокированы (без TTL)',
            False,
        ),
    ],
)
@pytest.mark.config(DRIVER_FIX_FETCH_TAGS_WITH_TTL=True)
async def test_restriction_on_tags_with_ttl(
        taxi_driver_fix,
        driver_tags_mocks,
        mockserver,
        mocked_time,
        mock_offer_requirements,
        taxi_config,
        now,
        tags_info,
        expected_title,
        expected_is_checked,
):
    mocked_time.set(datetime.datetime.fromisoformat(now))

    response = await _setup_and_perform_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        restriction_name='test_ttl_restriction',
        violate_if=['violate_tag'],
        apply_if=None,
        driver_tags=set(tags_info.keys()),
        show_in_offer_screen=True,
        use_ttl=True,
        driver_tags_info=tags_info,
    )

    offers = response.json()['offers']
    assert offers != []

    for offer in offers:
        is_checked, title = common.extract_check_value(
            offer['offer_screen'], 'Вы заблокированы',
        )
        assert is_checked == expected_is_checked
        assert title == expected_title


@use_role_config
@pytest.mark.parametrize(
    'driver_tags,apply_if,violate_if,expected_check_val',
    [
        (
            # driver_tags
            {'a', 'b', 'c'},
            # apply_if
            None,
            # violate_if
            {'any_of': ['a', 'e']},
            # expected_check_val
            False,
        ),
        (
            # driver_tags
            {'a', 'b', 'c'},
            # apply_if
            None,
            # violate_if
            {'any_of': ['d', 'e']},
            # expected_check_val
            True,
        ),
        (
            # driver_tags
            {'a', 'b', 'c'},
            # apply_if
            None,
            # violate_if
            {'and': [{'any_of': ['a', 'e']}, {'all_of': ['b', 'c']}]},
            # expected_check_val
            False,
        ),
        (
            # driver_tags
            {'a', 'b', 'c'},
            # apply_if
            {'all_of': ['e']},
            # violate_if
            {'any_of': ['a']},
            # expected_check_val
            None,
        ),
        (
            # driver_tags
            {'a', 'b', 'c'},
            # apply_if
            {'any_of': ['a']},
            # violate_if
            {'any_of': ['a']},
            # expected_check_val
            False,
        ),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
async def test_restriction_on_tags_using_formula(
        taxi_driver_fix,
        driver_tags_mocks,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        violate_if,
        apply_if,
        driver_tags,
        expected_check_val,
):
    response = await _setup_and_perform_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        restriction_name='test_restriction_on_tags',
        violate_if=violate_if,
        apply_if=apply_if,
        driver_tags=driver_tags,
        show_in_offer_screen=True,
    )

    offers = response.json()['offers']
    assert offers != []

    for offer in offers:
        ctor = offer['offer_screen']
        check_val = common.extract_check_value(
            ctor, 'test_restriction_on_tags_title',
        )
        if expected_check_val is None:
            assert check_val is None
            continue

        is_checked, _ = check_val
        assert is_checked is expected_check_val


@use_role_config
@pytest.mark.parametrize(
    'driver_tags_info,violate_if,expected_text',
    [
        (
            # driver_tags
            {
                'a': {'ttl': '2019-01-01T13:23:15+0000'},
                'b': {'ttl': '2019-01-01T14:01:00+0000'},
                'c': {},
            },
            # violate_if
            {'any_of': ['b', 'e']},
            # expected_text
            'Вы заблокированы до 17:01, осталось 2:1',
        ),
        (
            # driver_tags
            {
                'a': {'ttl': '2019-01-01T13:23:15+0000'},
                'b': {'ttl': '2019-01-01T14:01:00+0000'},
                'c': {},
            },
            # violate_if
            {'any_of': ['a', 'b']},
            # expected_text
            'Вы заблокированы до 17:01, осталось 2:1',
        ),
        (
            # driver_tags
            {
                'a': {'ttl': '2019-01-01T13:23:15+0000'},
                'b': {'ttl': '2019-01-01T14:00:00+0000'},
                'c': {},
            },
            # violate_if
            {'all_of': ['a', 'b']},
            # expected_text
            'Вы заблокированы до 16:23, осталось 1:23',
        ),
        (
            # driver_tags
            {
                'a': {'ttl': '2019-01-01T13:23:15+0000'},
                'b': {'ttl': '2019-01-01T14:00:00+0000'},
                'c': {},
            },
            # violate_if
            {'and': [{'any_of': ['c']}, {'all_of': ['a', 'b']}]},
            # expected_text
            'Вы заблокированы до 16:23, осталось 1:23',
        ),
        (
            # driver_tags
            {
                'a': {'ttl': '2019-01-01T13:23:15+0000'},
                'b': {'ttl': '2019-01-01T14:00:00+0000'},
                'c': {},
            },
            # violate_if
            {'or': [{'any_of': ['c']}, {'all_of': ['a', 'b']}]},
            # expected_text
            'Вы заблокированы (без TTL)',
        ),
        (
            # driver_tags
            {
                'a': {'ttl': '2019-01-01T13:23:15+0000'},
                'b': {'ttl': '2019-01-01T14:00:00+0000'},
                'c': {},
            },
            # violate_if
            {'or': [{'all_of': ['b', 'e']}, {'all_of': ['a']}]},
            # expected_text
            'Вы заблокированы до 16:23, осталось 1:23',
        ),
        (
            # driver_tags
            {
                'a': {'ttl': '2019-01-01T13:23:15+0000'},
                'b': {'ttl': '2019-01-01T14:00:00+0000'},
                'c': {},
            },
            # violate_if
            {'all_of': ['b', 'e']},
            # expected_text
            'Вы заблокированы (без TTL)',
        ),
    ],
)
@pytest.mark.config(DRIVER_FIX_FETCH_TAGS_WITH_TTL=True)
@pytest.mark.now('2019-01-01T12:00:00')
async def test_restriction_on_tags_with_ttl_using_formula(
        taxi_driver_fix,
        driver_tags_mocks,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        driver_tags_info,
        violate_if,
        expected_text,
):
    response = await _setup_and_perform_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        restriction_name='test_ttl_restriction',
        violate_if=violate_if,
        apply_if=None,
        driver_tags=None,
        show_in_offer_screen=True,
        use_ttl=True,
        driver_tags_info=driver_tags_info,
    )

    offers = response.json()['offers']
    assert offers != []

    for offer in offers:
        ctor = offer['offer_screen']
        _, text = common.extract_check_value(ctor, 'Вы заблокированы')
        assert text == expected_text


def _generate_do_x_get_y_rule(
        group_id=None, trips_bounds=None, week_days=None,
):
    prototype = {
        'budget': {
            'daily': None,
            'id': '86a43cca-0bcf-44b8-92d9-f10a9919e0ed',
            'rolling': None,
            'threshold': 100,
            'weekly': '1',
        },
        'currency': 'RUB',
        'cursor': 'mock_cursor',
        'days_span': 1,
        'end': '2020-06-01T00:00:00.000000+00:00',
        'geoareas': [],
        'group_id': '3d8eb989-b2d5-487a-b86a-6ee7eabc8c15',
        'has_commission': False,
        'hours': [12],
        'is_personal': False,
        'log': [],
        'order_payment_type': None,
        'payment_type': 'add',
        'start': '2018-06-01T00:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/5ecd3298a11531e403edc21f',
        'tags': [],
        'tariff_classes': [],
        'tariff_zones': ['moscow'],
        'taxirate': 'taxirate-01',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'trips_bounds': [],
        'type': 'add',
        'updated': '2018-06-01T00:00:00.000000+00:00',
        'visible_to_driver': True,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }

    rule = copy.deepcopy(prototype)
    if group_id is not None:
        rule['group_id'] = group_id
    if trips_bounds is not None:
        rule['trips_bounds'] = trips_bounds
    if week_days is not None:
        rule['week_days'] = week_days

    return rule


def _generate_goal_smart_rule(schedule, steps):
    prototype = {
        'activity_points': 50,
        'budget_id': '11111111-4c8d-4cda-aa9a-2939e5e79ef8',
        'counters': {'schedule': [], 'steps': []},
        'currency': 'RUB',
        'draft_id': '22222222-4c8d-4cda-aa9a-2939e5e79ef8',
        'end': '2021-01-26T21:00:00+00:00',
        # flake8: noqa E501
        'geonode': 'br_root/br_russia/br_tsentralnyj_fo/br_moskovskaja_obl/br_moscow/br_moscow_adm',
        'global_counters': [
            {'global': 'global_counter1', 'local': 'some_local_counter'},
        ],
        'id': '2f1377bb-4c8d-4cda-aa9a-2939e5e79ef8',
        'rule_type': 'goal',
        'schedule_ref': '22222222-4c8d-4cda-aa9a-2939e5e79ef8',
        'start': '2018-06-01T21:00:00+00:00',
        'tariff_class': 'econom',
        'updated_at': '2018-06-01T21:00:00+00:00',
        'window': 30,
    }

    rule = copy.deepcopy(prototype)
    if schedule is not None:
        rule['counters']['schedule'] = schedule
    if steps is not None:
        rule['counters']['steps'] = steps
    return rule


def _generate_driver_fix_rule(rates=None):
    prototype = common.DEFAULT_DRIVER_FIX_RULE
    rule = copy.deepcopy(prototype)
    if rates is not None:
        rule['rates'] = rates
    return rule


@pytest.mark.config(
    DRIVER_FIX_OFFER_SCREENS_BY_ROLE_V2={
        '__default__': {
            'offer_card': {
                'title': 'role_offer_card.title',
                'description': 'role_offer_card.description',
            },
            'offer_screen': [{'type': 'goals_info', 'markdown': True}],
            'memo_screen': [],
        },
    },
)
@pytest.mark.now('2019-01-01T12:00:00+0300')  # tuesday
@pytest.mark.parametrize(
    'mean_orders_per_hour,hours,days,pseudo_comission_coef,'
    'expected_goal_info_text',
    [
        (
            2.5,
            10,
            1,
            None,
            'Например, если вы проведете на линии 10 часов, '
            'то можете получить до 1000 ₽.',
        ),
        (
            2.5,
            8,
            2,
            None,
            'Например, если вы будете проводить на линии 8 часов '
            'каждый день в течение 2 дней, то можете получить 1360 ₽.',
        ),
        (
            3,
            10,
            6,
            None,
            'Например, если вы будете проводить на линии 10 часов '
            'каждый день в течение 6 дней, то можете получить 4440 ₽.',
        ),
        (
            2.5,
            10,
            1,
            1.051,
            'Например, если вы проведете на линии 10 часов, '
            'то можете получить до 1048 ₽.',
        ),
    ],
)
async def test_goals_info_text(
        taxi_driver_fix,
        driver_tags_mocks,
        mockserver,
        mock_offer_requirements,
        mock_driver_mode_index,
        taxi_config,
        mean_orders_per_hour,
        hours,
        days,
        pseudo_comission_coef,
        expected_goal_info_text,
):
    """
    Checks that:
    * goal text on offer screen is right
    * request to billing-subventions/rules/select tag from config
    """

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_driver_mode_index.set_virtual_tags(['mock_virtual_tag'])
    mock_offer_requirements.rules_select_value_by_type = {
        'driver_fix': [
            _generate_driver_fix_rule(
                rates=[
                    {
                        'week_day': 'tue',
                        'start': '00:00',
                        'rate_per_minute': '1.0',
                    },
                    {
                        'week_day': 'tue',
                        'start': '12:00',
                        'rate_per_minute': '2.0',
                    },
                    {
                        'week_day': 'tue',
                        'start': '18:00',
                        'rate_per_minute': '1.0',
                    },
                ],
            ),
        ],
        'goal': [
            _generate_do_x_get_y_rule(
                group_id='mock_group_id1',
                trips_bounds=[
                    {
                        'bonus_amount': '40.0',
                        'lower_bound': 20,
                        'upper_bound': 29,
                    },
                ],
                week_days=['tue'],
            ),
            _generate_do_x_get_y_rule(
                group_id='mock_group_id1',
                trips_bounds=[{'bonus_amount': '80.0', 'lower_bound': 30}],
            ),
        ],
    }

    tag_for_subvention = 'mock_tag_for_subvention'

    taxi_config.set_values(
        {
            'DRIVER_FIX_OFFER_GOALS_INFO_SETTINGS': {
                'constants': {'mean_orders_per_hour': mean_orders_per_hour},
                'by_role': {
                    'role1': {
                        'days': days,
                        'hours': hours,
                        'tag_for_subvention': tag_for_subvention,
                    },
                },
            },
        },
    )

    if pseudo_comission_coef is not None:
        taxi_config.set_values(
            {
                'DRIVER_FIX_PSEUDO_COMMISSION': [
                    {
                        'role': 'role1',
                        'tag': 'tag1',
                        'coefficient': pseudo_comission_coef,
                    },
                ],
            },
        )

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(['role1']),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    rs_reqv_checked = False
    for rs_reqv in mock_offer_requirements.rules_select_call_params:
        if 'goal' in rs_reqv['types']:
            assert set(rs_reqv['profile_tags']) == {tag_for_subvention}
            rs_reqv_checked = True
    assert rs_reqv_checked

    offers = response.json()['offers']
    assert offers != []

    for offer in offers:
        items = offer['offer_screen']['items']
        assert items[0]['text'] == expected_goal_info_text
        assert items[0]['markdown'] is True


def _extract_goal_bar(ctor, after_idx):
    separator_item = {'type': 'title'}
    items = ctor['items']

    titles = []
    for i in range(after_idx + 1, len(items)):
        if items[i] == separator_item:
            break
        titles.append(items[i]['title'])

    return titles


@pytest.mark.config(
    DRIVER_FIX_OFFER_SCREENS_BY_ROLE_V2={
        '__default__': {
            'offer_card': {
                'title': 'role_offer_card.title',
                'description': 'role_offer_card.description',
            },
            'offer_screen': [{'type': 'do_x_get_y_table'}],
            'memo_screen': [],
        },
    },
)
@pytest.mark.now('2019-01-02T12:00:00+0300')  # wednesday
@pytest.mark.parametrize(
    'do_x_get_y_rules,goal_smart_rules,expected_goal_bar',
    [
        (
            # do_x_get_y_rules
            [],
            # goal_smart_rules
            None,
            # expected_goal_bar
            None,
        ),
        (
            # do_x_get_y_rules
            [],
            # goal_smart_rules
            [],
            # expected_goal_bar
            None,
        ),
        (
            # do_x_get_y_rules
            [
                _generate_do_x_get_y_rule(
                    trips_bounds=[
                        {
                            'bonus_amount': '40.0',
                            'lower_bound': 10,
                            'upper_bound': 19,
                        },
                        {'bonus_amount': '80.0', 'lower_bound': 20},
                    ],
                ),
            ],
            # goal_smart_rules
            None,
            # expected_goal_bar
            ['10 заказов — 40 ₽', '20 заказов — 80 ₽'],
        ),
        (
            # do_x_get_y_rules
            [],
            # goal_smart_rules
            [
                _generate_goal_smart_rule(
                    schedule=[
                        {
                            'counter': 'counter1',
                            'start': '00:00',
                            'week_day': 'wed',
                        },
                        {'counter': '0', 'start': '21:00', 'week_day': 'wed'},
                    ],
                    steps=[
                        {
                            'id': 'counter1',
                            'steps': [
                                {'nrides': 10, 'amount': '40'},
                                {'nrides': 20, 'amount': '80'},
                            ],
                        },
                    ],
                ),
            ],
            # expected_goal_bar
            ['10 заказов — 40 ₽', '20 заказов — 80 ₽'],
        ),
        (
            # do_x_get_y_rules
            [
                _generate_do_x_get_y_rule(
                    trips_bounds=[
                        {
                            'bonus_amount': '40.0',
                            'lower_bound': 10,
                            'upper_bound': 19,
                        },
                        {'bonus_amount': '80.0', 'lower_bound': 20},
                    ],
                    week_days=['wed'],
                ),
                _generate_do_x_get_y_rule(
                    trips_bounds=[
                        {
                            'bonus_amount': '100.0',
                            'lower_bound': 1,
                            'upper_bound': 1,
                        },
                        {
                            'bonus_amount': '200.0',
                            'lower_bound': 2,
                            'upper_bound': 6,
                        },
                        {'bonus_amount': '300.0', 'lower_bound': 7},
                    ],
                    week_days=['wed'],
                ),
            ],
            # goal_smart_rules
            None,
            # expected_goal_bar
            [
                '1 заказ — 100 ₽',
                '2 заказа — 200 ₽',
                '7 заказов — 300 ₽',
                '10 заказов — 340 ₽',
                '20 заказов — 380 ₽',
            ],
        ),
        (
            # do_x_get_y_rules
            [],
            # goal_smart_rules
            [
                _generate_goal_smart_rule(
                    schedule=[
                        {
                            'counter': 'counter1',
                            'start': '21:00',
                            'week_day': 'fri',
                        },
                    ],
                    steps=[
                        {
                            'id': 'counter1',
                            'steps': [
                                {'nrides': 1, 'amount': '100'},
                                {'nrides': 2, 'amount': '200'},
                            ],
                        },
                    ],
                ),
            ],
            # expected_goal_bar
            ['1 заказ — 100 ₽', '2 заказа — 200 ₽'],
        ),
        (
            # do_x_get_y_rules
            [],
            # goal_smart_rules
            [
                _generate_goal_smart_rule(
                    schedule=[
                        {
                            'counter': 'counter1',
                            'start': '21:00',
                            'week_day': 'mon',
                        },
                    ],
                    steps=[
                        {
                            'id': 'counter1',
                            'steps': [
                                {'nrides': 1, 'amount': '100'},
                                {'nrides': 2, 'amount': '200'},
                            ],
                        },
                    ],
                ),
            ],
            # expected_goal_bar
            ['1 заказ — 100 ₽', '2 заказа — 200 ₽'],
        ),
        (
            # do_x_get_y_rules
            [],
            # goal_smart_rules
            [
                _generate_goal_smart_rule(
                    schedule=[
                        {
                            'counter': 'counter1',
                            'start': '21:00',
                            'week_day': 'sat',
                        },
                        {'counter': '0', 'start': '22:00', 'week_day': 'sat'},
                    ],
                    steps=[
                        {
                            'id': 'counter1',
                            'steps': [
                                {'nrides': 1, 'amount': '100'},
                                {'nrides': 2, 'amount': '200'},
                            ],
                        },
                    ],
                ),
            ],
            # expected_goal_bar
            None,
        ),
        (
            # do_x_get_y_rules
            [],
            # goal_smart_rules
            [
                _generate_goal_smart_rule(
                    schedule=[
                        {
                            'counter': 'counter1',
                            'start': '00:00',
                            'week_day': 'mon',
                        },
                        {'counter': '0', 'start': '21:00', 'week_day': 'wed'},
                        {
                            'counter': 'counter1',
                            'start': '21:00',
                            'week_day': 'sun',
                        },
                    ],
                    steps=[
                        {
                            'id': 'counter1',
                            'steps': [
                                {'nrides': 10, 'amount': '40'},
                                {'nrides': 20, 'amount': '80'},
                            ],
                        },
                    ],
                ),
            ],
            # expected_goal_bar
            ['10 заказов — 40 ₽', '20 заказов — 80 ₽'],
        ),
    ],
)
async def test_goals_info_bar(
        taxi_driver_fix,
        driver_tags_mocks,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        do_x_get_y_rules,
        goal_smart_rules,
        expected_goal_bar,
):
    """
    Checks that:
    * goal step bar on offer screen is right
    """

    common.default_init_mock_offer_requirements(mock_offer_requirements)

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.rules_select_value_by_type = {
        'driver_fix': [common.DEFAULT_DRIVER_FIX_RULE],
        'goal': do_x_get_y_rules,
    }
    if goal_smart_rules:
        mock_offer_requirements.bsx_rules_select_value = goal_smart_rules

    taxi_config.set_values(
        {
            'DRIVER_FIX_OFFER_GOALS_INFO_SETTINGS': {
                'constants': {'mean_orders_per_hour': 3},
                'by_role': {
                    'role1': {
                        'days': 2,
                        'hours': 10,
                        'tag_for_subvention': 'mock_tag_for_subvention',
                    },
                },
            },
            'DRIVER_FIX_OFFER_SCREENS_BY_ROLE_V2': {
                '__default__': {
                    'offer_screen': [{'type': 'do_x_get_y_table'}],
                    'memo_screen': [],
                    'offer_card': {
                        'title': 'offer_card.title',
                        'description': 'offer_card.description',
                    },
                },
            },
            'DRIVER_FIX_USE_SMART_GOALS': {
                'use_smart_goals': bool(goal_smart_rules),
                'use_old_goals_fallback': True,
            },
        },
    )

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(['role1']),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    offers = response.json()['offers']
    assert offers != []

    for offer in offers:
        ctor = offer['offer_screen']

        if expected_goal_bar is None:
            assert ctor['items'] == []
            return

        subheader, idx = common.extract_ctor_object_with_index(
            ctor, 'Персональная акция',
        )
        assert subheader is not None
        assert _extract_goal_bar(ctor, after_idx=idx) == expected_goal_bar


@use_role_config
@pytest.mark.now('2019-01-02T23:00:00+0300')
@pytest.mark.experiments3(filename='exp3_use_table_instead_chart.json')
@pytest.mark.config(
    DRIVER_FIX_PSEUDO_COMMISSION=[
        {'tag': 'tag1', 'role': 'role1', 'coefficient': 1.051},
    ],
)
async def test_pseudo_commission_chart(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        load_json,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json=_get_body_with_roles(['role1']),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200
    doc = response.json()

    expected_value = load_json('expected_tariffication_table.json')

    for offer in doc['offers']:
        ctor_items = offer['offer_screen']['items']
        charts = [item for item in ctor_items if item['type'] == 'selector']
        assert len(charts) == 1
        assert charts[0] == expected_value

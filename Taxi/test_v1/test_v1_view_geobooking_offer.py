import copy

import pytest

from tests_driver_fix import common

_DEFAULT_SCREEN_CONFIG = {
    'offer_card': {
        'title': 'offer_card.geobooking.title',
        'description': 'offer_card.geobooking.description',
        'rule_is_not_available_warning': (
            'offer_card.geobooking.rule_is_not_available_warning'
        ),
    },
    'offer_screen': [
        {
            'type': 'caption',
            'title': 'offer_screen.geobooking.title',
            'description': 'offer_screen.geobooking.description',
            'rule_is_not_available_warning': (
                'offer_screen.geobooking.rule_is_not_available_warning'
            ),
        },
        {
            'type': 'geobooking_conditions',
            'title': 'offer_screen.geobooking.conditions',
            'geoarea_text': 'offer_screen.geobooking.geoarea_format',
            'geoarea_subtitle': 'offer_screen.geobooking.geoarea',
        },
        {
            'type': 'geobooking_requirements',
            'title': 'offer_screen.geobooking.requirements',
            'items': [{'type': 'default_constraints'}],
        },
    ],
    'memo_screen': [
        {'type': 'header', 'caption': 'memo_screen.geobooking.header'},
        {
            'type': 'multy_paragraph_text',
            'text': 'memo_screen.geobooking.text',
        },
        {'type': 'image', 'image_url': 'geobooking_memo.png'},
    ],
}


_ROLE2_SCREEN_CONFIG = {
    'offer_card': {
        'title': 'role2_offer_card.geobooking.title',
        'description': 'role2_offer_card.geobooking.description',
    },
    'offer_screen': [
        {
            'type': 'caption',
            'title': 'role2_offer_screen.geobooking.title',
            'description': 'role2_offer_screen.geobooking.description',
        },
        {
            'type': 'geobooking_conditions',
            'title': 'role2_offer_screen.geobooking.conditions',
            'geoarea_text': 'role2_offer_screen.geobooking.geoarea_format',
            'geoarea_subtitle': 'role2_offer_screen.geobooking.geoarea',
        },
        {
            'type': 'geobooking_requirements',
            'title': 'role2_offer_screen.geobooking.requirements',
            'items': [{'type': 'default_constraints'}],
        },
    ],
    'memo_screen': [
        {'type': 'header', 'caption': 'role2_memo_screen.geobooking.header'},
        {
            'type': 'multy_paragraph_text',
            'text': 'role2_memo_screen.geobooking.text',
        },
        {'type': 'image', 'image_url': 'geobooking_memo.png.role2'},
    ],
}


@pytest.fixture(autouse=True)
def use_role_config(taxi_config):
    taxi_config.set_values(
        {
            'DRIVER_FIX_GEOBOOKING_SCREENS_BY_ROLE_V2': {
                '__default__': _DEFAULT_SCREEN_CONFIG,
                'role2': _ROLE2_SCREEN_CONFIG,
            },
        },
    )


@pytest.mark.parametrize('roles', [None, ['role1'], ['role1', 'role2']])
@pytest.mark.now('2020-01-01T12:00:00+03:00')
async def test_offer_basic(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        taxi_config,
        roles,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.rules_select_value = common.DEFAULT_GEOBOOKING_RULE

    body = {'driver_profile_id': 'uuid', 'park_id': 'dbid'}
    if roles is not None:
        body['roles'] = roles

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()

    assert len(doc['offers']) == 1 if roles is None else len(roles)

    for i, offer in enumerate(doc['offers']):
        expected_postfix = ''
        expected_offer_screen_path = 'expected_offer_screen.json'
        expected_memo_screen_path = 'expected_memo_screen.json'

        expected_role = '__default__' if roles is None else roles[i]
        if expected_role == 'role2':
            expected_postfix = ' role2'
            expected_offer_screen_path = 'expected_offer_screen_role2.json'
            expected_memo_screen_path = 'expected_memo_screen_role2.json'

        assert offer['offer_card'] == {
            'title': 'С минимальной гарантией дохода' + expected_postfix,
            'description': (
                'Получаете гарантированный доход за время на линии.'
                + expected_postfix
            ),
            'is_new': True,
            'enabled': True,
            'details': {
                'type': 'detail',
                'title': '07:00 — 18:00',
                'subtitle': 'Москва, Центр',
                'detail': '600 ₽/час',
                'accent': True,
            },
        }

        assert offer['offer_screen'] == load_json(expected_offer_screen_path)
        assert offer['memo_screen'] == load_json(expected_memo_screen_path)

        assert offer['key_params'] == {
            'tariff_zone': 'moscow',
            'subvention_geoarea': 'moscow_center',
            'tag': 'geobooking_moscow_2020',
        }

        assert offer['settings'] == {'rule_id': '_id/subvention_rule_id'}


@pytest.mark.now('2020-01-01T12:00:00+0300')
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
    'profile_payment_type, bs_payment_type,' 'expected_check_val',
    [
        ('none', 'none', (True, 'Принимать наличные и безналичные заказы')),
        ('none', 'online', (True, 'Принимать заказы по карте')),
        ('none', 'cash', (True, 'Принимать заказы с наличной оплатой')),
        ('none', 'any', None),
        ('online', 'none', (False, 'Принимать наличные и безналичные заказы')),
        ('online', 'online', (True, 'Принимать заказы по карте')),
        ('online', 'cash', (False, 'Принимать заказы с наличной оплатой')),
        ('online', 'any', None),
        ('cash', 'none', (False, 'Принимать наличные и безналичные заказы')),
        ('cash', 'online', (False, 'Принимать заказы по карте')),
        ('cash', 'cash', (True, 'Принимать заказы с наличной оплатой')),
        ('cash', 'any', None),
    ],
)
async def test_payment_type(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        profile_payment_type,
        bs_payment_type,
        expected_check_val,
        fetch_payment_type_from_candidates,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    rule = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
    rule['profile_payment_type_restrictions'] = bs_payment_type
    mock_offer_requirements.rules_select_value = rule

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

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200
    doc = response.json()

    ctor = doc['offers'][0]['offer_screen']
    check_val = common.extract_check_value(ctor, 'Принимать')
    assert check_val == expected_check_val


@pytest.mark.now('2020-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    'driver_classes,billing_classes,expected_check_val',
    [
        (['business'], ['econom'], (False, 'Включить тариф Эконом')),
        (['econom', 'business'], ['econom'], (True, 'Включить тариф Эконом')),
        (['econom', 'business'], ['econom'], (True, 'Включить тариф Эконом')),
        (
            ['econom'],
            ['econom', 'business'],
            (True, 'Включить тарифы Эконом, Комфорт'),
        ),
    ],
)
async def test_classes(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        driver_classes,
        billing_classes,
        expected_check_val,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    rule = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
    rule['tariff_classes'] = billing_classes
    mock_offer_requirements.rules_select_value = rule

    mock_offer_requirements.profiles_value['classes'] = driver_classes

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    doc = response.json()

    ctor = doc['offers'][0]['offer_screen']
    check_val = common.extract_check_value(ctor, 'Включить тариф')
    assert check_val == expected_check_val


@pytest.mark.now('2020-06-01T12:00:00+03:00')  # monday
@pytest.mark.parametrize(
    'rule_start,rule_end,rule_weekdays,rule_shift,expected_text',
    [
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            # rule_shift
            {'start': '07:00', 'end': '14:00'},
            # expected_text
            'Сегодня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            # rule_shift
            {'start': '07:00', 'end': '13:00'},
            # expected_text
            'Сегодня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            # rule_shift
            {'start': '07:00', 'end': '11:00'},
            # expected_text
            '2 июня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            # rule_shift
            {'start': '07:00', 'end': '12:00'},
            # expected_text
            '2 июня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            # rule_shift
            {'start': '18:00', 'end': '20:00'},
            # expected_text
            'Сегодня',
        ),
        (
            # rule_start
            '2020-06-01T21:00:00.000000+00:00',
            # rule_end
            '2020-06-10T21:00:00.000000+00:00',
            # rule_weekdays
            ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            # rule_shift
            {'start': '07:00', 'end': '12:00'},
            # expected_text
            '2 июня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['fri'],
            # rule_shift
            {'start': '07:00', 'end': '12:00'},
            # expected_text
            '5 июня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['wed', 'fri'],
            # rule_shift
            {'start': '07:00', 'end': '12:00'},
            # expected_text
            '3 июня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-15T21:00:00.000000+00:00',
            # rule_weekdays
            ['fri'],
            # rule_shift
            {'start': '07:00', 'end': '12:00'},
            # expected_text
            '5 июня',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-03T21:00:00.000000+00:00',
            # rule_weekdays
            ['fri'],
            # rule_shift
            {'start': '07:00', 'end': '12:00'},
            # expected_text
            '29 мая',
        ),
        (
            # rule_start
            '2020-05-15T21:00:00.000000+00:00',
            # rule_end
            '2020-06-01T21:00:00.000000+00:00',
            # rule_weekdays
            ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
            # rule_shift
            {'start': '07:00', 'end': '08:00'},
            # expected_text
            'Сегодня',  # no longer available today, but no next workday
        ),
    ],
)
async def test_workday(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        rule_start,
        rule_end,
        rule_weekdays,
        rule_shift,
        expected_text,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    rule = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
    rule['start'] = rule_start
    rule['end'] = rule_end
    rule['week_days'] = rule_weekdays
    rule['workshift'] = rule_shift
    mock_offer_requirements.rules_select_value = rule

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()

    if expected_text is None:
        assert doc['offers'] == []
        return

    offer_screen = doc['offers'][0]['offer_screen']

    # get constructor item with work rate. Workday should be in the same item
    ctor_item, _ = common.extract_ctor_object_with_index(
        offer_screen, '600 ₽/час',
    )

    assert ctor_item['subtitle'] == expected_text


@pytest.mark.parametrize(
    'days_forward,expected_time_range_end',
    [
        (0, '2020-01-01T09:00:01+00:00'),
        (1, '2020-01-02T09:00:01+00:00'),
        (31, '2020-02-01T09:00:01+00:00'),
    ],
)
@pytest.mark.now('2020-01-01T12:00:00+03:00')
async def test_rules_select_request(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        taxi_config,
        days_forward,
        expected_time_range_end,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    taxi_config.set_values(
        dict(
            DRIVER_FIX_VIEW_GEOBOOKING_OFFER_SETTINGS={
                'days_forward': days_forward,
            },
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        body = request.json

        assert body['status'] == 'enabled'
        assert body['time_range']['start'] == '2020-01-01T09:00:00+00:00'
        assert body['time_range']['end'] == expected_time_range_end
        assert body['types'] == ['geo_booking']
        assert body['is_personal'] is False

        return {'subventions': []}

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200


@pytest.mark.now('2020-01-01T12:00:00+0300')
async def test_offers_order(
        taxi_driver_fix, mockserver, mock_offer_requirements,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        rule1 = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
        rule1['start'] = '2019-01-15T00:00:00+03:00'
        rule1['end'] = '2020-01-05T00:00:00+03:00'
        rule1['geoareas'] = ['zelenograd']
        rule1['subvention_rule_id'] = 'id_rule_present_zelenograd'

        rule2 = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
        rule2['start'] = '2019-01-31T00:00:00+03:00'
        rule2['end'] = '2020-01-10T00:00:00+03:00'
        rule2['workshift'] = {'start': '07:00', 'end': '15:00'}
        rule2['geoareas'] = ['moscow_center']
        rule2['subvention_rule_id'] = 'id_rule_present_moscow_morning'

        rule3 = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
        rule3['start'] = '2019-01-31T00:00:00+03:00'
        rule3['end'] = '2020-01-10T00:00:00+03:00'
        rule3['workshift'] = {'start': '11:00', 'end': '14:00'}
        rule3['geoareas'] = ['moscow_center']
        rule3['subvention_rule_id'] = 'id_rule_present_moscow_day'

        rule4 = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
        rule4['start'] = '2019-01-31T00:00:00+03:00'
        rule4['end'] = '2020-01-05T00:00:00+03:00'
        rule4['geoareas'] = ['krasnogorsk']
        rule4['subvention_rule_id'] = 'id_rule_present_krasnogorsk'

        rule5 = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
        rule5['start'] = '2020-01-03T00:00:00+03:00'
        rule5['end'] = '2020-01-10T00:00:00+03:00'
        rule5['geoareas'] = ['zelenograd']
        rule5['subvention_rule_id'] = 'id_rule_future_zelenograd'

        rule6 = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
        rule6['start'] = '2020-01-03T00:00:00+03:00'
        rule6['end'] = '2020-01-10T00:00:00+03:00'
        rule6['geoareas'] = ['moscow_center']
        rule6['subvention_rule_id'] = 'id_rule_future_moscow'

        rule7 = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
        rule7['start'] = '2020-01-03T00:00:00+03:00'
        rule7['end'] = '2020-01-10T00:00:00+03:00'
        rule7['geoareas'] = ['krasnogorsk']
        rule7['subvention_rule_id'] = 'id_rule_future_krasnogorsk'

        return {
            'subventions': [rule4, rule6, rule2, rule3, rule7, rule5, rule1],
        }

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200
    doc = response.json()

    id_order = [offer['settings']['rule_id'] for offer in doc['offers']]

    expected_id_order = [
        'id_rule_present_zelenograd',
        'id_rule_present_krasnogorsk',
        'id_rule_present_moscow_morning',
        'id_rule_present_moscow_day',
        'id_rule_future_zelenograd',
        'id_rule_future_krasnogorsk',
        'id_rule_future_moscow',
    ]

    assert id_order == expected_id_order


@pytest.mark.now('2020-01-01T12:00:00+0300')
@pytest.mark.parametrize('future_rules_always_enabled', [False, True])
@pytest.mark.parametrize(
    'rule_start,rule_end,is_future_rule',
    [
        pytest.param(
            '2020-01-01T00:00:00+0300',
            '2020-01-02T00:00:00+0300',
            False,
            id='present_rule',
        ),
        pytest.param(
            '2020-01-02T00:00:00+0300',
            '2020-01-03T00:00:00+0300',
            True,
            id='future_rule',
        ),
    ],
)
async def test_future_rules_enabled(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        mock_offer_requirements,
        rule_start,
        rule_end,
        is_future_rule,
        future_rules_always_enabled,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    taxi_config.set_values(
        {
            'DRIVER_FIX_VIEW_GEOBOOKING_OFFER_SETTINGS': {
                'days_forward': 3,
                'future_rules_always_enabled': future_rules_always_enabled,
            },
        },
    )

    rule = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
    rule['start'] = rule_start
    rule['end'] = rule_end
    mock_offer_requirements.rules_select_value = rule

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200
    doc = response.json()

    offers = doc['offers']
    assert len(offers) == 1

    expected = future_rules_always_enabled or (not is_future_rule)
    assert offers[0]['offer_card']['enabled'] == expected


@pytest.mark.config(DRIVER_FIX_GEOBOOKING_OFFERS_USE_ROLES_AS_TAGS=True)
@pytest.mark.parametrize(
    'role, expected_rule_id',
    [('car', '_id/1'), ('pedestrian', '_id/2'), ('empty_response_role', None)],
)
@pytest.mark.parametrize('current_rule_id', [None, '_id/1', '_id/2'])
@pytest.mark.now('2020-01-01T12:00:00+0300')
async def test_use_roles(
        taxi_driver_fix,
        mock_offer_requirements,
        mockserver,
        role,
        expected_rule_id,
        current_rule_id,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        def _create_rule(rule_id, tag):
            rule = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
            rule['subvention_rule_id'] = rule_id
            rule['tags'] = [tag]
            return rule

        return {
            'subventions': [
                _create_rule('_id/1', 'moscow_center_car'),
                _create_rule('_id/2', 'moscow_center_pedestrian'),
                _create_rule('_id/3', 'moscow_center_smth_else'),
            ],
        }

    body = {
        'driver_profile_id': 'uuid',
        'park_id': 'dbid',
        'roles': [{'name': role}],
    }
    if current_rule_id is not None:
        body['current_mode_settings'] = {'rule_id': current_rule_id}

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json=body,
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    expected_rules = []
    if expected_rule_id is not None:
        expected_rules.append(expected_rule_id)
    if current_rule_id is not None and current_rule_id != expected_rule_id:
        expected_rules.append(current_rule_id)

    offers = response.json()['offers']
    got_rules = [offer['settings']['rule_id'] for offer in offers]

    assert sorted(expected_rules) == sorted(got_rules)


@pytest.mark.now('2020-01-03T12:00:00+00:00')
async def test_current_rule_is_ended(
        taxi_driver_fix, mockserver, mock_offer_requirements, load_json,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    rule = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
    rule['subvention_rule_id'] = '_id/current_rule'
    rule['end'] = '2020-01-02T21:00:00.000000+00:00'
    mock_offer_requirements.rules_select_value = rule

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json={
            'driver_profile_id': 'uuid',
            'park_id': 'dbid',
            'current_mode_settings': {'rule_id': '_id/current_rule'},
        },
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()

    assert len(doc['offers']) == 1

    offer = doc['offers'][0]
    assert offer['offer_card'] == {
        'title': 'С минимальной гарантией дохода',
        'description': 'Получаете гарантированный доход за время на линии.',
        'is_new': False,
        'enabled': False,
        'details': {
            'horizontal_divider_type': 'none',
            'padding': 'small_bottom',
            'text_color': '#F5523A',
            'text': (
                'Бонус больше не действует.\n'
                'Пожалуйста, вернитесь в режим «За заказы».'
            ),
            'type': 'text',
        },
    }

    assert offer['offer_screen'] == load_json(
        'expected_offer_screen_ended_rule.json',
    )
    assert offer['settings'] == {'rule_id': '_id/current_rule'}


@pytest.mark.parametrize('match_roles_for_tags', (True, False))
@pytest.mark.config(DRIVER_FIX_GEOBOOKING_OFFERS_USE_ROLES_AS_TAGS=True)
@pytest.mark.parametrize(
    'roles, expected_rule_id',
    [
        (['car', 'car_other'], '_id/1'),
        (['pedestrian', 'pedestrian_other'], '_id/2'),
        (['some_other_role'], None),
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
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    taxi_config.set(
        DRIVER_FIX_MATCH_ROLES_FOR_OFFERS={
            'driver_fix': False,
            'geo_booking': match_roles_for_tags,
        },
    )

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        def _create_rule(rule_id, tag):
            rule = copy.deepcopy(common.DEFAULT_GEOBOOKING_RULE)
            rule['subvention_rule_id'] = rule_id
            rule['tags'] = [tag]
            return rule

        return {
            'subventions': [
                _create_rule('_id/1', 'moscow_center_car'),
                _create_rule('_id/2', 'moscow_center_pedestrian'),
                _create_rule('_id/3', 'moscow_center_smth_else'),
            ],
        }

    body = {
        'driver_profile_id': 'uuid',
        'park_id': 'dbid',
        'roles': [{'name': role} for role in roles],
    }
    if current_rule_id is not None:
        body['current_mode_settings'] = {'rule_id': current_rule_id}

    response = await taxi_driver_fix.post(
        '/v1/view/geobooking_offer',
        json=body,
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    expected_rules = []
    if expected_rule_id is not None:
        expected_rules.append(expected_rule_id)
    if current_rule_id is not None and current_rule_id != expected_rule_id:
        expected_rules.append(current_rule_id)
    if not match_roles_for_tags:
        expected_rules = expected_rules * len(roles)

    offers = response.json()['offers']
    got_rules = [offer['settings']['rule_id'] for offer in offers]

    assert sorted(expected_rules) == sorted(got_rules)


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
        '/v1/view/geobooking_offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 404

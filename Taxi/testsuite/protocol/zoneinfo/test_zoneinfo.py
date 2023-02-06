import collections
import copy

import pytest

from taxi_tests.utils import ordered_object


TEST_USER_ID = 'a01d0000000000000000000000000000'
TEST_UNAUTHORIZED_USER_ID = 'a01d0000000000000000000000000001'
TEST_USER_PHONE_ID = '59246c5b6195542e9b084206'
TEST_USER_UID = '4003514353'
TEST_USER_UUID = 'de03de693ef0a0493f46cb27e5fb3930'
CHILDCHAIR_ICON = {
    'size_hint': 9999,
    'url_parts': {'key': 'TC', 'path': '/static/test-images/childchair_v2'},
}

WELCOME_SCREEN_DEFAULT = {
    'pool': {
        'image': 'welcome_pool_image',
        'items': [
            {'image': 'welcome_pool_image1', 'text': 'welcome.pool.text1'},
            {'image': 'welcome_pool_image2', 'text': 'welcome.pool.text2'},
            {'image': 'welcome_pool_image3', 'text': 'welcome.pool.text3'},
            {'image': 'welcome_pool_image4', 'text': 'welcome.pool.text4'},
        ],
        'subtitle': 'welcome.pool.subtitle',
        'title': 'welcome.pool.title',
    },
}


def zoneinfo_send_request(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )
    assert response.status_code == 200
    return response.json()


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.experiments3(filename='exp3_custom_endpoints_by_tariff.json')
def test_zoneinfo_custom_endpoints(taxi_protocol, load_json):
    data = zoneinfo_send_request(taxi_protocol)
    assert data['max_tariffs']

    for tariff in data['max_tariffs']:
        endpoints = tariff.get('custom_endpoints', [])
        if tariff['class'] == 'econom':
            assert endpoints == [
                {'type': 'route', 'path': '/4.0/custom-routes/v1/econom'},
            ]
        else:
            assert not endpoints


@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.experiments3(filename='exp3_comment_screen_requirements.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.parametrize('use_order_flow', [False, True])
def test_zoneinfo_simple(
        taxi_protocol,
        load_json,
        config,
        use_choices_handler,
        use_order_flow,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )
    if use_order_flow:
        config.set_values(
            dict(
                TARIFF_CATEGORIES_ORDER_FLOW={
                    'pool': {'order_flow': 'some_flow'},
                },
            ),
        )

    data = zoneinfo_send_request(taxi_protocol)
    expected_result = load_json('zoneinfo_simple_response.json')
    if use_order_flow:
        expected_result['max_tariffs'][0]['order_flow'] = 'some_flow'

    assert data == expected_result
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='full_auction',
    consumers=['protocol/zoneinfo'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'value': 'econom',
                                'arg_name': 'tariff_classes',
                                'set_elem_type': 'string',
                            },
                            'type': 'contains',
                        },
                    ],
                },
                'type': 'all_of',
            },
        },
    ],
)
def test_zoneinfo_auction(taxi_protocol, load_json, config):
    data = zoneinfo_send_request(taxi_protocol)
    max_tariffs = data['max_tariffs']
    for tariff in max_tariffs:
        enabled = tariff['class'] == 'econom'
        if enabled:
            tariff['full_auction'] == {'enabled': True}
        else:
            'full_auction' not in tariff


@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.experiments3(filename='exp3_comment_screen_requirements.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    HOURLY_RENTAL_ENABLED=True,
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    TARIFF_CATEGORIES_ORDER_FLOW={'pool': {'order_flow': 'delivery'}},
)
def test_zoneinfo_delivery_order_flow(
        taxi_protocol, load_json, config, dummy_choices,
):
    data = zoneinfo_send_request(taxi_protocol)
    assert 'order_flow' not in data['max_tariffs'][0]


@pytest.mark.parametrize('zone', ['moscow', 'almaty'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='skip_main_screen_config_control',
    consumers=['protocol/zoneinfo'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'set': ['moscow', 'almaty'],
                                'arg_name': 'zone',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                        {
                            'init': {
                                'set': [TEST_USER_UUID],
                                'arg_name': 'uuid',
                                'set_elem_type': 'string',
                            },
                            'type': 'in_set',
                        },
                    ],
                },
                'type': 'all_of',
            },
        },
    ],
)
def test_skip_main_screen_exp_enabled(taxi_protocol, zone):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zone,
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )
    assert response.status_code == 200
    assert 'skip_main_screen' in response.json()


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='skip_main_screen_config_control',
    consumers=['protocol/zoneinfo'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': False},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_skip_main_screen_exp_disabled(taxi_protocol):
    data = zoneinfo_send_request(taxi_protocol)
    assert 'skip_main_screen' not in data


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='skip_main_screen_config_control',
    consumers=['protocol/zoneinfo'],
    clauses=[{'title': 'a', 'value': {}, 'predicate': {'type': 'true'}}],
)
def test_skip_main_screen_exp_undefined(taxi_protocol):
    data = zoneinfo_send_request(taxi_protocol)
    assert 'skip_main_screen' in data


@pytest.mark.parametrize(
    'config_value',
    ([['MISTAKE'], ['bicycle', 'yellowcarnumber'], ['nosmoking']], []),
)
def test_zoneinfo_has_requirement_group_indices(
        taxi_protocol, config, config_value,
):
    config.set_values(dict(TARIFFS_REQUIREMENT_GROUP_INDICES=config_value))
    group_index = collections.defaultdict(lambda: 0)
    for i, group in enumerate(config_value):
        for name in group:
            group_index[name] = i
    data = zoneinfo_send_request(taxi_protocol)
    for tariff_info in data['max_tariffs']:
        if len(config_value) == 0:
            assert 'requirement_groups' not in tariff_info
            continue
        seen = list()
        for i, group in enumerate(tariff_info['requirement_groups']):
            assert len(group) > 0

            for j in group['indices']:
                seen.append(j)
                name = tariff_info['supported_requirements'][j]['name']
                assert group_index[name] == i

        assert sorted(seen) == list(
            range(len(tariff_info['supported_requirements'])),
        )


@pytest.mark.config(
    ALL_CATEGORIES=(
        'express',
        'econom',
        'business',
        'comfortplus',
        'vip',
        'minivan',
        'pool',
        'poputka',
        'business2',
        'kids',
        'uberx',
        'uberselect',
        'uberblack',
        'uberkids',
        'cargo',
    ),
)
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': [
            'express',
            'econom',
            'business',
            'comfortplus',
            'vip',
            'minivan',
            'pool',
            'poputka',
            'business2',
            'kids',
            'cargo',
        ],
        'yauber': ['uberx', 'uberselect', 'uberblack', 'uberkids'],
    },
)
@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.parametrize(
    'requirements_with_price_info, response_file',
    (
        pytest.param(
            [], 'zoneinfo_response_with_two_loaders.json', id='no_config',
        ),
        pytest.param(
            ['cargo_loaders'],
            'zoneinfo_response_with_one_loader.json',
            id='cargo_loaders_in_config',
        ),
    ),
)
def test_requirements_with_price_info(
        taxi_protocol,
        load_json,
        config,
        requirements_with_price_info,
        response_file,
):
    config.set_values(
        dict(REQUIREMENTS_WITH_PRICE_INFO=requirements_with_price_info),
    )
    data = zoneinfo_send_request(taxi_protocol)
    expected_result = load_json(response_file)
    assert data == expected_result


@pytest.mark.filldb(requirements='invalid_hourly_rental')
@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
def test_zoneinfo_invalid_hourly_rental(taxi_protocol, load_json, config):
    data = zoneinfo_send_request(taxi_protocol)
    expected_result = load_json('zoneinfo_hourly_rental_response.json')
    assert data == expected_result


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.filldb(tariff_settings='cash')
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_no_card(
        taxi_protocol, load_json, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    data = zoneinfo_send_request(taxi_protocol)
    expected_result = load_json('zoneinfo_simple_response_no_card.json')

    assert data == expected_result


@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.experiments3(filename='exp3_comment_screen_requirements.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.filldb(tariff_settings='creditcard')
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_works_with_creditcard(
        taxi_protocol, load_json, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    data = zoneinfo_send_request(taxi_protocol)
    expected_result = load_json('zoneinfo_simple_response.json')

    assert data == expected_result
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_options_400(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': 'invalid',
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )
    assert response.status_code == 400
    assert not dummy_choices.was_called()


@pytest.mark.filldb(localization_client_messages='zero_booster')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_zero_title_forms(
        taxi_protocol, load_json, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'zone_name': 'moscow', 'options': True},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()

    expected_result = load_json('zoneinfo_simple_response_zero_booster.json')

    assert data == expected_result
    assert dummy_choices.was_called() == use_choices_handler


DEFAULT_VISIBILITY_CONFIG = {
    'moscow': {
        'comfortplus': {
            'visible_by_default': False,
            'show_experiment': 'show_comfortplus',
        },
    },
    '__default__': {'pool': {'visible_by_default': False}},
}


@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'pool': {'visible_by_default': False},
            'poputka': {'visible_by_default': False},
        },
    },
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={'pool': {}},
    TARIFF_CATEGORIES_PROMO_INFO={
        'poputka': {
            'is_promo': True,
            'action_color': '#00ca50',
            'tint_color': '#00ca50',
            'title_highlight_color': '#41f98a',
            'app_url_scheme': 'yandexpoputka',
            'promo_open_links': {'web': 'test-'},
            'general_open_links': {'web': 'test-'},
        },
    },
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.now('2017-06-16T12:00:00+0300')
def test_zoneinfo_poputka(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'supports_hideable_tariffs': True,
        },
        headers={
            'Accept-Language': 'en',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()['max_tariffs']

    for cls in data:
        if cls['class'] == 'poputka':
            assert cls['is_promo']
            promo = cls['promo_app']
            assert promo['tint_color'] == '#00ca50'
            assert promo['action_color'] == '#00ca50'
            assert promo['title_highlight_color'] == '#41f98a'
            assert promo['app_name'] == 'app_name'
            assert promo['install_button'] == 'install_button'
            assert promo['install_button_short'] == 'install_button_short'
            assert promo['open_button'] == 'open_button'
            assert promo['open_button_short'] == 'open_button_short'
            assert promo['app_url_scheme'] == 'yandexpoputka'

    hidden_classes = [cls['class'] for cls in data if cls['is_hidden'] is True]
    all_classes = [cls['class'] for cls in data]
    assert len(all_classes) == 6
    assert hidden_classes == ['poputka']
    assert dummy_choices.was_called() == use_choices_handler


ORDER_FOR_ANOTHER_NO_INCLUDE_EXCLUDE: dict = {'rus': {}}

ORDER_FOR_ANOTHER_EMPTY_INCLUDE: dict = {'rus': {'include': []}}

ORDER_FOR_ANOTHER_EMPTY_EXCLUDE: dict = {'rus': {'exclude': []}}

ORDER_FOR_ANOTHER_NORMAL_INCLUDE = {'rus': {'include': ['econom', 'business']}}

ORDER_FOR_ANOTHER_NORMAL_EXCLUDE = {'rus': {'exclude': ['econom', 'business']}}

ORDER_FOR_ANOTHER_INCLUDE_EXCLUDE = {
    'rus': {'include': ['business'], 'exclude': ['econom']},
}


@pytest.mark.parametrize(
    'cfg, expected_classes',
    [
        (
            ORDER_FOR_ANOTHER_NO_INCLUDE_EXCLUDE,
            {'business', 'comfortplus', 'econom', 'minivan', 'vip'},
        ),
        (ORDER_FOR_ANOTHER_EMPTY_INCLUDE, {}),
        (ORDER_FOR_ANOTHER_NORMAL_INCLUDE, {'econom', 'business'}),
        (
            ORDER_FOR_ANOTHER_EMPTY_EXCLUDE,
            {'business', 'comfortplus', 'econom', 'minivan', 'vip'},
        ),
        (ORDER_FOR_ANOTHER_NORMAL_EXCLUDE, {'comfortplus', 'minivan', 'vip'}),
        (ORDER_FOR_ANOTHER_INCLUDE_EXCLUDE, {'business'}),
    ],
)
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_order_for_other(
        config,
        taxi_protocol,
        cfg,
        expected_classes,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    config.set_values(dict(ORDER_FOR_ANOTHER_COUNTRIES_AND_TARIFFS=cfg))

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'zone_name': 'moscow'},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()['max_tariffs']
    allowed_classes = {
        cls['class']
        for cls in data
        if cls['order_for_other_prohibited'] is False
    }
    assert allowed_classes == set(expected_classes)
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_cache(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'zone_name': 'moscow'},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 08:50:00 GMT',
        },
    )
    assert response.status_code == 304

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 06:50:00 GMT',
        },
    )
    assert response.status_code == 200
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.config(BILLING_PERSONAL_WALLET_ENABLED=True)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.experiments3(filename='experiments3_personal_wallet.json')
def test_zoneinfo_personal_wallet(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data['payment_options'] == {
        'corp': True,
        'coupon': True,
        'creditcard': True,
        'personal_wallet': True,
    }
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.parametrize(
    'match_enabled',
    [
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_not_force_apple_pay.json',
                ),
            ),
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_force_apple_pay.json',
                ),
            ),
        ),
    ],
)
def test_zoneinfo_applepay(taxi_protocol, config, match_enabled):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    if match_enabled:
        assert data['payment_options'] == {
            'corp': True,
            'coupon': True,
            'creditcard': True,
            'applepay': True,
        }
        assert (
            [
                item.get('restrict_by_payment_type', None)
                for item in data['max_tariffs']
            ]
            == [
                None,
                None,
                ['cash', 'applepay'],
                ['card', 'applepay'],
                ['applepay'],
            ]
        )
    else:
        assert data['payment_options'] == {
            'corp': True,
            'coupon': True,
            'creditcard': True,
        }
        assert [
            item.get('restrict_by_payment_type', None)
            for item in data['max_tariffs']
        ] == [None, None, ['cash'], ['card'], ['applepay']]


@pytest.mark.config(BILLING_COOP_ACCOUNT_ENABLED=True)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.user_experiments('coop_account')
def test_zoneinfo_coop_account(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data['payment_options'] == {
        'corp': True,
        'coupon': True,
        'creditcard': True,
        'coop_account': True,
    }
    assert dummy_choices.was_called() == use_choices_handler


def _make_method_exp_mark(method_name, matched, enabled):
    return pytest.mark.experiments3(
        match={
            'predicate': {'type': 'true' if matched else 'false'},
            'enabled': True,
        },
        name=method_name,
        consumers=['protocol/zoneinfo'],
        clauses=[
            {
                'title': 'default',
                'value': {'enabled': enabled},
                'predicate': {'type': 'true'},
            },
        ],
    )


def _make_yandex_card_exp_mark(matched=True, enabled=True):
    return _make_method_exp_mark('yandex_card', matched, enabled)


def _make_apple_pay_exp_mark(matched=True, enabled=True):
    return _make_method_exp_mark(
        'zoneinfo_applepay_settings', matched, enabled,
    )


def _make_google_pay_exp_mark(matched=True, enabled=True):
    return _make_method_exp_mark(
        'zoneinfo_googlepay_settings', matched, enabled,
    )


def _make_cargocorp_exp_mark(matched=True, enabled=True):
    return _make_method_exp_mark(
        'cargo_finance_methods_enabled', matched, enabled,
    )


def _make_sbp_exp_mark(matched=True, enabled=True):
    return _make_method_exp_mark('sbp_enabled', matched, enabled)


@pytest.mark.parametrize(
    'expected_sbp, config_enabled',
    [
        pytest.param(
            True,
            True,
            marks=[_make_sbp_exp_mark(matched=True, enabled=True)],
            id='exp-enabled_config-enabled',
        ),
        pytest.param(
            False,
            False,
            marks=[_make_sbp_exp_mark(matched=True, enabled=True)],
            id='exp-enabled_config-disabled',
        ),
        pytest.param(
            False,
            True,
            marks=[_make_sbp_exp_mark(matched=True, enabled=False)],
            id='exp-disabled_config-enabled',
        ),
        pytest.param(
            False,
            True,
            marks=[_make_sbp_exp_mark(matched=False, enabled=True)],
            id='exp-not-matched_config-enabled',
        ),
    ],
)
def test_zoneinfo_sbp(taxi_protocol, config, expected_sbp, config_enabled):
    config.set_values({'BILLING_SBP_ENABLED': config_enabled})
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    response_sbp = data['payment_options'].get('sbp', False)
    assert response_sbp == expected_sbp


@pytest.mark.parametrize(
    'expected_yandex_card',
    [
        pytest.param(
            True,
            marks=[_make_yandex_card_exp_mark(matched=True, enabled=True)],
            id='exp-enabled',
        ),
        pytest.param(
            False,
            marks=[_make_yandex_card_exp_mark(matched=True, enabled=False)],
            id='exp-disabled',
        ),
        pytest.param(
            False,
            marks=[_make_yandex_card_exp_mark(matched=False, enabled=True)],
            id='exp-not-matched',
        ),
    ],
)
def test_zoneinfo_yandex_card(taxi_protocol, expected_yandex_card):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    response_yandex_card = data['payment_options'].get('yandex_card', False)
    assert response_yandex_card == expected_yandex_card


@pytest.mark.filldb(tariff_settings='googlepay')
@pytest.mark.parametrize(
    'expected_google_pay',
    [
        pytest.param(
            True,
            marks=[_make_google_pay_exp_mark(matched=True, enabled=True)],
            id='exp-enabled',
        ),
        pytest.param(
            False,
            marks=[_make_google_pay_exp_mark(matched=True, enabled=False)],
            id='exp-disabled',
        ),
        pytest.param(
            True,
            marks=[_make_google_pay_exp_mark(matched=False, enabled=False)],
            id='exp-not-matched',
        ),
    ],
)
def test_zoneinfo_google_pay(taxi_protocol, expected_google_pay):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    response_google_pay = data['payment_options'].get('googlepay', False)
    assert response_google_pay == expected_google_pay


@pytest.mark.filldb(tariff_settings='applepay')
@pytest.mark.parametrize(
    'expected_apple_pay',
    [
        pytest.param(
            True,
            marks=[_make_apple_pay_exp_mark(matched=True, enabled=True)],
            id='exp-enabled',
        ),
        pytest.param(
            False,
            marks=[_make_apple_pay_exp_mark(matched=True, enabled=False)],
            id='exp-disabled',
        ),
        pytest.param(
            True,
            marks=[_make_apple_pay_exp_mark(matched=False, enabled=False)],
            id='exp-not-matched',
        ),
    ],
)
def test_zoneinfo_apple_pay(taxi_protocol, expected_apple_pay):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    response_apple_pay = data['payment_options'].get('applepay', False)
    assert response_apple_pay == expected_apple_pay


@pytest.mark.parametrize(
    'expected_cargocorp',
    [
        pytest.param(
            True,
            marks=[_make_cargocorp_exp_mark(matched=True, enabled=True)],
            id='exp-enabled',
        ),
        pytest.param(
            False,
            marks=[_make_cargocorp_exp_mark(matched=True, enabled=False)],
            id='exp-disabled',
        ),
        pytest.param(
            False,
            marks=[_make_cargocorp_exp_mark(matched=False, enabled=True)],
            id='exp-not-matched',
        ),
    ],
)
def test_zoneinfo_cargocorp(taxi_protocol, expected_cargocorp):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 ' '06:50:00 GMT',
        },
    )
    data = response.json()
    assert response.status_code == 200
    response_cargocorp = data['payment_options'].get('cargocorp', False)
    assert response_cargocorp == expected_cargocorp


@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'comfortplus': {
                'visible_by_default': True,
                'hide_experiment': 'show_comfortplus',
                'use_legacy_experiments': True,
            },
        },
        '__default__': {
            'pool': {'visible_by_default': False},
            'poputka': {'visible_by_default': False},
        },
    },
)
@pytest.mark.config(TARIFF_CATEGORIES_VISIBILITY=DEFAULT_VISIBILITY_CONFIG)
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={'pool': {}, 'poputka': {}},
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.user_experiments('show_comfortplus')
def test_zoneinfo_hidden_legacy_exp(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'supports_hideable_tariffs': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()['max_tariffs']
    hidden_classes = [cls['class'] for cls in data if cls['is_hidden'] is True]
    all_classes = [cls['class'] for cls in data]
    assert len(all_classes) == 5
    assert hidden_classes == ['comfortplus']
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        'moscow': {
            'comfortplus': {
                'visible_by_default': True,
                'hide_experiment': 'show_comfortplus',
            },
        },
        '__default__': {
            'pool': {'visible_by_default': False},
            'poputka': {'visible_by_default': False},
        },
    },
)
@pytest.mark.config(TARIFF_CATEGORIES_VISIBILITY=DEFAULT_VISIBILITY_CONFIG)
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={'pool': {}, 'poputka': {}},
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='show_comfortplus',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_zoneinfo_hidden_exp3(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'supports_hideable_tariffs': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()['max_tariffs']
    hidden_classes = [cls['class'] for cls in data if cls['is_hidden'] is True]
    all_classes = [cls['class'] for cls in data]
    assert len(all_classes) == 5
    assert hidden_classes == ['comfortplus']
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_fallback_locale(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'zone_name': 'moscow', 'options': True},
        headers={
            'Accept-Language': 'ka',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_vary_accept_language(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {'id': TEST_USER_ID, 'point': [37.588, 55.773]},
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 06:50:00 GMT',
        },
    )

    assert 'Accept-Language' in map(
        str.strip, response.headers['Vary'].split(','),
    )
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['child_tariff', 'econom'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['child_tariff', 'econom'],
    },
    ZONES_TARIFFS_SETTINGS={
        '__default__': {
            'child_tariff': {
                'options': [{'name': 'child_tariff', 'value': '3 min'}],
                'subtitle': 'card.subtitle.child_tariff',
            },
        },
    },
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.user_experiments('child_tariff')
def test_zoneinfo_child_tariff(
        taxi_protocol, config, use_choices_handler, dummy_choices, mockserver,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 100,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()
    data_econom = data['max_tariffs'][1]
    req_list = data_econom['supported_requirements']
    for i in req_list:
        if i['name'] == 'childchair_moscow':
            econom_chair = i
    assert econom_chair['redirect'] == {
        'tariff_class': 'child_tariff',
        'requirement_name': 'childchair_for_child_tariff',
        'description': 'Available in Kids',
    }

    econom_chair_booster = econom_chair['select']['options'][2]
    assert econom_chair['type'] == 'select'
    assert econom_chair_booster['title_forms'] == {
        '1': 'Бустер',
        '2': '2 бустера',
    }

    data_child = data['max_tariffs'][0]
    assert data_child['class'] == 'child_tariff'
    assert data_child['id'] == 'child_tariff'
    assert data_child['name'] == 'Kids'
    req_list = data_child['supported_requirements']
    for i in req_list:
        if i['name'] == 'childchair_for_child_tariff':
            child_tariff_chair = i

    assert child_tariff_chair['glued'] is True
    assert child_tariff_chair['persistent'] is True
    assert child_tariff_chair['tariff_specific'] is True
    assert child_tariff_chair['unavailable_text'] == 'Translated text'

    image2 = mockserver.url('static/images/image2')
    image3 = mockserver.url('static/images/image3')
    image4 = mockserver.url('static/images/image4')
    video_str = mockserver.url('static/images/video')
    preview = mockserver.url('static/images/video_preview')
    car = mockserver.url('static/images/branding_image')

    options = child_tariff_chair['select']['options']
    assert options[0]['icon']['url'] == image4
    assert options[1]['image']['url'] == image4
    assert options[2]['style'] == 'spinner'

    video = data_child['card']['video']
    assert video['video']['url'] == video_str
    assert video['preview']['url'] == preview
    assert video['fallback_url'] == 'https://youtu.be/SISXtyPq27c'

    assert data_child['card']['partner_logo']['url'] == image3
    assert data_child['card']['items'][3]['image']['url'] == image2
    assert data_child['icon']['url'] == car
    assert data_child['image']['url'] == car

    assert dummy_choices.was_called() == use_choices_handler


def check_requirements(
        tariff_data,
        expected_requirements,
        expected_glued_requirements=None,
        expected_glued_optional_requirements=None,
):
    req_list = tariff_data['supported_requirements']

    # check requirements list (order is important)
    req_names = [r['name'] for r in req_list]
    assert req_names == expected_requirements

    if expected_glued_requirements is not None:
        req_glued_names = [r['name'] for r in req_list if r.get('glued')]
        assert req_glued_names == expected_glued_requirements

    if expected_glued_optional_requirements is not None:
        req_optional_glued_names = [
            r['name'] for r in req_list if r.get('optional_glued')
        ]
        assert req_optional_glued_names == expected_glued_optional_requirements


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.filldb(tariff_settings='multiple_requirements')
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom']},
)
def test_zoneinfo_multiple_glued_requirements(taxi_protocol):

    expected_requirements = [
        'nosmoking',
        'bicycle',  # optional glued
        'animaltransport',  # glued
        'yellowcarnumber',  # optional glued
        'conditioner',  # glued
        'check',
    ]
    expected_glued_requirements = [
        'bicycle',
        'animaltransport',
        'yellowcarnumber',
        'conditioner',
    ]
    expected_glued_optional_requirements = ['bicycle', 'yellowcarnumber']

    data = zoneinfo_send_request(taxi_protocol)
    econom_data = data['max_tariffs'][0]
    assert econom_data['class'] == 'econom'
    check_requirements(
        econom_data,
        expected_requirements,
        expected_glued_requirements,
        expected_glued_optional_requirements,
    )


@pytest.mark.experiments3(filename='experiments3_only_one_glued.json')
@pytest.mark.filldb(tariff_settings='multiple_requirements')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'comfortplus'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'business', 'comfortplus'],
    },
)
def test_zoneinfo_only_one_glued_requirements(taxi_protocol):

    expected_requirements = [
        'nosmoking',
        'bicycle',  # optional glued in econom, business, comfortplus
        'animaltransport',  # glued in econom, business
        'yellowcarnumber',  # optional glued in econom, business, comfortplus
        'conditioner',  # glued in econom, business
        'check',
    ]
    expected_glued_requirements = {
        # defined in value of the only_one_glued_requrement experiment
        'econom': ['yellowcarnumber'],
        'business': ['animaltransport'],
    }

    data = zoneinfo_send_request(taxi_protocol)
    assert len(data['max_tariffs']) == 3

    for class_data in data['max_tariffs']:
        class_name = class_data['class']
        check_requirements(
            class_data,
            expected_requirements,
            expected_glued_requirements.get(class_name),
            None,
        )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='toggle_to_glued',
    consumers=['protocol/zoneinfo'],
    clauses=[
        {
            'title': 'a',
            'value': {'tariffs': ['econom', 'unknown']},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.filldb(tariff_settings='multiple_requirements')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom', 'business']},
)
@pytest.mark.parametrize('has_glued', [False, True])
def test_zoneinfo_toggle_to_glued_requirements(
        taxi_protocol, mongodb, has_glued,
):
    if not has_glued:
        mongodb.tariff_settings.update(
            {},
            {
                '$set': {
                    's.$[].glued_requirements': [],
                    's.$[].optional_glued_requirements': [],
                },
            },
        )

    expected_requirements = {
        'econom': [
            'nosmoking',
            'bicycle',  # optional glued in econom, business, comfortplus
            'animaltransport',  # glued in econom, business
            'yellowcarnumber',  # optional glued in
            # econom, business, comfortplus
            'conditioner',  # glued in econom, business
            'check',
        ],
    }
    expected_requirements['business'] = copy.deepcopy(
        expected_requirements['econom'],
    )

    expected_glued_requirements = {'econom': [], 'business': []}
    expected_glued_optional_requirements = copy.deepcopy(
        expected_glued_requirements,
    )

    if has_glued:
        # all econom requirements are glued
        expected_glued_requirements['econom'] = expected_requirements['econom']
        expected_glued_optional_requirements['econom'] = [
            'nosmoking',  # converted from non-glued
            'bicycle',  # optional glued in econom
            'yellowcarnumber',  # optional glued in econom
            'check',  # converted from non-glued
        ]
        # business reqs untouched
        expected_glued_requirements['business'] = [
            'bicycle',
            'animaltransport',
            'yellowcarnumber',
            'conditioner',
        ]
        expected_glued_optional_requirements['business'] = [
            'bicycle',
            'yellowcarnumber',
        ]

    data = zoneinfo_send_request(taxi_protocol)
    for tariff_data in data['max_tariffs']:
        tariff = tariff_data['class']
        assert tariff in ['econom', 'business']
        check_requirements(
            tariff_data,
            expected_requirements[tariff],
            expected_glued_requirements[tariff],
            expected_glued_optional_requirements[tariff],
        )


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.filldb(tariff_settings='multiple_requirements')
@pytest.mark.experiments3(filename='experiments3_disabled_requirement.json')
@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'vip', 'comfortplus'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'business', 'vip', 'comfortplus'],
    },
)
def test_zoneinfo_requirement_disabled_by_experiment(taxi_protocol):
    default_requirements = [
        'nosmoking',
        'bicycle',
        'animaltransport',
        'yellowcarnumber',
        'conditioner',
        'check',
    ]
    disabled_requirements = {  # by experiments3
        'econom': {'yellowcarnumber', 'conditioner'},
        'business': {'yellowcarnumber'},
        'vip': {'yellowcarnumber', 'nosmoking'},
        'comfortplus': {},
    }
    data = zoneinfo_send_request(taxi_protocol)
    for class_data in data['max_tariffs']:
        class_name = class_data['class']
        expected_requirements = [
            req
            for req in default_requirements
            if req not in disabled_requirements[class_name]
        ]
        check_requirements(class_data, expected_requirements)


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.filldb(tariff_settings='multiple_requirements')
@pytest.mark.config(
    ALL_CATEGORIES=['econom'],
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['econom']},
)
@pytest.mark.parametrize(
    'local_config,expected_requirements',
    [
        (
            [
                {'requirement_type': 'conditioner'},
                {'requirement_type': 'nosmoking'},
            ],
            ['bicycle', 'animaltransport', 'yellowcarnumber', 'check'],
        ),
        (
            [],
            [
                'nosmoking',
                'bicycle',
                'animaltransport',
                'yellowcarnumber',
                'conditioner',
                'check',
            ],
        ),
    ],
)
def test_zoneinfo_fake_requirements(
        taxi_protocol, taxi_config, local_config, expected_requirements,
):
    taxi_config.set_values({'FAKE_REQUIREMENTS_CONFIG': local_config})
    data = zoneinfo_send_request(taxi_protocol)
    assert len(data['max_tariffs']) == 1
    class_data = data['max_tariffs'][0]
    assert class_data['class'] == 'econom'
    check_requirements(class_data, expected_requirements)


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['poputka', 'econom'],
    ZONES_TARIFFS_SETTINGS={
        '__default__': {'poputka': {'subtitle': 'card.subtitle.poputka'}},
    },
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'poputka': {'visible_by_default': False}},
    },
    BRANDING_ITEMS_COUNT={'poputka': 2},
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.user_experiments('poputka_promo')
def test_zoneinfo_poputka_iems(
        taxi_protocol, config, use_choices_handler, dummy_choices, mockserver,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 100,
            'options': True,
            'supports_hideable_tariffs': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()

    all_classes = [cls['class'] for cls in data['max_tariffs']]
    assert all_classes == ['econom', 'poputka']

    image5 = mockserver.url('static/images/image5')
    image6 = mockserver.url('static/images/image6')

    data_child = data['max_tariffs'][1]
    items = data_child['card']['items']
    assert items[0]['text'] == 'poputka text item 1'
    assert items[0]['image']['url'] == image5
    assert items[1]['text'] == 'poputka text item 2'
    assert items[1]['image']['url'] == image5
    assert data_child['icon']['url'] == image6
    assert data_child['image']['url'] == image6

    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['poputka', 'econom'],
    ZONES_TARIFFS_SETTINGS={
        '__default__': {'poputka': {'subtitle': 'card.subtitle.poputka'}},
    },
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {'poputka': {'visible_by_default': False}},
    },
    BRANDING_ITEMS_COUNT={'poputka': 5},
)
@pytest.mark.user_experiments('poputka_promo')
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_poputka_iems_default(
        taxi_protocol, config, use_choices_handler, dummy_choices, mockserver,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    request_headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 100,
            'options': True,
            'supports_hideable_tariffs': True,
        },
        headers=request_headers,
    )

    assert response.status_code == 200
    data = response.json()

    all_classes = [cls['class'] for cls in data['max_tariffs']]
    assert all_classes == ['econom', 'poputka']

    data_child = data['max_tariffs'][1]
    items = data_child['card']['items']

    image_default = mockserver.url('static/images/branding_image_default')

    assert items[2]['text'] == 'poputka text item 4'
    assert items[2]['image']['url'] == image_default

    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.parametrize(
    'expected_status, zone_name, expected_cache_control',
    [
        (200, 'moscow', 'max-age=600'),
        (404, 'not_existed_zone_info_forever', 'no-store'),
        (400, '', ''),
    ],
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_CacheControl_normal_noStore_noExist(
        taxi_protocol,
        zone_name,
        expected_status,
        expected_cache_control,
        config,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    """
    Test checks what kind of information has 'Cache-Control' header of
        the response
    If everything ok, there should be a information like 'max-age=600'
    If not, but happened NotFound exception, there should be 'no-store'
        with reason to not overwrite cache
    In other cases there is no 'Cache-control'
    """

    request = {}
    request['id'] = TEST_USER_ID
    if zone_name != '':
        request['zone_name'] = zone_name

    response = taxi_protocol.post('3.0/zoneinfo', request)

    assert response.status_code == expected_status
    headers = response.headers

    if headers.get('Cache-Control'):
        cache_control = headers.get('Cache-Control')
    else:
        cache_control = ''

    assert cache_control == expected_cache_control

    expected_handler_usage = (expected_status == 200) and use_choices_handler
    assert dummy_choices.was_called() == expected_handler_usage


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['child_tariff', 'econom'],
    ZONES_TARIFFS_SETTINGS={
        '__default__': {
            'child_tariff': {
                'options': [{'name': 'child_tariff', 'value': '3 min'}],
                'subtitle': 'card.subtitle.child_tariff',
            },
        },
    },
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.user_experiments('child_tariff')
@pytest.mark.filldb(tariff_settings='no_branding')
def test_zoneinfo_branding_images(
        taxi_protocol, config, use_choices_handler, dummy_choices, mockserver,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 100,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()

    image = mockserver.url('static/images/image1')
    data_child = data['max_tariffs'][0]
    assert data_child['icon']['url'] == image
    assert data_child['image']['url'] == image
    assert dummy_choices.was_called() == use_choices_handler


TEST_ZONE_CALLCENTERS_CONFIG = {
    'ru': {
        'mcc': '250',
        'formatted_phone': '+7 (800) 301-33-30',
        'phone': '+78003013330',
        'zones': {
            'moscow': {
                'formatted_phone': '+7 (495) 999 99 99',
                'phone': '+7495999999',
            },
        },
    },
}


@pytest.mark.parametrize(
    'zone_name,cfg,expected',
    [
        (
            'moscow',
            TEST_ZONE_CALLCENTERS_CONFIG,
            [
                {
                    'type': 'national',
                    'country': 'RU',
                    'mcc': '250',
                    'formatted_phone': '+7 (800) 301-33-30',
                    'phone': '+78003013330',
                },
                {
                    'type': 'local',
                    'country': 'RU',
                    'mcc': '250',
                    'formatted_phone': '+7 (495) 999 99 99',
                    'phone': '+7495999999',
                },
            ],
        ),
    ],
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.user_experiments('enable_contact_options_in_zoneinfo')
def test_zoneinfo_contact_options_callcenters(
        config,
        taxi_protocol,
        zone_name,
        cfg,
        expected,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    config.set_values(dict(CALLCENTER_PHONES=cfg))
    headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zone_name,
            'size_hint': 640,
            'options': True,
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    contact_options = data['contact_options']
    assert contact_options == {'call_centers': expected}
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.parametrize(
    'zone,authorized,has_plus,uid_type,could_buy_plus',
    [
        ('moscow', False, False, 'phonish', False),
        ('moscow', True, True, 'phonish', False),
        ('moscow', True, False, 'phonish', True),
        ('moscow', True, False, 'portal', True),
        ('moscow', True, False, 'web_cookie', False),
        ('moscow', True, False, '', False),
        ('moscow', True, False, None, False),
        ('almaty', True, False, 'phonish', False),
    ],
)
@pytest.mark.filldb(price_modifiers='plus_promotion')
@pytest.mark.config(
    YAPLUS_SUMMARY_PROMO_BANNER_SETTINGS_BY_COUNTRY={
        '__default__': {
            'content': [
                {
                    'image_tag': 'music',
                    'tanker_key': 'ya_plus_promo_banner.content.music',
                },
                {
                    'image_tag': 'disk',
                    'tanker_key': 'ya_plus_promo_banner.content.disk',
                },
            ],
            'action': {'url': 'https://yandex.ru', 'color': '#FFFFFF'},
            'keys': {
                'banner_title': (
                    'common_strings.not_default.' 'ya_plus_promo_banner.title'
                ),
                'banner_subtitle': (
                    'common_strings.not_default.'
                    'ya_plus_promo_banner.subtitle'
                ),
                'button_text': (
                    'common_strings.not_default.'
                    'ya_plus_promo_banner.action.text'
                ),
            },
        },
    },
    YAPLUS_PROMO_BANNER_ENABLED=True,
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.user_experiments('could_buy_plus')
@pytest.mark.user_experiments('plus_summary_promo_login')
@pytest.mark.user_experiments('plus_summary_promo_no_login')
def test_zoneinfo_could_buy_plus(
        taxi_protocol,
        zone,
        db,
        authorized,
        could_buy_plus,
        uid_type,
        load_json,
        has_plus,
        config,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    user_id = TEST_USER_ID
    upd = {'authorized': authorized, 'has_ya_plus': has_plus}

    if uid_type:
        upd['yandex_uid_type'] = uid_type

    db.users.update({'_id': user_id}, {'$set': upd})

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': user_id,
            'zone_name': zone,
            'size_hint': 100,
            'options': True,
            'supports_hideable_tariffs': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['could_buy_plus'] == could_buy_plus

    plus_brandings = list(
        filter(
            lambda x: x['type'] == 'ya_plus_promo_banner',
            data.get('brandings', []),
        ),
    )
    if could_buy_plus:
        expected = load_json('zoneinfo_ya_plus_promo_banner.json')
        assert plus_brandings[0] == expected
    else:
        assert len(plus_brandings) == 0
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.config(
    YAPLUS_WELCOME_PROMO_BANNER_SETTINGS_BY_COUNTRY={
        '__default__': {
            'content': [
                {
                    'image_tag': 'music',
                    'tanker_key': 'ya_plus_promo_banner.content.music',
                },
                {
                    'image_tag': 'disk',
                    'tanker_key': 'ya_plus_promo_banner.content.disk',
                },
            ],
            'action': {'color': '#FFFFFF'},
            'keys': {
                'banner_title': (
                    'common_strings.not_default.'
                    'ya_plus_welcome_promo_banner.title'
                ),
                'banner_subtitle': (
                    'common_strings.not_default.'
                    'ya_plus_welcome_promo_banner.subtitle'
                ),
                'button_text': (
                    'common_strings.not_default.'
                    'ya_plus_welcome_promo_banner.action.text'
                ),
            },
        },
    },
    YAPLUS_WELCOME_PROMO_BANNER_ENABLED=True,
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_ya_plus_welcome_banner(
        taxi_protocol, load_json, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    user_id = TEST_USER_ID
    request_body = {
        'id': user_id,
        'zone_name': 'moscow',
        'size_hint': 100,
        'options': True,
        'supports_hideable_tariffs': True,
    }
    request_headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo', request_body, headers=request_headers,
    )

    assert response.status_code == 200
    data = response.json()

    promo = list(
        filter(
            lambda x: x['type'] == 'ya_plus_welcome_promo_banner',
            data.get('brandings', []),
        ),
    )[0]
    expected_promo = load_json('zoneinfo_ya_plus_welcome_promo_banner.json')
    assert promo == expected_promo
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.config(
    YAPLUS_PROMO_BANNER_ENABLED=True, YAPLUS_WELCOME_PROMO_BANNER_ENABLED=True,
)
@pytest.mark.filldb(price_modifiers='plus_promotion')
@pytest.mark.user_experiments('could_buy_plus')
@pytest.mark.user_experiments('plus_summary_promo_login')
@pytest.mark.user_experiments('plus_summary_promo_no_login')
def test_ya_plus_banner_default_keys(taxi_protocol, db):
    user_id = TEST_USER_ID

    upd = {
        'authorized': True,
        'has_ya_plus': False,
        'yandex_uid_type': 'portal',
    }

    db.users.update({'_id': user_id}, {'$set': upd})

    request_body = {
        'id': user_id,
        'zone_name': 'moscow',
        'size_hint': 100,
        'options': True,
        'supports_hideable_tariffs': True,
    }
    request_headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo', request_body, headers=request_headers,
    )

    assert response.status_code == 200
    data = response.json()

    plus = list(
        filter(
            lambda x: x['type'] == 'ya_plus_promo_banner',
            data.get('brandings', []),
        ),
    )[0]
    assert plus['title'] == 'YaPlus Promo Banner Title'
    assert plus['subtitle'] == 'YaPlus Promo Banner Subtitle 169 roubles'
    assert plus['action_button']['text'] == 'YaPlus Promo Banner Action Text'

    welcome = list(
        filter(
            lambda x: x['type'] == 'ya_plus_welcome_promo_banner',
            data.get('brandings', []),
        ),
    )[0]
    assert welcome['title'] == 'YaPlus Welcome title'
    assert welcome['subtitle'] == 'YaPlus Welcome subtitle'
    assert welcome['action_button']['text'] == 'YaPlus Welcome action text'


@pytest.mark.translations(
    client_messages={'cost_msg_rus': {'ru': 'price is 100 rub'}},
)
@pytest.mark.config(
    YAPLUS_PROMO_BANNER_ENABLED=True,
    YAPLUS_WELCOME_PROMO_BANNER_ENABLED=True,
    YAPLUS_SUMMARY_PROMO_BANNER_COST_BY_COUNTRY={'rus': 'cost_msg_rus'},
)
@pytest.mark.filldb(price_modifiers='plus_promotion')
@pytest.mark.user_experiments('could_buy_plus')
@pytest.mark.user_experiments('plus_summary_promo_login')
@pytest.mark.user_experiments('plus_summary_promo_no_login')
def test_ya_plus_banner_cost_msg(taxi_protocol, db):
    user_id = TEST_USER_ID

    upd = {
        'authorized': True,
        'has_ya_plus': False,
        'yandex_uid_type': 'portal',
    }

    db.users.update({'_id': user_id}, {'$set': upd})

    request_body = {
        'id': user_id,
        'zone_name': 'moscow',
        'size_hint': 100,
        'options': True,
        'supports_hideable_tariffs': True,
    }
    request_headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo', request_body, headers=request_headers,
    )

    assert response.status_code == 200
    data = response.json()

    plus = list(
        filter(
            lambda x: x['type'] == 'ya_plus_promo_banner',
            data.get('brandings', []),
        ),
    )[0]
    assert plus['subtitle'] == 'price is 100 rub'


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    GDPR_COUNTRIES=['kz'],
    NEED_ACCEPT_GDPR=True,
    EULA_POLICY_TTL={'__default__': 86400},
    LOCALES_APPLICATION_PREFIXES={
        'yango_android': 'yango',
        'yango_iphone': 'yango',
    },
    SUPPORTED_FEEDBACK_CHOICES={
        '__default__': {
            'uber_low_rating_reason': ['smellycar', 'badroute', 'notrip'],
        },
        'moscow': {
            'uber_low_rating_reason': [
                'badroute',
                'carcondition',
                'driverlate',
                'nochange',
                'notrip',
                'rudedriver',
                'smellycar',
            ],
        },
    },
    USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=False,
)
@pytest.mark.translations(
    client_messages={
        # GDPR requested (default)
        'gdpr.title': {'ru': 'default gdpr title'},
        'gdpr.text': {'ru': 'default gdpr text'},
        'gdpr.url.title': {'ru': 'default url title'},
        'gdpr.url.content': {'ru': 'default url content'},
        # GDPR requested (specified)
        'gdpr.title.kz': {'ru': 'kz title'},
        'gdpr.text.kz': {'ru': 'kz text'},
        'gdpr.url.title.kz': {'ru': 'gdpr kz url title'},
        'gdpr.url.content.kz': {'ru': 'gdpr kz url content'},
        # Yango GDPR requested (default)
        'yango.gdpr.title': {'ru': 'yango default gdpr title'},
        'yango.gdpr.text': {'ru': 'yango default gdpr text'},
        'yango.gdpr.url.title': {'ru': 'yango default url title'},
        'yango.gdpr.url.content': {'ru': 'yango default url content'},
        # Yango GDPR requested (specified)
        'yango.gdpr.title.kz': {'ru': 'yango kz title'},
        'yango.gdpr.text.kz': {'ru': 'yango kz text'},
        'yango.gdpr.url.title.kz': {'ru': 'yango gdpr kz url title'},
        'yango.gdpr.url.content.kz': {'ru': 'yango gdpr kz url content'},
    },
)
@pytest.mark.parametrize(
    'zone, user_agent, expected_gdpr_title, '
    'expected_gdpr_content, '
    'expected_gdpr_url_title, '
    'expected_gdpr_url_content',
    [
        (
            'moscow',
            'yandex-taxi/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
            None,
            None,
            None,
            None,
        ),
        (
            'moscow',
            'yango/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
            None,
            None,
            None,
            None,
        ),
        (
            'almaty',
            'yandex-taxi/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
            'kz title',
            'kz text',
            'gdpr kz url title',
            'gdpr kz url content',
        ),
        (
            'almaty',
            'yango/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
            'yango kz title',
            'yango kz text',
            'yango gdpr kz url title',
            'yango gdpr kz url content',
        ),
    ],
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_eula(
        taxi_protocol,
        zone,
        user_agent,
        expected_gdpr_title,
        expected_gdpr_content,
        expected_gdpr_url_title,
        expected_gdpr_url_content,
        config,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zone,
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
            'User-Agent': user_agent,
        },
    )

    assert response.status_code == 200
    data = response.json()

    if expected_gdpr_content is not None:
        assert data['need_acceptance'] == [
            {
                'type': 'gdpr',
                'title': expected_gdpr_title,
                'content': expected_gdpr_content,
                'header_image_tag': 'image_gdpr',
                'ttl': 86400,
            },
        ]

        assert data['policies'] == [
            {
                'type': 'gdpr',
                'url_title': expected_gdpr_url_title,
                'url_content': expected_gdpr_url_content,
            },
        ]
    else:
        assert 'need_acceptance' not in response
        assert 'policies' not in response
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.experiments3(filename='exp3_add_drive_cars.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(EULA_POLICY_TTL={'__default__': 86400})
@pytest.mark.translations(
    client_messages={
        'drive.agreement.title': {'ru': 'agreement'},
        'drive.agreement.content': {
            'ru': 'http://drive.yandex/agreement?l=ru',
        },
        'drive.terms_of_use.title': {'ru': 'terms of use'},
        'drive.terms_of_use.content': {'ru': 'http://drive.yandex/terms?l=ru'},
    },
)
@pytest.mark.parametrize(
    'zone,'
    'user_agent,'
    'expected_agreement_title,'
    'expected_agreement_content,'
    'expected_terms_of_use_title,'
    'expected_terms_of_use_content',
    [
        (
            'moscow',
            'yandex-taxi/3.99.0.0 Android/7.1.2 (Xiaomi; Mi A1)',
            'agreement',
            'http://drive.yandex/agreement?l=ru',
            'terms of use',
            'http://drive.yandex/terms?l=ru',
        ),
        (
            'almaty',
            'yandex-taxi/3.99.0.0 Android/7.1.2 (Xiaomi; Mi A1)',
            None,
            None,
            None,
            None,
        ),
        (
            'moscow',
            'yandex-taxi/3.97.0.0 Android/7.1.2 (Xiaomi; Mi A1)',
            None,
            None,
            None,
            None,
        ),
    ],
)
def test_zoneinfo_eula_drive(
        taxi_protocol,
        zone,
        user_agent,
        expected_agreement_title,
        expected_agreement_content,
        expected_terms_of_use_title,
        expected_terms_of_use_content,
):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zone,
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
            'User-Agent': user_agent,
        },
    )

    assert response.status_code == 200
    data = response.json()

    if expected_agreement_title is not None:
        assert data['policies'] == [
            {
                'type': 'drive',
                'url_title': expected_agreement_title,
                'url_content': expected_agreement_content,
            },
            {
                'type': 'drive',
                'url_title': expected_terms_of_use_title,
                'url_content': expected_terms_of_use_content,
            },
        ]
    else:
        assert 'policies' not in response


@pytest.mark.experiments3(filename='exp3_uber_referral_tou.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    EULA_POLICY_TTL={'__default__': 86400},
    ZONEINFO_POLICIES=[
        {
            'type': 'taxi',
            'title': 'uber.terms_of_use.title',
            'content': 'uber.terms_of_use.content',
            'experiment_name': 'uber_referral_tou',
        },
        {
            'type': 'taxi',
            'title': 'uber.terms_of_use.title2',
            'content': 'uber.terms_of_use.content2',
            'experiment_name': 'not_exists',
        },
    ],
)
@pytest.mark.translations(
    client_messages={
        'uber.terms_of_use.title': {'ru': 'terms of use'},
        'uber.terms_of_use.content': {
            'ru': 'https://support-uber.com/action/referral',
        },
        'uber.terms_of_use.title2': {'ru': 'terms of use2'},
        'uber.terms_of_use.content2': {
            'ru': 'https://support-uber.com/action/referral2',
        },
    },
)
@pytest.mark.parametrize(
    'zone,'
    'user_agent,'
    'expected_terms_of_use_title,'
    'expected_terms_of_use_content',
    [
        pytest.param(
            'moscow',
            'yandex-taxi/3.99.0.0 Android/7.1.2 (Xiaomi; Mi A1)',
            'terms of use',
            'https://support-uber.com/action/referral',
            id='show_terms_of_use',
        ),
        pytest.param(
            'moscow',
            'yandex-taxi/3.97.0.0 Android/7.1.2 (Xiaomi; Mi A1)',
            None,
            None,
            id='do_not_show_because_of_app_ver',
        ),
    ],
)
def test_zoneinfo_eula_config(
        taxi_protocol,
        zone,
        user_agent,
        expected_terms_of_use_title,
        expected_terms_of_use_content,
):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zone,
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
            'User-Agent': user_agent,
        },
    )

    assert response.status_code == 200
    data = response.json()

    if expected_terms_of_use_title is not None:
        assert data['policies'] == [
            {
                'type': 'taxi',
                'url_title': expected_terms_of_use_title,
                'url_content': expected_terms_of_use_content,
            },
        ]
    else:
        assert 'policies' not in data


@pytest.mark.config(
    ZONES_TARIFF_GROUPS={
        'moscow': [
            {'group_name': 'thrifty', 'tariffs': ['econom', 'minivan']},
            {'group_name': 'costly', 'tariffs': ['business', 'vip']},
        ],
    },
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
@pytest.mark.translations(
    tariff={
        'group.name.thrifty': {'en': 'Thrifty'},
        'group.name.costly': {'en': 'Costly'},
    },
)
@pytest.mark.parametrize(
    'zone_name,expected',
    [
        (
            'moscow',
            [
                {'name': 'Thrifty', 'classes': ['minivan', 'econom']},
                {'name': 'Costly', 'classes': ['vip', 'business']},
            ],
        ),
        ('almaty', []),
    ],
)
def test_zoneinfo_tariffgroups(
        taxi_protocol,
        zone_name,
        expected,
        config,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zone_name,
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'en',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()
    groups = data['tariff_groups']
    ordered_object.assert_eq(groups, expected, [''])
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['econom', 'business'],
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_short_description(
        taxi_protocol, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )
    assert response.status_code == 200
    data = response.json()['max_tariffs']
    short_descriptions = [cls['short_description'] for cls in data]
    expected = ['Cosy', 'Representative']
    assert short_descriptions == expected
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.experiments3(filename='exp3_comment_screen_requirements.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.translations(
    client_messages={'legal_entities.rus': {'ru': 'OOO Yandex'}},
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_legal_entity(
        taxi_protocol, load_json, config, use_choices_handler, dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()

    expected_result = load_json('zoneinfo_simple_response.json')
    expected_result['legal_entity'] = 'OOO Yandex'

    assert data == expected_result
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    ROUTE_SHOW_JAMS_BY_REGIONS={'__default__': False, 'rus': True},
)
@pytest.mark.parametrize(
    'zonename, expected_show_jams', [('moscow', True), ('almaty', False)],
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_show_jams(
        taxi_protocol,
        load_json,
        zonename,
        expected_show_jams,
        config,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zonename,
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert 'route_show_jams' in data
    assert data['route_show_jams'] == expected_show_jams
    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.experiments3(filename='experiments3_01.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
def test_zoneinfo_exp3(taxi_protocol):
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    content = response.json()
    assert len(content['typed_experiments']['items']) == 1


@pytest.mark.experiments3(filename='exp3_zoneinfo_supports_modes.json')
@pytest.mark.config(
    ZONEINFO_TARIFFS_SETTINGS_BY_MODES_IN_ZONES={
        'moscow': {
            'econom': ['sdc', 'default'],
            'vip': [],
            'business': ['sdc'],
            'minivan': ['sdc', 'default', 'minivan'],
        },
    },
)
@pytest.mark.parametrize(
    'zonename,result_json, user_agent',
    [
        (
            'moscow',
            'zoneinfo_tariff_by_modes_moscow_response_modes_not_supported'
            '.json',
            'yandex-taxi/3.97.2.63189 Android/8.0.0 (samsung; SM-A520F)',
        ),
        (
            'moscow',
            'zoneinfo_tariff_by_modes_moscow_response.json',
            'yandex-taxi/3.107.0.75750 Android/8.1.0 (Xiaomi; Redmi Note 5)',
        ),
        (
            'almaty',
            'zoneinfo_tariff_by_modes_almaty_response.json',
            'yandex-taxi/3.107.0.75750 Android/8.1.0 (Xiaomi; Redmi Note 5)',
        ),
    ],
)
@pytest.mark.now('2017-06-16T12:00:00+0300')
def test_zoneinfo_tariffs_by_modes(
        taxi_protocol, load_json, zonename, result_json, user_agent,
):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': zonename,
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
            'User-Agent': user_agent,
        },
    )

    assert response.status_code == 200
    data = response.json()

    expected_result = load_json(result_json)
    assert data == expected_result


@pytest.mark.config(
    MODES=[
        {'mode': 'default', 'title': 'zone_modes.default_title'},
        {
            'mode': 'sdc',
            'title': 'zone_modes.sdc_title',
            'title_logo': {
                'logo_tag': {
                    'ru': {
                        'default_logo_image_tag': 'default_tag',
                        'logo_overrides': {
                            'main_screen': 'other_logo_ultima',
                            'ride': 'other_logo_ultima',
                            'summary': 'other_logo_ultima',
                        },
                    },
                },
                'options': [
                    {
                        'on': 'select',
                        'actions': [
                            {'type': 'show_popup', 'title': 'sample popup'},
                        ],
                    },
                ],
            },
        },
    ],
    ZONEINFO_TARIFFS_SETTINGS_BY_MODES_IN_ZONES={
        'moscow': {
            'econom': ['sdc', 'default'],
            'vip': [],
            'business': ['sdc'],
            'minivan': ['sdc', 'default', 'minivan'],
        },
    },
)
@pytest.mark.now('2017-06-16T12:00:00+0300')
def test_zoneinfo_zone_modes(taxi_protocol, load_json, config):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'supported': ['support_modes'],
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()
    expected = [
        {
            'classes': ['econom', 'comfortplus', 'minivan'],
            'cover': {},
            'mode': 'default',
            'title': 'Обычный режим',
        },
        {
            'classes': ['econom', 'business', 'minivan'],
            'cover': {},
            'mode': 'sdc',
            'title': 'Беспилотный режим',
            'title_logo': {
                'logo_tag': {
                    'default_logo_image_tag': 'default_tag',
                    'logo_overrides': {
                        'main_screen': 'other_logo_ultima',
                        'ride': 'other_logo_ultima',
                        'summary': 'other_logo_ultima',
                    },
                },
                'options': [
                    {
                        'on': 'select',
                        'actions': [
                            {'type': 'show_popup', 'title': 'sample popup'},
                        ],
                    },
                ],
            },
        },
    ]
    assert data['zone_modes'] == expected


@pytest.mark.config(
    EULA_ACTIONS_IN_TARIFF={
        'business': [],
        'econom': [
            {
                'on': 'order_button_tap',
                'action': {
                    'type': 'show_eula_and_wait_for_accept',
                    'eula_type': 'econom_eula',
                },
            },
            {
                'on': 'order_button_tap',
                'action': {
                    'type': 'show_eula_and_wait_for_accept',
                    'eula_type': 'not_defined',
                },
            },
            {
                'on': 'order_button_tap',
                'action': {
                    'type': 'show_eula_and_wait_for_accept',
                    'eula_type': 'part_eula',
                },
            },
        ],
        'vip': [
            {
                'on': 'order_button_tap',
                'action': {
                    'type': 'show_eula_and_wait_for_accept',
                    'eula_type': 'part_eula',
                },
            },
        ],
    },
    EULA_DEFINITIONS=[
        {
            'type': 'econom_eula',
            'title': 'econom_eula.title',
            'content': 'econom_eula.content',
            'accept_button_title': 'econom_eula.accept_button_title',
            'cancel_button_title': 'econom_eula.cancel_button_title',
            'header_image_tag': 'econom_eula_image',
            'show_on_demand': True,
        },
        {
            'type': 'part_eula',
            'title': 'part_eula.title',
            'content': 'part_eula.content',
            'accept_button_title': 'part_eula.accept_button_title',
            'show_on_demand': False,
        },
    ],
)
@pytest.mark.user_experiments(
    'eula_actions_in_tariff', 'skolkovo_selfdriving_show',
)
@pytest.mark.now('2017-06-16T12:00:00+0300')
def test_zoneinfo_eula_actions_in_tariff(taxi_protocol, load_json):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
            'supported': ['eula_actions'],
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    # we need to check only this two fields
    data = response.json()
    for key in list(data):
        if key not in ('max_tariffs', 'need_acceptance'):
            data.pop(key)
    for tariff in data['max_tariffs']:
        for key in list(tariff):
            if key != 'actions':
                tariff.pop(key)

    expected_result = load_json('zoneinfo_tariffs_actions_response.json')
    assert data == expected_result


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.experiments3(filename='experiments3_superapp.json')
@pytest.mark.parametrize(
    'locale,url,major_version',
    [
        # testcase for common scenario without template
        ('ru', 'experiment_support_url', 4),
        # testcase for url with template experiment_{lang}_support_url
        ('kk', 'experiment_kk_support_url', 4),
        # testcase for lang not in experiment
        ('en', 'https://m.taxi.yandex.com/help', 4),
        # testcase for email
        ('ru', 'experiment_support_url', 6),
    ],
)
def test_zoneinfo_superapp_help(
        taxi_protocol, mockserver, locale, url, major_version,
):
    template = 'ru.yandex.taxi.inhouse/{}.41.8769 (iPhone; iOS 11.0; Darwin)'
    headers = {
        'Accept-Language': locale,
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        'Authorization': 'Bearer test_token',
        'User-Agent': template.format(major_version),
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['support_page']['url'] == url
    if major_version < 5:
        assert 'mailto' not in data['support_page']
    else:
        assert 'mailto' in data['support_page']
        assert data['support_page']['mailto'] == 'go.yandex.com'


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.parametrize(
    'user_info, status_code',
    [
        [{'id': TEST_USER_ID}, 200],
        [{'user': {'user_id': TEST_USER_ID}}, 200],
        [{'id': TEST_USER_ID, 'user': {'user_id': TEST_USER_ID}}, 200],
        [{'id': ''}, 400],
        [{'user': {'id': TEST_USER_ID}}, 400],
        [{'user': {}}, 400],
    ],
)
def test_zoneinfo_any_user_info(taxi_protocol, user_info, status_code):
    request = {'zone_name': 'moscow'}
    request.update(user_info)

    headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
    }

    response = taxi_protocol.post('3.0/zoneinfo', request, headers=headers)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'user_agent,multibranding, econom_exp_tags, comfortplus_exp_tags',
    [
        (
            pytest.param(
                'yandex-taxi/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
                True,
                frozenset(['ya_plus', 'ya_plus_visa', 'visa']),
                frozenset(['visa']),
            )
        ),
        (
            pytest.param(
                'yandex-taxi/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
                True,
                frozenset(['ya_plus', 'ya_plus_visa', 'visa']),
                frozenset(['visa']),
                marks=pytest.mark.experiments3(
                    filename='experiments3_enabled_ride_discounts_call.json',
                ),
                id='ride_discounts_call',
            )
        ),
        (
            pytest.param(
                'yandex-taxi/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
                True,
                frozenset(
                    [
                        'ya_plus',
                        'ya_plus_visa',
                        'visa',
                        'mastercard',
                        'ya_plus_mastercard',
                    ],
                ),
                frozenset(['visa', 'mastercard']),
                marks=pytest.mark.user_experiments('mastercard_discount'),
            )
        ),
        (
            pytest.param(
                'ru.yandex.ytaxi/4.45.11463 '
                '(iPhone; iPhone5,2; iOS 10.3.3; Darwin)',
                True,
                frozenset(['ya_plus', 'ya_plus_mastercard', 'mastercard']),
                frozenset(['mastercard']),
                marks=pytest.mark.user_experiments('mastercard_discount'),
            )
        ),
        (
            pytest.param(
                'ru.yandex.ytaxi/4.45.11463 '
                '(iPhone; iPhone5,2; iOS 10.3.3; Darwin)',
                True,
                frozenset(['ya_plus']),
                frozenset([]),
            )
        ),
        (
            pytest.param(
                'yandex-taxi/3.77.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
                False,
                frozenset(['ya_plus']),
                frozenset([]),
            )
        ),
        (
            pytest.param(
                'ru.yandex.ytaxi/4.44.11463 '
                '(iPhone; iPhone5,2; iOS 10.3.3; Darwin)',
                False,
                frozenset(['ya_plus']),
                frozenset([]),
            )
        ),
    ],
)
@pytest.mark.config(
    YANDEX_PLUS_DISCOUNT={'rus': {'econom': 0.1}},
    VISA_DISCOUNT_PLATFORMS=['android'],
)
@pytest.mark.parametrize(
    'use_choices_handler',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=False,
            ),
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=True,
            ),
        ),
    ],
)
@pytest.mark.config(ZONEINFO_USE_DISCOUNTS_SERVICE=True)
def test_zoneinfo_discounts(
        taxi_protocol,
        user_agent,
        multibranding,
        econom_exp_tags,
        comfortplus_exp_tags,
        config,
        discounts,
        use_choices_handler,
        dummy_choices,
        ride_discounts,
):
    ride_discounts.set_brandings_response(
        {
            'items': [
                {
                    'card_type': 'Visa',
                    'tariff': 'comfortplus',
                    'branding_keys': {},
                },
                {
                    'card_type': 'MIR',
                    'tariff': 'comfortplus',
                    'branding_keys': {},
                },
            ],
        },
    )
    discounts.set_branding_settings_by_zone_response(
        {
            'branding_items': [
                {
                    'classes': ['comfortplus'],
                    'bin_filter': ['400000', '123456', '234567'],
                    'branding_keys': {},
                    'combined_branding_keys': {},
                },
            ],
        },
    )

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 100,
            'options': True,
            'supports_hideable_tariffs': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
            'User-Agent': user_agent,
        },
    )

    assert response.status_code == 200
    data = response.json()

    # discount in econom
    assert data['max_tariffs'][0]['class'] == 'econom'
    assert 'brandings' in data['max_tariffs'][0]
    branding = data['max_tariffs'][0]['brandings']
    assert (
        frozenset([branding[i]['type'] for i in range(len(branding))])
        == econom_exp_tags
    )
    # discount comfortplus
    assert data['max_tariffs'][2]['class'] == 'comfortplus'
    if len(comfortplus_exp_tags) == 0:
        assert 'brandings' not in data['max_tariffs'][2]
    else:
        assert 'brandings' in data['max_tariffs'][2]
        branding = data['max_tariffs'][2]['brandings']
        assert (
            frozenset([branding[i]['type'] for i in range(len(branding))])
            == comfortplus_exp_tags
        )

    assert dummy_choices.was_called() == use_choices_handler


@pytest.mark.experiments3(filename='experiments3_disabled_phone_rules.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.translations(
    client_messages={
        'extra_phone_info.requirement_label': {'ru': 'requirement_label'},
        'extra_phone_info.selected_label': {'ru': 'selected_label'},
        'extra_phone_info.on_empty_popup.button_text': {
            'ru': 'on_empty_popup.button_text',
        },
        'extra_phone_info.on_empty_popup.description': {
            'ru': 'on_empty_popup.description',
        },
        'extra_phone_info.on_empty_popup.title': {
            'ru': 'on_empty_popup.title',
        },
        'extra_phone_info.phone_selection_screen.title': {
            'ru': 'phone_selection_screen.title',
        },
        'extra_phone_info.phone_selection_screen.read_contacts_permission': {
            'ru': 'phone_selection_screen.read_contacts_permission',
        },
        'extra_phone_info.phone_selection_screen.choose_one_label': {
            'ru': 'phone_selection_screen.choose_one_label',
        },
        'extra_phone_info.test.requirement_label': {
            'ru': 'requirement_label.test',
        },
        'extra_phone_info.test.selected_label': {'ru': 'selected_label.test'},
        'extra_phone_info.test.on_empty_popup.button_text': {
            'ru': 'on_empty_popup.button_text.test',
        },
        'extra_phone_info.test.on_empty_popup.description': {
            'ru': 'on_empty_popup.description.test',
        },
        'extra_phone_info.test.on_empty_popup.title': {
            'ru': 'on_empty_popup.title.test',
        },
        'extra_phone_info.test.phone_selection_screen.title': {
            'ru': 'phone_selection_screen.title.test',
        },
        'extra_phone_info.test.phone_selection_screen.'
        'read_contacts_permission': {
            'ru': 'phone_selection_screen.read_contacts_permission.test',
        },
        'extra_phone_info.test.phone_selection_screen.choose_one_label': {
            'ru': 'phone_selection_screen.choose_one_label.test',
        },
    },
)
@pytest.mark.parametrize(
    'for_another_options,expected_status,expected_extra_phones',
    [
        [
            {'__default__': {}, 'econom': {'required': False}},
            200,
            {
                'econom': {
                    'phone_required_popup_properties': {
                        'button_text': 'on_empty_popup.button_text',
                        'description': 'on_empty_popup.description',
                        'title': 'on_empty_popup.title',
                    },
                    'required': False,
                    'requirement_label': 'requirement_label',
                    'selected_label': 'selected_label',
                    'phone_selection_screen': {
                        'title': 'phone_selection_screen.title',
                        'read_contacts_permission': (
                            'phone_selection_screen.read_contacts_permission'
                        ),
                        'choose_one_label': (
                            'phone_selection_screen.choose_one_label'
                        ),
                    },
                },
            },
        ],
        [
            {
                '__default__': {},
                'econom': {
                    'required': True,
                    'tanker_prefix': 'test',
                    'disabled_by_experiment': 'undefined',
                },
            },
            200,
            {
                'econom': {
                    'phone_required_popup_properties': {
                        'button_text': 'on_empty_popup.button_text.test',
                        'description': 'on_empty_popup.description.test',
                        'title': 'on_empty_popup.title.test',
                    },
                    'required': True,
                    'requirement_label': 'requirement_label.test',
                    'selected_label': 'selected_label.test',
                    'phone_selection_screen': {
                        'title': 'phone_selection_screen.title.test',
                        'read_contacts_permission': (
                            'phone_selection_screen.'
                            'read_contacts_permission.test'
                        ),
                        'choose_one_label': (
                            'phone_selection_screen.choose_one_label.test'
                        ),
                    },
                },
            },
        ],
        [
            {
                '__default__': {},
                'econom': {
                    'required': True,
                    'tanker_prefix': 'test',
                    'disabled_by_experiment': 'disabled_phone_rules',
                },
            },
            200,
            None,
        ],
    ],
)
def test_zoneinfo_extra_phone(
        taxi_protocol,
        config,
        for_another_options,
        expected_status,
        expected_extra_phones,
):
    if not expected_extra_phones:
        expected_extra_phones = dict()
    config.set_values(dict(FOR_ANOTHER_OPTIONS_BY_TARIFF=for_another_options))
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == expected_status
    if expected_status != 200:
        return

    data = response.json()
    checked_count = 0
    for tariff in data['max_tariffs']:
        tariff_class = tariff['class']

        if tariff_class not in expected_extra_phones:
            assert 'extra_contact_phone_rules' not in tariff
        else:
            expected_options = expected_extra_phones[tariff_class]
            assert tariff['order_for_other_prohibited']
            assert tariff['extra_contact_phone_rules'] == expected_options
            checked_count += 1

    assert len(expected_extra_phones) == checked_count


@pytest.mark.parametrize(
    'config_value,supports_hideable',
    [
        (['econom', 'comfortplus'], False),
        (['econom', 'comfortplus'], True),
        (['econom'], True),
    ],
)
def test_alice_allowed_tariffs(
        taxi_protocol, config, db, config_value, supports_hideable,
):
    config.set_values({'ALICE_ALLOWED_TARIFFS': config_value})
    db.users.update({'_id': TEST_USER_ID}, {'$set': {'sourceid': 'alice'}})
    request = {
        'id': TEST_USER_ID,
        'zone_name': 'moscow',
        'supports_hideable_tariffs': supports_hideable,
    }
    response = taxi_protocol.post('3.0/zoneinfo', request)
    assert response.status_code == 200, response.text
    tariffs = response.json()['max_tariffs']
    visible_classes = [
        tariff['class'] for tariff in tariffs if not tariff.get('is_hidden')
    ]
    assert sorted(visible_classes) == sorted(config_value), tariffs
    if not supports_hideable:
        return
    response_classes = [tariff['class'] for tariff in tariffs]
    assert sorted(response_classes) == sorted(
        ['business', 'comfortplus', 'econom', 'minivan', 'vip'],
    )


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.config(
    MULTICLASS_ENABLED=True,
    MULTICLASS_TARIFFS_BY_ZONE={'__default__': ['econom', 'comfortplus']},
    MULTICLASS_SELECTOR_ICON='',
)
@pytest.mark.translations(
    client_messages={
        'multiclass.min_selected_count.text': {
            'ru': 'Выберите %(min_count)s и более классов',
        },
        'multiclass.popup.text': {'ru': 'Кто быстрей'},
    },
    tariff={
        'routestats.multiclass.name': {'ru': 'Fast'},
        'routestats.multiclass.details.description': {
            'ru': 'description of multiclass',
        },
        'routestats.multiclass.search_screen.title': {'ru': 'Searching'},
        'routestats.multiclass.search_screen.subtitle': {'ru': 'fastest car'},
        'routestats.multiclass.details.order_button.text': {
            'ru': 'choose tariffs',
        },
    },
)
@pytest.mark.parametrize('default_enabled', [True, False])
def test_zoneinfo_multiclass(
        taxi_protocol, load_json, default_enabled, config,
):

    config.set_values(dict(MULTICLASS_DEFAULT_ENABLED=default_enabled))

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()

    expected_result = load_json('zoneinfo_multiclass.json')
    expected_result['multiclass']['can_be_default'] = default_enabled

    assert data == expected_result


@pytest.mark.now('2019-12-06T12:00:00+0300')
@pytest.mark.experiments3(filename='experiments3_translations.json')
@pytest.mark.config(
    EXPERIMENTS3_CLIENT_TRANSLATIONS=['translatable', 'bad_keys'],
)
@pytest.mark.translations(
    client_messages={
        'exp3.l10n.str': {'en': 'Str translation'},
        'exp3.l10n.field': {'en': 'Field translation'},
    },
)
def test_zoneinfo_exp3_translations(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200
    data = response.json()

    print(data['typed_experiments']['items'])
    ordered_object.assert_eq(
        data['typed_experiments']['items'],
        [
            {
                'name': 'untranslatable',
                'value': {
                    'translate_obj': {
                        'translate_field': '$tanker.exp3.l10n.field',
                    },
                    'translate_str': '$tanker.exp3.l10n.str',
                },
            },
            {
                'name': 'translatable',
                'value': {
                    'translate_obj': {'translate_field': 'Field translation'},
                    'translate_str': 'Str translation',
                    'translatable_arr': ['Str translation', 'Str translation'],
                    'translatable_obj_arr': [
                        {'translate_field': 'Field translation'},
                    ],
                    'untranslatable_str': 'Prefix $tanker.',
                },
            },
        ],
        [''],
    )


@pytest.mark.config(ALICE_ALLOWED_COUNTRIES=[])
def test_zoneinfo_block_alice(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'point': [37.396272, 55.803944],
            'sourceid': 'alice',
        },
    )
    assert response.status_code == 404


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    ALL_CATEGORIES=['child_tariff', 'comfortplus', 'econom'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['child_tariff', 'comfortplus', 'econom'],
    },
    REQUIREMENTS_EXTRA_PARAMS={
        'childchair_v2': {
            'unset_order_button': (
                'compoundselect.childchair_v2.unset_order_button'
            ),
        },
    },
    REQUIREMENTS_PERSISTENCE_STORAGE_KEY={
        'childchair_v2': {
            'storage_key': 'childchair_v2',
            'category_names': ['child_tariff'],
        },
    },
)
@pytest.mark.user_experiments('child_tariff')
@pytest.mark.parametrize(
    'is_replaced, is_supported, is_compoundselect, is_locally_persistent',
    [
        pytest.param(
            False,
            True,
            True,
            False,
            id='default',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_childchair_v2_default.json',
                ),
            ),
        ),
        pytest.param(
            False,
            False,
            False,
            False,
            id='not_supported',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_childchair_v2_matches.json',
                ),
            ),
        ),
        pytest.param(
            True,
            True,
            False,
            False,
            id='multiselect',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_childchair_v2_matches.json',
                ),
            ),
        ),
        pytest.param(
            True,
            True,
            True,
            False,
            id='compoundselect',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_childchair_v2_matches.json',
                ),
                pytest.mark.experiments3(
                    filename='experiments3_compoundselect_support.json',
                ),
            ),
        ),
        pytest.param(
            True,
            True,
            False,
            True,
            id='multiselect, locally_persistent',
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_childchair_v2_matches.json',
                ),
            ),
        ),
    ],
)
def test_zoneinfo_requirement_overrides(
        taxi_protocol,
        config,
        mockserver,
        mongodb,
        is_replaced,
        is_supported,
        is_compoundselect,
        is_locally_persistent,
):
    mongodb.tariff_settings.update(
        {'hz': 'moscow', 's.n': 'child_tariff'},
        {
            '$push': {'s.$.client_requirements': 'childchair_v2'},
            '$set': {'s.$.requirement_flavor': {'childchair_v2': '3_2_2'}},
        },
    )
    mongodb.tariff_settings.update(
        {'hz': 'moscow', 's.n': 'comfortplus'},
        {
            '$push': {'s.$.client_requirements': 'childchair_v2'},
            '$set': {
                's.$.tariff_specific_overrides': {'childchair_v2': False},
                's.$.requirement_flavor': {'childchair_v2': '2_2_3'},
            },
        },
    )
    if is_replaced:
        CHILDCHAIR_ICON['url'] = mockserver.url('static/images/childchair_v2')
    CHILDCHAIR_ICON_DISABLED = {
        **CHILDCHAIR_ICON,
        'image_tag': 'childchair_v2.booster.icon_disabled',
    }
    CHILDCHAIR_ICON_FIRST = {
        **CHILDCHAIR_ICON,
        'image_tag': 'childchair_v2.first.icon_tag',
    }
    CHILDCHAIR_ICON_SECOND = {
        **CHILDCHAIR_ICON,
        'image_tag': 'childchair_v2.second.icon_tag',
    }

    request = {
        'id': TEST_USER_ID,
        'zone_name': 'moscow',
        'size_hint': 100,
        'options': True,
        'supported': [],
    }
    if is_supported:
        request['supported'].append('childchair_v2')
    if is_compoundselect:
        request['supported'].append('compoundselect')
    if is_locally_persistent:
        request['supported'].append('local_persistence_policy')

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        request,
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()

    # don't check zi options exist, assume it just works ;)
    def _check_overrides(reqs, **kwargs):
        req = next(req for req in reqs if req['name'] == 'childchair_v2')
        assert req['unset_order_button'] == 'Choose seats'
        assert req['options_drop_sequence'] == ['booster', 'chair', 'infant']
        if 'tariff_specific' in kwargs:
            tariff_specific = kwargs.pop('tariff_specific')
            if is_locally_persistent:
                assert 'tariff_specific' not in req
                assert 'persistent' not in req
                if tariff_specific:
                    exp_persistence_policy = {'type': 'local'}
                    if 'persistence_storage_key' in kwargs:
                        exp_persistence_policy['storage_key'] = kwargs.pop(
                            'persistence_storage_key',
                        )
                    assert req['persistence_policy'] == exp_persistence_policy
                else:
                    assert 'persistence_policy' not in req
            else:
                assert req['tariff_specific'] == tariff_specific
        if 'max_weight' in kwargs:
            assert req['max_weight'] == kwargs.pop('max_weight')

        for opt in req['select']['options']:
            name = opt['name']
            if name in kwargs:
                expected_opt = kwargs.pop(name)
                if expected_opt is None:
                    raise RuntimeError('unexpected option %s' % name)
                if 'max_count' in expected_opt:
                    assert opt['max_count'] == expected_opt['max_count']
                if 'weight' in expected_opt:
                    assert opt['weight'] == expected_opt['weight']

                if name == 'booster' and is_compoundselect:
                    assert 'title_forms' not in opt
                    assert opt['icon_disabled'] == CHILDCHAIR_ICON_DISABLED
                    assert opt['item_trail'] == 'Бустер, 6-12 лет'
                    assert opt['label_disabled'] == {
                        'max_count': 'Can not choose this type anymore',
                        'max_weight': 'Total number of seats exceeded',
                    }

        if is_compoundselect:
            assert req['type'] == 'compoundselect'
            items_num = kwargs.pop('items_num')

            items = req['compoundselect']['items']
            assert len(items) == items_num
            if items_num == 1:
                assert items == [
                    {
                        'cancel_button': 'Cancel',
                        'description': 'Onbording text',
                        'title': 'Just chair',
                        'title_on_label': 'First chair',
                        'title_popup': 'Just chair',
                        'title_selected': 'First',
                        'trail_placeholder': 'Select',
                        'icon': CHILDCHAIR_ICON_FIRST,
                    },
                ]
            else:
                assert items == [
                    {
                        'cancel_button': 'Cancel',
                        'description': 'Onbording text',
                        'title': 'First chair',
                        'title_on_label': 'First chair',
                        'title_popup': 'First chair',
                        'title_selected': 'First',
                        'trail_placeholder': 'Select',
                        'icon': CHILDCHAIR_ICON_FIRST,
                    },
                    {
                        'cancel_button': 'Cancel',
                        'description': 'Onbording text',
                        'title': 'Second chair',
                        'title_on_label': 'Second chair',
                        'title_popup': 'Second chair',
                        'title_selected': 'Second',
                        'trail_placeholder': 'Select',
                        'icon': CHILDCHAIR_ICON_SECOND,
                    },
                ]

    assert len(data['max_tariffs']) == 3
    for tariff in data['max_tariffs']:
        reqs = tariff['supported_requirements']
        names = [req['name'] for req in reqs]

        if tariff['id'] == 'comfortplus':
            expected, not_expected = (
                ('childchair_v2', 'childchair_moscow')
                if is_replaced
                else ('childchair_moscow', 'childchair_v2')
            )
            assert expected in names
            assert not_expected not in names
            if is_replaced:
                _check_overrides(
                    reqs,
                    tariff_specific=False,
                    max_weight=1,
                    infant={'weight': 2, 'max_count': 3},
                    own_chair=None,
                    items_num=1,
                )

        elif tariff['id'] == 'child_tariff':
            expected, not_expected = (
                ('childchair_v2', 'childchair_for_child_tariff')
                if is_replaced
                else ('childchair_for_child_tariff', 'childchair_v2')
            )
            assert expected in names
            assert not_expected not in names
            if is_replaced:
                _check_overrides(
                    reqs,
                    tariff_specific=True,
                    max_weight=2,
                    booster={'max_count': 3},
                    items_num=2,
                    persistence_storage_key='childchair_v2',
                )

        elif tariff['id'] == 'econom':
            # check redirect also switches to the new requirement
            econom_chair = next(
                req
                for req in tariff['supported_requirements']
                if req['name'] == 'childchair_moscow'
            )
            expected_req = (
                'childchair_v2'
                if is_replaced
                else 'childchair_for_child_tariff'
            )
            assert econom_chair['redirect'] == {
                'tariff_class': 'child_tariff',
                'requirement_name': expected_req,
                'description': 'Available in Kids',
            }
        else:
            assert False, f"Unexpected tariff category: {tariff['id']}"


def make_splash_exp_mark(enabled):
    return pytest.mark.experiments3(
        **{
            'name': 'uber_splash_price',
            'consumers': ['protocol/zoneinfo'],
            'match': {'predicate': {'type': 'true'}, 'enabled': True},
            'clauses': [],
            'default_value': {'enabled': enabled},
        },
    )


@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.experiments3(filename='exp3_comment_screen_requirements.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.parametrize(
    'is_exp_enabled',
    [
        pytest.param(False),
        pytest.param(False, marks=make_splash_exp_mark(False)),
        pytest.param(True, marks=make_splash_exp_mark(True)),
    ],
)
@pytest.mark.parametrize(
    'expected_minimal_price',
    [
        pytest.param(
            42,
            marks=pytest.mark.config(
                ZONEINFO_BRAND_MAP_CATEGORIES_FOR_MINIMAL_PRICE={},
            ),
            id='Check all categories for no brand in config',
        ),
        pytest.param(
            None,
            marks=pytest.mark.config(
                ZONEINFO_BRAND_MAP_CATEGORIES_FOR_MINIMAL_PRICE={'yataxi': []},
            ),
            id='No minimal price for an empty array',
        ),
        pytest.param(
            99,
            marks=pytest.mark.config(
                ZONEINFO_BRAND_MAP_CATEGORIES_FOR_MINIMAL_PRICE={
                    'yataxi': ['econom'],
                },
            ),
            id='Brand present in config',
        ),
    ],
)
def test_zoneinfo_minimal_price(
        taxi_protocol,
        mongodb,
        load_json,
        is_exp_enabled,
        expected_minimal_price,
):
    data = zoneinfo_send_request(taxi_protocol)
    expected_result = load_json('zoneinfo_simple_response.json')

    if is_exp_enabled and expected_minimal_price is not None:
        expected_result['minimal_price'] = expected_minimal_price

    assert data == expected_result


@pytest.mark.experiments3(filename='exp3_hourly_rental.json')
@pytest.mark.experiments3(filename='exp3_comment_screen_requirements.json')
@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.config(WELCOME_SCREEN=WELCOME_SCREEN_DEFAULT)
@pytest.mark.parametrize(
    'is_brand_in_config',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=pytest.mark.config(
                ZONEINFO_SEPARATE_IMAGE_TAG_BRANDS=['yataxi'],
            ),
        ),
    ],
)
def test_separate_brand_images(
        taxi_protocol, mockserver, mongodb, load_json, is_brand_in_config,
):
    CLASSES_WITH_IMAGE = {
        'pool',
        'econom',
        'business',
        'comfortplus',
        'minivan',
        'child_tariff',
        'cargo',
        'vip',
    }
    CLASSES_WITH_PLACEHOLDER = {'poputka'}

    mongodb.images.insert(
        [
            {
                '_id': f'brand_specific_{tariff_class}_image',
                'image_id': f'brand_specific_{tariff_class}_image',
                'size_hint': {
                    'android': 100,
                    'iphone': 9999,
                    'mobileweb': 9999,
                    'web': 9999,
                },
                'tags': [
                    f'class_yataxi_{tariff_class}_car',
                    f'class_yataxi_{tariff_class}_icon',
                ],
            }
            for tariff_class in CLASSES_WITH_IMAGE
        ],
    )
    mongodb.images.insert(
        {
            '_id': f'brand_specific_placeholder_image',
            'image_id': f'brand_specific_placeholder_image',
            'size_hint': {
                'android': 100,
                'iphone': 9999,
                'mobileweb': 9999,
                'web': 9999,
            },
            'tags': [
                f'class_yataxi_placeholder_car',
                f'class_yataxi_placeholder_icon',
            ],
        },
    )

    data = zoneinfo_send_request(taxi_protocol)
    expected_result = load_json('zoneinfo_simple_response.json')

    if is_brand_in_config:
        url_base = mockserver.url('static/images/')
        for tariff in expected_result['max_tariffs']:
            tariff_id = tariff['id']
            if tariff_id in CLASSES_WITH_PLACEHOLDER:
                ph_image_url = f'{url_base}brand_specific_placeholder_image'
                tariff['icon']['url'] = ph_image_url
                tariff['icon']['image_tag'] = 'class_yataxi_placeholder_icon'
                tariff['image']['url'] = ph_image_url
                tariff['image']['image_tag'] = 'class_yataxi_placeholder_car'
                ph_url_pat = (
                    '/static/test-images/brand_specific_placeholder_image'
                )
                tariff['icon']['url_parts']['path'] = ph_url_pat
                tariff['image']['url_parts']['path'] = ph_url_pat
            else:
                img_url = f'{url_base}brand_specific_{tariff_id}_image'
                tariff_class = tariff['class']
                tariff['icon']['url'] = img_url
                tariff['icon'][
                    'image_tag'
                ] = f'class_yataxi_{tariff_class}_icon'
                tariff['image']['url'] = img_url
                tariff['image'][
                    'image_tag'
                ] = f'class_yataxi_{tariff_class}_car'

                url_part = (
                    f'/static/test-images/brand_specific_{tariff_id}_image'
                )
                tariff['icon']['url_parts']['path'] = url_part
                tariff['image']['url_parts']['path'] = url_part

    assert data == expected_result


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'pool': {'visible_by_default': False},
            'poputka': {'visible_by_default': False},
            'econom': {'visible_by_default': False},
            'business': {'visible_by_default': False},
            'comfortplus': {'visible_by_default': False},
            'vip': {'visible_by_default': False},
            'minivan': {'visible_by_default': False},
        },
    },
)
def test_zoneinfo_hide_tariffs(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': TEST_USER_ID,
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )
    assert response.status_code == 404

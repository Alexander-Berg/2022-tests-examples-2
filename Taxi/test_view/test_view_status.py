# pylint: disable=C0302
import copy
import datetime
import json

import pytest


from tests_driver_fix import common


def _native_restricitons_enabled(enabled, supported_features):
    return (
        enabled
        and supported_features
        and 'native_restrictions' in supported_features
    )


def _native_restriction_from_config(title, native_restriction_config):
    restriction = {'title': title}
    restriction['severity'] = native_restriction_config.get(
        'severity', 'warning',
    )
    icon = native_restriction_config.get('icon', {})
    icon['icon_type'] = icon.get('icon_type', 'pulsating')
    restriction['icon'] = icon
    progress_bar = native_restriction_config.get('progress_bar')
    if progress_bar is not None:
        restriction['progress_bar'] = progress_bar
    return restriction


def _restrictions_equal(restrictions, config_restriction) -> bool:
    assert 'id' in restrictions
    restrictions_copy = dict(restrictions)
    restrictions_copy.pop('id')
    return restrictions_copy == config_restriction


@pytest.fixture(autouse=True)
def use_default_by_driver(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-01T00:00:01+03:00',
                        'end_time': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 600,
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {'amount': '1000', 'currency': 'RUB'},
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            ],
        }


@pytest.mark.now('2019-10-15T12:00:00+03')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_status_view_invalid_mode_error(
        mockserver,
        taxi_driver_fix,
        taxi_config,
        use_native_restrictions,
        supported_features,
):
    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        assert request.args['driver_profile_id'] == 'uuid'
        assert request.args['park_id'] == 'dbid'
        return {
            'mode': {
                'name': 'orders',
                'started_at': '2019-05-01T08:00:00+0300',
            },
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 405
    assert response.json() == {'code': '405', 'message': 'NOT ALLOWED'}
    assert _driver_mode_subscription_mode_info.times_called == 1


@pytest.mark.parametrize(
    'mode_info, error_code, message',
    (
        (None, 500, 'Internal Server Error'),
        (
            {'name': 'driver_fix', 'started_at': '2019-05-01T08:00:00+0300'},
            405,
            'NOT ALLOWED',
        ),
        (
            {
                'name': 'driver_fix',
                'started_at': '2019-05-01T08:00:00+0300',
                'features': [{'name': 'tags'}],
            },
            405,
            'NOT ALLOWED',
        ),
        (
            {
                'name': 'driver_fix',
                'started_at': '2019-05-01T08:00:00+0300',
                'features': [{'name': 'driver_fix'}],
            },
            405,
            'NOT ALLOWED',
        ),
    ),
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_status_view_mode_info_error(
        taxi_driver_fix,
        mockserver,
        mode_info,
        error_code,
        message,
        taxi_config,
        use_native_restrictions,
        supported_features,
):
    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        assert request.args['driver_profile_id'] == 'uuid'
        assert request.args['park_id'] == 'dbid'
        return {'mode': mode_info}

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == error_code
    assert response.json() == {'code': str(error_code), 'message': message}


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features',
    (
        None,
        [],
        ['native_restrictions'],
        ['native_restrictions', 'native_restrictions'],
        ['native_restrictions', 'invalid_supported_feature'],
        ['invalid_supported_feature', 'native_restrictions'],
    ),
)
async def test_status_view_ok(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        redis_store,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    if (
            supported_features
            and 'invalid_supported_feature' in supported_features
    ):
        assert response.status_code == 400
        return

    assert response.status_code == 200

    assert {
        'keep_in_busy': False,
        'panel_body': {'items': []},
        'panel_header': {
            'icon': 'time',
            'subtitle': '10;1000 ₽',
            'title': 'Driver-fix',
        },
        'reminiscent_overlay': {'text': '10'},
        'status': 'subscribed',
    } == response.json()

    assert response.headers['X-Polling-Delay'] == '60'


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.parametrize(
    'time, amount, expected_check_val',
    [
        (0, 0, '0;0 ₽'),
        (600, 100, '10;100 ₽'),
        (3600, 100, '1;100 ₽'),
        (3660, 100, '1:1;100 ₽'),
    ],
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_money(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        amount,
        time,
        expected_check_val,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-01T00:00:00+03:00',
                        'end_time': '2019-01-01T23:59:59+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '0',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': time,
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {
                            'amount': str(amount),
                            'currency': 'RUB',
                        },
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    assert {
        'keep_in_busy': False,
        'panel_body': {'items': []},
        'panel_header': {
            'icon': 'time',
            'subtitle': expected_check_val,
            'title': 'Driver-fix',
        },
        'reminiscent_overlay': {
            'text': expected_check_val[0 : expected_check_val.index(';')],
        },
        'status': 'subscribed',
    } == response.json()


@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_vbd_not_found(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )
    assert response.status_code == 200

    assert response.json() == {
        'keep_in_busy': False,
        'panel_body': {'items': []},
        'panel_header': {
            'icon': 'time',
            'subtitle': '0;0 ₽',
            'title': 'Driver-fix',
        },
        'reminiscent_overlay': {'text': '0'},
        'status': 'subscribed',
    }


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    'driver_classes, billing_classes, expected_check_val',
    [
        (['econom', 'business'], ['econom'], True),
        (['econom'], ['econom', 'business'], False),
    ],
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.parametrize(
    'native_restriction_cfg',
    (
        {},
        {
            'classes': {
                'priority': 2,
                'severity': 'info',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
        },
        {
            'classes': {
                'priority': 2,
                'severity': 'error',
                'icon': {'icon_type': 'pulsating'},
                'progress_bar': {'max_time_ms': 2},
            },
        },
    ),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_classes(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        driver_classes,
        billing_classes,
        expected_check_val,
        use_native_restrictions,
        supported_features,
        native_restriction_cfg,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = driver_classes
    mock_offer_requirements.rules_select_value[
        'profile_tariff_classes'
    ] = billing_classes

    common.set_native_restrictions_cfg(
        taxi_config, use_native_restrictions, native_restriction_cfg,
    )

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )
    assert response.status_code == 200
    doc = response.json()
    if expected_check_val:
        assert doc['panel_body']['items'] == []
    else:
        if _native_restricitons_enabled(
                use_native_restrictions, supported_features,
        ):
            assert doc['panel_body']['items'] == []
            config_restriction = _native_restriction_from_config(
                'Не те классы (title)',
                native_restriction_cfg.get('classes', {}),
            )

            assert _restrictions_equal(doc['restriction'], config_restriction)
        else:
            ctor = doc['panel_body']['items'][0]
            assert ctor['title'] == 'Не те классы (preview)'
            assert (
                ctor['payload']['items'][1]['title']
                == 'Нужны классы Эконом, Комфорт'
            )

    assert doc['status'] == 'subscribed'


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    'profile_payment_type, bs_payment_type, expected_check_val',
    [
        ('none', 'none', (True, '')),
        ('none', 'online', (True, '')),
        ('none', 'cash', (True, '')),
        ('none', 'any', (True, '')),
        ('online', 'none', (False, 'Принимать любой способ оплаты')),
        ('online', 'online', (True, '')),
        ('online', 'cash', (False, 'Принимать заказы с наличной оплатой')),
        ('online', 'any', (True, '')),
        ('cash', 'none', (False, 'Принимать любой способ оплаты')),
        ('cash', 'online', (False, 'Принимать заказы по карте')),
        ('cash', 'cash', (True, '')),
        ('cash', 'any', (True, '')),
    ],
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.parametrize(
    'native_restriction_cfg',
    (
        {},
        {
            'payment_type': {
                'priority': 2,
                'severity': 'common',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
        },
        {
            'payment_type': {
                'priority': 2,
                'severity': 'data',
                'icon': {'icon_type': 'pulsating'},
                'progress_bar': {'max_time_ms': 2},
            },
        },
    ),
)
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
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_payment_type(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        profile_payment_type,
        bs_payment_type,
        expected_check_val,
        use_native_restrictions,
        supported_features,
        native_restriction_cfg,
        fetch_payment_type_from_candidates,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    common.set_native_restrictions_cfg(
        taxi_config, use_native_restrictions, native_restriction_cfg,
    )

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

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    doc = response.json()
    if expected_check_val is None or expected_check_val[0]:
        assert doc['panel_body']['items'] == []
    else:
        if _native_restricitons_enabled(
                use_native_restrictions, supported_features,
        ):
            assert doc['panel_body']['items'] == []
            config_restriction = _native_restriction_from_config(
                'Не те payment (title)',
                native_restriction_cfg.get('payment_type', {}),
            )
            assert _restrictions_equal(doc['restriction'], config_restriction)
        else:
            ctor = doc['panel_body']['items'][0]
            assert (
                ctor['payload']['items'][1]['title'] == expected_check_val[1]
            )


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    'native_restriction_cfg',
    (
        {
            'classes': {
                'priority': 2,
                'severity': 'info',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
            'payment_type': {
                'priority': 1,
                'severity': 'common',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
        },
        {
            'classes': {
                'priority': 1,
                'severity': 'data',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
            'payment_type': {
                'priority': 2,
                'severity': 'warning',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
        },
        {
            'classes': {
                'priority': 1,
                'severity': 'error',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
            'payment_type': {
                'priority': 1,
                'severity': 'warning',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
        },
    ),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_restrictions_priority(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        load_json,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        native_restriction_cfg,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom']

    common.set_native_restrictions_cfg(
        taxi_config, True, native_restriction_cfg,
    )
    profile_payment_type = 'online'
    payment_types = mock_offer_requirements.payment_types_values[0][
        'payment_types'
    ]
    for payment_type in payment_types:
        payment_type['active'] = (
            payment_type['payment_type'] == profile_payment_type
        )

    bs_payment_type = 'none'
    mock_offer_requirements.rules_select_value[
        'profile_payment_type_restrictions'
    ] = bs_payment_type
    mock_offer_requirements.rules_select_value['profile_tariff_classes'] = [
        'econom',
        'business',
    ]

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(['native_restrictions']),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    doc = response.json()
    assert doc['panel_body']['items'] == []
    classes_cfg = native_restriction_cfg['classes']
    payment_type_cfg = native_restriction_cfg['payment_type']
    classes_restriction = _native_restriction_from_config(
        'Не те классы (title)', classes_cfg,
    )
    payment_type_restriction = _native_restriction_from_config(
        'Не те payment (title)', payment_type_cfg,
    )
    if classes_cfg['priority'] == payment_type_cfg['priority']:
        assert _restrictions_equal(
            doc['restriction'], classes_restriction,
        ) or _restrictions_equal(doc['restriction'], payment_type_restriction)
    elif classes_cfg['priority'] > payment_type_cfg['priority']:
        assert _restrictions_equal(doc['restriction'], classes_restriction)
    else:
        assert _restrictions_equal(
            doc['restriction'], payment_type_restriction,
        )


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
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
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.parametrize(
    'native_restriction_cfg',
    (
        {},
        {
            'zone': {
                'priority': 2,
                'severity': 'info',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
        },
        {
            'zone': {
                'priority': 2,
                'severity': 'error',
                'icon': {'icon_type': 'pulsating'},
                'progress_bar': {'max_time_ms': 2},
            },
        },
    ),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_driver_position(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        driver_position,
        expected_check_val,
        use_native_restrictions,
        supported_features,
        native_restriction_cfg,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = driver_position

    common.set_native_restrictions_cfg(
        taxi_config, use_native_restrictions, native_restriction_cfg,
    )

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    doc = response.json()
    if expected_check_val is None or expected_check_val[0]:
        assert doc['panel_body']['items'] == []
    else:
        if _native_restricitons_enabled(
                use_native_restrictions, supported_features,
        ):
            assert doc['panel_body']['items'] == []
            assert _restrictions_equal(
                doc['restriction'],
                _native_restriction_from_config(
                    'Не та зона (title)',
                    native_restriction_cfg.get('zone', {}),
                ),
            )
        else:
            ctor = doc['panel_body']['items'][0]
            assert (
                ctor['payload']['items'][1]['title'] == expected_check_val[1]
            )


@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.config(DRIVER_FIX_STATUS_POLLING_DELAY=238)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_custom_polling_delay(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )
    assert response.status_code == 200
    assert response.headers['X-Polling-Delay'] == '238'


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.config(
    DRIVER_FIX_STATUS_SCREEN_CUT_SETTINGS={
        'show_on_busy': 'restrictions',
        'show_on_free': 'restrictions',
    },
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_show_on(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['business']

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    doc = response.json()
    if _native_restricitons_enabled(
            use_native_restrictions, supported_features,
    ):
        assert doc['panel_body']['items'] == []
        assert _restrictions_equal(
            doc['restriction'],
            _native_restriction_from_config('Не те классы (title)', {}),
        )
    else:
        assert doc['panel_body']['items'] != []
        assert (
            doc['panel_body']['collapsed_panel_last_item_busy']
            == 'restrictions'
        )
        assert (
            doc['panel_body']['collapsed_panel_last_item_free']
            == 'restrictions'
        )


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.parametrize(
    'expected_busy',
    [
        pytest.param(
            False,
            marks=[pytest.mark.config(DRIVER_FIX_KEEP_IN_BUSY_REASONS=[])],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(DRIVER_FIX_KEEP_IN_BUSY_REASONS=['zone']),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    DRIVER_FIX_KEEP_IN_BUSY_REASONS=[
                        'classes',
                        'rule_expired',
                    ],
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.parametrize(
    'native_restriction_cfg',
    (
        {},
        {
            'rule_expired': {
                'priority': 2,
                'severity': 'info',
                'icon': {'icon_type': 'static'},
                'progress_bar': {},
            },
        },
        {
            'rule_expired': {
                'priority': 2,
                'severity': 'error',
                'icon': {'icon_type': 'pulsating'},
                'progress_bar': {'max_time_ms': 2},
            },
        },
    ),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_expired(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        expected_busy,
        load_json,
        use_native_restrictions,
        supported_features,
        native_restriction_cfg,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    mock_offer_requirements.rules_select_value = copy.deepcopy(
        mock_offer_requirements.rules_select_value,
    )
    mock_offer_requirements.rules_select_value[
        'start'
    ] = '2018-01-01T00:00:00.000000+03:00'
    mock_offer_requirements.rules_select_value[
        'end'
    ] = '2018-02-01T00:00:00.000000+03:00'

    common.set_native_restrictions_cfg(
        taxi_config, use_native_restrictions, native_restriction_cfg,
    )

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    doc = response.json()
    assert doc['keep_in_busy'] == expected_busy
    assert doc['status'] == 'expired'
    if _native_restricitons_enabled(
            use_native_restrictions, supported_features,
    ):
        assert doc['panel_body']['items'] == []
        assert _restrictions_equal(
            doc['restriction'],
            _native_restriction_from_config(
                'Правило закончилось (title)',
                native_restriction_cfg.get('rule_expired', {}),
            ),
        )
    else:
        ctor = doc['panel_body']['items'][0]
        assert ctor['payload']['items'][1]['title'] == 'Правило закончилось'


@pytest.mark.config(
    DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True,
    DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_use_taximeter_coordinate_as_fallback(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    mock_offer_requirements.set_position_fallback([22.88, 14.88])

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    @mockserver.json_handler('/protocol/3.0/nearestzone')
    def _protocol(request):
        doc = request.json
        assert 'point' in doc
        assert doc['point'] == [22.88, 14.88]
        return {'nearest_zone': 'moscow'}

    params = common.get_enriched_params(supported_features)
    params['lon'] = 22.88
    params['lat'] = 14.88
    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=params,
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('reset_on_shift_close', (True, False))
@pytest.mark.parametrize(
    'shift_close_time, value_arr, expected_check_vals',
    [
        (
            '00:00:00+03:00',
            [
                {
                    'amount': 61,
                    'time': 6000,
                    'start': '2019-01-01T00:00:00+03:00',
                    'end': '2019-01-02T00:00:00+03:00',
                },
            ],
            ('1:40;61 ₽',),
        ),
        (
            '00:00:00+02:00',
            [
                {
                    'amount': 61,
                    'time': 6000,
                    'start': '2019-01-01T00:00:00+02:00',
                    'end': '2019-01-02T00:00:00+02:00',
                },
            ],
            ('1:40;61 ₽',),
        ),
        (
            '00:00:00+04:00',
            [
                {
                    'amount': 61,
                    'time': 6000,
                    'start': '2019-01-01T00:00:00+04:00',
                    'end': '2019-01-02T00:00:00+04:00',
                },
            ],
            ('1:40;61 ₽',),
        ),
        (
            '11:00:59+03:00',
            [
                {
                    'amount': 61,
                    'time': 6000,
                    'start': '2019-01-01T11:00:59+03:00',
                    'end': '2019-01-02T11:00:59+03:00',
                },
            ],
            ('1:40;61 ₽',),
        ),
        (
            '12:00:01+03:00',
            [
                {
                    'amount': 61,
                    'time': 6000,
                    'start': '2018-12-31T12:00:01+03:00',
                    'end': '2019-01-01T12:00:01+03:00',
                },
            ],
            ('1:40;61 ₽',),
        ),
        (
            '12:00:01+03:00',
            [
                {
                    'amount': 61,
                    'time': 30,
                    'start': '2018-12-31T12:00:01+03:00',
                    'end': '2019-01-01T12:00:01+03:00',
                },
                {
                    'amount': 61,
                    'time': 30,
                    'start': '2018-12-31T12:00:01+03:00',
                    'end': '2019-01-01T12:00:01+03:00',
                },
            ],
            ('1;122 ₽',),
        ),
        (
            '12:00:01+03:00',
            [
                {
                    'amount': 61,
                    'time': 31,
                    'start': '2018-12-31T12:00:02+03:00',
                    'end': '2019-01-01T12:00:00+03:00',
                },
                {
                    'amount': 61,
                    'time': 30,
                    'start': '2018-12-31T12:00:01+03:00',
                    'end': '2019-01-01T12:00:01+03:00',
                },
            ],
            ('1;122 ₽',),
        ),
        (
            '12:00:01+03:00',
            [
                {
                    'amount': 61,
                    'time': 29,
                    'start': '2018-12-31T12:00:01+03:00',
                    'end': '2019-01-01T12:00:01+03:00',
                },
                {
                    'amount': 61,
                    'time': 30,
                    'start': '2018-12-31T12:00:01+03:00',
                    'end': '2019-01-01T12:00:01+03:00',
                },
            ],
            ('0;122 ₽',),
        ),
        (
            '12:00:01+03:00',
            [
                {
                    'amount': 61,
                    'time': 60,
                    'start': '2018-12-30T12:00:01+03:00',
                    'end': '2018-12-31T12:00:01+03:00',
                },
                {
                    'amount': 61,
                    'time': 60,
                    'start': '2018-12-31T12:00:01+03:00',
                    'end': '2019-01-01T12:00:01+03:00',
                },
            ],
            ('1;61 ₽', '2;122 ₽'),
        ),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_money_offsets(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        shift_close_time,
        value_arr,
        expected_check_vals,
        reset_on_shift_close,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    taxi_config.set(
        DRIVER_FIX_ONLINE_TIME_RESET_ON_SHIFT_CLOSE_ENABLED=(
            reset_on_shift_close
        ),
    )

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        subventions = []
        for val in value_arr:
            subventions.append(
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': val['start'],
                        'end_time': val['end'],
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': val['time'],
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {
                            'amount': str(val['amount']),
                            'currency': 'RUB',
                        },
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            )
        return {'subventions': subventions}

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        assert request.args['driver_profile_id'] == 'uuid'
        assert request.args['park_id'] == 'dbid'
        return {
            'mode': {
                'name': 'driver_fix_mode',
                'started_at': '2019-05-01T08:00:00+0300',
                'features': [
                    {
                        'name': 'driver_fix',
                        'settings': {
                            'rule_id': 'subvention_rule_id',
                            'shift_close_time': shift_close_time,
                        },
                    },
                    {'name': 'tags'},
                ],
            },
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    expected_check_val = expected_check_vals[0]
    if not reset_on_shift_close:
        expected_check_val = expected_check_vals[-1]

    assert {
        'keep_in_busy': False,
        'panel_body': {'items': []},
        'panel_header': {
            'icon': 'time',
            'subtitle': expected_check_val,
            'title': 'Driver-fix',
        },
        'reminiscent_overlay': {
            'text': expected_check_val[0 : expected_check_val.index(';')],
        },
        'status': 'subscribed',
    } == response.json()


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['shift'])
@pytest.mark.parametrize(
    'client_time_zone, expected_tarification',
    [
        pytest.param(
            'Europe/Moscow',
            {'subdetail': '288 ₽ час', 'subtitle': '01:02 - 24:00'},
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
        ),
        pytest.param(
            'Europe/Moscow',
            {'subdetail': '288 ₽ час', 'subtitle': '00:00 - 12:00'},
            marks=[pytest.mark.now('2019-01-02T11:59:00+0300')],
        ),
        pytest.param(
            'Europe/Moscow',
            {'subdetail': '288 ₽ час', 'subtitle': '00:00 - 12:00'},
            marks=[pytest.mark.now('2019-01-02T00:00:00+0300')],
        ),
        pytest.param(
            'Europe/Moscow',
            {'subdetail': '360 ₽ час', 'subtitle': '00:00 - 01:02'},
            marks=[pytest.mark.now('2019-01-01T01:00:00+0300')],
        ),
        pytest.param(
            'Europe/Moscow',
            {'subdetail': '300 ₽ час', 'subtitle': '00:00 - 05:00'},
            marks=[pytest.mark.now('2018-12-31T01:00:00+0300')],
        ),
        pytest.param(
            'Europe/Moscow',
            {'subdetail': '330 ₽ час', 'subtitle': '05:00 - 13:00'},
            marks=[pytest.mark.now('2018-12-31T06:00:00+0300')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '288 ₽ час', 'subtitle': '03:47 - 24:00'},
            marks=[pytest.mark.now('2019-01-01T12:00:00+0300')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '288 ₽ час', 'subtitle': '00:00 - 14:45'},
            marks=[pytest.mark.now('2019-01-02T11:59:00+0300')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '288 ₽ час', 'subtitle': '00:00 - 14:45'},
            marks=[pytest.mark.now('2019-01-02T00:00:00+0300')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '360 ₽ час', 'subtitle': '00:00 - 03:47'},
            marks=[pytest.mark.now('2019-01-01T01:00:00+0300')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '300 ₽ час', 'subtitle': '02:45 - 07:45'},
            marks=[pytest.mark.now('2018-12-31T01:00:00+0300')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '330 ₽ час', 'subtitle': '07:45 - 15:45'},
            marks=[pytest.mark.now('2018-12-31T06:00:00+0300')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '288 ₽ час', 'subtitle': '03:47 - 24:00'},
            marks=[pytest.mark.now('2019-01-01T12:00:00+0545')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '288 ₽ час', 'subtitle': '00:00 - 14:45'},
            marks=[pytest.mark.now('2019-01-02T11:59:00+0545')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '288 ₽ час', 'subtitle': '00:00 - 14:45'},
            marks=[pytest.mark.now('2019-01-02T00:00:00+0545')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '360 ₽ час', 'subtitle': '00:00 - 03:47'},
            marks=[pytest.mark.now('2019-01-01T01:00:00+0545')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '270 ₽ час', 'subtitle': '00:00 - 02:45'},
            marks=[pytest.mark.now('2018-12-31T01:00:00+0545')],
        ),
        pytest.param(
            'Asia/Kathmandu',
            {'subdetail': '300 ₽ час', 'subtitle': '02:45 - 07:45'},
            marks=[pytest.mark.now('2018-12-31T06:00:00+0545')],
        ),
    ],
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_status_tariffication(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        expected_tarification,
        use_native_restrictions,
        supported_features,
        client_time_zone,
):
    uri = (
        'taximeter://screen/driver_mode?id=driver_fix_mode_subvention_rule_id'
    )
    default_tarrification_item = {
        'horizontal_divider_type': 'bottom_gap',
        'id': 'shift',
        'payload': {'type': 'deeplink', 'url': uri},
        'reverse': True,
        'right_icon': 'navigate',
        'title': 'Тарификация',
        'type': 'detail',
    }

    common.default_init_mock_offer_requirements(mock_offer_requirements)

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    params = common.get_enriched_params(supported_features)
    params['tz'] = client_time_zone
    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=params,
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    ctor = response.json()['panel_body']['items'][0]
    assert {**default_tarrification_item, **expected_tarification} == ctor


@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_FIX_STATUS_PANEL_ITEMS=['wearness'],
    DRIVER_FIX_IMAGE_SETTINGS={
        'enabled': True,
        'weariness_nested_screen_image': {
            'enabled': True,
            'image_url': 'sleepy_driver.png',
        },
    },
)
@pytest.mark.parametrize(
    'test_data',
    [
        pytest.param(
            {'seconds': 0, 'should_show': True},
            marks=[pytest.mark.config(DRIVER_FIX_WEARNESS_WARNING_LIMIT=0)],
        ),
        pytest.param(
            {'seconds': 10, 'should_show': True},
            marks=[pytest.mark.config(DRIVER_FIX_WEARNESS_WARNING_LIMIT=0)],
        ),
        pytest.param(
            {'seconds': 10, 'should_show': False},
            marks=[pytest.mark.config(DRIVER_FIX_WEARNESS_WARNING_LIMIT=11)],
        ),
        pytest.param(
            {'seconds': 10, 'should_show': True},
            marks=[pytest.mark.config(DRIVER_FIX_WEARNESS_WARNING_LIMIT=10)],
        ),
        pytest.param(
            {'seconds': 11, 'should_show': True},
            marks=[pytest.mark.config(DRIVER_FIX_WEARNESS_WARNING_LIMIT=10)],
        ),
    ],
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_status_wearness(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        load_json,
        test_data,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-01T00:00:00+03:00',
                        'end_time': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': test_data['seconds'],
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {'amount': '1000', 'currency': 'RUB'},
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    response_body = response.json()['panel_body']
    if test_data['should_show']:
        assert response_body['items'][0]
        assert response_body['items'][0]['payload'] == load_json(
            'expected_weariness_payload_constructor.json',
        )
    else:
        assert not response_body['items']


@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_FIX_STATUS_PANEL_ITEMS=['shift', 'wearness'],
    DRIVER_FIX_WEARNESS_WARNING_LIMIT=0,
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_status_item_order(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-01T00:00:00+03:00',
                        'end_time': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 10,
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {'amount': '1000', 'currency': 'RUB'},
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    response_body = response.json()['panel_body']
    assert response_body['items'][0]['id'] == 'shift'
    assert response_body['items'][1]['id'] == 'wearness'


@pytest.mark.now('2019-02-01T12:00:00+0300')
@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['payments'])
@pytest.mark.parametrize(
    'test_data',
    [
        {'income': 0, 'guarantee': 0, 'comission': 0},
        {'income': 0, 'guarantee': 10, 'comission': 0},
        {'income': 0, 'guarantee': 10, 'comission': 10},
        {
            'income': 250,
            'guarantee': 100,
            'comission': 150,
            'expected': {
                'type': 'detail',
                'title': 'Получено наличными',
                'detail': '250 ₽',
                'right_icon': 'navigate',
                'horizontal_divider_type': 'bottom_gap',
                'id': 'payments',
                'payload': {
                    'type': 'constructor',
                    'tag': 'tag',
                    'title': 'Доход',
                    'subtitle': 'в режиме «За время»',
                    'items': [
                        {
                            'type': 'detail',
                            'title': 'Время на линии',
                            'subtitle': '15',
                            'reverse': True,
                            'subdetail': '100 ₽',
                            'detail_primary_text_color': '#9E9B98',
                            'horizontal_divider_type': 'bottom_gap',
                        },
                        {
                            'type': 'detail',
                            'title': 'Наличными',
                            'detail': '250 ₽',
                            'detail_primary_text_color': '#9E9B98',
                            'horizontal_divider_type': 'bottom_gap',
                        },
                        {
                            'type': 'detail',
                            'subtitle': 'Переплата',
                            'markdown': True,
                            'reverse': True,
                            'subdetail': '**150 ₽**',
                            'horizontal_divider_type': 'bottom_gap',
                        },
                        {
                            'type': 'text',
                            'horizontal_divider_type': 'none',
                            'text': (
                                'Переплата спишется с баланса в 23:00'
                                ', если наличными вы получите больше'
                                ', чем за время на линии.'
                            ),
                        },
                    ],
                },
            },
        },
        {
            'income': 250,
            'guarantee': 250,
            'comission': 0,
            'expected': {
                'type': 'detail',
                'title': 'Получено наличными',
                'detail': '250 ₽',
                'right_icon': 'navigate',
                'horizontal_divider_type': 'bottom_gap',
                'id': 'payments',
                'payload': {
                    'type': 'constructor',
                    'tag': 'tag',
                    'title': 'Доход',
                    'subtitle': 'в режиме «За время»',
                    'items': [
                        {
                            'type': 'detail',
                            'title': 'Время на линии',
                            'subtitle': '15',
                            'reverse': True,
                            'subdetail': '250 ₽',
                            'detail_primary_text_color': '#9E9B98',
                            'horizontal_divider_type': 'bottom_gap',
                        },
                        {
                            'type': 'detail',
                            'title': 'Наличными',
                            'detail': '250 ₽',
                            'detail_primary_text_color': '#9E9B98',
                            'horizontal_divider_type': 'bottom_gap',
                        },
                        {
                            'type': 'detail',
                            'subtitle': 'Переплата',
                            'markdown': True,
                            'reverse': True,
                            'subdetail': '**0 ₽**',
                            'horizontal_divider_type': 'bottom_gap',
                        },
                        {
                            'type': 'text',
                            'horizontal_divider_type': 'none',
                            'text': (
                                'В случае возникновения переплаты'
                                ' она будет списана в 23:00.'
                            ),
                        },
                    ],
                },
            },
        },
    ],
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
async def test_status_payments(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        test_data,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-31T23:00:00+03:00',
                        'end_time': '2019-01-01T23:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 900,
                        'cash_income': {
                            'amount': str(test_data['income']),
                            'currency': 'RUB',
                        },
                        'guarantee': {
                            'amount': str(test_data['guarantee']),
                            'currency': 'RUB',
                        },
                        'cash_commission': {
                            'amount': str(test_data['comission']),
                            'currency': 'RUB',
                        },
                    },
                },
            ],
        }

    @mockserver.json_handler('/driver-mode-subscription/v1/mode/info')
    def _driver_mode_subscription_mode_info(request):
        assert request.args['driver_profile_id'] == 'uuid'
        assert request.args['park_id'] == 'dbid'
        return {
            'mode': {
                'name': 'driver_fix_mode',
                'started_at': '2019-05-01T08:00:00+0300',
                'features': [
                    {
                        'name': 'driver_fix',
                        'settings': {
                            'rule_id': 'subvention_rule_id',
                            'shift_close_time': '23:00:00+03:00',
                        },
                    },
                    {'name': 'tags'},
                ],
            },
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    response_body = response.json()['panel_body']
    if test_data['income']:
        assert response_body['items'][0] == test_data['expected']
    else:
        assert not response_body['items']


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize(
    'driver_position, rule_end_time, constraint_types',
    [
        ([37.63361316, 55.75419758], '2020-01-01T12:00:00.000000+03:00', []),
        (
            [37.64899583, 55.76904453],  # close to but outside zone
            '2020-01-01T12:00:00.000000+03:00',
            ['zone'],
        ),
        (
            [37.63361316, 55.75419758],
            '2018-02-01T00:00:00.000000+03:00',
            ['rule_expired'],
        ),
        (
            [37.64899583, 55.76904453],  # close to but outside zone
            '2018-02-01T00:00:00.000000+03:00',
            ['rule_expired', 'zone'],
        ),
    ],
)
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_notifications(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        driver_position,
        rule_end_time,
        constraint_types,
        load_json,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['position'] = driver_position
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    mock_offer_requirements.rules_select_value = copy.deepcopy(
        mock_offer_requirements.rules_select_value,
    )
    mock_offer_requirements.rules_select_value[
        'start'
    ] = '2018-01-01T00:00:00.000000+03:00'
    mock_offer_requirements.rules_select_value['end'] = rule_end_time

    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    doc = response.json()
    is_rule_expired = 'rule_expired' in constraint_types
    is_zone = 'zone' in constraint_types
    if is_rule_expired or is_zone:
        assert 'notifications' in doc
        notifications = doc['notifications']
        assert notifications
        assert len(notifications) == len(constraint_types)
        zone_notification_id = 'notification_unmet_zone_constraint'
        rule_expired_notification_id = (
            'notification_unmet_rule_expired_constraint'
        )
        if is_zone:
            notification = notifications[0]
            assert notification['id'] == zone_notification_id
            assert notification['delay_on_order']

            assert 'push_notification' in notification
            push = notification['push_notification']
            assert push == load_json('expected_geozone_push_notification.json')

            assert 'fullscreen_notification' not in notification
        else:
            assert notifications[0]['id'] != zone_notification_id

        if is_rule_expired:
            notification = notifications[-1]
            assert notification['id'] == rule_expired_notification_id
            assert notification['delay_on_order']

            assert 'push_notification' in notification
            push = notification['push_notification']
            assert push == load_json(
                'expected_ruleexpired_push_notification.json',
            )

            assert 'fullscreen_notification' in notification
            fullscreen = notification['fullscreen_notification']
            assert fullscreen == load_json(
                'expected_ruleexpired_fullscreen_notification.json',
            )
        else:
            assert notifications[-1]['id'] != rule_expired_notification_id
    else:
        assert 'notifications' not in doc


@pytest.mark.parametrize(
    'enable_online_time_tags, check_enabled,'
    'zone_tags_config, common_tags_config,'
    'current_tags, add_tags, remove_tags',
    (
        (False, False, None, None, None, None, None),
        (False, True, None, None, None, None, None),
        (True, False, None, None, None, None, None),
        (True, True, None, None, None, None, None),
        # add non-existing tag:
        (
            True,
            True,
            {600: {'add_tags': ['t0'], 'remove_tags': []}},
            None,
            [],
            ['t0'],
            [],
        ),
        # skip add existing tag:
        (
            True,
            True,
            {600: {'add_tags': ['t0'], 'remove_tags': []}},
            None,
            ['t0'],
            [],
            [],
        ),
        # skip add/remove tag:
        (
            True,
            True,
            {600: {'add_tags': ['t0'], 'remove_tags': ['t0']}},
            None,
            [],
            [],
            [],
        ),
        # remove existing tag:
        (
            True,
            True,
            {600: {'add_tags': [], 'remove_tags': ['t0']}},
            None,
            ['t0'],
            [],
            ['t0'],
        ),
        # skip remove non-existing tag:
        (
            True,
            True,
            {600: {'add_tags': [], 'remove_tags': ['t0']}},
            None,
            [],
            [],
            [],
        ),
        # merge with common:
        (
            True,
            True,
            {600: {'add_tags': [], 'remove_tags': ['t0']}},
            {600: {'add_tags': ['t0'], 'remove_tags': []}},
            ['t0'],
            [],
            [],
        ),
        # some combination of tags:
        (
            True,
            True,
            {
                600: {'add_tags': ['t0_0'], 'remove_tags': ['t0_1']},
                601: {'add_tags': ['t1_1'], 'remove_tags': ['t1_1']},
            },
            {
                600: {'add_tags': ['t0_2'], 'remove_tags': ['t0_1']},
                601: {'add_tags': ['t1_3'], 'remove_tags': ['t1_4']},
            },
            ['t0_1', 't0_2', 't1_1', 't1_3'],
            ['t0_0'],
            ['t0_1', 't1_3'],
        ),
        (
            True,
            True,
            None,
            {
                599: {'add_tags': ['t1_1'], 'remove_tags': []},
                600: {'add_tags': ['t2_1'], 'remove_tags': ['t1_1']},
            },
            ['t1_1'],
            ['t2_1'],
            ['t1_1'],
        ),
        (
            True,
            True,
            None,
            {
                601: {'add_tags': ['t1_1'], 'remove_tags': []},
                602: {'add_tags': ['t2_1'], 'remove_tags': ['t1_1']},
            },
            ['t2_1'],
            [],
            ['t2_1'],
        ),
    ),
)
@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_online_tags(
        taxi_driver_fix,
        mockserver,
        driver_tags_mocks,
        mock_offer_requirements,
        stq,
        taxi_config,
        taxi_dms_mock,
        enable_online_time_tags,
        check_enabled,
        zone_tags_config,
        common_tags_config,
        current_tags,
        add_tags,
        remove_tags,
        use_native_restrictions,
        supported_features,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    driver_tags_mocks.set_tags_info('dbid', 'uuid', current_tags)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    common.set_native_restrictions_cfg(taxi_config, use_native_restrictions)
    taxi_config.set_values(
        dict(
            DRIVER_FIX_ONLINE_TIME_TAGS_ENABLED=enable_online_time_tags,
            DRIVER_FIX_STQ_CONFIG=[
                {
                    'enabled': check_enabled,
                    'reschedule_timeshift_ms': 2000,
                    'schedule_timeshift_ms': 2000,
                    'check_settings': {'check_type': 'online_time_tags'},
                },
            ],
        ),
    )
    tags_config = common.generate_online_time_tags_config(
        'moscow', zone_tags_config, common_tags_config,
    )

    if tags_config:
        taxi_config.set_values(dict(DRIVER_FIX_DRIVER_TAGS=tags_config))

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    assert {
        'keep_in_busy': False,
        'panel_body': {'items': []},
        'panel_header': {
            'icon': 'time',
            'subtitle': '10;1000 ₽',
            'title': 'Driver-fix',
        },
        'reminiscent_overlay': {'text': '10'},
        'status': 'subscribed',
    } == response.json()

    assert response.headers['X-Polling-Delay'] == '60'

    assert stq.driver_fix.times_called == bool(add_tags) or bool(remove_tags)

    if stq.driver_fix.times_called:
        kwargs = stq.driver_fix.next_call()['kwargs']
        check_settings_str = kwargs['check_settings']
        check_settings = json.loads(check_settings_str)['check_settings']
        assert check_settings['check_type'] == 'online_time_tags'
        assert check_settings['add_tags'] == add_tags
        assert check_settings['remove_tags'] == remove_tags


@pytest.mark.parametrize('use_reposition_constraints', (True, False))
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_repositions_constraints(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        use_reposition_constraints,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    if use_reposition_constraints:
        taxi_config.set(
            DRIVER_FIX_REPOSITION_TIME_CONSTRAINTS={
                'reposition_time_constraints': [
                    {
                        'reposition_mode_id': 'poi_driver_fix',
                        'min_time_on_line_in_seconds': 4200,
                    },
                    {
                        'reposition_mode_id': 'home_driver_fix',
                        'min_time_on_line_in_seconds': 500,
                    },
                    {
                        'reposition_mode_id': 'strange_mode_id',
                        'min_time_on_line_in_seconds': 4200,
                    },
                ],
            },
        )
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params={'tz': 'Europe/Moscow', 'park_id': 'dbid'},
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    expected_result = {
        'keep_in_busy': False,
        'panel_body': {'items': []},
        'panel_header': {
            'icon': 'time',
            'subtitle': '10;1000 ₽',
            'title': 'Driver-fix',
        },
        'reminiscent_overlay': {'text': '10'},
        'status': 'subscribed',
    }
    if use_reposition_constraints:
        expected_result['reposition_constraints'] = [
            {
                'reposition_mode_id': 'poi_driver_fix',
                'is_usage_allowed': False,
                'dialog': {
                    'title': 'Режим доступен после 1:10 работы на линии',
                    'text': (
                        'Заказы по пути по делам доступны '
                        'после 1:10 работы на линии'
                    ),
                },
            },
            {
                'reposition_mode_id': 'home_driver_fix',
                'is_usage_allowed': True,
            },
            {
                'reposition_mode_id': 'strange_mode_id',
                'is_usage_allowed': False,
                'dialog': {
                    'title': 'Режим доступен после 1:10 работы на линии',
                    'text': 'Режим доступен после 1:10 работы на линии',
                },
            },
        ]
    assert expected_result == response.json()
    assert response.headers['X-Polling-Delay'] == '60'


async def _setup_and_make_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        supported_features,
        restriction_name,
        violate_if,
        apply_if,
        driver_tags,
        should_freeze_timer,
        show_in_status_panel,
        use_ttl=None,
        driver_tags_info=None,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    driver_tags_mocks.set_tags_info(
        'dbid',
        'uuid',
        driver_tags if driver_tags_info is None else None,
        driver_tags_info,
    )
    common.set_native_restrictions_cfg(taxi_config, enabled=True)

    taxi_config.set(
        DRIVER_FIX_CONSTRAINTS_ON_TAGS=(
            common.build_constraint_on_tags_config(
                restriction_name,
                violate_if=violate_if,
                apply_if=apply_if,
                should_freeze_timer=should_freeze_timer,
                show_in_status_panel=show_in_status_panel,
                use_ttl=use_ttl,
            )
        ),
        DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'],
    )

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(
            supported_features=supported_features,
        ),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    return response


@pytest.mark.parametrize('should_freeze_timer', [False, True])
@pytest.mark.parametrize(
    'show_in_status_panel,apply_if',
    [(True, None), (True, {'apply_tag'}), (False, set())],
)
@pytest.mark.parametrize(
    'driver_tags', [{'violate_tag'}, {'apply_tag', 'vioate_tag'}],
)
@pytest.mark.parametrize('violate_if', [{'violate_tag'}, {'never'}])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_restriction_on_tags_native(
        taxi_driver_fix,
        driver_tags_mocks,
        taxi_dms_mock,
        mock_offer_requirements,
        taxi_config,
        violate_if,
        apply_if,
        driver_tags,
        should_freeze_timer,
        show_in_status_panel,
):
    restriction_name = 'test_restriction_on_tags'
    supported_features = ['frozen_penalty_statuses', 'native_restrictions']
    response = await _setup_and_make_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        supported_features,
        restriction_name,
        violate_if=list(violate_if),
        apply_if=list(apply_if) if apply_if else None,
        driver_tags=driver_tags,
        should_freeze_timer=should_freeze_timer,
        show_in_status_panel=show_in_status_panel,
    )

    should_be_applied = apply_if is None or apply_if.issubset(driver_tags)
    if not show_in_status_panel:
        should_be_applied = False

    should_be_violated = violate_if.issubset(driver_tags)

    assert response.status_code == 200
    response_json = response.json()

    if not should_be_applied or not should_be_violated:
        assert 'restriction' not in response_json['panel_body']
        return

    assert (
        response_json['status'] == 'frozen'
        if should_freeze_timer
        else 'subscribed'
    )

    restriction = response_json['restriction']
    assert restriction['title'] == restriction_name + '_title (status)'
    assert restriction['severity'] == 'warning'
    assert restriction['icon'] == {'icon_type': 'pulsating'}


@pytest.mark.parametrize('should_freeze_timer', [False, True])
@pytest.mark.parametrize(
    'show_in_status_panel,apply_if',
    [(True, None), (True, {'apply_tag'}), (False, set())],
)
@pytest.mark.parametrize(
    'driver_tags', [{'violate_tag'}, {'apply_tag', 'vioate_tag'}],
)
@pytest.mark.parametrize('violate_if', [{'violate_tag'}, {'never'}])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_restriction_on_tags_constructor(
        taxi_driver_fix,
        driver_tags_mocks,
        taxi_dms_mock,
        mock_offer_requirements,
        taxi_config,
        violate_if,
        apply_if,
        driver_tags,
        should_freeze_timer,
        show_in_status_panel,
):
    restriction_name = 'test_restriction_on_tags'
    supported_features = []
    response = await _setup_and_make_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        supported_features,
        restriction_name,
        violate_if=list(violate_if),
        apply_if=list(apply_if) if apply_if else None,
        driver_tags=driver_tags,
        should_freeze_timer=should_freeze_timer,
        show_in_status_panel=show_in_status_panel,
    )

    should_be_applied = apply_if is None or apply_if.issubset(driver_tags)
    if not show_in_status_panel:
        should_be_applied = False

    should_be_violated = violate_if.issubset(driver_tags)

    assert response.status_code == 200
    response_json = response.json()

    if not should_be_applied or not should_be_violated:
        assert response_json['panel_body']['items'] == []
        return

    items = response_json['panel_body']['items']
    assert len(items) == 1
    item = items[0]

    assert item['title'] == restriction_name + '_preview (status)'
    assert item['payload']['title'] == restriction_name + '_text (status)'
    assert len(item['payload']['items']) == 2
    assert (
        item['payload']['items'][0]['subtitle']
        == restriction_name + '_caption (status)'
    )
    assert (
        item['payload']['items'][1]['title']
        == restriction_name + '_title (status)'
    )

    expected_button_url = (
        'taximeter://screen/main'
        if should_freeze_timer
        else 'taximeter://screen/driver_mode?id=orders'
    )
    expected_button_text = 'Понятно' if should_freeze_timer else 'На заказы'

    assert (
        item['payload']['bottom_items'][0]['payload']['url']
        == expected_button_url
    )
    assert item['payload']['bottom_items'][0]['title'] == expected_button_text


@pytest.mark.parametrize(
    'now,tags_info,expected_title',
    [
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-01T13:23:15+0000'}},
            'Вы заблокированы до 16:23, осталось 1:23',
        ),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-01T13:00:15+0000'}},
            'Вы заблокированы до 16:00, осталось 1',
        ),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-03T13:11:15+0000'}},
            'Вы заблокированы до 3 января 16:11, осталось 49:11',
        ),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {'ttl': '2019-01-01T10:00:00+0000'}},
            'Вы заблокированы (без TTL)',
        ),
        (
            '2019-01-01T12:00:00',
            {'violate_tag': {}},
            'Вы заблокированы (без TTL)',
        ),
    ],
)
@pytest.mark.config(DRIVER_FIX_FETCH_TAGS_WITH_TTL=True)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_restriction_on_tags_with_ttl(
        taxi_driver_fix,
        driver_tags_mocks,
        taxi_dms_mock,
        mock_offer_requirements,
        mocked_time,
        taxi_config,
        now,
        tags_info,
        expected_title,
):
    mocked_time.set(datetime.datetime.fromisoformat(now))

    response = await _setup_and_make_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        supported_features=['frozen_penalty_statuses', 'native_restrictions'],
        restriction_name='test_ttl_restriction',
        violate_if=['violate_tag'],
        apply_if=None,
        driver_tags=set(tags_info.keys()),
        should_freeze_timer=True,
        show_in_status_panel=True,
        use_ttl=True,
        driver_tags_info=tags_info,
    )

    assert response.status_code == 200
    response_json = response.json()

    restriction = response_json['restriction']
    assert restriction['title'] == expected_title


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
@pytest.mark.now('2019-01-01T12:00:00')
@pytest.mark.config(DRIVER_FIX_FETCH_TAGS_WITH_TTL=True)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_restriction_on_tags_using_formula(
        taxi_driver_fix,
        driver_tags_mocks,
        taxi_dms_mock,
        mock_offer_requirements,
        mocked_time,
        taxi_config,
        driver_tags,
        apply_if,
        violate_if,
        expected_check_val,
):
    restriction_name = 'test_restriction_on_tags'
    response = await _setup_and_make_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        supported_features=['frozen_penalty_statuses', 'native_restrictions'],
        restriction_name=restriction_name,
        violate_if=violate_if,
        apply_if=apply_if,
        driver_tags=driver_tags,
        should_freeze_timer=True,
        show_in_status_panel=True,
    )

    assert response.status_code == 200
    response_json = response.json()

    if expected_check_val is None or expected_check_val is True:
        assert 'restriction' not in response_json['panel_body']
    else:
        assert (
            response_json['restriction']['title']
            == restriction_name + '_title (status)'
        )


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
    ],
)
@pytest.mark.now('2019-01-01T12:00:00')
@pytest.mark.config(DRIVER_FIX_FETCH_TAGS_WITH_TTL=True)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_restriction_on_tags_using_formula_with_ttl(
        taxi_driver_fix,
        driver_tags_mocks,
        taxi_dms_mock,
        mock_offer_requirements,
        mocked_time,
        taxi_config,
        driver_tags_info,
        violate_if,
        expected_text,
):
    response = await _setup_and_make_restriction_on_tags_test(
        taxi_driver_fix,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        supported_features=['frozen_penalty_statuses', 'native_restrictions'],
        restriction_name='test_ttl_restriction',
        violate_if=violate_if,
        apply_if=None,
        driver_tags=None,
        should_freeze_timer=True,
        show_in_status_panel=True,
        use_ttl=True,
        driver_tags_info=driver_tags_info,
    )

    assert response.status_code == 200
    response_json = response.json()

    restriction = response_json['restriction']
    assert restriction['title'] == expected_text


@pytest.mark.parametrize('use_gps_constraint', (True, False))
@pytest.mark.parametrize(
    'fallback_coordinate', ([37.63361316, 55.75419758], None),
)
@pytest.mark.config(DRIVER_FIX_USE_TAXIMETER_GEOPOINT_AS_FALLBACK=True)
@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_coordinate_not_found(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        use_gps_constraint,
        fallback_coordinate,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    taxi_config.set(
        DRIVER_FIX_COORDINATE_NOT_FOUND_CONSTRAINT=use_gps_constraint,
    )

    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']
    mock_offer_requirements.profiles_value['position'] = [0, 0]
    if fallback_coordinate:
        mock_offer_requirements.set_position_fallback(fallback_coordinate)

    request_params = {'tz': 'Europe/Moscow', 'park_id': 'dbid'}
    if fallback_coordinate:
        request_params['lon'] = fallback_coordinate[0]
        request_params['lat'] = fallback_coordinate[1]

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=request_params,
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    if not fallback_coordinate:
        assert response.status_code == 404
        return

    assert response.status_code == 200

    response_json = response.json()

    if not use_gps_constraint:
        assert not response_json['panel_body']['items']
        return

    assert 'items' in response_json['panel_body']
    items = response_json['panel_body']['items']
    assert len(items) == 1
    item = items[0]
    assert 'title' in item
    assert item['title'] == 'Проблемы с GPS (preview)'
    assert 'payload' in item
    assert item['payload']['title'] == 'Проблемы с GPS (text)'
    assert len(item['payload']['items']) == 2
    assert (
        item['payload']['items'][0]['subtitle'] == 'Проблемы с GPS (caption)'
    )
    assert (
        item['payload']['items'][1]['title'] == 'Проблемы с GPS (restriction)'
    )


@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.config(DRIVER_FIX_SEND_TIMER_TOOLTIP=True)
@pytest.mark.config(DRIVER_FIX_TIMER_TOOLTIP_THRESHOLD=60)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.parametrize('use_native_restrictions', (True, False))
@pytest.mark.parametrize(
    'supported_features', (None, [], ['native_restrictions']),
)
@pytest.mark.parametrize(
    'offer_classes,offer_end,accounted_time,expected_show_tooltip',
    [
        (['vip'], '2020-02-01T00:00:00.000000+03:00', 1, False),
        (['econom', 'business'], '2018-02-01T00:00:00.000000+03:00', 1, False),
        (
            ['econom', 'business'],
            '2020-02-01T00:00:00.000000+03:00',
            61,
            False,
        ),
        (['econom', 'business'], '2020-02-01T00:00:00.000000+03:00', 59, True),
    ],
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_show_timer_tooltip(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        load_json,
        use_native_restrictions,
        supported_features,
        offer_classes,
        offer_end,
        accounted_time,
        expected_show_tooltip,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = offer_classes
    mock_offer_requirements.rules_select_value = copy.deepcopy(
        mock_offer_requirements.rules_select_value,
    )
    mock_offer_requirements.rules_select_value[
        'start'
    ] = '2018-01-01T00:00:00.000000+03:00'
    mock_offer_requirements.rules_select_value['end'] = offer_end

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-01T00:00:00+03:00',
                        'end_time': '2019-01-01T23:59:59+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '0',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': accounted_time,
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {'amount': '100', 'currency': 'RUB'},
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    doc = response.json()
    assert doc['show_timer_tooltip'] == expected_show_tooltip


@pytest.mark.config(DRIVER_FIX_USE_BSX_VIRTUAL_BY_DRIVER=True)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_bsx_virtual_by_driver(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        redis_store,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    @mockserver.json_handler('/billing-subventions-x/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': '_id/subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start': '2019-01-01T00:00:01+03:00',
                        'end': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 120,
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {'amount': '1000', 'currency': 'RUB'},
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                        'total_income': {'amount': '1000', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features=None),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    assert _get_by_driver.times_called == 1
    response_json = response.json()
    assert response_json == {
        'panel_header': {
            'title': 'Driver-fix',
            'subtitle': '2;1000 ₽',
            'icon': 'time',
        },
        'panel_body': {'items': []},
        'reminiscent_overlay': {'text': '2'},
        'status': 'subscribed',
        'keep_in_busy': False,
    }


@pytest.mark.config(
    DRIVER_FIX_USE_BSX_VIRTUAL_BY_DRIVER=True,
    DRIVER_FIX_STATUS_PANEL_ITEMS=['payments'],
    DRIVER_FIX_PSEUDO_COMMISSION=[
        {'role': 'role1', 'tag': 'mock_tag1', 'coefficient': 1.051},
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_view_money_with_pseudo_comission(
        taxi_driver_fix,
        mockserver,
        driver_tags_mocks,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        redis_store,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    driver_tags_mocks.set_tags_info('dbid', 'uuid', ['mock_tag1'])
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    @mockserver.json_handler('/billing-subventions-x/v1/virtual_by_driver')
    async def _get_by_driver(request):
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': '_id/subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start': '2019-01-01T00:00:01+03:00',
                        'end': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '0',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 600,
                        'cash_income': {'amount': '1020', 'currency': 'RUB'},
                        'guarantee': {'amount': '1000', 'currency': 'RUB'},
                        'cash_commission': {
                            'amount': '200',
                            'currency': 'RUB',
                        },
                        'total_income': {'amount': '1000', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features=None),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    response_json = response.json()

    assert response_json['panel_header'] == {
        'title': 'Driver-fix',
        'subtitle': '10;1051 ₽',
        'icon': 'time',
    }

    assert response_json['panel_body']['items'][0] == {
        'type': 'detail',
        'title': 'Получено наличными',
        'detail': '1020 ₽',
        'right_icon': 'navigate',
        'horizontal_divider_type': 'bottom_gap',
        'id': 'payments',
        'payload': {
            'type': 'constructor',
            'tag': 'tag',
            'title': 'Доход',
            'subtitle': 'в режиме «За время»',
            'items': [
                {
                    'type': 'detail',
                    'title': 'Время на линии',
                    'subtitle': '10',
                    'reverse': True,
                    'subdetail': '1051 ₽',
                    'detail_primary_text_color': '#9E9B98',
                    'horizontal_divider_type': 'bottom_gap',
                },
                {
                    'type': 'detail',
                    'title': 'Наличными',
                    'detail': '1020 ₽',
                    'detail_primary_text_color': '#9E9B98',
                    'horizontal_divider_type': 'bottom_gap',
                },
                {
                    'type': 'detail',
                    'subtitle': 'Переплата',
                    'markdown': True,
                    'reverse': True,
                    'subdetail': '**20 ₽**',
                    'horizontal_divider_type': 'bottom_gap',
                },
                {
                    'type': 'text',
                    'horizontal_divider_type': 'none',
                    'text': (
                        'Переплата спишется с баланса в 00:00, '
                        'если наличными вы получите больше, '
                        'чем за время на линии.'
                    ),
                },
            ],
        },
    }


@pytest.mark.parametrize(
    'there_is_subvention, expected_subtitle,' 'expected_reminiscent_overlay',
    [(False, '0;0 ₪', '0'), (True, '3;1000 ₪', '3')],
)
@pytest.mark.config(
    DRIVER_FIX_USE_BSX_VIRTUAL_BY_DRIVER=True,
    DRIVER_FIX_ONLINE_TIME_RESET_ON_SHIFT_CLOSE_ENABLED=False,
)
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_different_currency(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        there_is_subvention,
        expected_subtitle,
        expected_reminiscent_overlay,
):
    rule = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
    rule['currency'] = 'ILS'

    mock_offer_requirements.init(
        profiles_value=common.PROFILES_DEFAULT_VALUE,
        dcb_value=common.DCB_DEFAULT_VALUE,
        payment_types_values=common.PAYMENT_TYPES_DEFAULT_VALUES,
        nearestzone_value=common.NEARESTZONE_DEFAULT_VALUE,
        rules_select_value=rule,
        rules_select_value_by_type=None,
        by_driver_subventions=None,
    )

    @mockserver.json_handler('/billing-subventions-x/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        subventions = (
            []
            if not there_is_subvention
            else [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': '_id/subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'ILS'},
                    'period': {
                        'start': '2019-01-01T00:00:01+03:00',
                        'end': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'ILS',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 120,
                        'cash_income': {'amount': '0', 'currency': 'ILS'},
                        'guarantee': {'amount': '1000.12', 'currency': 'ILS'},
                        'cash_commission': {'amount': '0', 'currency': 'ILS'},
                        'total_income': {
                            'amount': '1000.12',
                            'currency': 'ILS',
                        },
                    },
                },
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': '_id/subvention_rule_id',
                    'payoff': {'amount': '99', 'currency': 'RUB'},
                    'period': {
                        'start': '2019-01-01T00:00:01+03:00',
                        'end': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '99',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 60,
                        'cash_income': {'amount': '11', 'currency': 'RUB'},
                        'guarantee': {'amount': '99', 'currency': 'RUB'},
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                        'total_income': {'amount': '99', 'currency': 'RUB'},
                    },
                },
            ]
        )
        return {'subventions': subventions}

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(supported_features=None),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200
    assert _get_by_driver.times_called == 1
    response_json = response.json()
    assert response_json == {
        'panel_header': {
            'title': 'Driver-fix',
            'subtitle': expected_subtitle,
            'icon': 'time',
        },
        'panel_body': {'items': []},
        'reminiscent_overlay': {'text': expected_reminiscent_overlay},
        'status': 'subscribed',
        'keep_in_busy': False,
    }

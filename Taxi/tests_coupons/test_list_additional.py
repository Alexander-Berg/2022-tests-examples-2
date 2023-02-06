import pytest

from tests_coupons import util


@pytest.mark.parametrize(
    'version_in',
    [
        pytest.param(None, id='none_version_in'),
        pytest.param('4001:1', id='some_version_in'),
    ],
)
@pytest.mark.parametrize(
    'uids,expected_codes',
    [
        pytest.param(
            ['4001', '4002', '4003'],
            ['percentreferral', 'secondpromocode', 'firstpromocode'],
        ),
    ],
)
async def test_version(
        taxi_coupons,
        mongodb,
        uids,
        version_in,
        expected_codes,
        local_services,
):
    if version_in:
        encode_version = util.encode_version(version_in)
    request = util.mock_request_list(
        uids, version=encode_version if version_in else None,
    )
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()
    assert util.decode_version(response.json()['version']) == '4001:1,4002:1'

    response_codes = [x['code'] for x in response_json['coupons']]
    assert response_codes == expected_codes


SERVICES_TITLES_CONFIG = {
    'taxi': {
        'title_for_one': 'coupons.ui.block_title.for_one.taxi',
        'title_for_many': 'coupons.ui.block_title.for_many.taxi',
    },
    'eats': {
        'title_for_one': 'coupons.ui.block_title.for_one.eda',
        'title_for_many': 'coupons.ui.block_title.for_many.eda',
    },
    'grocery': {
        'title_for_one': 'coupons.ui.block_title.for_one.lavka',
        'title_for_many': 'coupons.ui.block_title.for_many.lavka',
    },
}

EDA_ACTION = {
    'type': 'deeplink',
    'deeplink': 'eda://link',
    'title': 'Это сообщение еды',
}

LAVKA_ACTION = {
    'type': 'deeplink',
    'deeplink': 'lavka://link',
    'title': 'Это сообщение лавки',
}


@pytest.mark.translations(
    client_messages={
        'list.additional_action.lavka': {'ru': 'Это сообщение лавки'},
        'list.additional_action.eda': {'ru': 'Это сообщение еды'},
    },
)
@pytest.mark.config(COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG)
@pytest.mark.parametrize(
    'uids,promocodes,expected_actions',
    [
        # For user 4018 we have two promocodes: with empty services
        # list and with taxi. Testing that everything will be fine
        # if we pass empty list or only taxi
        pytest.param(['4018'], [], [], id='empty_plus_taxi'),
        # Promocode with three services inside, we have to return
        # only one on which we have additional action (lavka).
        # The rest will be ignored.
        pytest.param(
            [],
            ['servicespromocode'],
            [LAVKA_ACTION],
            marks=pytest.mark.config(
                COUPONS_ADDITIONAL_ACTIONS_CONFIG={
                    'grocery': {
                        'deeplink': 'lavka://link',
                        'title': 'list.additional_action.lavka',
                    },
                },
            ),
            id='taxi_eda_lavka_promocode_one_additional_action',
        ),
        # Same as previous test, but with two expected additional
        # actions in respone
        pytest.param(
            [],
            ['servicespromocode'],
            [EDA_ACTION, LAVKA_ACTION],
            id='taxi_eda_lavka_two_additional_actions',
            marks=pytest.mark.config(
                COUPONS_ADDITIONAL_ACTIONS_CONFIG={
                    'eats': {
                        'deeplink': 'eda://link',
                        'title': 'list.additional_action.eda',
                    },
                    'grocery': {
                        'deeplink': 'lavka://link',
                        'title': 'list.additional_action.lavka',
                    },
                },
            ),
        ),
    ],
)
async def test_promocodes_additional_actions(
        taxi_coupons,
        mongodb,
        uids,
        promocodes,
        expected_actions,
        local_services,
):
    if uids == []:
        yandex_uids = [
            util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb),
        ]
    else:
        yandex_uids = uids

    request = util.mock_request_list(yandex_uids)
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()

    for coupon in response_json['coupons']:
        for action in coupon['action']['actions']:
            assert action in expected_actions


@pytest.mark.parametrize(
    'promocodes,selected_promocodes,application_name',
    [
        pytest.param(
            ['onlylavka1'],
            [],
            'iphone',
            id='external_promocode_is_not_selected',
        ),
        pytest.param(
            ['servicespromocode'],
            ['servicespromocode'],
            'iphone',
            id='promocode_with_several_services_is_selected',
        ),
    ],
)
async def test_promocodes_select_only_if_taxi_service_exists(
        taxi_coupons,
        promocodes,
        selected_promocodes,
        mongodb,
        application_name,
        local_services,
):
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)
    request = util.mock_request_list([uid], application_name)
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()

    assert 'coupons' in response_json
    for coupon in response_json['coupons']:
        is_selected = coupon['code'] in selected_promocodes
        assert coupon['selected'] is is_selected


VALID_EXTERNAL_SERVICES = ['eats', 'grocery']


@pytest.mark.config(COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG)
@pytest.mark.parametrize(
    (
        'valid',
        'eats_result_code',
        'error_code',
        'promocode_type',
        'services',
        'taxi_services',
    ),
    [
        pytest.param(
            True,
            200,
            None,
            'fixed',
            ['eats'],
            ['eats'],
            id='valid_eats_coupon_fixed',
        ),
        pytest.param(
            True,
            200,
            None,
            'fixed',
            ['grocery'],
            ['grocery'],
            id='valid_grocery_coupon_fixed',
        ),
        pytest.param(
            True,
            200,
            None,
            'percent',
            ['eats'],
            ['eats'],
            id='valid_eats_coupon_percent',
        ),
        pytest.param(
            True,
            200,
            None,
            'text',
            ['eats'],
            ['eats'],
            id='valid_eats_coupon_text',
        ),
        pytest.param(
            False,
            200,
            None,
            'fixed',
            ['eats'],
            ['eats'],
            id='not_valid_eats_coupon',
        ),
        pytest.param(
            False,
            200,
            'not_found',
            None,
            None,
            None,
            id='not_found_eats_coupon',
        ),
        pytest.param(
            None, 200, None, None, None, None, id='error_empty_eats_response',
        ),
        pytest.param(
            None, 400, None, None, None, None, id='eats_error_bad_request',
        ),
        pytest.param(
            None, 401, None, None, None, None, id='eats_error_unauthorized',
        ),
        pytest.param(
            None, 404, None, None, None, None, id='eats_error_not_found',
        ),
        pytest.param(
            None, 500, None, None, None, None, id='eats_internal_server_error',
        ),
        pytest.param(
            True,
            200,
            None,
            'fixed',
            ['unknown_service'],
            None,
            id='bad_promocode_unknown_service',
        ),
        pytest.param(
            True,
            200,
            None,
            'fixed',
            ['eats', 'grocery'],
            ['eats', 'grocery'],
            id='promocode_with_two_services',
        ),
        pytest.param(
            True,
            200,
            None,
            'fixed',
            ['eats', 'unknown_service'],
            ['eats'],
            id='promocode_with_one_unknown_service',
        ),
    ],
)
# pass yandex_uids as a parameter for eats_local_server mock
@pytest.mark.parametrize('yandex_uids', [pytest.param(['4019'])])
async def test_promocodes_list_eda_external_coupon(
        taxi_coupons,
        local_services,
        eats_local_server,
        valid,
        eats_result_code,
        error_code,
        promocode_type,
        services,
        taxi_services,
        yandex_uids,
):
    application_name = 'iphone'
    promocodes_services = ['taxi'] + (services or [])
    request = util.mock_request_list(
        yandex_uids, application_name, services=promocodes_services,
    )
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200

    if valid is not None:
        coupon = response.json()['coupons'][0]
        assert coupon['code'] == 'edaexternal'
        if valid and any(i in VALID_EXTERNAL_SERVICES for i in services):
            assert coupon['status'] == 'valid'
            assert set(coupon['services']) == set(taxi_services)
            if promocode_type == 'fixed':
                title = 'Скидка 100 $SIGN$$CURRENCY$'
            elif promocode_type == 'percent':
                title = 'Скидка 20%'
            elif promocode_type == 'text':
                title = 'Подарок за первый заказ'
            assert coupon['title'] == title

            action = coupon['action']
            assert action['title'] == title
            assert len(action['descriptions']) == 1
            assert (
                action['descriptions'][0]['text'] == 'Промокод на первый заказ'
            )
            assert not action['details']
        else:
            assert coupon['status'] != 'valid'
            assert coupon['error']['code'] == (
                'ERROR_EXTERNAL_VALIDATION_FAILED'
                if valid
                else 'ERROR_EXTERNAL_INVALID_CODE'
            )
    else:
        assert not response.json()['coupons']


@pytest.mark.config(COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG)
@pytest.mark.parametrize(
    (
        'valid',
        'eats_result_code',
        'error_code',
        'promocode_type',
        'services',
        'yandex_uids',
    ),
    [pytest.param(True, 200, None, 'fixed', ['eats'], ['4019'])],
)
async def test_external_promocodes_no_services_in_request(
        taxi_coupons,
        local_services,
        eats_local_server,
        valid,
        eats_result_code,
        error_code,
        promocode_type,
        services,
        yandex_uids,
):
    application_name = 'iphone'
    request = util.mock_request_list(yandex_uids, application_name)
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200
    assert len(response.json()['coupons']) == 1
    coupon = response.json()['coupons'][0]
    assert coupon['services'] == services


@pytest.mark.config(
    COUPONS_USER_AGENT_RESTRICTIONS={
        'hon30': '^.+\\(HUAWEI; (BMH|EBG)-AN10\\)$',
    },
)
@pytest.mark.parametrize(
    'code, need_check_ua',
    [
        pytest.param('prefixhonsuffix', False),
        pytest.param('prefixhon30suffix', False),
        pytest.param('hon30', False),
        pytest.param('hon30suffix', True),
    ],
)
@pytest.mark.parametrize(
    'user_agent, ua_match',
    [
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; CLT-L29)',
            False,
            id='other_huawei',
        ),
        pytest.param(
            'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)',
            False,
            id='other_android',
        ),
        pytest.param(
            'ru.yandex.taxi/9.99.9 (iPhone; x86_64; iOS 12.2; Darwin)',
            False,
            id='iphone',
        ),
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; BMH-AN10)',
            True,
            id='honor_30',
        ),
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; EBG-AN10)',
            True,
            id='honor_30_pro',
        ),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_reserve_user_agent(
        taxi_coupons,
        mongodb,
        local_services,
        code,
        need_check_ua,
        user_agent,
        ua_match,
):
    yandex_uids = [
        util.generate_virtual_user_coupons({code}, 'yataxi', mongodb),
    ]
    request = util.mock_request_list(yandex_uids)

    local_services.add_card()
    response = await util.make_list_request(
        taxi_coupons, request, headers={'User-Agent': user_agent},
    )

    assert response.status_code == 200
    content = response.json()

    valid = not need_check_ua or ua_match
    assert len(content['coupons']) == 1
    coupon = response.json()['coupons'][0]
    if valid:
        assert coupon['status'] == 'valid'
        assert coupon['code'] == code
    else:
        assert coupon['status'] == 'invalid'
        assert coupon['error']['code'] == 'ERROR_MANUAL_ACTIVATION_IS_REQUIRED'


SERIES_TO_EXCLUDE = ['paymentmethods', 'nonexisting series id']


@pytest.mark.config(
    COUPONS_SERIES_TO_EXCLUDE_FROM_COUPONLIST=SERIES_TO_EXCLUDE,
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_remove_promocodes_with_specified_series(
        taxi_coupons, local_services, mongodb,
):
    yandex_uids = ['4015']
    expected_coupon_codes = ['emptypaymentmethods1', 'bizpaymentmethod1']

    def check_coupons_in_db():
        initial_expected_coupon_codes = [
            'emptypaymentmethods1',
            'bizpaymentmethod1',
            'paymentmethods1',
        ]
        user_coupons = mongodb.user_coupons.find_one(
            {'yandex_uid': yandex_uids[0]},
        )
        initial_coupon_codes = [
            coupon['code'] for coupon in user_coupons['promocodes']
        ]
        assert sorted(initial_coupon_codes) == sorted(
            initial_expected_coupon_codes,
        )

    check_coupons_in_db()

    request = util.mock_request_list(yandex_uids)
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()
    coupons_codes = [coupon['code'] for coupon in response_json['coupons']]

    check_coupons_in_db()
    assert sorted(expected_coupon_codes) == sorted(coupons_codes)


@pytest.mark.config(COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG)
@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    (
        'valid',
        'eats_result_code',
        'error_code',
        'promocode_type',
        'services',
        'taxi_services',
    ),
    [
        pytest.param(
            True,
            200,
            None,
            'percent',
            ['eats'],
            ['eats'],
            id='valid_eats_coupon_fixed',
        ),
    ],
)
# pass yandex_uids as a parameter for eats_local_server mock
@pytest.mark.parametrize('yandex_uids', [pytest.param(['4021'])])
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_promocodes_list_eats_coupon(
        taxi_coupons,
        localizations,
        local_services,
        eats_local_server,
        valid,
        eats_result_code,
        error_code,
        promocode_type,
        services,
        taxi_services,
        yandex_uids,
):
    local_services.add_card()
    application_name = 'eats_iphone'
    request = util.mock_request_list(
        yandex_uids, application_name, services=services,
    )
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200

    coupon = response.json()['coupons'][0]
    assert coupon['services'] == ['eats']
    assert coupon['code'] == 'edapromic'
    assert coupon['title'] == '400 $SIGN$$CURRENCY$ на заказ в еде'

    action = coupon['action']
    assert action['title'] == 'Скидка 400 $SIGN$$CURRENCY$'
    assert action['descriptions'][0]['text'] == '2 заказов в еде'


@pytest.mark.config(COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG)
@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    (
        'valid',
        'eats_result_code',
        'error_code',
        'promocode_type',
        'services',
        'taxi_services',
    ),
    [
        pytest.param(
            True,
            200,
            None,
            'percent',
            ['eats'],
            ['eats'],
            id='valid_eats_coupon_fixed',
        ),
    ],
)
# pass yandex_uids as a parameter for eats_local_server mock
@pytest.mark.parametrize('yandex_uids', [pytest.param(['4022'])])
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_promocodes_list_eats_coupon_series_description(
        taxi_coupons,
        localizations,
        local_services,
        eats_local_server,
        valid,
        eats_result_code,
        error_code,
        promocode_type,
        services,
        taxi_services,
        yandex_uids,
):
    local_services.add_card()
    application_name = 'eats_iphone'
    request = util.mock_request_list(
        yandex_uids, application_name, services=services,
    )
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200

    coupon = response.json()['coupons'][0]
    assert coupon['services'] == ['eats']
    assert coupon['code'] == 'edapromic2'
    assert coupon['title'] == '20% на заказ в еде'

    action = coupon['action']
    assert action['title'] == 'Скидка 20%'
    assert (
        action['descriptions'][0]['text']
        == '2 заказов в ресторане (описание из серии)'
    )

import pytest

from test_persey_payments import conftest


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[123])
@pytest.mark.pgsql('persey_payments', files=['create.sql'])
@pytest.mark.parametrize(
    [
        'request_json',
        'request_headers',
        'expected_resp',
        'expected_ride_subs',
        'expected_events',
        'expected_seen_bound_uids',
    ],
    [
        (
            {
                'subscription_source': 'new_platform',
                'brands': {
                    'yataxi': {'mod': 123, 'goal': {'fund_id': 'friends'}},
                    'lavka': {'mod': 10, 'goal': {'fund_id': 'friends'}},
                },
            },
            {
                'X-Yandex-UID': 'phonish_uid',
                'X-YaTaxi-PhoneId': 'bbbbbbbbbbbbbbbbbbbbbbbb',
                'X-YaTaxi-Pass-Flags': 'phonish',
                'X-Request-Application': 'app_name=android,app_brand=yataxi',
                'X-Request-Language': 'ru',
            },
            'expected_resp_create.json',
            'expected_ride_subs_create.json',
            'expected_events_create.json',
            [],
        ),
        pytest.param(
            {
                'brands': {
                    'yataxi': {'mod': 123, 'goal': {'fund_id': 'friends'}},
                    'lavka': {'mod': 10, 'goal': {'fund_id': 'friends'}},
                },
            },
            {
                'X-Yandex-UID': 'phonish_uid',
                'X-YaTaxi-PhoneId': 'bbbbbbbbbbbbbbbbbbbbbbbb',
                'X-YaTaxi-Pass-Flags': 'phonish',
                'X-Request-Application': 'app_name=android,app_brand=yataxi',
                'X-Request-Language': 'ru',
            },
            'expected_resp_create_with_retry.json',
            'expected_ride_subs_create_with_retry.json',
            'expected_events_create_with_retry.json',
            [],
            marks=pytest.mark.pgsql(
                'persey_payments', files=['create_with_retry.sql'],
            ),
        ),
        (
            {
                'brands': {
                    'yataxi': {'mod': 123, 'goal': {'fund_id': 'friends'}},
                    'lavka': {'mod': 10, 'goal': {'fund_id': 'friends'}},
                },
            },
            {
                'X-Yandex-UID': 'phonish_uid',
                'X-YaTaxi-PhoneId': 'bbbbbbbbbbbbbbbbbbbbbbbb',
                'X-YaTaxi-Pass-Flags': 'phonish',
                'X-Request-Application': 'app_brand=yataxi',
                'X-Request-Language': 'ru',
            },
            'expected_resp_create.json',
            'expected_ride_subs_create_no_application.json',
            'expected_events_create.json',
            [],
        ),
    ],
)
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_create(
        taxi_persey_payments_web,
        stq,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        platform,
        request_json,
        request_headers,
        expected_resp,
        expected_ride_subs,
        expected_events,
        expected_seen_bound_uids,
):
    response = await taxi_persey_payments_web.post(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/ride_subs',
        json=request_json,
        headers=request_headers,
    )

    assert response.status == 201, await response.json()
    assert await response.json() == load_json(expected_resp)
    assert get_ride_subs('application', 'subscription_source') == load_json(
        expected_ride_subs,
    )
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['create.sql'])
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_create_mod_whitelist(
        taxi_persey_payments_web,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        platform,
):
    response = await taxi_persey_payments_web.post(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/ride_subs',
        json={
            'brands': {
                'yataxi': {'mod': 123, 'goal': {'fund_id': 'friends'}},
                'lavka': {'mod': 10, 'goal': {'fund_id': 'friends'}},
            },
        },
        headers={
            'X-Yandex-UID': 'phonish_uid',
            'X-YaTaxi-PhoneId': 'bbbbbbbbbbbbbbbbbbbbbbbb',
            'X-YaTaxi-Pass-Flags': 'phonish',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-Request-Language': 'ru',
        },
    )

    assert response.status == 400
    assert (await response.json())['code'] == 'MOD_NOT_ALLOWED'
    assert get_ride_subs('application') == load_json(
        'expected_ride_subs_create_mod_whitelist.json',
    )
    check_ride_subs_events('expected_events_empty.json')
    assert get_seen_bound_uids() == []


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    [
        'request_brands',
        'request_headers',
        'expected_resp',
        'expected_ride_subs',
        'expected_events',
        'expected_seen_bound_uids',
    ],
    [
        pytest.param(
            'yataxi,lavka',
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-Bound-Uids': 'phonish_uid',
                'X-Request-Application': 'app_name=android',
                'X-Request-Language': 'ru',
            },
            'expected_resp_read.json',
            'expected_ride_subs_read.json',
            'expected_events_read.json',
            [['portal_uid', 'phonish_uid']],
            marks=pytest.mark.pgsql('persey_payments', files=['read.sql']),
        ),
        pytest.param(
            'yataxi,lavka',
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-Bound-Uids': 'phonish_uid',
                'X-Request-Application': 'app_name=android',
                'X-Request-Language': 'ru',
            },
            'expected_resp_no_subs_but_contribution.json',
            'expected_ride_subs_no_subs_but_contribution.json',
            'expected_events_empty.json',
            [['portal_uid', 'phonish_uid']],
            marks=pytest.mark.pgsql(
                'persey_payments', files=['no_subs_but_contribution.sql'],
            ),
        ),
    ],
)
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_read(
        taxi_persey_payments_web,
        stq,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        platform,
        request_brands,
        request_headers,
        expected_resp,
        expected_ride_subs,
        expected_events,
        expected_seen_bound_uids,
):
    response = await taxi_persey_payments_web.get(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/ride_subs',
        params={'brands': request_brands},
        headers=request_headers,
    )

    assert response.status == 200, await response.json()
    assert await response.json() == load_json(expected_resp)
    assert get_ride_subs() == load_json(expected_ride_subs)
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    [
        'request_brands',
        'request_headers',
        'expected_resp',
        'expected_ride_subs',
        'expected_events',
        'expected_seen_bound_uids',
    ],
    [
        pytest.param(
            'yataxi,lavka',
            {'X-Yandex-UID': 'portal_uid', 'X-Request-Language': 'ru'},
            'expected_resp_read.json',
            'expected_ride_subs_read.json',
            'expected_events_read.json',
            [['portal_uid', 'phonish_uid']],
            marks=pytest.mark.pgsql('persey_payments', files=['read.sql']),
        ),
        pytest.param(
            'yataxi,lavka',
            {'X-Yandex-UID': 'portal_uid', 'X-Request-Language': 'ru'},
            'expected_resp_no_subs_but_contribution.json',
            'expected_ride_subs_no_subs_but_contribution.json',
            'expected_events_empty.json',
            [['portal_uid', 'phonish_uid']],
            marks=pytest.mark.pgsql(
                'persey_payments', files=['no_subs_but_contribution.sql'],
            ),
        ),
        pytest.param(
            'yataxi,lavka',
            {'X-Yandex-UID': 'portal_uid', 'X-Request-Language': 'ru'},
            'expected_resp_read.json',
            'expected_ride_subs_read.json',
            'expected_events_read.json',
            [],
            marks=[
                pytest.mark.pgsql('persey_payments', files=['read.sql']),
                pytest.mark.config(PERSEY_PAYMENTS_TRACK_BOUND_UIDS=False),
            ],
        ),
    ],
)
async def test_read_internal(
        taxi_persey_payments_web,
        stq,
        load_json,
        mock_zalogin,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        request_brands,
        request_headers,
        expected_resp,
        expected_ride_subs,
        expected_events,
        expected_seen_bound_uids,
):
    zalogin_mock = mock_zalogin('portal_uid', 'zalogin_resp.json')
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/multibrand/ride_subs',
        params={'brands': request_brands},
        headers=request_headers,
    )

    assert response.status == 200, await response.json()
    assert await response.json() == load_json(expected_resp)
    assert get_ride_subs() == load_json(expected_ride_subs)
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids
    assert zalogin_mock.times_called == 1


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka', 'market']})
@pytest.mark.pgsql('persey_payments', files=['read.sql'])
@pytest.mark.config(PERSEY_PAYMENTS_TRACK_BOUND_UIDS=False)
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    ['request_brands', 'zalogin_times'],
    [pytest.param('market,lavka', 1), pytest.param('market', 0)],
)
async def test_read_internal_no_zalogin(
        taxi_persey_payments_web,
        stq,
        load_json,
        mock_zalogin,
        request_brands,
        zalogin_times,
):
    zalogin_mock = mock_zalogin('portal_uid', 'zalogin_resp.json')
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/multibrand/ride_subs',
        params={'brands': request_brands},
        headers={'X-Yandex-UID': 'portal_uid', 'X-Request-Language': 'ru'},
    )

    assert response.status == 200
    assert zalogin_mock.times_called == zalogin_times


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[30, 40])
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['read.sql'])
@pytest.mark.parametrize(
    [
        'request_json',
        'request_headers',
        'expected_resp',
        'expected_ride_subs',
        'expected_events',
        'expected_seen_bound_uids',
    ],
    [
        (
            {
                'brands': {'yataxi': {'mod': 30}, 'lavka': {'mod': 40}},
                'subscription_source': 'new_platform',
            },
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-Bound-Uids': 'phonish_uid',
                'X-Request-Application': 'app_name=android',
                'X-Request-Language': 'ru',
            },
            'expected_resp_update.json',
            'expected_ride_subs_update.json',
            'expected_events_update.json',
            [['portal_uid', 'phonish_uid']],
        ),
    ],
)
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_update(
        taxi_persey_payments_web,
        stq,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        request_json,
        request_headers,
        platform,
        expected_resp,
        expected_ride_subs,
        expected_events,
        expected_seen_bound_uids,
):
    response = await taxi_persey_payments_web.put(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/ride_subs',
        json=request_json,
        headers=request_headers,
    )

    assert response.status == 200
    assert await response.json() == load_json(expected_resp)
    assert get_ride_subs('application', 'subscription_source') == load_json(
        expected_ride_subs,
    )
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['read.sql'])
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_update_mod_whitelist(
        taxi_persey_payments_web,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        platform,
):
    response = await taxi_persey_payments_web.put(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/ride_subs',
        json={'brands': {'yataxi': {'mod': 30}, 'lavka': {'mod': 40}}},
        headers={
            'X-Yandex-UID': 'portal_uid',
            'X-YaTaxi-Bound-Uids': 'phonish_uid',
            'X-Request-Application': 'app_name=android',
            'X-Request-Language': 'ru',
        },
    )

    assert response.status == 400
    assert (await response.json())['code'] == 'MOD_NOT_ALLOWED'
    assert get_ride_subs() == load_json(
        'expected_ride_subs_update_mod_whitelist.json',
    )
    check_ride_subs_events('expected_events_empty.json')
    assert get_seen_bound_uids() == []


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.pgsql('persey_payments', files=['delete.sql'])
@pytest.mark.parametrize(
    [
        'request_brands',
        'request_headers',
        'expected_ride_subs',
        'expected_events',
        'expected_seen_bound_uids',
    ],
    [
        (
            'yataxi,lavka',
            {
                'X-Yandex-UID': 'portal_uid',
                'X-YaTaxi-Bound-Uids': 'phonish_uid',
                'X-Request-Application': 'app_name=android',
                'X-Request-Language': 'ru',
            },
            'expected_ride_subs_delete.json',
            'expected_events_delete.json',
            [['portal_uid', 'phonish_uid']],
        ),
    ],
)
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_delete(
        taxi_persey_payments_web,
        stq,
        load_json,
        get_ride_subs,
        check_ride_subs_events,
        get_seen_bound_uids,
        platform,
        request_brands,
        request_headers,
        expected_ride_subs,
        expected_events,
        expected_seen_bound_uids,
):
    response = await taxi_persey_payments_web.delete(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/ride_subs',
        params={'brands': request_brands},
        headers=request_headers,
    )

    assert response.status == 204
    assert get_ride_subs() == load_json(expected_ride_subs)
    check_ride_subs_events(expected_events)
    assert get_seen_bound_uids() == expected_seen_bound_uids


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[12, 21])
@pytest.mark.translations(
    client_messages={
        'persey-payments.contribution.participants_tmpl': {
            'ru': [
                '$PARTICIPANTS_NUM$ человек',
                '$PARTICIPANTS_NUM$ человека',
                '$PARTICIPANTS_NUM$ человека',
            ],
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['main_screen.sql'])
@pytest.mark.parametrize(
    'request_brands, expected_resp',
    [(['yataxi', 'lavka'], 'expected_resp_main_screen.json')],
)
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_main_screen(
        taxi_persey_payments_web,
        load_json,
        platform,
        request_brands,
        expected_resp,
        mock_participant_count,
):
    response = await taxi_persey_payments_web.post(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/main_screen',
        json={'brands': {brand: {} for brand in request_brands}},
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        },
    )

    assert response.status == 200, await response.json()
    assert await response.json() == load_json(expected_resp)


@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['read.sql'])
@pytest.mark.parametrize(
    'exp_amount',
    [
        '321 $SIGN$$CURRENCY$',
        pytest.param(
            '321,12 $SIGN$$CURRENCY$',
            marks=pytest.mark.config(
                CURRENCY_FORMATTING_RULES={
                    'RUB': {'__default__': 0, 'charity_contribution': 2},
                    '__default__': {'__default__': 777},
                },
            ),
        ),
        pytest.param(
            '321 $SIGN$$CURRENCY$',
            marks=pytest.mark.config(
                CURRENCY_FORMATTING_RULES={
                    'RUB': {'__default__': 0},
                    '__default__': {'__default__': 777},
                },
            ),
        ),
    ],
)
async def test_contribution_precision(taxi_persey_payments_web, exp_amount):
    response = await taxi_persey_payments_web.get(
        f'/4.0/persey-payments/v1/mobile/charity/multibrand/ride_subs',
        params={'brands': 'yataxi'},
        headers={
            'X-Yandex-UID': 'phonish_uid',
            'X-Request-Application': 'app_name=android',
            'X-Request-Language': 'ru',
        },
    )

    assert response.status == 200, await response.json()

    response_json = await response.json()
    assert (
        response_json['brands']['yataxi']['contribution']['amount']
        == exp_amount
    )


def exp3_mark(value):
    return pytest.mark.client_experiments3(
        consumer='persey-payments/ride_subs',
        experiment_name='persey_payments_ride_subs_mod_suggest',
        args=[
            {'name': 'yandex_uid', 'type': 'string', 'value': '123'},
            {'name': 'platform', 'type': 'string', 'value': 'go_android'},
            {
                'name': 'phone_id',
                'type': 'string',
                'value': 'af35af35af35af35af35af35',
            },
            {'name': 'application', 'type': 'string', 'value': 'android'},
        ],
        value=value,
    )


@pytest.mark.config(
    PERSEY_PAYMENTS_FALLBACK_MOD_SUGGEST={
        '__default__': {'default_index': 0, 'options': [432]},
    },
)
@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[12, 21, 432, 444, 555, 777])
@pytest.mark.translations(
    client_messages={
        'persey-payments.contribution.participants_tmpl': {
            'ru': [
                '$PARTICIPANTS_NUM$ человек',
                '$PARTICIPANTS_NUM$ человека',
                '$PARTICIPANTS_NUM$ человека',
            ],
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['main_screen.sql'])
@pytest.mark.parametrize(
    'request_platform, expected_resp',
    [
        ({}, 'expected_resp_mod_suggest_no_platform.json'),
        (
            {'platform': 'go_android'},
            'expected_resp_mod_suggest_no_match.json',
        ),
        pytest.param(
            {'platform': 'go_android'},
            'expected_resp_mod_suggest_simple.json',
            marks=exp3_mark(
                {
                    '__default__': {'default_index': 0, 'options': [777]},
                    'brands': {
                        'yataxi': {'default_index': 0, 'options': [555]},
                    },
                    'overall': {
                        'newbie': {'default_index': 0, 'options': [444]},
                    },
                },
            ),
        ),
        pytest.param(
            {'platform': 'go_android'},
            'expected_resp_mod_suggest_bad.json',
            marks=exp3_mark(
                {
                    '__default__': {'default_index': 0, 'options': [777]},
                    'brands': {'yataxi': {'default_index': 0, 'options': []}},
                    'overall': {
                        'newbie': {
                            'default_index': 777,
                            'options': [444, 555],
                        },
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_mod_suggest(
        taxi_persey_payments_web,
        load_json,
        platform,
        request_platform,
        expected_resp,
        mock_participant_count,
):
    request_json = {'brands': {'yataxi': {}, 'lavka': {}}}
    request_json.update(request_platform)

    response = await taxi_persey_payments_web.post(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/main_screen',
        json=request_json,
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        },
    )

    assert response.status == 200, await response.json()

    expected_resp_json = load_json(expected_resp)
    resp_json = await response.json()
    resp_brands_mod_info = {
        brand: brand_json['mod_info']
        for brand, brand_json in resp_json['brands'].items()
    }

    assert (
        resp_json['overall'].get('mod_info')
        == expected_resp_json['overall.mod_info']
    )
    assert resp_brands_mod_info == expected_resp_json['brands.mod_info']


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.translations(
    client_messages={
        'persey-payments.contribution.participants_tmpl': {
            'ru': [
                '$PARTICIPANTS_NUM$ человек',
                '$PARTICIPANTS_NUM$ человека',
                '$PARTICIPANTS_NUM$ человека',
            ],
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['main_screen.sql'])
@pytest.mark.parametrize(
    'exp_mod_infos',
    [
        pytest.param(
            {
                'yataxi': {'default_index': 1, 'options': [21, 12]},
                'lavka': {'default_index': 1, 'options': [21, 12]},
            },
            marks=pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[12, 21]),
        ),
        {
            'yataxi': {'default_index': 0, 'options': [10]},
            'lavka': {'default_index': 0, 'options': [10]},
        },
    ],
)
@pytest.mark.parametrize('platform', ['web', 'mobile'])
async def test_main_screen_mod_whitelist(
        taxi_persey_payments_web,
        platform,
        exp_mod_infos,
        mock_participant_count,
):
    response = await taxi_persey_payments_web.post(
        f'/4.0/persey-payments/v1/{platform}/charity/multibrand/main_screen',
        json={'brands': {'yataxi': {}, 'lavka': {}}},
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        },
    )

    assert response.status == 200

    response_json = await response.json()
    assert {
        brand: {
            'default_index': resp['mod_info']['default_index'],
            'options': [o['value'] for o in resp['mod_info']['options']],
        }
        for brand, resp in response_json['brands'].items()
    } == exp_mod_infos


@conftest.ride_subs_config({'allowed_brands': ['yataxi', 'lavka']})
@pytest.mark.pgsql('persey_payments', files=['read.sql'])
@pytest.mark.translations(
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.parametrize(
    'request_brands, exp_overall_amount_number',
    [('yataxi', '321.123'), ('lavka', None)],
)
async def test_read_overall_brands(
        taxi_persey_payments_web,
        stq,
        mock_zalogin,
        request_brands,
        exp_overall_amount_number,
        mock_participant_count,
):
    mock_zalogin('portal_uid', 'zalogin_resp.json')
    response = await taxi_persey_payments_web.get(
        '/internal/v1/charity/multibrand/ride_subs',
        params={'brands': request_brands},
        headers={'X-Yandex-UID': 'portal_uid', 'X-Request-Language': 'ru'},
    )

    assert response.status == 200, await response.json()

    response_json = await response.json()
    overall_amount_number = (
        response_json['overall'].get('contribution', {}).get('amount_number')
    )
    assert overall_amount_number == exp_overall_amount_number

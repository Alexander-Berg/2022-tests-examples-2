from typing import Dict
from typing import List

import pytest

from tests_coupons.referral import util


RANDOM_COUNTRY = 'ita'


SHARED_PAYMENTS_WITH_BUSINESS_NO_RIDES = {
    'accounts': [
        {
            'id': 'acc1',
            'details': {},
            'member_role': 'owner',
            'type': 'family',
            'is_active': True,
            'description': '',
            'has_rides': False,
        },
        {
            'id': 'acc2',
            'details': {},
            'member_role': 'owner',
            'type': 'business',
            'is_active': True,
            'description': '',
            'has_rides': False,
        },
    ],
    'payment_methods': [],
}


SHARED_PAYMENTS_WITH_BUSINESS = {
    'accounts': [
        {
            'id': 'acc1',
            'details': {},
            'member_role': 'owner',
            'type': 'family',
            'is_active': True,
            'description': '',
            'has_rides': False,
        },
        {
            'id': 'acc2',
            'details': {},
            'member_role': 'owner',
            'type': 'business',
            'is_active': True,
            'description': '',
            'has_rides': True,
        },
    ],
    'payment_methods': [],
}

SHARED_PAYMENTS_WO_BUSINESS = {
    'accounts': [
        {
            'id': 'acc1',
            'details': {},
            'member_role': 'owner',
            'type': 'family',
            'is_active': True,
            'description': '',
            'has_rides': False,
        },
        {
            'id': 'acc2',
            'details': {},
            'member_role': 'owner',
            'type': 'family',
            'is_active': True,
            'description': '',
            'has_rides': True,
        },
    ],
    'payment_methods': [],
}

SHARED_PAYMENTS_EMPTY: Dict[str, List] = {
    'accounts': [],
    'payment_methods': [],
}


@pytest.mark.parametrize(
    'is_business_exp3_on',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='referral_campaign_light_business_experiments3.json',
            ),
        ),
        False,
    ],
)
@pytest.mark.experiments3(filename='referral_taxi_check_db_first_exp3.json')
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
@pytest.mark.parametrize('user_with_common', [True, False])
@pytest.mark.parametrize('user_with_business', [True, False])
@pytest.mark.parametrize('new_common_available', [True, False])
@pytest.mark.parametrize(
    'shared_payments_response, shared_payment_status, new_business_available',
    [
        (SHARED_PAYMENTS_WITH_BUSINESS_NO_RIDES, 200, False),
        (SHARED_PAYMENTS_WITH_BUSINESS, 200, True),
        (SHARED_PAYMENTS_WO_BUSINESS, 200, False),
        (SHARED_PAYMENTS_EMPTY, 200, False),
        ({}, 500, False),
    ],
)
async def test_business_account(
        mockserver,
        taxi_coupons,
        user_statistics_services,
        referrals_postgres_db,
        shared_payments_response,
        shared_payment_status,
        user_with_common,
        user_with_business,
        is_business_exp3_on,
        new_common_available,
        new_business_available,
):
    @mockserver.json_handler('/taxi-shared-payments/internal/stats')
    def _mock_shared_payments(request):
        return mockserver.make_response(
            status=shared_payment_status, json=shared_payments_response,
        )

    yandex_uid = (
        util.YANDEX_UID_CAMPAINGS
        if user_with_business and user_with_common
        else util.YANDEX_UID_BUSINESS
        if user_with_business
        else util.YANDEX_UID_COMMON
        if user_with_common
        else util.YANDEX_UID_EMPTY
    )
    zone_name = 'spb' if new_common_available else 'moscow_business'

    common_expected = user_with_common or new_common_available
    business_expected = is_business_exp3_on and (
        user_with_business or new_business_available
    )

    expected = 200 if common_expected or business_expected else 406
    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        phone_id=util.PHONE_ID_EMPTY,
        expected_code=expected,
        zone_name=zone_name,
    )

    was_shared_payments_called = _mock_shared_payments.times_called > 0
    assert was_shared_payments_called == (
        is_business_exp3_on and not user_with_business
    )

    if expected == 200:
        user_ref_records = util.referrals_from_postgres(
            yandex_uid, referrals_postgres_db,
        )
        compaigns_in_db = {
            record['campaign_id'] for record in user_ref_records
        }

        if common_expected:
            assert 0 in compaigns_in_db
        if user_with_business or business_expected:
            assert 1 in compaigns_in_db
        assert len(response) == common_expected + business_expected


@pytest.mark.experiments3(
    filename='referral_campaign_light_business_exp3_spb.json',
)
@pytest.mark.experiments3(filename='referral_taxi_check_db_first_exp3.json')
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
@pytest.mark.parametrize(
    'yandex_uid, zone_name, expected_business_code',
    [
        pytest.param(
            util.YANDEX_UID_BUSINESS,
            'spb',
            None,
            id='code from disabled zone, even if current zone is enabled',
            # user has code from moscow_business zone disabled by exp3
        ),
        pytest.param(
            util.YANDEX_UID_CAMPAINGS,
            'moscow_business',
            'referral1',
            id='zone is disabled by exp3, but code from enabled zone',
        ),
        pytest.param(
            util.YANDEX_UID_CAMPAINGS,
            'houston',
            'referral1',
            id='zone has no business config, but code from enabled zone',
        ),
    ],
)
async def test_business_account_zones(
        mockserver,
        taxi_coupons,
        user_statistics_services,
        referrals_postgres_db,
        yandex_uid,
        zone_name,
        expected_business_code,
):
    @mockserver.json_handler('/taxi-shared-payments/internal/stats')
    def _mock_shared_payments(request):
        return mockserver.make_response(
            status=200, json=SHARED_PAYMENTS_WITH_BUSINESS,
        )

    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        zone_name=zone_name,
    )
    assert _mock_shared_payments.times_called == 0

    if expected_business_code:
        assert len(response) == 2  # user has common & business referral
        assert response[1]['promocode'] == expected_business_code
    else:
        assert len(response) == 1  # zone is ok for common referral


async def test_yango_default_campaign_enabled(
        mockserver, taxi_coupons, user_statistics_services,
):
    user_statistics_services.set_phone_id(util.PHONE_ID_EMPTY)

    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_EMPTY,
        application='yango_iphone',
    )
    assert len(response) == 1


YANGO_MESSAGE = (
    'I use Yango. Click on the link to get a 300 rub discount on your '
    'first ride. https://m.yango.yandex.ru/invite/{promocode} '
    'Discount applies to credit card payments only. '
    'After the app is installed use promocode {promocode}'
)
YANGO_DESCR = (
    'Gift your friend 300 $SIGN$$CURRENCY$ off their first ride in '
    'Yango! Discount applies to credit card payments only'
)
YANGO_REFERRALS_URL_CONFIG = {
    '__default__': {'__default__': 'https://m.taxi.yandex.ru/invite/{}'},
    'yango_android': {'__default__': 'https://m.yango.yandex.ru/invite/{}'},
}


@pytest.mark.config(
    LOCALES_APPLICATION_PREFIXES={'yango_android': 'yango'},
    REFERRALS_URL_TEMPLATE_MAP=YANGO_REFERRALS_URL_CONFIG,
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
async def test_yango(taxi_coupons, user_statistics_services):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_NO_PERCENT,
        phone_id=util.PHONE_ID_NO_PERCENT,
        application='yango_android',
    )
    assert content[-1]['descr'] == YANGO_DESCR
    assert content[-1]['message'] == YANGO_MESSAGE.format(
        promocode='promonopercentyango',
    )
    assert content[-1]['promocode'] == 'promonopercentyango'


YANGO_EXTRA_MESSAGE = (
    'I use Yango with prefix. Click on the link to get a 300 rub discount '
    'on your first ride. https://m.yango.yandex.ru/invite/{promocode} '
    'Discount applies to credit card payments only. '
    'After the app is installed use promocode {promocode}'
)
YANGO_EXTRA_DESCR = (
    'Gift your friend 300 $SIGN$$CURRENCY$ off their first ride in '
    'Yango with prefix! Discount applies to credit card payments only'
)
PREFIX_MESSAGE = (
    'I\'m a Yandex.Taxi prefix user. Click on the link to get a 300 rub '
    'discount on your first ride. '
    'https://m.taxi.yandex.ru/invite/{promocode} Discount '
    'applies to credit card payments only. '
    'After the app is installed use promocode {promocode}'
)
PREFIX_DESCR = (
    'Gift your friend 300 $SIGN$$CURRENCY$ off their first ride! '
    'Discount applies to credit card payments only prefix'
)


@pytest.mark.experiments3(
    filename='referral_campaign_light_business_experiments3.json',
)
@pytest.mark.experiments3(
    filename='referral_campaign_light_business_yango_experiments3.json',
)
@pytest.mark.config(
    LOCALES_APPLICATION_PREFIXES={'yango_android': 'yango'},
    REFERRALS_URL_TEMPLATE_MAP=YANGO_REFERRALS_URL_CONFIG,
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
    queries=[
        util.add_or_modify_creator_config(
            config_id=1, zone_name='moscow_no_prefix',
        ),
        util.add_or_modify_referral_campaign(
            campaign_id=1,
            campaign_name='light_business',
            tanker_prefix='prefix',
        ),
        util.add_or_modify_creator_config(
            config_id=3, campaign_id=1, zone_name='moscow_prefix',
        ),
        util.add_or_modify_creator_config(
            config_id=12, campaign_id=2, zone_name='moscow_no_prefix',
        ),
        util.add_or_modify_referral_campaign(
            campaign_id=3,
            campaign_name='light_business_yango',
            tanker_prefix='prefix',
            brand_name='yango',
        ),
        util.add_or_modify_creator_config(
            config_id=13, campaign_id=3, zone_name='moscow_prefix',
        ),
    ],
)
@pytest.mark.parametrize(
    'yandex_uid, phone_id, referral_exist',
    [
        pytest.param(
            util.YANDEX_UID_EMPTY,
            util.PHONE_ID_EMPTY,
            False,
            id='new_referral_user',
        ),
        pytest.param(
            util.YANDEX_UID_NO_PERCENT,
            util.PHONE_ID_NO_PERCENT,
            True,
            id='existed_referral_user',
        ),
    ],
)
@pytest.mark.parametrize(
    'application, app_prefix, promocode',
    [
        pytest.param(
            'yango_android', True, 'promobusinessyango', id='app_with_prefix',
        ),
        pytest.param('iphone', False, 'promonopercent', id='app_wo_prefix'),
    ],
)
@pytest.mark.parametrize(
    'zone_name, extra_prefix_for_new_referral',
    [
        pytest.param('moscow_prefix', True, id='zone_with_prefix'),
        pytest.param('moscow_no_prefix', False, id='zone_wo_prefix'),
    ],
)
async def test_prefixes(
        taxi_coupons,
        yandex_uid,
        phone_id,
        referral_exist,
        application,
        app_prefix,
        promocode,
        zone_name,
        extra_prefix_for_new_referral,
        user_statistics_services,
):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        phone_id=phone_id,
        application=application,
        zone_name=zone_name,
    )
    # all existing promocodes has rerferral with prefix
    extra_prefix = extra_prefix_for_new_referral or referral_exist
    if app_prefix and extra_prefix:
        expected_descr = YANGO_EXTRA_DESCR
        expected_message = YANGO_EXTRA_MESSAGE
    elif app_prefix:
        expected_descr = YANGO_DESCR
        expected_message = YANGO_MESSAGE
    elif extra_prefix:
        expected_descr = PREFIX_DESCR
        expected_message = PREFIX_MESSAGE
    else:
        expected_descr = util.COMMON_NO_PERCENT_DESCR
        expected_message = util.COMMON_NO_PERCENT_MESSAGE

    assert content[-1]['descr'] == expected_descr
    if referral_exist:
        assert content[-1]['message'] == expected_message.format(
            promocode=promocode,
        )
    else:
        util.check_message(content[-1], expected_message)


@pytest.mark.experiments3(
    filename='referral_campaign_common_uber_experiments3.json',
)
@pytest.mark.config(
    REFERRALS_URL_TEMPLATE_MAP={
        '__default__': {
            '__default__': (
                'https://default.default.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
            util.COUNTRY_WITH_REFERRAL: (
                'https://default.country_with_referral.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
        },
        'android': {
            '__default__': (
                'https://yandex.default.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
            util.COUNTRY_WITH_REFERRAL: (
                'https://yandex.country_with_referral.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
        },
        'yango_iphone': {
            '__default__': (
                'https://yango.default.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
            util.COUNTRY_WITH_REFERRAL: (
                'https://yango.country_with_referral.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
        },
        'uber_android': {
            '__default__': (
                'https://uber.default.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
            util.COUNTRY_WITH_REFERRAL: (
                'https://uber.country_with_referral.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
        },
        'uber_by_android': {
            '__default__': (
                'https://uber_by.default.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
            util.COUNTRY_WITH_REFERRAL: (
                'https://uber_by.country_with_referral.'
                'adjust_links_website.yandex.com/invite/{}'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'application,app_url_piece',
    [
        ('win', 'default'),
        ('android', 'yandex'),
        ('uber_by_android', 'uber_by'),
        ('uber_android', 'uber'),
        ('yango_iphone', 'yango'),
    ],
)
@pytest.mark.parametrize(
    'country,country_url_piece',
    [
        (util.COUNTRY_WITH_REFERRAL, 'country_with_referral'),
        (RANDOM_COUNTRY, 'default'),
    ],
)
async def test_config_adjust_links(
        taxi_coupons,
        user_statistics_services,
        application,
        app_url_piece,
        country,
        country_url_piece,
):
    res = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_WITH_PERCENT,
        phone_id=util.REFERRAL_USER_PHONE_ID,
        application=application,
        country=country,
    )
    assert len(res) == 1
    body = res[0]
    assert 'message' in body and 'promocode' in body
    msg, code = body['message'], body['promocode']
    expected_url = (
        'https://{}.{}.adjust_links_website.' 'yandex.com/invite/{}'
    ).format(app_url_piece, country_url_piece, code)

    assert expected_url in msg


@pytest.mark.parametrize(
    'referral_exp_on,expected_referrals_count',
    [
        pytest.param(
            True,
            2,
            marks=pytest.mark.experiments3(
                filename='external_referral_experiments3.json',
            ),
        ),
        (False, 1),
    ],
)
@pytest.mark.experiments3(filename='banner_experiments3.json')
@pytest.mark.parametrize(
    'yandex_uid, correct_text_fields, image_tag_expected',
    [
        pytest.param('0000001', True, False, id='banner_with_title_and_text'),
        pytest.param('0000002', False, False, id='banner_only_with_title'),
        pytest.param('0000003', False, False, id='banner_only_with_text'),
        pytest.param(
            '0000004', False, False, id='banner_without_title_and_text',
        ),
        pytest.param(
            '1000001',
            False,
            False,
            id='banner_with_title_and_text_bad_exp3_keys',
        ),
        pytest.param(
            '1000002', False, False, id='banner_only_with_title_bad_exp3_keys',
        ),
        pytest.param(
            '1000003', False, False, id='banner_only_with_text_bad_exp3_keys',
        ),
        pytest.param(
            '1000004',
            False,
            False,
            id='banner_without_title_and_text_bad_exp3_keys',
        ),
        pytest.param(
            '2000001',
            False,
            False,
            id='banner_with_title_and_text_bad_tanker_args',
        ),
        pytest.param(
            '2000002',
            False,
            False,
            id='banner_only_with_title_bad_tanker_args',
        ),
        pytest.param(
            '2000003',
            False,
            False,
            id='banner_only_with_text_bad_tanker_args',
        ),
        pytest.param(
            '2000004',
            False,
            False,
            id='banner_without_title_and_text_bad_tanker_args',
        ),
        pytest.param(
            '3000001', True, True, id='banner_with_title_and_text_and_image',
        ),
        pytest.param(
            '3000002', False, False, id='banner_with_title_and_image',
        ),
        pytest.param('3000003', False, False, id='banner_with_text_and_image'),
        pytest.param('3000004', False, False, id='banner_only_with_image'),
        pytest.param(
            '3000005',
            False,
            False,
            id='banner_with_title_and_text_and_image_bad_tanker_keys',
        ),
        pytest.param(
            '3000006',
            False,
            False,
            id='banner_with_title_and_text_and_image_bad_tanker_args',
        ),
    ],
)
async def test_banner_simple(
        taxi_coupons,
        user_statistics_services,
        eda_promocodes,
        referral_exp_on,
        expected_referrals_count,
        yandex_uid,
        correct_text_fields,
        image_tag_expected,
        mockserver,
):
    """
    1) 0000001 - 0000004 : Those tests are intended to check that banner
    either will contain both title and text or won't be in the response
    whatsoever
    2) 1000001 - 1000004 : Those tests are intended to check that if
    experiments3 returns tanker key which doesn't exist service will
    catch exception, respond with '200' without banner
    3) 2000001 - 2000004 : Those tests are intended to check that if
    tanker template requires args which aren't given in C++ code
    service will catch exception, respond with '200' without banner
    4) 3000001 - 3000006 : Those tests are intended to check that if
    there is optional `image` field in the experiments3 response
    it might be added to the referral response, but only in case
    if title and text are provided.
    """

    content = await util.referral_request_and_check(
        taxi_coupons, user_statistics_services, yandex_uid, expected_code=200,
    )
    assert len(content) == expected_referrals_count
    resp = content[-1]

    if correct_text_fields:
        assert 'banner' in resp

        banner = resp['banner']
        assert 'title' in banner
        assert 'text' in banner
        assert (
            banner['title']
            == 'Call to action title! (value 300 $SIGN$$CURRENCY$%)'
        )
        assert banner['text'] == (
            'This is Yandex.Taxi banner! Give your friend a discount'
            ' in 300 $SIGN$$CURRENCY$% (not more than 300 '
            '$SIGN$$CURRENCY$) for the first trip paid with card!'
        )

        if image_tag_expected:
            assert 'image' in banner
            assert banner['image'] == 'image_tag'
    else:
        assert 'banner' not in resp


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
@pytest.mark.parametrize(
    'yandex_uid, image, extected_text',
    [
        pytest.param(
            util.YANDEX_UID_WITH_PERCENT,
            'super',
            '58 promocodes left',
            id='existed code with moscow overrides (in houston)',
        ),
        pytest.param(
            util.YANDEX_UID_EMPTY,
            'houston',
            '100 promocodes left for houston',
            id='new code with houston overrides',
        ),
    ],
)
@pytest.mark.experiments3(filename='referral_overrides_experiments3.json')
async def test_overrides(
        taxi_coupons,
        yandex_uid,
        image,
        extected_text,
        user_statistics_services,
):
    content = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        zone_name='houston',
        phone_id=util.REFERRAL_USER_PHONE_ID,
    )
    overrides = content[-1].get('overrides')

    assert overrides == {
        'referral_screen': {
            'image': f'{image}_rides',
            'rides_left_text': extected_text,
        },
    }


async def test_metrics_exist(
        taxi_coupons, taxi_coupons_monitor, user_statistics_services,
):
    await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        util.YANDEX_UID_WITH_PERCENT,
        util.REFERRAL_USER_PHONE_ID,
    )

    metrics_name = 'referral-statistics'
    metrics = await taxi_coupons_monitor.get_metrics(metrics_name)
    value = metrics[metrics_name]
    assert 'taxi' in value['stats']['iphone']['rus']


@pytest.mark.parametrize(
    'services,expected_promocode',
    [
        pytest.param(None, 'promowithpercent', id='without services param'),
        pytest.param(
            ['grocery'], 'grocerypromo', id='filter only grocery service',
        ),
        pytest.param(
            ['taxi'], 'promowithpercent', id='filter only taxi service',
        ),
    ],
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
    queries=[
        util.add_or_modify_referral_campaign(
            campaign_id=6,
            campaign_name='grocerycomp',
            tanker_prefix='prefix',
            service='grocery',
        ),
        util.add_or_modify_creator_config(
            config_id=14, campaign_id=6, zone_name='moscow',
        ),
        util.SQL_INSERT_GROCERY_PROMOCODE,
    ],
)
async def test_service_filter(
        taxi_coupons,
        user_statistics_services,
        mockserver,
        services,
        expected_promocode,
):
    yandex_uid = util.YANDEX_UID_COMMON

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _grocery_marketing(request):
        return {'usage_count': 1, 'personal_phone_id_usage_count': 1}

    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        phone_id=util.PHONE_ID_EMPTY,
        services=services,
    )

    assert len(response) == 1
    if services:
        assert response[0]['referral_service'] == services[0]
    else:
        assert response[0]['referral_service'] == 'taxi'
    assert response[0]['promocode'] == expected_promocode


@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME,
    files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
    queries=[
        util.add_or_modify_referral_campaign(
            campaign_id=6,
            campaign_name='grocerycomp',
            tanker_prefix='prefix',
            service='grocery',
        ),
        util.add_or_modify_creator_config(
            config_id=14, campaign_id=6, zone_name='moscow',
        ),
    ],
)
async def test_grocery_referral_generate(
        taxi_coupons, user_statistics_services, mockserver,
):
    yandex_uid = util.YANDEX_UID_COMMON
    personal_phone_id = 'some_personal_prone_id'
    appmetrica_device_id = 'some_device_id'
    eats_id = 'some_eats_id'

    headers = {
        'X-Yandex-UID': yandex_uid,
        'X-AppMetrica-DeviceId': appmetrica_device_id,
        'X-YaTaxi-User': 'eats_user_id=%s, personal_phone_id=%s' % (
            eats_id,
            personal_phone_id,
        ),
    }

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _grocery_marketing(request):
        body = request.json
        assert body['yandex_uid'] == yandex_uid
        assert body['personal_phone_id'] == personal_phone_id
        assert body['eats_id'] == eats_id
        assert body['appmetrica_device_id'] == appmetrica_device_id

        return {'usage_count': 1, 'personal_phone_id_usage_count': 1}

    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        phone_id=util.PHONE_ID_EMPTY,
        services=['grocery'],
        headers=headers,
    )

    assert len(response) == 1
    assert response[0]['referral_service'] == 'grocery'
    assert response[0]['promocode']


@pytest.mark.translations(
    client_messages={
        'first_title_tanker_key': {'ru': 'first description item title'},
        'first_text_tanker_key': {'ru': 'first description item text'},
        'second_title_tanker_key': {'ru': 'second description item title'},
        'second_text_tanker_key': {'ru': 'second description item text'},
        'attributed_title_text_tanker_key_first': {'ru': 'first text'},
        'attributed_title_text_tanker_key_second': {'ru': 'second text'},
    },
)
@pytest.mark.experiments3(filename='referral_screen_experiments.json')
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
async def test_referral_screen_fields(taxi_coupons, user_statistics_services):
    response = (
        await util.referral_request_and_check(
            taxi_coupons, user_statistics_services, util.YANDEX_UID_COMMON,
        )
    )[0]

    assert response['image_tag'] == 'some_image_tag'
    assert response['attributed_title'] == {
        'items': [
            {'type': 'text', 'text': 'first text'},
            {'type': 'text', 'text': 'second text', 'font_weight': 'medium'},
        ],
    }
    assert response['description_items'] == [
        {
            'title': 'first description item title',
            'text': 'first description item text',
        },
        {
            'title': 'second description item title',
            'text': 'second description item text',
        },
    ]

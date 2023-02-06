import pytest

from tests_coupons import util as common_util
from tests_coupons.referral import util


GET_FOODTECH_CREATOR_PROMOCODE_TEMPLATE = (
    'SELECT promocode FROM referral.external_referral_creators '
    'WHERE yandex_uid = \'{}\' and referral_name=\'{}\''
)

APPLICATION_MAP_BRAND = {
    '__default__': 'yataxi',
    'iphone': 'yataxi',
    'uber_android': 'yauber',
    'yango_android': 'yango',
    'vezet_iphone': 'vezet',
}

YANDEX_UID_1 = '01'
YANDEX_UID_2 = '02'

EDA_GROCERY_RESPONSES = {
    YANDEX_UID_1: {
        'value': {
            'type': 'percent',
            'discount_currency': 'RUB',
            'discount_limit': 100,
            'discount_percent': 20,
        },
        'code': 'percent_grocery_ref',
        'limit': 1500,
        'usages': 2,
    },
    YANDEX_UID_2: {
        'value': {
            'type': 'total',
            'discount_currency': 'RUB',
            'discount_total': 777,
        },
        'code': 'total_grocery_ref',
        'limit': 500,
        'usages': 0,
    },
}


@pytest.fixture(name='make_referral_request')
def _make_referral_request(taxi_coupons, testpoint, user_statistics_services):
    @testpoint('save_grocery_referral_creator::started')
    def save_creator_grocery_started(data):
        pass

    @testpoint('save_grocery_referral_creator::finished')
    def save_creator_grocery_finished(data):
        pass

    async def _request_maker(*args, **kwargs):
        response = await util.referral_request_and_check(
            taxi_coupons, user_statistics_services, *args, **kwargs,
        )
        if save_creator_grocery_started.times_called:
            # wait for detached scope
            await save_creator_grocery_finished.wait_call()
        return response

    return _request_maker


@pytest.fixture(name='is_user_referral_creator')
def _is_user_referral_creator(referrals_postgres_db):
    def _referral_creator_checker(
            yandex_uid, referral_type, expected_code=None,
    ):
        referrals_postgres_db.execute(
            GET_FOODTECH_CREATOR_PROMOCODE_TEMPLATE.format(
                yandex_uid, referral_type,
            ),
        )
        result = [row[0] for row in referrals_postgres_db]

        if expected_code:
            assert result == [expected_code]

        assert len(result) < 2
        return len(result) == 1

    return _referral_creator_checker


def is_referral_in_response(referral_type, content):
    for cont in content:
        if cont['referral_service'] == referral_type:
            return True
    return False


def is_only_taxi_in_response(content):
    return len(content) == 1 and content[0]['referral_service'] == 'taxi'


@pytest.mark.parametrize(
    'yandex_uid,phone_id, expected_grocery_response,expected_grocery_banner',
    [
        pytest.param(
            YANDEX_UID_1,
            '4f45e',
            'PERCENT_GIVEGET_GROCERY_RESPONSE',
            'PERCENT_GIVEGET_GROCERY_BANNER',
            id='percent_ref',
        ),
        pytest.param(
            YANDEX_UID_2,
            '5714f',
            'TOTAL_GIVEGET_GROCERY_RESPONSE',
            'TOTAL_GIVEGET_GROCERY_BANNER',
            id='total_ref',
        ),
        pytest.param(
            YANDEX_UID_2,
            '45e98',
            'TOTAL_GIVEGET_GROCERY_RESPONSE',
            None,
            id='total_ref_no_banner',
        ),
    ],
)
@pytest.mark.config(APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND)
@pytest.mark.parametrize('zone_name', ['moscow', 'spb'])
@pytest.mark.parametrize('application', ['iphone', 'yango_android'])
@pytest.mark.parametrize(
    'version, version_enabled',
    [([1, 2, 3], True), ([1, 2, 4], False), (None, True)],
)
@pytest.mark.experiments3(filename='external_referral_experiments3.json')
async def test_referral_external_giveget_service_enabled(
        eda_promocodes,
        make_referral_request,
        user_statistics_services,
        is_user_referral_creator,
        yandex_uid,
        phone_id,
        expected_grocery_response,
        expected_grocery_banner,
        zone_name,
        application,
        version,
        version_enabled,
        load_json,
):
    grocery_response_for_yandex_uid = EDA_GROCERY_RESPONSES.get(yandex_uid)
    eda_promocodes.set_grocery_response(grocery_response_for_yandex_uid)

    app_map_brand = APPLICATION_MAP_BRAND
    brand = app_map_brand.get(application, app_map_brand.get('__default__'))

    content = await make_referral_request(
        yandex_uid=yandex_uid,
        zone_name=zone_name,
        application=application,
        version=version,
        phone_id=phone_id,
    )

    is_external_grocery_expected = (
        zone_name == 'spb' and brand == 'yataxi' and version_enabled
    )

    if is_external_grocery_expected:
        referral_promocode = content[0]
        responses = load_json('external_referral_responses.json')
        expected = responses[expected_grocery_response]
        if expected_grocery_banner:
            expected['banner'] = responses[expected_grocery_banner]

        assert referral_promocode == expected

        promocode = grocery_response_for_yandex_uid.get('code')
        assert is_user_referral_creator(
            yandex_uid, 'grocery', expected_code=promocode,
        )
    else:
        assert not is_user_referral_creator(yandex_uid, 'grocery')
        assert is_only_taxi_in_response(content)


@pytest.mark.parametrize(
    'external_service_code', [400, 401, 404, 406, 500, common_util.TIMEOUT],
)
@pytest.mark.parametrize(
    'referral_exp_on',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='external_referral_experiments3.json',
            ),
        ),
        False,
    ],
)
@pytest.mark.parametrize('referral_type,zone', [('grocery', 'spb')])
async def test_referral_external_giveget_service_disabled(
        eda_promocodes,
        make_referral_request,
        user_statistics_services,
        is_user_referral_creator,
        referral_exp_on,
        referral_type,
        external_service_code,
        zone,
):
    eda_promocodes.set_error(external_service_code)

    content = await make_referral_request(
        yandex_uid=YANDEX_UID_1, zone_name=zone, version=[1, 2, 3],
    )
    assert is_only_taxi_in_response(content)
    assert not is_user_referral_creator(YANDEX_UID_1, referral_type)


@pytest.mark.parametrize(
    'referral_exp_on',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='external_referral_experiments3.json',
            ),
        ),
        False,
    ],
)
@pytest.mark.parametrize(
    'was_user_referral_creator',
    [
        pytest.param(
            True,
            marks=pytest.mark.pgsql(
                util.REFERRALS_DB_NAME,
                files=[util.PGSQL_DEFAULT, 'foodtech_referral_creators.sql'],
            ),
        ),
        False,
    ],
)
@pytest.mark.parametrize(
    'external_service_code', [200, 400, 500, common_util.TIMEOUT],
)
@pytest.mark.parametrize('zone_name', ['spb', 'moscow'])
async def test_grocery_referral_creators_flow(
        referral_exp_on,
        was_user_referral_creator,
        external_service_code,
        zone_name,
        eda_promocodes,
        make_referral_request,
        user_statistics_services,
        is_user_referral_creator,
):
    """
    In particular, the following cases are covered here:
        1. eda - ERR, zone - OK => no grocery, not creator
        2. eda - OK, zone - not OK => no grocery, not creator
        3. eda - OK, zone - OK => grocery & creator
        4. eda - OK, zone - not OK, creator => grocery & still creator
        5. eda - ERR, zone - OK, creator => no grocery & still creator
        6. eda - ERR, zone - not OK, creator => no grocery & still creator
        7. eda - OK, zone - OK, creator => grocery & still creator (only 1 row)
    """
    yandex_uid = YANDEX_UID_1

    if external_service_code == 200:
        eda_promocodes.set_grocery_response(
            EDA_GROCERY_RESPONSES.get(yandex_uid),
        )
    else:
        eda_promocodes.set_error(external_service_code)

    is_grocery_expected = (
        external_service_code == 200
        and referral_exp_on
        and (was_user_referral_creator or zone_name == 'spb')
    )

    is_user_creator_expected = was_user_referral_creator or is_grocery_expected

    content = await make_referral_request(
        yandex_uid=yandex_uid, zone_name=zone_name,
    )

    if is_grocery_expected:
        assert is_referral_in_response('grocery', content)

    if not is_user_creator_expected:
        assert is_only_taxi_in_response(content)

    assert (
        is_user_referral_creator(yandex_uid, 'grocery')
        == is_user_creator_expected
    )

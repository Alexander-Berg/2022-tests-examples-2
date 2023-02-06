import pytest

from tests_coupons.referral import util


@pytest.mark.parametrize(
    'yandex_uid, creator_properties',
    [
        pytest.param(
            util.YANDEX_UID_NO_PERCENT,
            {
                'value': '300',
                'currency': 'RUB',
                'external_meta': {'first_limit': 1},
            },
            id='fixed promocode',
        ),
        pytest.param(
            util.YANDEX_UID_WITH_PERCENT,
            {
                'value': '200',
                'percent': '28',
                'limit': '200',
                'currency': 'RUB',
            },
            id='percent promocode (limit)',
        ),
    ],
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
async def test_creator_properties(
        taxi_coupons, user_statistics_services, yandex_uid, creator_properties,
):
    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        phone_id=util.PHONE_ID_EMPTY,
        services=['taxi'],
        zone_name='moscow',
    )
    assert len(response) == 1
    assert response[0]['creator_properties'] == creator_properties


@pytest.mark.parametrize('referral_properties_enabled', [True, False])
@pytest.mark.parametrize(
    'zone_name, country, has_consumer_properties',
    [
        pytest.param('moscow', 'rus', True, id='found consumer_config'),
        pytest.param('houston', 'gbr', False, id='no consumer config'),
        pytest.param(
            'moscow_no_percent_promocode',
            'rus',
            True,
            id='country consumer_config',
        ),
    ],
)
@pytest.mark.pgsql(
    util.REFERRALS_DB_NAME, files=[util.PGSQL_DEFAULT, 'promocodes.sql'],
)
async def test_consumer_properties(
        taxi_coupons,
        user_statistics_services,
        taxi_config,
        referral_properties_enabled,
        zone_name,
        country,
        has_consumer_properties,
):
    taxi_config.set_values(
        {'COUPONS_REFERRAL_PROPERTIES_ENABLED': referral_properties_enabled},
    )
    yandex_uid = util.YANDEX_UID_EMPTY
    response = await util.referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        phone_id=util.PHONE_ID_EMPTY,
        services=['taxi'],
        zone_name=zone_name,
        country=country,
    )

    assert len(response) == 1
    if not referral_properties_enabled or not has_consumer_properties:
        assert 'consumer_properties' not in response[0]
    else:
        consumer_properties = {
            'value': '300',
            'currency': 'RUB',
            'external_meta': {'first_limit': 1},
        }
        assert response[0]['consumer_properties'] == consumer_properties

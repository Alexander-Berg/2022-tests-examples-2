REFERRAL_USER_PHONE_ID = '539eb438e7e5b1f5397f67f5'


# referral promocodes, new flow via postgres
REFERRALS_DB_NAME = 'user_referrals'
PGSQL_DEFAULT = f'pg_{REFERRALS_DB_NAME}.sql'
PGSQL_REFERRAL = [
    f'tests_coupons/referral/static/default/{file_name}'
    for file_name in (PGSQL_DEFAULT, 'referral.sql')
]

SQL_UPSERT_REFERRAL_CAMPAIGN = """
INSERT INTO referral.campaigns
(id, campaign_name, extra_check, tanker_prefix, brand_name, service)
VALUES ({id}, '{campaign_name}', {extra_check}, {tanker_prefix},
'{brand_name}', '{service}')
ON CONFLICT(id) DO UPDATE SET campaign_name='{campaign_name}',
extra_check={extra_check}, tanker_prefix={tanker_prefix},
brand_name='{brand_name}'"""

SQL_UPSERT_REFERRAL_CREATOR_CONFIG = """
INSERT INTO referral.creator_configs
(id, campaign_id, zone_name, zones, country,
reward_series, success_activations_limit, enabled, status)
VALUES ({id}, {campaign_id}, '{zone_name}', '{{"{zone_name}"}}', NULL,
        '{series}', {limit}, TRUE, 'for_new_users')
ON CONFLICT(id) DO UPDATE SET
campaign_id={campaign_id}, zones='{{"{zone_name}"}}'"""

SQL_INSERT_GROCERY_PROMOCODE = """
INSERT INTO referral.promocodes
(id, yandex_uid, campaign_id, promocode, country, config_id, phone_id)
VALUES ('40000000000000000000000000000000', '222222222', 6,
        'grocerypromo', 'rus', 14, '5714f45e98956f06baaae3d6')"""

# variable from ./static/test_referral/config.json
SUCCESS_ACTIVATIONS_LIMIT = 50

YANDEX_UID_CAMPAINGS = '444444444'  # user has several referral campaigns
YANDEX_UID_BUSINESS = '555555555'  # user has light_business code
YANDEX_UID_WITH_PERCENT = YANDEX_UID_COMMON = '222222222'
YANDEX_UID_NO_PERCENT = '333333333'
YANDEX_UID_EMPTY = '00001'

PHONE_ID_NO_PERCENT = '5714f45e98956f06baaae3d6'
PHONE_ID_EMPTY = '5714f45e98956f06baaae3d7'

SQL_CLEAR_REFERRAL_CONSUMER_CONFIGS = 'DELETE FROM referral.consumer_configs'

SQL_INSERT_REFERRAL_CONSUMER_CONFIG_FMT = """
  INSERT INTO referral.consumer_configs
  (campaign_id, zones, country, series_id, duration_days) VALUES
  ({campaign_id}, '{{"{zone_name}"}}', 'rus', '{series_id}', {duration_days});
"""

GET_USER_PROMOCODES_TEMPLATE = (
    'SELECT p.*, c.brand_name FROM referral.promocodes p '
    'JOIN referral.campaigns c ON p.campaign_id=c.id '
    'WHERE yandex_uid = \'{}\' ORDER BY campaign_id DESC'
)

GET_USER_SUCCESS_ACTIVATIONS_TEMPLATE = (
    'SELECT * FROM referral.promocode_success_activations '
    'WHERE yandex_uid = \'{}\''
)


def insert_referral_consumer_config(campaign_id=0, duration_days=10, **kwargs):
    sql = SQL_INSERT_REFERRAL_CONSUMER_CONFIG_FMT.format(
        campaign_id=campaign_id, duration_days=duration_days, **kwargs,
    )
    return sql.replace('\'{"None"}\'', 'NULL')


SQLS_REFERRAL_CONSUMER_CONFIG_PERCENT = [
    SQL_CLEAR_REFERRAL_CONSUMER_CONFIGS,
    insert_referral_consumer_config(
        zone_name='moscow',
        series_id='seriespercentreferral',
        duration_days=31,
    ),
]

COMMON_NO_PERCENT_MESSAGE = (
    'I\'m a Yandex.Taxi user. Click on the link to get a 300 rub '
    'discount on your first ride. '
    'https://m.taxi.yandex.ru/invite/{promocode} Discount '
    'applies to credit card payments only. '
    'After the app is installed use promocode {promocode}'
)
COMMON_NO_PERCENT_DESCR = (
    'Gift your friend 300 $SIGN$$CURRENCY$ off their first ride! '
    'Discount applies to credit card payments only'
)


def add_or_modify_referral_campaign(
        campaign_id=0,
        campaign_name='new',
        extra_check=None,
        tanker_prefix=None,
        brand_name='yataxi',
        service='taxi',
):
    return SQL_UPSERT_REFERRAL_CAMPAIGN.format(
        id=campaign_id,
        campaign_name=campaign_name,
        extra_check=f'\'{extra_check}\'' if extra_check else 'NULL',
        tanker_prefix=f'\'{tanker_prefix}\'' if tanker_prefix else 'NULL',
        brand_name=brand_name,
        service=service,
    )


def add_or_modify_creator_config(
        config_id=0,
        campaign_id=0,
        zone_name='',
        series='',
        limit=SUCCESS_ACTIVATIONS_LIMIT,
):
    return SQL_UPSERT_REFERRAL_CREATOR_CONFIG.format(
        id=config_id,
        campaign_id=campaign_id,
        zone_name=zone_name,
        series=series,
        limit=limit,
    )


def check_message(got_response, expected_message):
    generated_promocode = got_response['promocode']
    expected_message = expected_message.format(promocode=generated_promocode)
    assert got_response['message'] == expected_message


COUNTRY_WITH_REFERRAL = 'rus'


def mock_referral_request(
        yandex_uid,
        phone_id,
        format_currency,
        application,
        country,
        zone_name,
        version,
        payment_options,
        services,
):
    if version is None:
        version = [0, 0, 0]
    app = {
        'name': application,
        'version': version,
        'platform_version': [0, 0, 0],
    }

    return {
        'application': app,  # TODO(jolfzverb): to header User-Agent
        'zone_name': zone_name,
        'phone_id': phone_id,
        'yandex_uid': yandex_uid,
        'payment_options': payment_options,
        'country': country,
        'currency': 'RUB',
        'format_currency': format_currency,
        'locale': 'en',  # TODO(jolfzverb): to header Accept-Language
        'services': services,
    }


async def referral_request_and_check(
        taxi_coupons,
        user_statistics_services,
        yandex_uid,
        phone_id=PHONE_ID_EMPTY,
        format_currency=True,
        application='iphone',
        zone_name='moscow',
        expected_code=200,
        country=COUNTRY_WITH_REFERRAL,
        version=None,
        payment_options=None,
        services=None,
        headers=None,
):
    user_statistics_services.set_phone_id(phone_id)

    if payment_options is None:
        payment_options = ['card', 'coupon']
    request = mock_referral_request(
        yandex_uid,
        phone_id,
        format_currency,
        application,
        country,
        zone_name,
        version,
        payment_options,
        services,
    )
    response = await taxi_coupons.post(
        'v1/coupons/referral', json=request, headers=headers,
    )
    assert expected_code == response.status_code

    return response.json()


def get_pg_records_as_dicts(sql, db):
    db.execute(sql)
    columns = [desc[0] for desc in db.description]
    records = list(db)
    return [dict(zip(columns, rec)) for rec in records]


def referrals_from_postgres(yandex_uid, db):
    return get_pg_records_as_dicts(
        GET_USER_PROMOCODES_TEMPLATE.format(yandex_uid), db,
    )


def referral_success_activations(yandex_uid, db):
    return get_pg_records_as_dicts(
        GET_USER_SUCCESS_ACTIVATIONS_TEMPLATE.format(yandex_uid), db,
    )


def get_consumer_configs(db):
    return get_pg_records_as_dicts(
        'SELECT * FROM referral.consumer_configs ORDER BY id', db,
    )


def get_creator_configs(db):
    return get_pg_records_as_dicts(
        'SELECT * FROM referral.creator_configs ORDER BY id', db,
    )

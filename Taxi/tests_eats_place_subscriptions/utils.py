# flake8: noqa
import psycopg2
import pytest
import datetime

BILLING_PROCESSOR_URL = '/eats-billing-processor/v1/create'
CATALOG_STORAGE_URL = (
    '/eats-catalog-storage/internal/eats-catalog-storage'
    + '/v1/places/retrieve-by-ids'
)

TARIFF_ERRORS_METRICS = 'tariff-errors'
SUBSCRIPTION_ERRORS_METRICS = 'subscription-errors'
PLACE_ERRORS_METRICS = 'place-errors'
COMMON_METRICS = 'common-metrics'

PG_TIMEZONE = psycopg2.tz.FixedOffsetTimezone(offset=0, name=None)
MSC_TIMEZONE = psycopg2.tz.FixedOffsetTimezone(offset=180, name=None)


async def db_get_subscription(pgsql, place_id):
    cursor = pgsql['eats_place_subscriptions'].cursor()
    cursor.execute(
        f"""SELECT place_id, tariff, next_tariff, 
        is_partner_updated, is_trial, next_is_trial,
        valid_until, activated_at, last_partner_downdate_time
         FROM eats_place_subscriptions.subscriptions
            WHERE place_id = '{place_id}';""",
    )
    res = cursor.fetchone()
    return res


async def db_get_latest_change_log(pgsql, place_id):
    cursor = pgsql['eats_place_subscriptions'].cursor()
    cursor.execute(
        f"""SELECT
                place_id,
                change_type,
                author,
                state_before,
                state_after
            FROM eats_place_subscriptions.subscriptions_change_log
            WHERE revision = (
                SELECT revision
                FROM eats_place_subscriptions.subscriptions
                WHERE place_id = {place_id}
            )
        """,
    )
    res = cursor.fetchone()
    return res


def check_change_log(db_change_log, expected):
    assert db_change_log[0] == expected[0], 'place_id not match'
    assert db_change_log[1] == expected[1], 'change_type not match'
    assert db_change_log[2] == expected[2], 'author not match'
    if expected[3]:
        assert (
            expected[3].items() <= db_change_log[3].items()
        ), 'state_before not match'
    else:
        assert db_change_log[3] is None
    if expected[4]:
        assert (
            expected[4].items() <= db_change_log[4].items()
        ), 'state_before not match'
    else:
        assert db_change_log[4] is None


async def db_get_counter(pgsql):
    cursor = pgsql['eats_place_subscriptions'].cursor()
    cursor.execute(
        """SELECT place_id, date, count
         FROM eats_place_subscriptions.subscription_order_counter
            ORDER BY place_id, date
            """,
    )
    return cursor


async def db_get_subscription_dict(pg_realdict_cursor, place_id):
    pg_realdict_cursor.execute(
        f"""
        SELECT
            place_id,
            tariff,
            next_tariff,
            is_trial,
            activated_at,
            valid_until,
            is_partner_updated,
            revision
         FROM eats_place_subscriptions.subscriptions
         WHERE place_id = {place_id}
        """,
    )
    return pg_realdict_cursor.fetchone()


async def db_get_sub_with_place_dict(pg_realdict_cursor, place_id):
    pg_realdict_cursor.execute(
        f"""
        SELECT
            place_id,
            tariff,
            next_tariff,
            is_trial,
            activated_at,
            valid_until,
            is_partner_updated,
            revision,
            business_type,
            country_code,
            timezone,
            region_id,
            inn
         FROM eats_place_subscriptions.subscriptions
         JOIN eats_place_subscriptions.places USING(place_id)
         WHERE place_id = {place_id}
        """,
    )
    return pg_realdict_cursor.fetchone()


async def db_get_change_log_dict(pg_realdict_cursor, revision):
    pg_realdict_cursor.execute(
        f"""SELECT
                place_id,
                change_type,
                author,
                state_before,
                state_after
            FROM eats_place_subscriptions.subscriptions_change_log
            WHERE revision = {revision}
        """,
    )
    return pg_realdict_cursor.fetchone()


def set_tariffs_experiment(value):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_place_subscriptions_tariffs',
        consumers=['eats-place-subscriptions/tariffs'],
        clauses=[],
        default_value=value,
    )

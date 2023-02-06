# pylint: disable=redefined-outer-name
import datetime

import psycopg2
import pytest


from classifier_worker.generated.cron import run_cron


async def check_results(cursor, mode):
    if mode == 'full':
        condition = ''
    if mode == 'only_deleted':
        condition = '\nWHERE is_deleted = TRUE'
    if mode == 'only_existed':
        condition = '\nWHERE is_deleted = FALSE'
    cursor.execute(
        f"""
            SELECT
                id,
                car_number,
                zones,
                tariffs,
                started_at,
                ended_at
            FROM classifier.exceptions_v2 {condition}
            ORDER BY car_number
        """,
    )
    existed_exceptions = [
        (
            '9bbffe69c5cf4213b0df8411d611e811',
            'А228АА777',
            ['moscow', 'spb'],
            ['econom'],
            datetime.datetime(
                2020,
                8,
                21,
                23,
                55,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                8,
                22,
                0,
                5,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        (
            '9bbffe69c5cf4213b0df8411d611e812',
            'В777ВВ777',
            ['balashiha', 'bryansk'],
            ['vip', 'child_tariff'],
            datetime.datetime(
                2020,
                8,
                21,
                23,
                51,
                40,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                8,
                22,
                0,
                8,
                20,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        (
            '9bbffe69c5cf4213b0df8411d611e810',
            'Х492НК77',
            [],
            ['minivan'],
            datetime.datetime(
                2020,
                8,
                21,
                23,
                55,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                8,
                22,
                0,
                5,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]
    deleted_exceptions = [
        (
            'd384mvxo373jndks93n5vxrz723',
            'A777AA777',
            ['chelyabinsk'],
            ['vip', 'uberblack'],
            datetime.datetime(
                2020,
                2,
                20,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2021,
                2,
                20,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]
    if mode == 'full':
        deleted_exceptions.extend(existed_exceptions)
        assert cursor.fetchall() == deleted_exceptions
    if mode == 'only_deleted':
        assert cursor.fetchall() == deleted_exceptions
    if mode == 'only_existed':
        assert cursor.fetchall() == existed_exceptions


@pytest.mark.now('2020-08-22T00:00:00+00:00')
async def test_classifier_exceptions_migration(cron_context, pgsql):
    await run_cron.main(
        [
            'classifier_worker.crontasks.classifier_exceptions_migration_v2',
            '-t',
            '0',
        ],
    )

    cursor = pgsql['classifier'].cursor()
    await check_results(cursor, 'only_existed')

    await run_cron.main(
        [
            'classifier_worker.crontasks.classifier_exceptions_migration_v2',
            '-t',
            '0',
        ],
    )

    # check idempotency
    await check_results(cursor, 'only_existed')


@pytest.mark.pgsql('classifier', files=['exceptions_v2.sql'])
@pytest.mark.now('2020-08-22T00:00:00+00:00')
async def test_classifier_remove_exceptions(cron_context, pgsql):
    await run_cron.main(
        [
            'classifier_worker.crontasks.classifier_exceptions_migration_v2',
            '-t',
            '0',
        ],
    )

    cursor = pgsql['classifier'].cursor()
    await check_results(cursor, 'only_deleted')


@pytest.mark.pgsql('classifier', files=['exceptions_v2.sql'])
@pytest.mark.now('2020-08-22T00:00:00+00:00')
async def test_classifier_full_exceptions(cron_context, pgsql):
    await run_cron.main(
        [
            'classifier_worker.crontasks.classifier_exceptions_migration_v2',
            '-t',
            '0',
        ],
    )

    cursor = pgsql['classifier'].cursor()
    await check_results(cursor, 'full')

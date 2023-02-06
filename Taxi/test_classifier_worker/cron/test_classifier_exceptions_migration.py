# pylint: disable=redefined-outer-name
import datetime

import psycopg2
import pytest


from classifier_worker.generated.cron import run_cron


async def check_results(cursor):
    cursor.execute(
        """
            SELECT
                car_number,
                zones,
                tariffs,
                started_at,
                ended_at
            FROM classifier.exceptions
            ORDER BY car_number
        """,
    )

    assert cursor.fetchall() == [
        (
            'А228АА777',
            ['moscow', 'spb'],
            ['econom'],
            datetime.datetime(
                2020,
                8,
                22,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                8,
                22,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        (
            'В777ВВ777',
            ['balashiha', 'bryansk'],
            ['vip', 'child_tariff'],
            datetime.datetime(
                2020,
                8,
                22,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                8,
                22,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
        (
            'Х492НК77',
            [],
            ['minivan'],
            datetime.datetime(
                2020,
                8,
                22,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
            datetime.datetime(
                2020,
                8,
                22,
                3,
                0,
                tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=180, name=None),
            ),
        ),
    ]


@pytest.mark.now('2020-08-22T23:00:00+00:00')
async def test_classifier_exceptions_migration(cron_context, pgsql):
    await run_cron.main(
        [
            'classifier_worker.crontasks.classifier_exceptions_migration',
            '-t',
            '0',
        ],
    )

    cursor = pgsql['classifier'].cursor()
    await check_results(cursor)

    await run_cron.main(
        [
            'classifier_worker.crontasks.classifier_exceptions_migration',
            '-t',
            '0',
        ],
    )

    # check idempotency
    await check_results(cursor)


@pytest.mark.pgsql('classifier', files=['exceptions.sql'])
@pytest.mark.now('2020-08-22T23:00:00+00:00')
async def test_classifier_remove_exceptions(cron_context, pgsql):
    await run_cron.main(
        [
            'classifier_worker.crontasks.classifier_exceptions_migration',
            '-t',
            '0',
        ],
    )

    cursor = pgsql['classifier'].cursor()
    await check_results(cursor)

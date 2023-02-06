# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
# flake8: noqa: E501

import time

from metrics_aggregations import helpers as metrics_helpers
import psycopg2
import pytest

DISTLOCK_NAME = 'scooters-misc-db-cleaner'


@pytest.mark.config(
    SCOOTERS_MISC_DB_CLEANER_SETTINGS={
        'sleep-time-ms': 10000,
        'enabled': True,
        'batch_size': 3,
        'max_age': 60 * 60 * 24,  # 1 day
    },
)
async def test_simple(
        taxi_scooters_misc,
        pgsql,
        generate_uuid,
        taxi_scooters_misc_monitor,
        get_single_metric_by_label_values,
):
    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )

    now = int(time.time())
    hour = 60 * 60

    insert_query = f"""
        INSERT INTO drive_offers
            (id, constructor_id, object_id, user_id, deadline, data)
        VALUES
            ('offer_1', 'minutes', '{generate_uuid}', '{generate_uuid}', {now - 20 * hour}, ''),
            ('offer_2', 'minutes', '{generate_uuid}', '{generate_uuid}', {now - 25 * hour}, ''),
            ('offer_3', 'minutes', '{generate_uuid}', '{generate_uuid}', {now - 30 * hour}, ''),
            ('offer_4', 'minutes', '{generate_uuid}', '{generate_uuid}', {now - 35 * hour}, ''),
            ('offer_5', 'minutes', '{generate_uuid}', '{generate_uuid}', {now - 40 * hour}, '');
    """
    cursor.execute(insert_query)

    select_query = 'SELECT id FROM drive_offers;'

    cursor.execute(select_query)
    offers_before_cleaning = cursor.fetchall()
    assert len(offers_before_cleaning) == 5

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)

    cursor.execute(select_query)
    offers_after_cleaning = cursor.fetchall()
    assert len(offers_after_cleaning) == 2
    assert offers_after_cleaning == [{'id': 'offer_1'}, {'id': 'offer_2'}]

    sensor = 'scooters_misc_db_cleaner_metrics'
    metric = await get_single_metric_by_label_values(
        taxi_scooters_misc_monitor, sensor=sensor, labels={'sensor': sensor},
    )
    assert metric == metrics_helpers.Metric(
        labels={'sensor': sensor, 'table': 'drive_offers'}, value=3,
    )

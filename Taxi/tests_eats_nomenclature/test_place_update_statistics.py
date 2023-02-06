import datetime as dt

import pytest

PERIODIC_NAME = 'eats_nomenclature-collect_metrics-place_update'
METRICS_NAME = 'place-update-metrics'


def settings(
        assortment_outdated_threshold_in_hours=2,
        availabilities_outdated_threshold_in_minutes=30,
        stocks_outdated_threshold_in_minutes=30,
        on_enabled_delay_in_hours=2,
):
    return {
        '__default__': {
            'assortment_outdated_threshold_in_hours': (
                assortment_outdated_threshold_in_hours
            ),
            'place_availabilities_outdated_threshold_in_minutes': (
                availabilities_outdated_threshold_in_minutes
            ),
            'place_stocks_outdated_threshold_in_minutes': (
                stocks_outdated_threshold_in_minutes
            ),
            'place_on_enabled_delay_in_hours': on_enabled_delay_in_hours,
        },
    }


@pytest.mark.suspend_periodic_tasks('place-update-metrics')
@pytest.mark.config(EATS_NOMENCLATURE_VERIFICATION=settings())
@pytest.mark.parametrize(
    'metric_name, metric_threshold_config_name, sql_update_at_name',
    [
        (
            'places_with_old_assortment_count',
            'assortment_outdated_threshold_in_hours',
            'assortment_activated_at',
        ),
        (
            'places_with_old_availabilities_count',
            'place_availabilities_outdated_threshold_in_minutes',
            'availability_update_started_at',
        ),
        (
            'places_with_old_stocks_count',
            'place_stocks_outdated_threshold_in_minutes',
            'stock_update_started_at',
        ),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_dictionaries.sql'])
async def test_metrics(
        pgsql,
        taxi_config,
        taxi_eats_nomenclature,
        taxi_eats_nomenclature_monitor,
        metric_name,
        metric_threshold_config_name,
        sql_update_at_name,
):
    class Test:
        last_metric_value = 0
        last_place_id = 0

        @staticmethod
        async def check_metrics(expected_count):
            metrics = await taxi_eats_nomenclature_monitor.get_metrics()
            assert metric_name in metrics[METRICS_NAME]
            assert metrics[METRICS_NAME][metric_name] == expected_count

        async def perform(self, place_data, is_expected_to_increase):
            self.last_place_id += 1
            sql_add_place_data(
                pgsql,
                place_id=self.last_place_id,
                slug=f'place_{self.last_place_id}',
                update_at_name=sql_update_at_name,
                **place_data,
            )
            await taxi_eats_nomenclature.run_periodic_task(PERIODIC_NAME)

            if is_expected_to_increase:
                self.last_metric_value += 1
            await Test.check_metrics(self.last_metric_value)

    def get_time_now(offset_in_minutes):
        return (
            dt.datetime.now() - dt.timedelta(minutes=offset_in_minutes)
        ).strftime('%Y-%m-%d %H:%M:%S')

    config = taxi_config.get('EATS_NOMENCLATURE_VERIFICATION')['__default__']
    threshold_in_minutes = config[metric_threshold_config_name]
    assert metric_threshold_config_name.endswith(
        'minutes',
    ) or metric_threshold_config_name.endswith('hours')
    if metric_threshold_config_name.endswith('hours'):
        threshold_in_minutes *= 60
    enabled_at_delay_in_minutes = (
        config['place_on_enabled_delay_in_hours'] * 60
    )

    test = Test()

    # No data
    await test.check_metrics(0)

    # New data
    await test.perform(
        place_data={
            'updated_at': '2039-01-01',
            'is_enabled': True,
            'enabled_at': get_time_now(enabled_at_delay_in_minutes * 2),
        },
        is_expected_to_increase=False,
    )

    # Old data, but above threshold (by a lot)
    await test.perform(
        place_data={
            'updated_at': '2019-01-01',
            'is_enabled': True,
            'enabled_at': get_time_now(enabled_at_delay_in_minutes * 2),
        },
        is_expected_to_increase=True,
    )

    # Old data, but above threshold (barely)
    await test.perform(
        place_data={
            'updated_at': get_time_now(threshold_in_minutes * 2),
            'is_enabled': True,
            'enabled_at': get_time_now(enabled_at_delay_in_minutes * 2),
        },
        is_expected_to_increase=True,
    )

    # Old data, but below threshold
    await test.perform(
        place_data={
            'updated_at': get_time_now(threshold_in_minutes / 2),
            'is_enabled': True,
            'enabled_at': get_time_now(enabled_at_delay_in_minutes * 2),
        },
        is_expected_to_increase=False,
    )

    # Old data and above threshold, but disabled
    await test.perform(
        place_data={
            'updated_at': get_time_now(threshold_in_minutes * 2),
            'is_enabled': False,
            'enabled_at': get_time_now(enabled_at_delay_in_minutes * 2),
        },
        is_expected_to_increase=False,
    )

    # Old data and above threshold, but delay for enabled has not expired
    await test.perform(
        place_data={
            'updated_at': get_time_now(threshold_in_minutes * 2),
            'is_enabled': True,
            'enabled_at': get_time_now(enabled_at_delay_in_minutes / 2),
        },
        is_expected_to_increase=False,
    )

    # Old data and is_vendor = true
    await test.perform(
        place_data={
            'updated_at': get_time_now(threshold_in_minutes * 2),
            'is_enabled': True,
            'enabled_at': get_time_now(enabled_at_delay_in_minutes * 2),
            'is_vendor': True,
        },
        is_expected_to_increase=True,
    )


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=False)


def sql_add_place_data(
        pgsql,
        place_id,
        slug,
        is_enabled,
        update_at_name,
        updated_at,
        enabled_at,
        is_vendor=False,
):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.places (id, slug, is_enabled, is_vendor)
        values ({place_id}, '{slug}', {str(is_enabled).lower()}, {is_vendor})
        """,
    )
    if update_at_name == 'assortment_activated_at':
        # insert default values into place_update_statuses
        # so that join with it is not empty
        cursor.execute(
            f"""
            insert into
              eats_nomenclature.place_update_statuses
            (
              place_id
            )
            values ({place_id})
            """,
        )
        # insert outdated assortment into place_assortments
        cursor.execute(
            f"""
                insert into eats_nomenclature.assortments
                default values
                returning id;
                """,
        )
        assortment_id = list(cursor)[0][0]
        cursor.execute(
            f"""
            insert into eats_nomenclature.place_assortments(
                place_id, assortment_id, assortment_activated_at
            )
            values ({place_id}, {assortment_id}, '{updated_at}')
            on conflict (place_id, coalesce(trait_id, -1)) do update
            set
                assortment_id = excluded.assortment_id,
                assortment_activated_at = excluded.assortment_activated_at,
                updated_at = now();
            """,
        )
    else:
        cursor.execute(
            f"""
            insert into
              eats_nomenclature.place_update_statuses
            (
              place_id,
              {update_at_name}
            )
            values ({place_id}, '{updated_at}')
            """,
        )

    if is_enabled:
        cursor.execute(
            f"""
            update eats_nomenclature.place_update_statuses
              set enabled_at = '{enabled_at}', updated_at = now()
            where place_id = {place_id}
            """,
        )

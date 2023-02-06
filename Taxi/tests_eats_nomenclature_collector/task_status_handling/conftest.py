import pytest


@pytest.fixture
def config_set_push_model(update_taxi_config):
    def impl(brand_ids=None, place_ids=None):
        update_taxi_config(
            'EATS_PLACE_GROUPS_REPLICA_SWITCH_TO_PUSH_MODEL',
            {'brand_ids': brand_ids or [], 'place_ids': place_ids or []},
        )

    return impl


@pytest.fixture
def sql_add_place_task_for_task_status_test(
        pg_cursor,
):  # pylint: disable=C0103
    def impl(task_id, place_id, brand_id, task_type, status, synced_at):
        pg_cursor.execute(
            f"""
            insert into eats_nomenclature_collector.brands(
                id,
                slug
            )
            values
                ({brand_id}, {brand_id})
            on conflict(id)
            do nothing
            """,
        )

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature_collector.place_groups(
                id,
                name,
                parser_days_of_week,
                parser_hours,
                stop_list_enabled,
                is_vendor
            )
            values (
                {brand_id},
                {brand_id},
                '1111111',
                '0:00',
                true,
                false
            )
            on conflict(id)
            do nothing
            """,
        )

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature_collector.places(
                id,
                slug,
                brand_id,
                place_group_id,
                is_enabled,
                is_parser_enabled,
                stop_list_enabled
            )
            values (
                {place_id},
                {place_id},
                {brand_id},
                {brand_id},
                true,
                true,
                false
            )
            on conflict(id)
            do nothing
            """,
        )

        if task_type == 'nomenclature':
            pg_cursor.execute(
                f"""
            insert into eats_nomenclature_collector.nomenclature_brand_tasks(
                id, brand_id, status
            )
            values
                ({brand_id}, {brand_id}, 'created')
            on conflict(id)
            do nothing
            """,
            )

            pg_cursor.execute(
                f"""
            insert into eats_nomenclature_collector.nomenclature_place_tasks(
                id,
                place_id,
                nomenclature_brand_task_id,
                status,
                status_synchronized_at
            )
            values
                (
                    '{task_id}',
                    {place_id},
                    {brand_id},
                    '{status}',
                    '{synced_at}'
                )
            """,
            )
        else:
            pg_cursor.execute(
                f"""
            insert into eats_nomenclature_collector.{task_type}_tasks(
                id, place_id, status, file_path, status_synchronized_at
            )
            values
                ('{task_id}', {place_id}, '{status}', null, '{synced_at}')
            """,
            )

    return impl

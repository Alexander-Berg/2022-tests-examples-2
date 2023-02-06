from eats_integration_shooter.stq import update_place_group_settings


async def test_should_correct_run(stq_runner, stq3_context, task_info, pgsql):
    await update_place_group_settings.task(
        stq3_context,
        task_info,
        place_group_settings=[
            {
                'parser_name': 'retail_parser',
                'parser_options': '{}',
                'place_group_id': '1',
            },
        ],
        settings_type='parser_settings',
    )
    assert _get_count(pgsql, 'place_group_settings')


def _get_count(pgsql, table_name):
    with pgsql['eats_integration_shooter'].dict_cursor() as cursor:
        cursor.execute(f'select count(*) from {table_name}')
        count = cursor.fetchone()
    return count[0]

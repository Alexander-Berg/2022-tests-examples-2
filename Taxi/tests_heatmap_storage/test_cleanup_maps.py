import pytest


def execute_query(query, pgsql):
    pg_cursor = pgsql['heatmap-storage'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


@pytest.mark.config(HEATMAPS_STORAGE_TTL_MIN={'__default__': 120, 'aaa': 60})
@pytest.mark.now('2020-01-31T00:00:00')
@pytest.mark.suspend_periodic_tasks('task-maps_cleanup-periodic')
async def test_add_map(taxi_heatmap_storage, pgsql):

    res = execute_query(
        'INSERT INTO maps.maps(content_key, created_time) values (\'akey\', '
        '\'2020-01-30T00:00:00\') returning id, created_time',
        pgsql,
    )
    inserted_id = res[0][0]
    await taxi_heatmap_storage.run_periodic_task('task-maps_cleanup-periodic')
    res = execute_query(
        f'select content_key from maps.maps where id = {inserted_id}', pgsql,
    )
    assert not res

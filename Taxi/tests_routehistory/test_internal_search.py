import pytest

from . import utils


@pytest.mark.now('2025-03-24T16:45:17+0000')
async def test_pg_cleaner(routehistory_internal, load_json, pgsql):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    await routehistory_internal.call('CleanSearches', 1576800, None)
    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)

    cursor.execute(
        'SELECT c FROM routehistory.search_history c ORDER BY '
        'yandex_uid, created',
    )
    search_history = utils.convert_pg_result(cursor.fetchall())
    expected = [(10000000, '2024-03-24T16:45:17')]
    assert expected == list(
        map(
            lambda x: (x['yandex_uid'], x['created'].isoformat()),
            search_history,
        ),
    )

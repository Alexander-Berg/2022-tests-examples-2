import pytest

from tests_persey_core import utils


@pytest.mark.parametrize(
    'uids,expected_resp_file',
    [
        ([1234], 'expected_resp_non_existent.json'),
        ([100], 'expected_resp_1.json'),
        ([100, 1234], 'expected_resp_1.json'),
        ([102], 'expected_resp_2.json'),
        ([100, 102], 'expected_resp_merge_1.json'),
        ([100, 101, 102], 'expected_resp_merge_2.json'),
    ],
)
async def test_user_ride_subs_status(
        taxi_persey_core, load_json, pgsql, uids, expected_resp_file,
):
    cursor = pgsql['persey_payments'].cursor()
    utils.fill_db(cursor, load_json('db.json'))
    await taxi_persey_core.invalidate_caches(
        clean_update=True, cache_names=['ride-subs-cache', 'donations-cache'],
    )
    response = await taxi_persey_core.get(
        '/persey-core/user-ride-subs-status',
        params={'uid': ','.join(str(uid) for uid in uids)},
    )
    assert response.status == 200
    assert response.json() == load_json(expected_resp_file)

import copy

import pytest

from . import utils

BASIC_HEADERS = {
    'X-YaTaxi-Bound-Uids': '5555555551,5555555552',
    'X-YaTaxi-PhoneId': '1dcf5804abae14bb0d31d02d',
    'X-Yandex-UID': '5555555553',
}


def _get_searches(cursor):
    cursor.execute(
        'SELECT yandex_uid, created '
        'FROM routehistory.search_history '
        'ORDER BY yandex_uid, created',
    )
    search_ids = utils.convert_pg_result(cursor.fetchall())
    return set(map(lambda x: (x[0], x[1].hour), search_ids))


def _get_phone_history(cursor_ph):
    cursor_ph.execute(
        'SELECT order_id '
        'FROM routehistory_ph.phone_history2 '
        'ORDER BY yandex_uid, created',
    )
    return set(utils.convert_pg_result(cursor_ph.fetchall()))


@pytest.mark.parametrize('basic_headers', [{}, BASIC_HEADERS])
@pytest.mark.parametrize(
    'order_to_forget,expected_deleted_ph,expected_deleted_searches,'
    'additional_headers,',
    [
        pytest.param(
            '11111111000000000000000000000001',
            {'11111111-0000-0000-0000-000000000001'},
            {(12345678, 10), (12345678, 15)},
            {},
            marks=[pytest.mark.now('2025-01-01T18:00:00+0000')],
        ),
        pytest.param(
            '11111111000000000000000000000001',
            {'11111111-0000-0000-0000-000000000001'},
            set(),
            {},
            marks=[pytest.mark.now('2025-01-02T18:00:00+0000')],
        ),
        pytest.param(
            '11111111000000000000000000000002',
            {'11111111-0000-0000-0000-000000000002'},
            {(12345678, 10)},
            {},
            marks=[pytest.mark.now('2025-01-01T18:00:00+0000')],
        ),
        pytest.param(
            '11111111000000000000000000000003',
            {'11111111-0000-0000-0000-000000000003'},
            set(),
            {},
            marks=[pytest.mark.now('2025-01-01T18:00:00+0000')],
        ),
        pytest.param(
            '11111111000000000000000000000003',
            {'11111111-0000-0000-0000-000000000003'},
            {(1, 5)},
            {'X-Yandex-UID': '1'},
            marks=[pytest.mark.now('2025-01-01T18:00:00+0000')],
        ),
        pytest.param(
            '11111111000000000000000000000003',
            {'11111111-0000-0000-0000-000000000003'},
            {(1, 5)},
            {'X-YaTaxi-Bound-Uids': '1,2,12345678'},
            marks=[pytest.mark.now('2025-01-01T18:00:00+0000')],
        ),
        pytest.param(
            '11111111000000000000000000000004',
            set(),
            set(),
            {'X-Yandex-UID': '1'},
            marks=[pytest.mark.now('2025-01-01T18:00:00+0000')],
        ),
    ],
)
async def test_forget(
        taxi_routehistory,
        load_json,
        pgsql,
        order_to_forget,
        expected_deleted_ph,
        expected_deleted_searches,
        basic_headers,
        additional_headers,
):
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    utils.fill_db(cursor, load_json('db.json'))
    utils.fill_db(cursor_ph, load_json('db_ph.json'))

    ph_before = _get_phone_history(cursor_ph)
    searches_before = _get_searches(cursor)

    headers = copy.deepcopy(basic_headers)
    headers.update(additional_headers)
    response = await taxi_routehistory.post(
        'routehistory/forget', {'order_id': order_to_forget}, headers=headers,
    )

    ph_after = _get_phone_history(cursor_ph)
    searches_after = _get_searches(cursor)

    ph_diff = ph_before - ph_after
    searches_diff = searches_before - searches_after
    assert ph_diff == expected_deleted_ph
    assert searches_diff == expected_deleted_searches

    if expected_deleted_ph:
        assert response.status_code == 200
        assert response.json() == {}
    else:
        assert response.status_code == 204

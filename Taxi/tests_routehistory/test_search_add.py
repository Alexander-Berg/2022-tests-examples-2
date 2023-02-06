import pytest

from . import utils

YANDEX_UID = '12345678'


async def test_search_add(taxi_routehistory, load_json, pgsql):
    response = await taxi_routehistory.post(
        'routehistory/search-add',
        load_json('request.json'),
        headers={'X-Yandex-UID': YANDEX_UID},
    )
    assert response.status_code == 200

    cursor = pgsql['routehistory'].cursor()
    utils.register_user_types(cursor)

    def _test_result():
        cursor.execute(
            'SELECT c FROM routehistory.search_history c ORDER BY '
            'yandex_uid, created',
        )
        search_history = utils.convert_pg_result(cursor.fetchall())
        utils.decode_searches(search_history)
        cursor.execute(
            'SELECT c FROM routehistory.common_strings c ORDER BY id',
        )
        strings = utils.convert_pg_result(cursor.fetchall())

        expected = load_json('expected_db.json')
        assert strings == expected.get('common_strings', [])
        assert search_history == expected.get('search_history', [])

    _test_result()

    # Test idempotency
    response = await taxi_routehistory.post(
        'routehistory/search-add',
        load_json('request.json'),
        headers={'X-Yandex-UID': YANDEX_UID},
    )
    assert response.status_code == 200
    _test_result()


@pytest.mark.parametrize(
    'request_file,code,msg',
    [
        ('bad_request_1.json', 'missing_a', ''),
        ('bad_request_2.json', 'missing_b', ''),
        ('bad_request_3.json', 'repeated_type', 'a'),
        ('bad_request_4.json', 'bad_type', 'mid_'),
        ('bad_request_5.json', 'non_sequential_types', ''),
    ],
)
async def test_bad_request(
        taxi_routehistory, load_json, request_file, code, msg,
):
    response = await taxi_routehistory.post(
        'routehistory/search-add',
        load_json(request_file),
        headers={'X-Yandex-UID': YANDEX_UID},
    )
    assert response.status_code == 400
    assert response.json() == {'code': code, 'message': msg}

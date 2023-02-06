import pytest

from . import utils


async def test_write_bulk(routehistory_internal, load_json, pgsql):
    await routehistory_internal.call(
        'WritePhoneHistory', load_json('records.json'),
    )
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    records = utils.read_phone_history_db(cursor, cursor_ph)
    assert records.strings == load_json('expected_db_strings.json')
    assert records.phone_history == load_json('expected_db_phone_history.json')
    assert records.users == load_json('expected_db_users.json')

    # TODO: duplicates and user index update tests


async def test_write_single(routehistory_internal, load_json):
    await routehistory_internal.call(
        'WritePhoneHistory', [load_json('records.json')[0]],
    )


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='unsharded', marks=[]),
        pytest.param(
            id='sharded',
            marks=[
                pytest.mark.config(
                    ROUTEHISTORY_PARTITION={
                        'phone_history': [
                            {
                                'key_min': 0,
                                'key_max': 50,
                                'type': 'read_write',
                                'shard': 1,
                            },
                            {
                                'key_min': 50,
                                'key_max': 100,
                                'type': 'read_write',
                                'shard': 2,
                            },
                        ],
                        'user_index': [
                            {
                                'key_min': 0,
                                'key_max': 6,
                                'type': 'read_write',
                                'shard': 1,
                            },
                            {
                                'key_min': 6,
                                'key_max': 100,
                                'type': 'read_write',
                                'shard': 1,
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
async def test_read_simple(routehistory_internal, load_json, pgsql):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))
    result = await routehistory_internal.call(
        'ReadPhoneHistory',
        [4567, 123456],
        [],
        ['yataxi', 'yauber'],
        None,
        None,
        None,
        True,
    )
    assert result == load_json('expected_records.json')


async def test_write_ph_to_shard(routehistory_internal, load_json, pgsql):
    await routehistory_internal.call(
        'WritePhoneHistoryToShard', 12, load_json('records.json'),
    )
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    records = utils.read_phone_history_db(cursor, cursor_ph)
    assert records.strings == load_json('expected_db_strings.json')
    assert records.phone_history == load_json('expected_db_phone_history.json')
    assert records.users == []


@pytest.mark.parametrize(
    'is_portal_uid,last_created,last_order_id,limit,expected_ids',
    [
        pytest.param(
            True,
            '2021-04-01T00:00:00+0000',
            '00000000000000000000000000000000',
            100,
            ['6c35cd7d05453ed7b58f6c45572b0921'],
            id='portal',
        ),
        pytest.param(
            True,
            '2021-04-01T00:00:00+0000',
            '6c35cd7d05453ed7b58f6c45572b0921',
            100,
            [],
            id='portal_with_last_id',
        ),
        pytest.param(
            True,
            '2020-04-01T00:00:00+0000',
            '00000000000000000000000000000000',
            100,
            ['6c35cd7d05453ed7b58f6c45572b0921'],
            id='portal_filter_by_date',
        ),
        pytest.param(
            True,
            '2019-04-01T00:00:00+0000',
            '00000000000000000000000000000000',
            100,
            [],
            id='portal_filter_by_date_2',
        ),
        pytest.param(
            False,
            '2021-04-01T00:00:00+0000',
            '00000000000000000000000000000000',
            100,
            ['7b58f6cd7d05453ed45572b09216c35c'],
            id='non_portal',
        ),
        pytest.param(
            False,
            '2021-04-01T00:00:00+0000',
            '7b58f6cd7d05453ed45572b09216c35c',
            100,
            [],
            id='non_portal_with_last_id',
        ),
        pytest.param(
            False,
            '2020-04-01T00:00:00+0000',
            '00000000000000000000000000000000',
            100,
            [],
            id='non_portal_filter_by_date',
        ),
    ],
)
async def test_read_ph_shard(
        routehistory_internal,
        load_json,
        pgsql,
        is_portal_uid,
        last_created,
        last_order_id,
        limit,
        expected_ids,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))
    result = await routehistory_internal.call(
        'ReadPhoneHistoryShard',
        12,
        is_portal_uid,
        last_created,
        last_order_id,
        limit,
    )
    records = load_json('expected_records.json')
    expected_result = [
        next(record for record in records if record['order_id'] == order_id)
        for order_id in expected_ids
    ]
    assert result == expected_result


@pytest.mark.parametrize(
    'is_portal_uid,last_updated,last_yandex_uid,'
    'last_phone_id,limit,expected_uids',
    [
        pytest.param(
            True,
            '2021-04-01T00:00:00+0000',
            0,
            '000000000000000000000000',
            100,
            [123456],
            id='portal',
        ),
        pytest.param(
            True,
            '2020-04-01T00:00:00+0000',
            0,
            '000000000000000000000000',
            100,
            [123456],
            id='portal_filter_by_date',
        ),
        pytest.param(
            True,
            '2019-04-01T00:00:00+0000',
            0,
            '000000000000000000000000',
            100,
            [],
            id='portal_filter_by_date',
        ),
        pytest.param(
            True,
            '2021-04-01T00:00:00+0000',
            123456,
            '000000000000000000000000',
            100,
            [123456],
            id='portal_same_uid',
        ),
        pytest.param(
            True,
            '2021-04-01T00:00:00+0000',
            0,
            '5e663654e344a249db330a66',
            100,
            [123456],
            id='portal_same_phone_id',
        ),
        pytest.param(
            True,
            '2021-04-01T00:00:00+0000',
            123456,
            '5e663654e344a249db330a66',
            100,
            [],
            id='portal_same_uid_and_phone_id',
        ),
        pytest.param(
            False,
            '2021-04-01T00:00:00+0000',
            0,
            '000000000000000000000000',
            100,
            [4567],
            id='non_portal',
        ),
        pytest.param(
            False,
            '2020-04-01T00:00:00+0000',
            0,
            '000000000000000000000000',
            100,
            [],
            id='non_portal_filter_by_date',
        ),
        pytest.param(
            False,
            '2025-04-01T00:00:00+0000',
            4567,
            '6634a249db654e34330a665e',
            100,
            [],
            id='non_portal_same_uid_phone_id',
        ),
    ],
)
async def test_read_ui_shard(
        routehistory_internal,
        load_json,
        pgsql,
        is_portal_uid,
        last_updated,
        last_yandex_uid,
        last_phone_id,
        limit,
        expected_uids,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))
    result = await routehistory_internal.call(
        'ReadUserIndexShard',
        12,
        is_portal_uid,
        last_updated,
        last_yandex_uid,
        last_phone_id,
        limit,
    )
    users = load_json('expected_users.json')
    expected_result = [
        next(user for user in users if user['yandex_uid'] == uid)
        for uid in expected_uids
    ]
    assert result == expected_result


async def test_write_ui_to_shard(routehistory_internal, load_json, pgsql):
    await routehistory_internal.call(
        'WriteUserIndexToShard', 12, load_json('users.json'),
    )
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    records = utils.read_phone_history_db(cursor, cursor_ph)
    assert records.strings == []
    assert records.phone_history == []
    assert records.users == load_json('expected_db_users.json')


async def test_ui_safe_upsert(routehistory_internal, load_json, pgsql):
    cursor_ph = pgsql['routehistory_ph'].cursor()
    utils.register_user_types_ph(cursor_ph)

    async def _do_upsert(file):
        await routehistory_internal.call(
            'WriteUserIndexToShard', 12, load_json(file),
        )
        cursor_ph.execute(
            'SELECT c.ctid, c FROM routehistory_ph.users c '
            'ORDER BY yandex_uid, phone_id',
        )
        db_result = utils.convert_pg_result(cursor_ph.fetchall())
        ctids = list(map(lambda x: x[0], db_result))
        users = list(map(lambda x: x[1], db_result))
        return (ctids, users)

    # First do an insert and an identical update:
    for _ in range(2):
        (ctids, users) = await _do_upsert('users.json')
        assert ctids == ['(0,1)', '(0,2)']
        assert users == load_json('expected_db_users.json')
    # Now update some users two times to be sure:
    for _ in range(2):
        (ctids, users) = await _do_upsert('users_for_update.json')
        assert ctids == ['(0,3)', '(0,2)']
        assert users == load_json('expected_db_users_updated.json')


@pytest.mark.parametrize(
    'order_ids,expected_db_ids',
    [
        pytest.param(
            ['6c35cd7d05453ed7b58f6c45572b0921'],
            ['7b58f6cd-7d05-453e-d455-72b09216c35c'],
            id='remove_1',
        ),
        pytest.param(
            ['7b58f6cd7d05453ed45572b09216c35c'],
            ['6c35cd7d-0545-3ed7-b58f-6c45572b0921'],
            id='remove_2',
        ),
        pytest.param(
            [
                '6c35cd7d05453ed7b58f6c45572b0921',
                '7b58f6cd7d05453ed45572b09216c35c',
            ],
            [],
            id='remove_both',
        ),
        pytest.param(
            [],
            [
                '6c35cd7d-0545-3ed7-b58f-6c45572b0921',
                '7b58f6cd-7d05-453e-d455-72b09216c35c',
            ],
            id='remove_none',
        ),
        pytest.param(
            [
                '00000000000000000000000000000001',
                '00000000000000000000000000000002',
            ],
            [
                '6c35cd7d-0545-3ed7-b58f-6c45572b0921',
                '7b58f6cd-7d05-453e-d455-72b09216c35c',
            ],
            id='remove_other',
        ),
        pytest.param(
            [
                '6c35cd7d05453ed7b58f6c45572b0921',
                '7b58f6cd7d05453ed45572b09216c35c',
                '00000000000000000000000000000001',
                '00000000000000000000000000000002',
            ],
            [],
            id='remove_more',
        ),
    ],
)
async def test_delete_ph_shard(
        routehistory_internal, load_json, pgsql, order_ids, expected_db_ids,
):
    await routehistory_internal.call(
        'WritePhoneHistory', load_json('records.json'),
    )
    await routehistory_internal.call(
        'DeletePhoneHistoryFromShard', 12, order_ids,
    )
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    records = utils.read_phone_history_db(cursor, cursor_ph)
    assert records.strings == load_json('expected_db_strings.json')
    all_phone_history = load_json('expected_db_phone_history.json')
    expected_result = [
        next(
            record
            for record in all_phone_history
            if record['order_id'] == order_id
        )
        for order_id in expected_db_ids
    ]
    assert records.phone_history == expected_result
    assert records.users == load_json('expected_db_users.json')


@pytest.mark.parametrize(
    'keys,expected_db_uids',
    [
        pytest.param(
            [{'yandex_uid': 123456, 'phone_id': '5e663654e344a249db330a66'}],
            [4567],
            id='remove_1',
        ),
        pytest.param(
            [{'yandex_uid': 4567, 'phone_id': '6634a249db654e34330a665e'}],
            [123456],
            id='remove_2',
        ),
        pytest.param(
            [
                {'yandex_uid': 123456, 'phone_id': '5e663654e344a249db330a66'},
                {'yandex_uid': 4567, 'phone_id': '6634a249db654e34330a665e'},
            ],
            [],
            id='remove_both',
        ),
        pytest.param([], [4567, 123456], id='remove_none'),
        pytest.param(
            [
                {'yandex_uid': 123456, 'phone_id': '000000000000000000000001'},
                {'yandex_uid': 4567, 'phone_id': '000000000000000000000002'},
                {'yandex_uid': 0, 'phone_id': '5e663654e344a249db330a66'},
                {'yandex_uid': 1, 'phone_id': '6634a249db654e34330a665e'},
            ],
            [4567, 123456],
            id='remove_other',
        ),
        pytest.param(
            [
                {'yandex_uid': 123456, 'phone_id': '000000000000000000000001'},
                {'yandex_uid': 123456, 'phone_id': '5e663654e344a249db330a66'},
            ],
            [4567],
            id='remove_with_other',
        ),
    ],
)
async def test_delete_ui_shard(
        routehistory_internal, load_json, pgsql, keys, expected_db_uids,
):
    await routehistory_internal.call(
        'WritePhoneHistory', load_json('records.json'),
    )
    await routehistory_internal.call('DeleteUsersFromShard', 12, keys)
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    records = utils.read_phone_history_db(cursor, cursor_ph)
    assert records.strings == load_json('expected_db_strings.json')

    assert records.phone_history == load_json('expected_db_phone_history.json')
    all_users = load_json('expected_db_users.json')
    expected_result = [
        next(record for record in all_users if record['yandex_uid'] == uid)
        for uid in expected_db_uids
    ]
    assert records.users == expected_result


@pytest.mark.parametrize(
    'yandex_uids,phone_ids,created_min,created_max,expected_result',
    [
        pytest.param(
            [], ['6634a249db654e34330a665e'], None, None, True, id='Test1',
        ),
        pytest.param(
            [],
            [
                '6634a249db654e34330a665e',
                '100000000000000000000001',
                '100000000000000000000002',
                '100000000000000000000003',
                '100000000000000000000004',
                '100000000000000000000005',
                '100000000000000000000006',
                '100000000000000000000007',
                '100000000000000000000008',
            ],
            None,
            None,
            True,
            id='Test2',
        ),
        pytest.param(
            [],
            [
                '100000000000000000000001',
                '100000000000000000000002',
                '100000000000000000000003',
                '100000000000000000000004',
                '100000000000000000000005',
                '100000000000000000000006',
                '100000000000000000000007',
                '100000000000000000000008',
                '6634a249db654e34330a665e',
            ],
            None,
            None,
            True,
            id='Test3',
        ),
        pytest.param(
            [],
            [
                '100000000000000000000001',
                '100000000000000000000002',
                '100000000000000000000003',
                '100000000000000000000004',
                '100000000000000000000005',
                '100000000000000000000006',
                '100000000000000000000007',
                '6634a249db654e34330a665e',
            ],
            None,
            None,
            True,
            id='Test4',
        ),
        pytest.param(
            [],
            [
                '100000000000000000000001',
                '100000000000000000000002',
                '100000000000000000000003',
                '100000000000000000000004',
                '100000000000000000000005',
                '100000000000000000000006',
                '100000000000000000000007',
                '100000000000000000000008',
                '100000000000000000000009',
            ],
            None,
            None,
            False,
            id='Test5',
        ),
        pytest.param([123456], [], None, None, True, id='Test6'),
        pytest.param(
            [123456], [], '2020-03-01T00:00:00+0000', None, True, id='Test7',
        ),
        pytest.param(
            [123456], [], '2020-03-01T00:00:01+0000', None, False, id='Test8',
        ),
        pytest.param(
            [123456], [], None, '2020-03-01T00:00:01+0000', True, id='Test9',
        ),
        pytest.param(
            [123456], [], None, '2020-02-01T00:00:00+0000', False, id='Test10',
        ),
        pytest.param(
            [123456],
            [],
            '2019-03-01T00:00:00+0000',
            '2020-04-01T00:00:00+0000',
            True,
            id='Test11',
        ),
    ],
)
async def test_check_has_phone_history(
        routehistory_internal,
        load_json,
        yandex_uids,
        phone_ids,
        created_min,
        created_max,
        expected_result,
):
    await routehistory_internal.call(
        'WritePhoneHistory', load_json('records.json'),
    )
    result = await routehistory_internal.call(
        'CheckHasPhoneHistory',
        yandex_uids,
        phone_ids,
        created_min,
        created_max,
    )
    assert result == expected_result


@pytest.mark.parametrize(
    'yandex_uids,phone_ids,created_min,created_max,'
    'max_records_at_once,expected_orders',
    [
        pytest.param(
            [],
            [],
            None,
            None,
            10,
            [
                '6c35cd7d-0545-3ed7-b58f-6c45572b0921',
                '7b58f6cd-7d05-453e-d455-72b09216c35c',
            ],
            id='KeepBoth',
        ),
        pytest.param(
            [123456],
            ['6634a249db654e34330a665e'],
            None,
            None,
            10,
            [],
            id='DeleteBoth',
        ),
        pytest.param(
            [123456],
            [],
            None,
            None,
            10,
            ['7b58f6cd-7d05-453e-d455-72b09216c35c'],
            id='DeleteYaUid',
        ),
        pytest.param(
            [],
            ['6634a249db654e34330a665e'],
            None,
            None,
            10,
            ['6c35cd7d-0545-3ed7-b58f-6c45572b0921'],
            id='DeletePhoneId',
        ),
        pytest.param(
            [123456],
            ['6634a249db654e34330a665e'],
            None,
            None,
            1,
            [],
            id='DeleteBothByOne',
        ),
        pytest.param(
            [123456],
            ['6634a249db654e34330a665e'],
            '2020-01-01T00:00:00+0000',
            '2021-10-01T00:00:00+0000',
            1,
            [],
            id='DeleteBothWithTimeLimit1',
        ),
        pytest.param(
            [123456],
            ['6634a249db654e34330a665e'],
            '2021-03-01T00:00:00+0000',
            None,
            1,
            ['6c35cd7d-0545-3ed7-b58f-6c45572b0921'],
            id='DeleteBothWithTimeLimit2',
        ),
        pytest.param(
            [123456],
            ['6634a249db654e34330a665e'],
            '2020-03-01T00:00:00+0000',
            '2020-03-02T00:00:00+0000',
            10,
            ['7b58f6cd-7d05-453e-d455-72b09216c35c'],
            id='DeleteBothWithTimeLimit3',
        ),
    ],
)
async def test_delete_phone_history(
        routehistory_internal,
        load_json,
        pgsql,
        yandex_uids,
        phone_ids,
        created_min,
        created_max,
        max_records_at_once,
        expected_orders,
):
    await routehistory_internal.call(
        'WritePhoneHistory', load_json('records.json'),
    )
    await routehistory_internal.call(
        'DeletePhoneHistory',
        yandex_uids,
        phone_ids,
        created_min,
        created_max,
        max_records_at_once,
    )
    cursor = pgsql['routehistory'].cursor()
    cursor_ph = pgsql['routehistory_ph'].cursor()
    records = utils.read_phone_history_db(cursor, cursor_ph).phone_history
    order_ids = list(map(lambda x: x['order_id'], records))
    assert order_ids == expected_orders

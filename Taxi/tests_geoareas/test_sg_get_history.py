import copy
import datetime

import pytest

from testsuite.utils import ordered_object


@pytest.mark.filldb(subvention_geoareas='spb_msk2')
async def test_get_history_erroneous_parameters(taxi_geoareas):
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': 'name_1',
            'from_timestamp': '2021-02-03T02:02:02.000000Z',
            'to_timestamp': '2021-02-02T02:02:02.000000Z',
        },
    )

    assert res.status_code == 400
    assert (
        res.json()['message']
        == 'to_timestamp can\'t be less than from_timestamp'
    )


@pytest.mark.filldb(subvention_geoareas='history')
@pytest.mark.parametrize(
    'from_timestamp, to_timestamp, expected_ids',
    [
        ('2010-02-01T02:02:02.000000Z', '2010-02-01T02:02:02.000000Z', []),
        (
            '2010-02-02T02:02:02.000000Z',
            '2010-02-02T02:02:02.000000Z',
            ['c_draft_id'],
        ),
        (
            '2010-02-03T02:02:02.000000Z',
            '2010-02-03T02:02:02.000000Z',
            ['c_draft_id'],
        ),
        ('2010-01-31T02:02:02.000000Z', '2010-02-01T02:02:02.000000Z', []),
        (
            '2010-02-01T02:02:02.000000Z',
            '2010-02-03T02:02:02.000000Z',
            ['c_draft_id'],
        ),
        (
            '2010-02-03T02:02:02.000000Z',
            '2010-02-04T02:02:01.000000Z',
            ['c_draft_id'],
        ),
    ],
)
async def test_get_history_from_equal_to(
        taxi_geoareas, from_timestamp, to_timestamp, expected_ids,
):
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': 'only_created',
            'from_timestamp': from_timestamp,
            'to_timestamp': to_timestamp,
        },
    )

    ordered_object.assert_eq(res.json()['draft_ids'], expected_ids, '')


@pytest.mark.filldb(subvention_geoareas='history')
@pytest.mark.parametrize(
    'name', ['created_and_removed', 'created_and_removed_in_future'],
)
@pytest.mark.parametrize(
    'from_timestamp, to_timestamp, expected_ids',
    [
        ('2010-02-01T02:02:02.000000Z', '2010-02-01T02:02:02.000000Z', []),
        (
            '2010-02-03T02:02:02.000000Z',
            '2010-02-03T02:02:02.000000Z',
            ['c_draft_id', 'r_draft_id'],
        ),
        ('2010-02-05T02:02:02.000000Z', '2010-02-05T02:02:02.000000Z', []),
        (
            '2010-02-02T02:02:02.000000Z',
            '2010-02-02T02:02:02.000000Z',
            ['c_draft_id', 'r_draft_id'],
        ),
        (
            '2010-02-04T02:02:02.000000Z',
            '2010-02-04T02:02:02.000000Z',
            ['c_draft_id', 'r_draft_id'],
        ),
        ('2010-01-31T02:02:02.000000Z', '2010-02-01T02:02:01.000000Z', []),
        (
            '2010-02-01T02:02:02.000000Z',
            '2010-02-03T02:02:01.000000Z',
            ['c_draft_id', 'r_draft_id'],
        ),
        (
            '2010-02-01T02:02:02.000000Z',
            '2010-02-05T02:02:01.000000Z',
            ['c_draft_id', 'r_draft_id'],
        ),
        (
            '2010-02-03T02:02:02.000000Z',
            '2010-02-05T02:02:01.000000Z',
            ['c_draft_id', 'r_draft_id'],
        ),
        ('2010-02-05T02:02:02.000000Z', '2010-02-06T02:02:01.000000Z', []),
    ],
)
async def test_get_history_remove_and_remove_in_future(
        taxi_geoareas, name, from_timestamp, to_timestamp, expected_ids,
):
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': name,
            'from_timestamp': from_timestamp,
            'to_timestamp': to_timestamp,
        },
    )

    ordered_object.assert_eq(res.json()['draft_ids'], expected_ids, '')


@pytest.mark.filldb(subvention_geoareas='history')
@pytest.mark.parametrize('now', ['2010-02-16T02:02:02', '2010-02-18T02:02:02'])
@pytest.mark.parametrize(
    'from_timestamp, to_timestamp, ids',
    [
        (
            '2010-02-01T02:02:02.000000Z',
            '2010-02-20T02:02:02.000000Z',
            [
                'draft_id_not_found',
                'draft_id_not_found',
                'c_1',
                'draft_id_not_found',
                'draft_id_not_found',
                'r_2',
                'c_3',
                'cr_1',
                'cr_1',
            ],
        ),
    ],
)
async def test_get_long_history(
        taxi_geoareas, mocked_time, now, from_timestamp, to_timestamp, ids,
):
    now_datetime = datetime.datetime.fromisoformat(now)
    mocked_time.set(now_datetime)
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': 'long_history',
            'from_timestamp': from_timestamp,
            'to_timestamp': to_timestamp,
        },
    )
    expected_ids = copy.deepcopy(ids)

    last_version_remove_datetime = datetime.datetime.fromisoformat(
        '2010-02-17T02:02:02',
    )
    is_last_version_removed = last_version_remove_datetime < now_datetime
    if is_last_version_removed:
        expected_ids.append('draft_id_not_found')
    ordered_object.assert_eq(res.json()['draft_ids'], expected_ids, '')


@pytest.mark.now('2010-02-02T02:02:02+0000')
@pytest.mark.config(SUBVENTION_GEOAREAS_IGNORE_MISSING_TRANSLATIONS=True)
async def test_creare_update_remove(taxi_geoareas, load_json, mocked_time):
    name = 'c_u_r_name'
    from_timestamp = '2010-02-01T02:02:02.000000Z'
    to_timestamp = '2010-02-11T02:02:02.000000Z'
    request = load_json('request_create_update_remove.json')

    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': name,
            'from_timestamp': from_timestamp,
            'to_timestamp': to_timestamp,
        },
    )
    ordered_object.assert_eq(res.json()['draft_ids'], [], '')

    # create
    create_draft_id = 'c_draft_id'
    res = await taxi_geoareas.post(
        '/subvention-geoareas/admin/v1/create_geoarea',
        request,
        headers={'X-YaTaxi-Draft-Id': create_draft_id},
    )
    assert res.status_code == 200
    create_response = res.json()
    mocked_time.sleep(1)
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': name,
            'from_timestamp': from_timestamp,
            'to_timestamp': to_timestamp,
        },
    )
    assert res.status_code == 200
    ordered_object.assert_eq(res.json()['draft_ids'], [create_draft_id], '')

    mocked_time.sleep(1)

    # update
    request = {'id': create_response['id'], 'geoarea': request['geoarea']}
    update_draft_id = 'u_draft_id'
    res = await taxi_geoareas.put(
        '/subvention-geoareas/admin/v1/update_geoarea',
        request,
        headers={'X-YaTaxi-Draft-Id': update_draft_id},
    )
    assert res.status_code == 200
    update_response = res.json()
    mocked_time.sleep(1)
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': name,
            'from_timestamp': from_timestamp,
            'to_timestamp': to_timestamp,
        },
    )
    assert res.status_code == 200
    ordered_object.assert_eq(
        res.json()['draft_ids'],
        [create_draft_id, update_draft_id, update_draft_id],
        '',
    )

    mocked_time.sleep(1)

    # remove
    request = {'id': update_response['id']}
    remove_draft_id = 'r_draft_id'
    res = await taxi_geoareas.put(
        '/subvention-geoareas/admin/v1/remove_geoarea',
        request,
        headers={'X-YaTaxi-Draft-Id': remove_draft_id},
    )
    assert res.status_code == 200
    mocked_time.sleep(1)
    res = await taxi_geoareas.get(
        '/subvention-geoareas/admin/v1/history',
        params={
            'name': name,
            'from_timestamp': from_timestamp,
            'to_timestamp': to_timestamp,
        },
    )
    assert res.status_code == 200
    ordered_object.assert_eq(
        res.json()['draft_ids'],
        [create_draft_id, update_draft_id, update_draft_id, remove_draft_id],
        '',
    )

from __future__ import unicode_literals

import datetime

from pymongo import errors
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi.internal import driver_manager

UDRIVER_RESULT = {
    '_id': 'driver_to',
    'created': datetime.datetime(2016, 5, 1),
    'updated': datetime.datetime(2016, 5, 23, 16, 0, 12),
    'licenses': [
        {'license': 'LTO1'}, {'license': 'LTO2'},
        {'license': 'LFROM1'}, {'license': 'LFROM2'},
    ],
    'profiles': [
        {'driver_id': 'DTO1'}, {'driver_id': 'DTO2'},
        {'driver_id': 'DFROM1'}, {'driver_id': 'DFROM2'},
    ],
    'license_ids': [
        {'id': 'LIDTO1'},
        {'id': 'LIDTO2'},
        {'id': 'LIDFROM1'},
        {'id': 'LIDFROM2'},
    ],
    'exam_score': 5,
    'exam_created': datetime.datetime(2016, 5, 2),
    'new_score': {
        'unified': {
            'total': 0.5
        }
    },
    'is_blacklisted': True,
    'mqc_passed': datetime.datetime(2016, 5, 3),
    'fraud': True,
    'pe': {
        'econom': 4,
        'business': -4,
        'vip': 2,
    },
    'pl': {
        'econom': 4,
        'business': 2,
        'vip': 4,
    },
    'gl': {
        'econom': 'moscow',
        'business': 'ekb',
        'vip': 'muhosransk',
    },
    "blocking_by_activity": {
        "is_blocked": False,
        "blocked_until": None,
        "counter": 3,
        "timestamp": None
    },
    'unioned_with': ['some_id', 'driver_from'],
}


UDRIVER_EMPTY_RESULT = {
    '_id': 'driver_empty_to',
    'created': datetime.datetime(2016, 5, 3),
    'updated': datetime.datetime(2016, 5, 23, 16, 0, 12),
    'licenses': [
        {'license': 'LEMPTY_TO'}, {'license': 'LEMPTY_FROM'},
    ],
    'profiles': [
        {'driver_id': 'DEMPTY_TO'}, {'driver_id': 'DEMPTY_FROM'},
    ],
    'license_ids': [
        {'id': 'LIDEMPTY_TO'}, {'id': 'LIDEMPTY_FROM'},
    ],
    'unioned_with': ['driver_empty_from'],
}


@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_success_union1():
    udriver_from = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    task = yield driver_manager.union_unique_drivers(udriver_from, udriver_to)
    yield driver_manager._union_unique_drivers_task(task)
    with pytest.raises(dbh.unique_drivers.NotFound):
        yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    tasks = yield dbh.union_unique_drivers.Doc.find_many()
    assert tasks == []
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver_result_copy = UDRIVER_RESULT.copy()
    udriver_result_copy['updated'] = udriver_to['updated']
    udriver_result_copy['updated_ts'] = udriver_to['updated_ts']
    assert dict(udriver_to) == udriver_result_copy


@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_success_union2():
    udriver_from = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    task = yield driver_manager.union_unique_drivers(udriver_from, udriver_to)
    yield driver_manager._union_unique_drivers_task(task)
    with pytest.raises(dbh.unique_drivers.NotFound):
        yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    tasks = yield dbh.union_unique_drivers.Doc.find_many()
    assert tasks == []
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver_result_copy = UDRIVER_RESULT.copy()
    udriver_result_copy['updated'] = udriver_to['updated']
    udriver_result_copy['updated_ts'] = udriver_to['updated_ts']
    assert dict(udriver_to) == udriver_result_copy


@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_union_move_scores_success1():
    udriver1_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver2_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    yield dbh.unique_drivers.Doc.union_move_fields(udriver1_orig, udriver2_orig)
    udriver1 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver2 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver2_result = UDRIVER_RESULT.copy()
    udriver2_result['licenses'] = udriver2_orig['licenses']
    udriver2_result['license_ids'] = udriver2_orig['license_ids']
    udriver2_result['updated'] = udriver2['updated']
    udriver2_result['updated_ts'] = udriver2['updated_ts']
    assert dict(udriver1) == dict(udriver1_orig)
    assert dict(udriver2) == dict(udriver2_result)
    yield dbh.unique_drivers.Doc.union_move_fields(udriver1, udriver2)
    udriver1 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver2 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    assert udriver1 == udriver1_orig
    assert udriver2 == udriver2_result


@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_union_move_scores_success_empty():
    udriver1_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty_from')
    udriver2_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty_to')
    yield dbh.unique_drivers.Doc.union_move_fields(udriver1_orig, udriver2_orig)
    udriver1 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty_from')
    udriver2 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty_to')
    udriver2_result = UDRIVER_EMPTY_RESULT.copy()
    udriver2_result['licenses'] = udriver2_orig['licenses']
    udriver2_result['license_ids'] = udriver2_orig['license_ids']
    udriver2_result['updated'] = udriver2['updated']
    udriver2_result['updated_ts'] = udriver2['updated_ts']
    assert udriver1 == udriver1_orig
    assert udriver2 == udriver2_result
    yield dbh.unique_drivers.Doc.union_move_fields(udriver1, udriver2)
    udriver1 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty_from')
    udriver2 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty_to')
    assert udriver1 == udriver1_orig
    assert udriver2 == udriver2_result


@pytest.mark.parametrize(
    'ack_from, ack_to, ack_expected',
    [
        (
            datetime.datetime(2016, 5, 10, 10, 0, 0),
            None,
            datetime.datetime(2016, 5, 10, 10, 0, 0),
        ),
        (
            None,
            datetime.datetime(2016, 5, 10, 10, 0, 0),
            datetime.datetime(2016, 5, 10, 10, 0, 0),
        ),
        (
            datetime.datetime(2016, 5, 7, 10, 0, 0),
            datetime.datetime(2016, 5, 10, 10, 0, 0),
            datetime.datetime(2016, 5, 10, 10, 0, 0),
        ),
        (
            datetime.datetime(2016, 5, 10, 10, 0, 0),
            datetime.datetime(2016, 5, 7, 10, 0, 0),
            datetime.datetime(2016, 5, 10, 10, 0, 0),
        ),
        (
            None,
            None,
            None,
        )
    ]
)
@pytest.inline_callbacks
def test_union_score_acknowledged(ack_from, ack_to, ack_expected):

    @async.inline_callbacks
    def set_ack(unique_driver_id, ack_date):
        if ack_date is not None:
            yield dbh.unique_drivers.Doc._update(
                {
                    dbh.unique_drivers.Doc._id: unique_driver_id,
                },
                {
                    '$set': {
                        dbh.unique_drivers.Doc.acknowledged.date: ack_date
                    }
                }
            )
        driver = yield dbh.unique_drivers.Doc.find_one_by_id(unique_driver_id)
        async.return_value(driver)

    udriver_from = yield set_ack('driver_from', ack_from)
    udriver_to = yield set_ack('driver_to', ack_to)

    yield dbh.unique_drivers.Doc.union_move_fields(udriver_from, udriver_to)
    udriver_to_result = yield dbh.unique_drivers.Doc.find_one_by_id(
        'driver_to')
    ack_result = udriver_to_result.acknowledged.date or None
    assert ack_result == ack_expected


@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_union_move_scores_success3():
    yield db.unique_drivers.update(
        {'_id': 'driver_to'},
        {
            '$unset': {
                'exam_created': True,
                'new_score': True,
                'mqc_passed': True,
            },
        },
    )
    udriver1_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver2_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    yield dbh.unique_drivers.Doc.union_move_fields(udriver1_orig, udriver2_orig)
    udriver1 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver2 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver2_result = UDRIVER_RESULT.copy()
    udriver2_result['licenses'] = udriver2_orig['licenses']
    udriver2_result['license_ids'] = udriver2_orig['license_ids']
    udriver2_result['new_score'] = udriver1['new_score']
    udriver2_result['updated'] = udriver2['updated']
    udriver2_result['updated_ts'] = udriver2['updated_ts']
    assert udriver1 == udriver1_orig
    assert udriver2 == udriver2_result


@pytest.mark.now('2016-05-07 03:00:00+03')
@pytest.inline_callbacks
def test_union_move_scores_empty():
    udriver1_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty')
    udriver2_orig = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    yield dbh.unique_drivers.Doc.union_move_fields(udriver1_orig, udriver2_orig)
    udriver1 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty')
    udriver2 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver2_orig['unioned_with'].append('driver_empty')
    udriver2_orig['profiles'][2:] = udriver1_orig['profiles']
    udriver2_orig['updated'] = udriver2['updated']
    udriver2_orig['updated_ts'] = udriver2['updated_ts']
    assert udriver1 == udriver1_orig
    assert udriver2 == udriver2_orig


@pytest.mark.now('2016-05-23 16:00:00')
@pytest.inline_callbacks
def test_union_create_task(patch):
    @patch('uuid.uuid4')
    def uuid4():
        patch.hex = '1234'
        return patch

    udriver1 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver2 = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    yield driver_manager.union_unique_drivers(udriver1, udriver2)
    task = {
        '_id': '1234',
        'created': datetime.datetime(2016, 5, 23, 16),
        'licenses': [
            {'license': 'LFROM1'}, {'license': 'LFROM2'},
            {'license': 'LTO1'}, {'license': 'LTO2'}
        ],
        'license_ids': [
            {'id': 'LIDFROM1'}, {'id': 'LIDFROM2'},
            {'id': 'LIDTO1'}, {'id': 'LIDTO2'}
        ],
        'unique_drivers': [
            {'unique_driver_id': 'driver_from'},
            {'unique_driver_id': 'driver_to'},
        ]
    }
    task_ = yield dbh.union_unique_drivers.Doc.find_one_by_id('1234')
    assert task_ == task


@pytest.mark.filldb(union_unique_drivers='data')
@pytest.inline_callbacks
def test_union_not_found():
    task = yield dbh.union_unique_drivers.Doc.find_one_by_id('1234')
    yield db.unique_drivers.remove({'_id': 'driver_to'})
    with pytest.raises(driver_manager.NotFoundError):
        yield driver_manager._union_unique_drivers_task(task)


@pytest.mark.filldb(union_unique_drivers='data')
@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_union_twice():
    task = yield dbh.union_unique_drivers.Doc.find_one_by_id('1234')
    for _ in range(2):
        yield driver_manager._union_unique_drivers_task(task)
        with pytest.raises(dbh.unique_drivers.NotFound):
            yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
        tasks = yield dbh.union_unique_drivers.Doc.find_many()
        assert len(tasks) == 2
        udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
        udriver_result_copy = UDRIVER_RESULT.copy()
        udriver_result_copy['updated'] = udriver_to['updated']
        udriver_result_copy['updated_ts'] = udriver_to['updated_ts']
        assert udriver_to == udriver_result_copy


@pytest.mark.filldb(union_unique_drivers='data')
@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_union_empty():
    task = yield dbh.union_unique_drivers.Doc.find_one_by_id('8765')
    yield driver_manager._union_unique_drivers_task(task)
    tasks = yield dbh.union_unique_drivers.Doc.find_many()
    assert len(tasks) == 2
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty_to')
    udriver_result_copy = UDRIVER_EMPTY_RESULT.copy()
    udriver_result_copy['updated'] = udriver_to['updated']
    udriver_result_copy['updated_ts'] = udriver_to['updated_ts']
    assert udriver_to == udriver_result_copy


@pytest.mark.filldb(union_unique_drivers='data')
@pytest.mark.now('2016-05-07 03:00:00+03')
@pytest.inline_callbacks
def test_union_duplicate_key():
    task = yield dbh.union_unique_drivers.Doc.find_one_by_id('1234')
    udriver_to_ = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    yield db.unique_drivers.remove({'_id': 'driver_from'})
    yield db.unique_drivers.update(
        {'_id': 'driver_empty'},
        {'$push': {'licenses': {'license': 'LFROM1'}}},
    )
    yield driver_manager._union_unique_drivers_task(task)
    with pytest.raises(dbh.unique_drivers.NotFound):
        yield dbh.unique_drivers.Doc.find_one_by_id('driver_empty')
    tasks = yield dbh.union_unique_drivers.Doc.find_many()
    assert len(tasks) == 2
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver_to_['licenses'] += [{'license': 'LFROM1'}, {'license': 'LFROM2'}]
    udriver_to_['license_ids'] += [{'id': 'LIDFROM1'}, {'id': 'LIDFROM2'}]
    udriver_to_['updated'] = udriver_to['updated']
    udriver_to_['updated_ts'] = udriver_to['updated_ts']
    assert udriver_to == udriver_to_


@pytest.mark.parametrize('licenses, license_ids, ids', [
    (['LFROM1'], ['LIDFROM1'], ['tmp_id']),
    (['LTO1'], ['LIDTO1'], ['tmp_id']),
    (['tmp_id'], ['tmp_pid'], ['driver_from']),
    (['tmp_id'], ['tmp_pid'], ['driver_to']),
])
@pytest.inline_callbacks
def test_union_unique_test(licenses, license_ids, ids):
    yield dbh.union_unique_drivers.Doc.new_doc(licenses, license_ids, ids)
    udriver_from = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    with pytest.raises(errors.DuplicateKeyError):
        yield driver_manager.union_unique_drivers(udriver_from, udriver_to)


@pytest.mark.now('2016-05-23 16:00:12')
@pytest.mark.filldb(union_unique_drivers='data')
@pytest.inline_callbacks
def test_union_continue():
    yield driver_manager.union_unique_drivers_continue()
    with pytest.raises(dbh.unique_drivers.NotFound):
        yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    tasks = yield dbh.union_unique_drivers.Doc.find_many()
    assert len(tasks) == 2
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver_result_copy = UDRIVER_RESULT.copy()
    udriver_result_copy['updated'] = udriver_to['updated']
    udriver_result_copy['updated_ts'] = udriver_to['updated_ts']
    assert udriver_to == udriver_result_copy


@pytest.mark.parametrize(
    'unique_driver_id_from,unique_driver_id_to,'
    'expected_first_order_complete', [
        (
            'unique_driver_with_younger_first_order_complete_id',
            'unique_driver_with_older_first_order_complete_id',
            {
                'id': 'test_order_id2',
                'completed': 200,
            }
        ),
        (
            'unique_driver_with_younger_first_order_complete_id',
            'unique_driver_with_older_first_order_complete_id',
            {
                'id': 'test_order_id2',
                'completed': 200,
            }
        ),
        (
            'unique_driver_with_younger_first_order_complete_id',
            'unique_driver_without_first_order_complete_id',
            {
                'id': 'test_order_id1',
                'completed': 300,
            }
        ),
        (
            'unique_driver_without_first_order_complete_id',
            'unique_driver_with_younger_first_order_complete_id',
            {
                'id': 'test_order_id1',
                'completed': 300,
            }
        ),
])
@pytest.mark.filldb(unique_drivers='for_first_order_complete_union')
@pytest.inline_callbacks
def test_first_order_complete_union(
        unique_driver_id_from, unique_driver_id_to,
        expected_first_order_complete):
    udriver_from = yield dbh.unique_drivers.Doc.find_one_by_id(
        unique_driver_id_from
    )
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id(
        unique_driver_id_to
    )
    yield dbh.unique_drivers.Doc.union_move_fields(
        udriver_from, udriver_to
    )
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id(
        unique_driver_id_to
    )
    assert udriver_to.first_order_complete == expected_first_order_complete


@pytest.mark.now('2016-05-23 16:00:12')
@pytest.inline_callbacks
def test_union_blocking():
    driver_to_blocking = {
        "is_blocked": True,
        "blocked_until": None,
        "counter": 1,
        "timestamp": None
    }
    yield db.unique_drivers.update(
        {'_id': 'driver_to'},
        {
            '$set': {
                'blocking_by_activity': driver_to_blocking
            },
        },
    )
    udriver_from = yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    assert udriver_to.blocking == driver_to_blocking
    task = yield driver_manager.union_unique_drivers(udriver_from, udriver_to)
    yield driver_manager._union_unique_drivers_task(task)
    with pytest.raises(dbh.unique_drivers.NotFound):
        yield dbh.unique_drivers.Doc.find_one_by_id('driver_from')
    tasks = yield dbh.union_unique_drivers.Doc.find_many()
    assert tasks == []
    udriver_to = yield dbh.unique_drivers.Doc.find_one_by_id('driver_to')
    udriver_result_copy = UDRIVER_RESULT.copy()
    udriver_result_copy['updated'] = udriver_to['updated']
    udriver_result_copy['updated_ts'] = udriver_to['updated_ts']
    assert udriver_to == udriver_result_copy

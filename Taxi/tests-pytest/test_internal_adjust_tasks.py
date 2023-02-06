# -*- coding: utf-8 -*-

import datetime

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import adjust
from taxi.internal import adjust_manager
from taxi.internal import adjust_tasks
from taxi.internal import dbh
from taxi.util import dates

NOW = datetime.datetime(2016, 2, 9, 12, 35, 55)
CREATED = datetime.datetime(2016, 2, 9, 9, 35, 34)
MOSCOW_TZ = 'Europe/Moscow'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='blank_patchable')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_blank_success(patch):
    """
    There is task in db.
    task.device_type is not set - task should be patched with adjust user data.
    task.next_call has past - we can process it.
    task.user_id is present in adjust_users collection.
    adjust request will be successful.
    task should be removed from db as a result.
    """
    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        expected = {
            'event_token': 'nm4buh',
            'app_token': '55ug2ntb3uzf',
            'device_id_key': 'android_id',
            'device_id_value': '30a160b3502a4a81a7cf0822d7c246b9',
            'created_at': dates.localize(CREATED, MOSCOW_TZ),
            'revenue': 600,
            'currency': settings.DEFAULT_CURRENCY,
            'log_extra': None
        }
        yield
        assert kwargs == expected
        assert args == ()
        async.return_value({'response': 'ok'})

    yield adjust_tasks.send_events()

    try:
        yield dbh.adjust_tasks.Doc.find_one_by_id(
            '13b278aa54a94422a6e72ae5801b7eae'
        )
    except dbh.adjust_tasks.TaskNotFound:
        pass
    else:
        assert False, 'Task should have been removed from collection'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='patched')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_patched_success(patch):
    """
    There is task in db.
    task.device_type is set - task should NOT be patched with adjust user data.
    task.next_call has past - we can process it.
    adjust request will be successful.
    task should be removed from db as a result.
    """
    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        expected = [
            {
                'event_token': 'tr7d7e',
                'app_token': '55ug2ntb3uzf',
                'device_id_key': 'android_id',
                'device_id_value': '30a160b3502a4a81a7cf0822d7c246b9',
                'created_at': CREATED,
                'revenue': None,
                'currency': None,
                'log_extra': None
            },
            {
                'event_token': '5vsvjx',
                'app_token': '55ug2ntb3uzf',
                'device_id_key': 'android_id',
                'device_id_value': '019bd651d1304081a38cd4da57898580',
                'created_at': CREATED,
                'revenue': None,
                'currency': None,
                'log_extra': None
            },
            {
                'event_token': 'nm4buh',
                'app_token': '55ug2ntb3uzf',
                'device_id_key': 'android_id',
                'device_id_value': 'b51e11a7499d41b9bf2f5c7f63c32601',
                'created_at': CREATED,
                'revenue': None,
                'currency': None,
                'log_extra': None
            },
        ]
        yield
        assert kwargs in expected
        assert args == ()
        async.return_value({'response': 'ok'})

    yield adjust_tasks.send_events()

    try:
        yield dbh.adjust_tasks.Doc.find_one_by_id(
            '13b278aa54a94422a6e72ae5801b7eae'
        )
    except dbh.adjust_tasks.TaskNotFound:
        pass
    else:
        assert False, 'Task should have been removed from collection'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='blank_non_patchable')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_could_not_patch(patch):
    """
    There is task in db.
    task.device_type is set - task should NOT be patched with adjust user data.
    task.next_call has past - we can process it.
    task.user_id is absent in adjust_users collection - entry won't be patched.
    adjust request won't be executed at all.
    task should have its' next_call time updated to later date.
    """

    request_was_called = {'result': False}

    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        request_was_called['result'] = True
        yield

    yield adjust_tasks.send_events()

    assert not request_was_called['result']

    task = yield dbh.adjust_tasks.Doc.find_one_by_id(
        '13b278aa54a94422a6e72ae5801b7eae')
    assert not task.device_type
    assert task.next_call == NOW + datetime.timedelta(
        hours=settings.ADJUST_PATCH_DELAY)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='blank_patchable')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_blank_could_not_send(patch):
    """
    There is task in db.
    task.device_type is NOT set - task should be patched with adjust user data.
    task.next_call has past - we can process it.
    task.user_id is present in adjust_users collection - entry will be patched.
    adjust request will be executed, but will fail.
    task should have its' next_call time updated to later date.
    task should be patched by available device_type and device_id data.
    """
    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    valid_args = {'result': False}

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        expected = {
            'event_token': 'nm4buh',
            'app_token': '55ug2ntb3uzf',
            'device_id_key': 'android_id',
            'device_id_value': '30a160b3502a4a81a7cf0822d7c246b9',
            'created_at': dates.localize(CREATED, MOSCOW_TZ),
            'revenue': 600,
            'currency': settings.DEFAULT_CURRENCY,
            'log_extra': None
        }
        assert kwargs == expected
        assert args == tuple()
        valid_args['result'] = True
        raise adjust.AdjustRequestError('bad')

    yield adjust_tasks.send_events()

    assert valid_args['result']

    task = yield dbh.adjust_tasks.Doc.find_one_by_id(
        '13b278aa54a94422a6e72ae5801b7eae')
    assert task.device_type
    assert task.device_id
    assert task.next_call == NOW + datetime.timedelta(
        hours=settings.ADJUST_SEND_DELAY)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='blank_old_non_patchable')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_blank_old_could_not_send(patch):
    """
    There is task in db.
    task.device_type is NOT set - task should be patched with adjust user data.
    task.next_call has past - we can process it.
    task.user_id is present in adjust_users collection,
    but adjust_user does not have device_id_key.
    adjust request will not be executed.
    task should have its' next_call time updated to later date.
    task should not be patched.
    """
    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        assert False, 'Adjust.request should not be called.'
        yield

    yield adjust_tasks.send_events()

    task = yield dbh.adjust_tasks.Doc.find_one_by_id(
        '13b278aa54a94422a6e72ae5801b7eae')
    assert not task.device_type
    assert not task.device_id
    assert not task.device_id_key
    assert task.next_call == NOW + datetime.timedelta(
        hours=settings.ADJUST_PATCH_DELAY)
    try:
        yield dbh.adjust_users.Doc.find_one_by_id(
            'dcde046481d14f57b307796ac904288f'
        )
    except dbh.adjust_users.UserDocNotFound:
        pass
    else:
        assert False, 'Invalid user should be removed.'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='patched')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_patched_could_not_send(patch):
    """
    There is task in db.
    task.device_type is set - task should NOT be patched with adjust user data.
    task.next_call has past - we can process it.
    adjust request will be executed, but will fail.
    task should have its' next_call time updated to later date.
    """

    valid_args = {'result': False}

    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        expected = [
            {
                'event_token': 'tr7d7e',
                'app_token': '55ug2ntb3uzf',
                'device_id_key': 'android_id',
                'device_id_value': '30a160b3502a4a81a7cf0822d7c246b9',
                'created_at': CREATED,
                'revenue': None,
                'currency': None,
                'log_extra': None
            },
            {
                'event_token': '5vsvjx',
                'app_token': '55ug2ntb3uzf',
                'device_id_key': 'android_id',
                'device_id_value': '019bd651d1304081a38cd4da57898580',
                'created_at': CREATED,
                'revenue': None,
                'currency': None,
                'log_extra': None
            },
            {
                'event_token': 'nm4buh',
                'app_token': '55ug2ntb3uzf',
                'device_id_key': 'android_id',
                'device_id_value': 'b51e11a7499d41b9bf2f5c7f63c32601',
                'created_at': CREATED,
                'revenue': None,
                'currency': None,
                'log_extra': None
            },
        ]
        yield
        assert kwargs in expected
        assert args == ()
        valid_args['result'] = True
        if kwargs['device_id_value'] == 'b51e11a7499d41b9bf2f5c7f63c32601':
            raise adjust.AdjustRequestError('bad')

    yield adjust_tasks.send_events()

    assert valid_args['result']

    task = yield dbh.adjust_tasks.Doc.find_one_by_id(
        '74d7353a5e254db489492481abee13ca')
    assert task.device_type
    assert task.next_call == NOW + datetime.timedelta(
        hours=settings.ADJUST_SEND_DELAY)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='patched')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_patched_could_not_send_invalid_device(patch):
    """
    There is task in db.
    task.device_type is set - task should NOT be patched with adjust user data.
    task.next_call has past - we can process it.
    adjust request will be executed, but will fail.
    task should have its' next_call time updated to later date.
    """

    valid_args = {'result': False}

    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        expected = {
            'event_token': 'tr7d7e',
            'app_token': '55ug2ntb3uzf',
            'device_id_key': 'android_id',
            'device_id_value': '30a160b3502a4a81a7cf0822d7c246b9',
            'created_at': CREATED,
            'revenue': None,
            'currency': None,
            'log_extra': None
        }
        yield
        assert kwargs == expected
        assert args == ()
        valid_args['result'] = True
        raise adjust.InvalidAdjustUserError('bad')

    yield adjust_tasks.send_events()

    assert valid_args['result']

    task = yield dbh.adjust_tasks.Doc.find_one_by_id(
        '13b278aa54a94422a6e72ae5801b7eae')
    assert not task.device_type
    assert not task.device_id
    try:
        yield dbh.adjust_users.Doc.find_one_by_id(
            '2a9a63e31a024f01995744cbc4f723c9')
    except dbh.adjust_users.UserDocNotFound:
        pass
    else:
        assert False, 'user should have been removed'
    assert task.next_call == NOW + datetime.timedelta(
        hours=settings.ADJUST_PATCH_DELAY)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='blank_sleeping')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_time_has_not_come(patch):
    """
    There is task in db.
    task.next_call has not yet come. Task should not be processed at all.
    there is data for user_id in adjust_users collection,
    so if it would be processed - it would be patched and
    adjust request would be executed and therefor - task would be removed
    from queue.
    But time has not yet come for that.
    """

    request_called = {'result': False}

    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        request_called['result'] = True
        yield

    yield adjust_tasks.send_events()

    assert not request_called['result']

    task = yield dbh.adjust_tasks.Doc.find_one_by_id(
        '13b278aa54a94422a6e72ae5801b7eae')
    assert not task.device_type
    assert not task.device_id
    assert task.next_call == datetime.datetime.strptime(
        '2016-02-10T06:34:55.0', '%Y-%m-%dT%H:%M:%S.%f')


@pytest.mark.filldb(adjust_tasks='stats')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_stats(patch):
    success, not_sent, not_patched = 7, 13, 42

    @patch('taxi.util.graphite.send_cluster_metric')
    def send_metric(metric, value, stamp_):
        metric_to_value = {
            'stats.adjust.queue.new': 1,
            'stats.adjust.queue.patched': 2,
            'stats.adjust.queue_processing.success': success,
            'stats.adjust.queue_processing.not_sent': not_sent,
            'stats.adjust.queue_processing.not_patched': not_patched,
            'stats.adjust.requests.success': 10,
            'stats.adjust.requests.not_sent': 5,
            'stats.adjust.requests.not_patched': 3,
        }
        assert metric_to_value[metric] == value

    yield adjust_tasks.send_stats(
        success=success,
        not_sent=not_sent,
        not_patched=not_patched,
    )

    stats = yield db.adjust_stats.find_one({'_id': 'requests'})
    assert stats[adjust_manager.SUCCESS] == 0
    assert stats[adjust_manager.NOT_SENT] == 0
    assert stats[adjust_manager.NOT_PATCHED] == 0


@pytest.mark.now(NOW.isoformat())
@pytest.mark.filldb(adjust_tasks='patched_old')
@pytest.mark.asyncenv('async')
@pytest.inline_callbacks
def test_send_events_patched_old_failure(patch):
    """
    There is task in db.
    task.device_type is set - task should NOT be patched with adjust user data.
    task.next_call has past - we can process it.
    task.device_id_key is not set - task was patched before usage of new
    adjust_user parsing.
    adjust request should not be called.
    task should be unpatched.
    """
    @patch('taxi_stq.client.adjust_sender_recall')
    @async.inline_callbacks
    def task_call(log_extra):
        yield

    @patch('taxi.external.adjust.request')
    @async.inline_callbacks
    def adjust_request(*args, **kwargs):
        yield
        assert False, 'Adjust.request should not be called'

    yield adjust_tasks.send_events()

    task = yield dbh.adjust_tasks.Doc.find_one_by_id(
        '74d7353a5e254db489492481abee13ca')
    assert not task.device_type
    assert not task.device_id
    assert task.next_call == NOW + datetime.timedelta(
        hours=settings.ADJUST_PATCH_DELAY)

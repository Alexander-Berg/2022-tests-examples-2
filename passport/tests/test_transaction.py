# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tracks.exceptions import TrackNotFoundError
from passport.backend.core.tracks.faker import FakeTrackManager
from passport.backend.core.tracks.transaction import TrackTransaction
from passport.backend.core.tracks.utils import (
    get_node_id_from_track_id,
    make_redis_subkey,
)


@with_settings_hosts()
class TestTrackTransaction(TestCase):

    def setUp(self):
        self.manager = FakeTrackManager()
        self.manager.start()
        self.track_manager, self.track_id = self.manager.get_manager_and_trackid()

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = 'old_uid'
            track.login = 'old_login'
        self.track = track

    def tearDown(self):
        self.manager.stop()
        del self.manager
        del self.track_manager
        del self.track

    @property
    def transaction(self):
        return TrackTransaction(self.track, self.track_manager)

    @property
    def track_data(self):
        return self.track_manager.read(self.track_id)._data

    def test_init(self):
        transaction = self.transaction
        ok_(transaction.track is self.track)
        ok_(transaction.manager is self.track_manager)

    def test_rollback_on_error_without_error(self):
        with self.transaction.rollback_on_error() as track:
            track.uid = 'new_uid'
            track.login = None
        eq_(self.track_data['uid'], 'new_uid')
        ok_('login' not in self.track_data)

    def test_rollback_on_error_with_error(self):
        with assert_raises(ValueError):
            with self.transaction.rollback_on_error() as track:
                track.uid = 'new_uid'
                track.login = None
                raise ValueError()
        eq_(self.track_data['uid'], 'old_uid')
        eq_(self.track_data['login'], 'old_login')
        eq_(track.uid, 'old_uid')
        eq_(track.login, 'old_login')

    def test_commit_on_error_without_error(self):
        with self.transaction.commit_on_error() as track:
            track.uid = 'new_uid'
            track.login = None
        eq_(self.track_data['uid'], 'new_uid')
        ok_('login' not in self.track_data)

    def test_commit_on_error_with_error(self):
        with assert_raises(ValueError):
            with self.transaction.commit_on_error() as track:
                track.uid = 'new_uid'
                track.login = None
                raise ValueError()
        eq_(self.track_data['uid'], 'new_uid')
        ok_('login' not in self.track_data)
        eq_(track.uid, 'new_uid')
        ok_(track.login is None)

    def test_delete(self):
        list_names = list(self.track.list_names)
        eq_(
            sorted(list_names),
            sorted(['restore_methods_select_order', 'suggested_logins', 'phone_operation_confirmations', 'totp_push_device_ids']),
        )

        with self.transaction.delete():
            pass
        assert_raises(TrackNotFoundError, self.track_manager.read, self.track_id)

        node_id = get_node_id_from_track_id(self.track_id)
        redis_node = self.track_manager.redis_track_managers.get(node_id)
        ok_(not redis_node.exists(self.track_id))
        for list_name in list_names:
            ok_(not redis_node.exists(make_redis_subkey(self.track_id, list_name)))

    @raises(RuntimeError)
    def test_nested_transactions_error(self):
        with self.transaction.rollback_on_error():
            with self.transaction.commit_on_error():
                pass  # pragma: no cover

    def test_nested_transactions_allowed(self):
        with self.transaction.rollback_on_error() as track:
            track.uid = 'new_uid'
            with TrackTransaction(self.track, self.track_manager, allow_nested=True).commit_on_error() as track2:
                track2.login = 'new_login'

        eq_(self.track_data['uid'], 'new_uid')
        eq_(self.track_data['login'], 'new_login')

    @raises(RuntimeError)
    def test_nested_transactions_allowed_but_error_on_counter(self):
        with self.transaction.rollback_on_error() as track:
            track.uid = 'new_uid'
            with TrackTransaction(self.track, self.track_manager, allow_nested=True).commit_on_error() as track2:
                track2.suggest_login_count.incr()

    @raises(RuntimeError)
    def test_nested_transactions_allowed_but_error_on_list(self):
        with self.transaction.rollback_on_error() as track:
            track.uid = 'new_uid'
            with TrackTransaction(self.track, self.track_manager, allow_nested=True).commit_on_error() as track2:
                track2.suggested_logins.append('another_login')

    def test_error_on_entering_context_manager(self):
        self.track.snapshot = mock.Mock(side_effect=Exception, return_value=self.track)
        with assert_raises(Exception):
            with self.transaction.rollback_on_error():
                pass  # pragma: no cover

        # проверим, что новые транзакции не ломаются
        self.track.snapshot.side_effect = None
        with self.transaction.rollback_on_error():
            pass

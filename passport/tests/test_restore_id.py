# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.restore_id import RestoreId


class TestRestoreIdType(PassportTestCase):
    def test_from_args(self):
        restore_id = RestoreId.from_args('0x7F', 123, 12345.234, 1, 'track_id')
        eq_(restore_id.host_id, '0x7F')
        eq_(restore_id.pid, '123')
        eq_(restore_id.timestamp, '12345.234')
        eq_(restore_id.uid, 1)
        eq_(restore_id.track_id, 'track_id')

    def test_from_string(self):
        restore_id = RestoreId.from_string('0x7F,123,12345.234,1,track_id')
        eq_(restore_id.host_id, '0x7F')
        eq_(restore_id.pid, '123')
        eq_(restore_id.timestamp, '12345.234')
        eq_(restore_id.uid, 1)
        eq_(restore_id.track_id, 'track_id')

    def test_to_string(self):
        restore_id = RestoreId.from_string('0x7F,123,12345.234,1,track_id')
        eq_(restore_id.to_string(), '0x7F,123,12345.234,1,track_id')

    @raises(ValueError)
    def test_invalid_uid(self):
        RestoreId.from_string('0x7F,123,12345.234,not an UID,track_id')

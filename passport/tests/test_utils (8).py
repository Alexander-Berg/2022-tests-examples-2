# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_not_equal,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tracks.exceptions import InvalidTrackIdError
from passport.backend.core.tracks.utils import (
    check_track_id,
    create_short_track_id,
    create_track_id,
    get_node_id_from_track_id,
    make_redis_key,
    make_redis_subkey,
)


TEST_SHORT_TRACK_ID = 'YXPUGZ277F'


@with_settings_hosts(
    SHORT_TRACK_LENGTH=10,
    ALLOWED_TRACK_LENGTHS={10, 34},
)
class TestTrackIdFunctions(unittest.TestCase):

    def test_create_track_id(self):
        track_id = create_track_id()
        ok_(track_id)
        eq_(len(track_id), 34)
        eq_(int(track_id[-2:], 16), 0x7F)
        assert_not_equal(track_id, create_track_id())

    def test_create_short_track_id(self):
        track_id = create_short_track_id()
        eq_(len(track_id), 10)
        eq_(int(track_id[-2:], 16), 0x7F)

    def test_get_node_id_from_track_id(self):
        track_id = 'ab' * 16
        host_id = '0f'
        eq_(get_node_id_from_track_id(track_id + host_id), 15)

    def test_get_node_id_from_short_track_id(self):
        eq_(get_node_id_from_track_id(TEST_SHORT_TRACK_ID), 0x7f)

    def test_check_track_id(self):
        check_track_id('ab' * 16 + '0f')

    def test_check_short_track_id(self):
        check_track_id(TEST_SHORT_TRACK_ID)

    @raises(InvalidTrackIdError)
    def test_check_track_id_wrong_host_id(self):
        check_track_id('ab' * 16 + 'ww')

    @raises(InvalidTrackIdError)
    def test_check_track_id_error(self):
        check_track_id('cd')

    @raises(InvalidTrackIdError)
    def test_check_track_id_error_unicode(self):
        check_track_id(u'аб' * 16 + 'ww')

    def test_make_redis_key(self):
        eq_(make_redis_key('key'), 'track:key')

    def test_make_redis_subkey(self):
        eq_(make_redis_subkey('key', 'list'), 'track:key:list')

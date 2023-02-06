# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.blackbox import BaseBlackboxError
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.conf import settings
from passport.backend.core.cookies.lrandoms import (
    _LRandomsManager,
    get_lrandoms_manager,
)
from passport.backend.core.disk_cache import (
    DiskCache,
    DiskCacheWriteError,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


EXPECTED_TIMESORTED_LRANDOMS = [
    {
        'body': '000000111111222222333333444444555555666666777777888888999999pppp',
        'created_timestamp': 1297400450,
        'id': '1000006',
    },
    {
        'body': '000000111111222222333333444444555555666666777777888888999999llll',
        'created_timestamp': 1297400440,
        'id': '1000005',
    },
    {
        'body': '000000111111222222333333444444555555666666777777888888999999oooo',
        'created_timestamp': 1297400430,
        'id': '1000004',
    },
    {
        'body': '000000111111222222333333444444555555666666777777888888999999zzzz',
        'created_timestamp': 1297400420,
        'id': '1000003',
    },
    {
        'body': '000000111111222222333333444444555555666666777777888888999999yyyy',
        'created_timestamp': 1297400410,
        'id': '1000002',
    },
    {
        'body': '000000111111222222333333444444555555666666777777888888999999xxxx',
        'created_timestamp': 1297400401,
        'id': '1000001',
    },
]


@with_settings(
    BLACKBOX_URL='http://localhost/',
    LRANDOMS_CACHE_TIME=180,
    LRANDOMS_EXPIRE_OFFSET=60,
)
class TestLRandomsManager(unittest.TestCase):
    def setUp(self):
        lrandoms_response = '''
            1000001;000000111111222222333333444444555555666666777777888888999999xxxx;1297400401
            1000002;000000111111222222333333444444555555666666777777888888999999yyyy;1297400410
            1000003;000000111111222222333333444444555555666666777777888888999999zzzz;1297400420
            1000004;000000111111222222333333444444555555666666777777888888999999oooo;1297400430
            1000005;000000111111222222333333444444555555666666777777888888999999llll;1297400440
            1000006;000000111111222222333333444444555555666666777777888888999999pppp;1297400450
        '''.strip()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.blackbox = FakeBlackbox()
        self.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)
        self.blackbox.start()
        DiskCache('lrandoms').flush()

    def tearDown(self):
        self.blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.blackbox
        del self.fake_tvm_credentials_manager
        DiskCache('lrandoms').flush()

    def test_basic(self):
        lrandom = _LRandomsManager()
        lrandom.load()
        ok_(DiskCache('lrandoms').exists())
        eq_(lrandom._timesorted_lrandoms, EXPECTED_TIMESORTED_LRANDOMS)

        eq_(
            lrandom.get_lrandom('1000001'),
            {
                'body': '000000111111222222333333444444555555666666777777888888999999xxxx',
                'created_timestamp': 1297400401,
                'id': '1000001',
            },
        )

    def test_small_lrandoms(self):
        lrandom = _LRandomsManager()
        lrandoms_response = '''
            1000001;000000111111222222333333444444555555666666777777888888999999xxxx;1297400401
            1000002;000000111111222222333333444444555555666666777777888888999999yyyy;1297400410
        '''.strip()
        self.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)
        assert lrandom.load()
        expected_timesorted = [
            {
                'id': u'1000002',
                'body': u'000000111111222222333333444444555555666666777777888888999999yyyy',
                'created_timestamp': 1297400410,
            },
            {
                'id': u'1000001',
                'body': u'000000111111222222333333444444555555666666777777888888999999xxxx',
                'created_timestamp': 1297400401,
            },
        ]
        assert lrandom._timesorted_lrandoms == expected_timesorted
        assert lrandom.current_lrandom() == expected_timesorted[1]

    def test_get_lrandom_not_found(self):
        lrandom = _LRandomsManager()
        ok_(lrandom.load())
        ok_(DiskCache('lrandoms').exists())
        eq_(lrandom.get_lrandom('xxxxx'), None)

    def test_load_lrandoms_empty(self):
        lrandom = _LRandomsManager()
        DiskCache('lrandoms').dump(EXPECTED_TIMESORTED_LRANDOMS)
        lrandoms_response = ''
        self.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)
        ok_(not lrandom.load())
        eq_(lrandom._timesorted_lrandoms, EXPECTED_TIMESORTED_LRANDOMS)

    def test_load_lrandoms_with_blackbox_error(self):
        lrandom = _LRandomsManager()
        DiskCache('lrandoms').dump(EXPECTED_TIMESORTED_LRANDOMS)
        self.blackbox.set_blackbox_lrandoms_response_side_effect(BaseBlackboxError('Error'))
        ok_(not lrandom.load())
        eq_(lrandom._timesorted_lrandoms, EXPECTED_TIMESORTED_LRANDOMS)

    def test_load_lrandoms_empty_without_disk_cache(self):
        lrandom = _LRandomsManager()
        DiskCache('lrandoms').flush()
        lrandoms_response = ''
        self.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)
        ok_(not lrandom.load())
        eq_(lrandom._timesorted_lrandoms, [])

    def test_load_lrandoms_with_blackbox_error_without_disk_cache(self):
        lrandom = _LRandomsManager()
        DiskCache('lrandoms').flush()
        self.blackbox.set_blackbox_lrandoms_response_side_effect(BaseBlackboxError('Error'))
        ok_(not lrandom.load())
        eq_(lrandom._timesorted_lrandoms, [])

    def test_reload_lrandoms(self):
        lrandom = _LRandomsManager()
        ok_(lrandom.load())
        ok_(DiskCache('lrandoms').exists())

        lrandoms_response = '''
            1000002;000000111111222222333333444444555555666666777777888888999999xxxx;1297400401
            1000003;000000111111222222333333444444555555666666777777888888999999yyyy;1297400430
        '''.strip()
        self.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)
        lrandom._expired_time -= settings.LRANDOMS_CACHE_TIME + 2 * settings.LRANDOMS_EXPIRE_OFFSET
        ok_(lrandom.load())
        eq_(
            lrandom._timesorted_lrandoms,
            [
                {
                    'body': '000000111111222222333333444444555555666666777777888888999999yyyy',
                    'created_timestamp': 1297400430,
                    'id': '1000003',
                },
                {
                    'body': '000000111111222222333333444444555555666666777777888888999999xxxx',
                    'created_timestamp': 1297400401,
                    'id': '1000002',
                },
            ],
        )

    def test_reload_lrandoms_empty(self):
        lrandom = _LRandomsManager()
        ok_(lrandom.load())
        ok_(DiskCache('lrandoms').exists())
        timesorted_lrandoms = list(lrandom._timesorted_lrandoms)

        lrandoms_response = ''
        self.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)
        lrandom._expired_time -= settings.LRANDOMS_CACHE_TIME + 2 * settings.LRANDOMS_EXPIRE_OFFSET
        ok_(not lrandom.load())
        eq_(timesorted_lrandoms, lrandom._timesorted_lrandoms)

    def test_reload_lrandoms_with_blackbox_error(self):
        lrandom = _LRandomsManager()
        ok_(lrandom.load())
        ok_(DiskCache('lrandoms').exists())
        timesorted_lrandoms = list(lrandom._timesorted_lrandoms)

        self.blackbox.set_blackbox_lrandoms_response_side_effect(BaseBlackboxError('Error'))
        lrandom._expired_time -= settings.LRANDOMS_CACHE_TIME + 2 * settings.LRANDOMS_EXPIRE_OFFSET
        ok_(not lrandom.load())
        eq_(timesorted_lrandoms, lrandom._timesorted_lrandoms)

    @mock.patch.object(DiskCache, 'dump')
    def test_fail_dump_to_disk_cache(self, mock_method):
        lrandom = _LRandomsManager()
        mock_method.side_effect = DiskCacheWriteError
        ok_(lrandom.load())
        ok_(not DiskCache('lrandoms').exists())

    def test_no_reload(self):
        lrandom = _LRandomsManager()
        ok_(lrandom.load())
        ok_(DiskCache('lrandoms').exists())
        timesorted_lrandoms = list(lrandom._timesorted_lrandoms)

        self.blackbox.set_blackbox_lrandoms_response_value('1;2;3')
        ok_(not lrandom.load())
        eq_(timesorted_lrandoms, lrandom._timesorted_lrandoms)

    def test_current_lrandom(self):
        lrandom = _LRandomsManager()
        ok_(lrandom.load())
        ok_(DiskCache('lrandoms').exists())

        eq_(
            lrandom.current_lrandom(),
            {
                'body': '000000111111222222333333444444555555666666777777888888999999xxxx',
                'created_timestamp': 1297400401,
                'id': '1000001',
            },
        )

    def test_current_lrandom_not_loaded(self):
        lrandoms_response = ''
        self.blackbox.set_blackbox_lrandoms_response_value(lrandoms_response)

        lrandom = _LRandomsManager()
        eq_(lrandom.current_lrandom(), None)

    def test_str(self):
        lrandom = _LRandomsManager(cache_time=7200)
        ok_(lrandom.load())
        ok_(DiskCache('lrandoms').exists())
        eq_(
            str(lrandom),
            '_LRandomsManager: expired_time=%s' % lrandom._expired_time,
        )

    def test_get_lrandoms_manager(self):
        lrandoms_manager = get_lrandoms_manager()
        ok_(lrandoms_manager)

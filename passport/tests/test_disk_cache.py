# -*- coding: utf-8 -*-
import os
import tempfile
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.disk_cache import (
    DiskCache,
    DiskCacheReadError,
    DiskCacheWriteError,
)


class TestDiskCache(unittest.TestCase):
    def setUp(self):
        _, self.lock_file = tempfile.mkstemp(prefix='disk_cache')
        self.folder, self.filename = os.path.split(self.lock_file)

        self.disk_cache = DiskCache(self.filename, self.folder)

    def tearDown(self):
        self.disk_cache.flush()
        os.remove(self.lock_file)

    def test_ok(self):
        data = 'test'
        self.disk_cache.dump(data)
        eq_(self.disk_cache.load(), data)

    def test_ok_compound_data(self):
        data = [
            {
                'key': 'value',
                'ukey': u'значение',
            },
            'str',
            1,
            1.0,
            [
                'str2',
                2,
            ]
        ]
        self.disk_cache.dump(data)
        eq_(self.disk_cache.load(), data)

    @raises(DiskCacheWriteError)
    def test_no_write_access(self):
        DiskCache(self.filename, folder='/').dump('test')

    @raises(DiskCacheWriteError)
    def test_unsupported_type(self):
        self.disk_cache.dump(Exception())

    @raises(DiskCacheReadError)
    def test_file_missing(self):
        self.disk_cache.flush()
        self.disk_cache.load()

    @raises(DiskCacheReadError)
    def test_malformed_file_contents(self):
        with open(self.disk_cache._filepath, 'w') as f:
            f.write('["malformed JSON"')
        self.disk_cache.load()

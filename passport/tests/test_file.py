# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.core.types.file import File
from six import StringIO


class TestFile(PassportTestCase):
    def test_init(self):
        stream = StringIO('data')
        file = File('file', stream)

        ok_(file)
        eq_(repr(file), '<File file>')
        eq_(file.filename, 'file')
        eq_(file.stream, stream)

    def test_len(self):
        file1 = File('file1', StringIO('data'))
        file2 = File('file2', StringIO('da\x00ta\nda\x00ta'))
        eq_(len(file1), 4)
        eq_(len(file2), 11)
        file1.stream.read()
        eq_(len(file1), 4)

    def test_eq_ne(self):
        stream = StringIO('data')
        file1 = File('file1', stream)
        file2 = File('file1', stream)
        file3 = File('file3', stream)
        file4 = File('file1', StringIO('data'))
        file5 = File('file1', StringIO('data\ndata'))

        ok_(file1 != object)
        ok_(file1 == file1)
        ok_(file1 == file2)
        ok_(file1 == file4)
        ok_(file1 != file3)
        ok_(file1 != file5)

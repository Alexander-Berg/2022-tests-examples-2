# coding: utf-8
from __future__ import absolute_import, print_function, unicode_literals

import sys

import six
import pytest

from sandbox.common import encoding


class TestEncoding(object):

    def test__force_unicode_exception(self):
        # Mostly copied from Django 1.11.21

        if six.PY2 and sys.getdefaultencoding() == "utf-8":
            # This test does not make sense under non-standard default encoding
            return

        # Broken __unicode__/__str__ actually raises an error.
        class MyString(object):
            def __str__(self):
                return b"\xc3\xb6\xc3\xa4\xc3\xbc"

            __unicode__ = __str__

        # str(s) raises a TypeError on python 3 if the result is not a text type.
        # python 2 fails when it tries converting from str to unicode (via ASCII).
        exception = TypeError if six.PY3 else UnicodeError
        with pytest.raises(exception):
            encoding.force_unicode(MyString())

    def test__force_unicode(self):
        # Mostly copied from Django 1.11.21

        class Test(object):
            if six.PY3:
                def __str__(self):
                    return "ŠĐĆŽćžšđ"
            else:
                def __str__(self):
                    return "ŠĐĆŽćžšđ".encode("utf-8")

        class TestU(object):
            if six.PY3:
                def __str__(self):
                    return "ŠĐĆŽćžšđ"

                def __bytes__(self):
                    return b"Foo"
            else:
                def __str__(self):
                    return b"Foo"

                def __unicode__(self):
                    return "\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111"

        assert encoding.force_unicode(Test()) == "\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111"
        assert encoding.force_unicode(TestU()) == "\u0160\u0110\u0106\u017d\u0107\u017e\u0161\u0111"
        assert encoding.force_unicode(1) == "1"
        assert encoding.force_unicode("foo") == "foo"

        class BrokenException(Exception):
            def __unicode__(self):
                return b"\xfc".decode(encoding="ascii")  # raises `UnicodeDecodeError`
            __str__ = __unicode__

        assert encoding.force_unicode(BrokenException("ABC", u"ŠĐĆŽćžšđ")) == u"ABC ŠĐĆŽćžšđ"

    def test__force_unicode_safe(self):
        assert encoding.force_unicode_safe(b"invalid \xfc") == u"invalid \N{REPLACEMENT CHARACTER}"

    def test__escape(self):

        class TestClass(object):
            def __str__(self):
                return self.__class__.__name__

        @six.python_2_unicode_compatible
        class TestClassWithUnicode(TestClass):
            REPR = u"class"

            def __str__(self):
                return self.REPR

        assert encoding.escape(b'<a href="aaa?bbb&ccc"> \xc5\xa0') == u'&lt;a href="aaa?bbb&amp;ccc"&gt; Š'

        text = u""
        assert encoding.escape(text) is text
        text = u"йцукен"
        assert encoding.escape(text.encode("utf-8")) == text
        text = "<>&"
        assert encoding.escape(text) == u"&lt;&gt;&amp;"
        assert encoding.escape(TestClass()) == TestClass.__name__
        assert encoding.escape(TestClassWithUnicode()) == TestClassWithUnicode.REPR

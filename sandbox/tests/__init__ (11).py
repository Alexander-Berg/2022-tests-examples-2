from __future__ import absolute_import, unicode_literals

import textwrap
import datetime as dt

import six
import pytest
import aniso8601

from sandbox.common import format as cf


class TestFormat(object):

    @pytest.mark.parametrize("s", (lambda x: x, lambda x: six.b(x)))
    def test__print_table(self, s):

        buf = six.StringIO()

        def printer(v):
            buf.write(v)
            buf.write("\n")

        expected = textwrap.dedent("""
            +---+---+---+
            | X | 0 | - |
            +---+---+---+
            | 0 | X | - |
            +---+---+---+
            | - | - | X |
            +---+---+---+
        """).lstrip()

        cf.print_table([["X", 0, "-"], None, ["0", "X", "-"], None, ["-", "-", "X"]], printer=printer)

        assert buf.getvalue() == expected

    @pytest.mark.parametrize("s", (lambda x: x, lambda x: six.b(x)))
    def test__str2size(self, s):
        assert cf.str2size(s("1024")) == 1024
        assert cf.str2size(100500) == 100500
        assert cf.str2size(s("1K")) == 1 << 10
        assert cf.str2size(s("2M")) == 2 << 20
        assert cf.str2size(s("3G")) == 3 << 30
        assert cf.str2size(s("4.5T")) == int((1 << 40) * 4.5)

    def test__size2str(self):
        assert cf.size2str(640) == "640.00byte(s)"
        assert cf.size2str(10352) == "10.11KiB"
        assert cf.size2str(103520000) == "98.72MiB"
        assert cf.size2str(103520000, till="k") == "101093.75KiB"
        assert cf.size2str(103520000, till=b"k") == "101093.75KiB"
        assert cf.size2str(10352000000) == "9.64GiB"
        assert cf.size2str(3452466511216) == "3.14TiB"

    def test__td2str(self):
        assert cf.td2str(dt.timedelta(seconds=32)) == "32s"
        assert cf.td2str(dt.timedelta(seconds=60)) == "01m 00s"
        assert cf.td2str(dt.timedelta(seconds=3600)) == "01h 00m 00s"
        assert cf.td2str(3600) == "01h 00m 00s"
        assert cf.td2str(dt.timedelta(days=1)) == "01d 00h 00m 00s"
        assert cf.td2str(dt.timedelta(seconds=99999)) == "01d 03h 46m 39s"

        long_td = dt.timedelta(days=1, hours=100, minutes=100, seconds=100)
        assert cf.td2str(long_td) == "05d 05h 41m 40s"
        assert cf.td2str(long_td, full=True) == "05 day(s) 05 hour(s) 41 minute(s) 40 second(s)"

    def test__dt2str(self):
        assert cf.dt2str(dt.datetime(2015, 3, 5, 7, 8, 3)) == "2015-03-05 07:08:03"
        assert cf.dt2str(None) == "None"

    def test__utcdt2iso(self):
        now = dt.datetime.utcnow()
        now_parsed = aniso8601.parse_datetime(cf.utcdt2iso()).replace(tzinfo=None)
        assert (now_parsed - now) < dt.timedelta(seconds=5)

        assert cf.utcdt2iso(dt.datetime(2015, 3, 5, 7, 8, 3)) == "2015-03-05T07:08:03Z"

    def test__format_exception(self):
        try:
            raise ValueError("boom")
        except ValueError:
            assert "Traceback (most recent call last)" in cf.format_exception()

    @pytest.mark.parametrize("s", (lambda x: x, lambda x: six.b(x)))
    def test__obfuscate_token(self, s):
        assert cf.obfuscate_token(s("1234")) == s("1234")
        assert cf.obfuscate_token(s("de93fc42f73d07aceb4001b")) == s("de93fc42")

    @pytest.mark.parametrize("s", (lambda x: x, lambda x: six.b(x)))
    def test__ident(self, s):
        assert cf.ident(s("ALLUPPER")) == "ALLUPPER"
        assert cf.ident(s("CamelCase")) == "CAMEL_CASE"
        assert cf.ident(s("ADangerousExample")) == "ADANGEROUS_EXAMPLE"

        with pytest.raises(ValueError):
            assert cf.ident(s("23AndMe"))

    @pytest.mark.parametrize("s", (lambda x: x, lambda x: six.b(x)))
    def test__brace_expansion(self, s):
        assert cf.brace_expansion([s("a{b,c}e"), s("k{l}o"), s("foo")]) == ["abe", "ace", "klo", "foo"]
        assert cf.brace_expansion([s("aa{b,c,d}")]) == ["aab", "aac", "aad"]
        assert cf.brace_expansion([s("k{1..4}o")]) == ["k1o", "k2o", "k3o", "k4o"]
        assert cf.brace_expansion([s("k{08..12}o")]) == ["k08o", "k09o", "k10o", "k11o", "k12o"]
        assert cf.brace_expansion([s("k{08..12}o")], join=":") == "k08o:k09o:k10o:k11o:k12o"

# -*- coding: utf-8 -*-

import os

import pytest

from sandbox.projects.common.teamcity import ant

NT_ONLY = pytest.mark.skipif(os.name != 'nt', reason='NT-only test')
POSIX_ONLY = pytest.mark.skipif(os.name == 'nt', reason='Posix-only test')


@pytest.mark.parametrize(('pattern', 'constant_part', 'glob_part'), (
    pytest.param('/foo/bar/baz', '/foo/bar/baz', '', marks=POSIX_ONLY),
    pytest.param('foo/bar/baz', 'foo/bar/baz', '', marks=POSIX_ONLY),
    pytest.param('/foo/*/bar', '/foo', '*/bar', marks=POSIX_ONLY),
    pytest.param('/*', '/', '*', marks=POSIX_ONLY),
    pytest.param('?foo/bar', '', '?foo/bar', marks=POSIX_ONLY),
    pytest.param(u'тест/*/кек', u'тест', u'*/кек', marks=POSIX_ONLY),
    pytest.param('C:\\foo\\bar\\baz', 'C:\\foo\\bar\\baz', '', marks=NT_ONLY),
    pytest.param('foo\\bar\\baz', 'foo\\bar\\baz', '', marks=NT_ONLY),
    pytest.param('D:\\foo\\*\\bar', 'D:\\foo', '*\\bar', marks=NT_ONLY),
    pytest.param('C:\\*', 'C:\\', '*', marks=NT_ONLY),
    pytest.param('?foo\\bar', '', '?foo\\bar', marks=NT_ONLY),
    pytest.param(u'тест\\*\\кек', u'тест', u'*\\кек', marks=NT_ONLY),
))
def test_split_pattern(pattern, constant_part, glob_part):
    assert ant._split_pattern(pattern) == (constant_part, glob_part)


class TestPattern(object):
    @pytest.mark.parametrize(('pattern', 'result'), (
        ('/foo/bar/*', True),
        ('/foo/bar/*/', True),
        ('foo/*', False),
        ('foo/*/', False),
    ))
    def test_is_absolute(self, pattern, result):
        pattern = ant.Pattern(pattern)
        assert pattern.is_absolute() == result

    @pytest.mark.parametrize(('pattern', 'path', 'result'), (
        pytest.param('bar/*', '/foo', '/foo/bar/*', marks=POSIX_ONLY),
        pytest.param('bar/*/', '/foo', '/foo/bar/*/', marks=POSIX_ONLY),
        pytest.param(u'кек/*', u'/тест', u'/тест/кек/*', marks=POSIX_ONLY),
        pytest.param('bar\\*', 'C:\\foo', 'C:\\foo\\bar\\*', marks=NT_ONLY),
        pytest.param('bar\\*\\', 'C:\\foo', 'C:\\foo\\bar\\*\\', marks=NT_ONLY),
        pytest.param(u'кек\\*', u'C:\\тест', u'C:\\тест\\кек\\*', marks=NT_ONLY),
    ))
    def test_prepend(self, pattern, path, result):
        pattern = ant.Pattern(pattern)
        assert unicode(pattern.prepend(path)) == result

    @pytest.mark.parametrize(('pattern', 'path', 'result'), (
        pytest.param('/foo/bar/*', '/foo', 'bar/*', marks=POSIX_ONLY),
        pytest.param('/foo/bar/*/', '/foo', 'bar/*/', marks=POSIX_ONLY),
        pytest.param(u'/тест/кек/*', u'/тест', u'кек/*', marks=POSIX_ONLY),
        pytest.param('C:\\foo\\bar\\*', 'C:\\foo', 'bar\\*', marks=NT_ONLY),
        pytest.param('C:\\foo\\bar\\*\\', 'C:\\foo', 'bar\\*\\', marks=NT_ONLY),
        pytest.param('C:/foo\\bar\\*/', 'C:\\foo', 'bar\\*\\', marks=NT_ONLY),
        pytest.param(u'C:\\тест\\кек\\*', u'C:\\тест', u'кек\\*', marks=NT_ONLY),
    ))
    def test_relative_to(self, pattern, path, result):
        pattern = ant.Pattern(pattern)
        assert unicode(pattern.relative_to(path)) == result

    @pytest.mark.parametrize(('pattern', 'matched', 'not_matched'), (
        (
            'foo',
            ('foo',),
            ('bar',),
        ),
        (
            '?abc/*/*.java',
            ('xabc/foobar/test.java',),
            ('abc/foobar/test.java', 'abc/foo/bar/test.java', u'abc/кек/тест.java'),
        ),
        (
            '**/CVS/*',
            ('CVS/Repository', 'org/apache/CVS/Entries', 'org/apache/jakarta/tools/ant/CVS/Entries'),
            ('org/apache/CVS/foo/bar/Entries',),
        ),
        (
            'org/apache/jakarta/**',
            ('org/apache/jakarta/tools/ant/docs/index.html', 'org/apache/jakarta/test.xml'),
            ('org/apache/xyz.java',),
        ),
        (
            'org/apache/**/CVS/*',
            ('org/apache/CVS/Entries', 'org/apache/jakarta/tools/ant/CVS/Entries'),
            ('org/apache/CVS/foo/bar/Entries',),
        ),
        (
            'test/**',
            ('test/x.java', 'test/foo/bar/xyz.html'),
            ('xyz.xml', 'foo/test.xml'),
        ),
        (
            'test/',
            ('test/x.java', 'test/foo/bar/xyz.html'),
            ('xyz.xml', 'foo/test.xml'),
        ),
        pytest.param(
            'test/',
            (u'test/кек/лол.java', u'test/foo.html'),
            ('test.xml',),
            marks=pytest.mark.skipif(os.name == 'nt', reason='Unicode paths are not supported on Windows')
        ),
        pytest.param(
            u'тест/',
            (u'тест/кек/лол.java', u'тест/foo.html'),
            (u'тест.xml',),
            marks=pytest.mark.skipif(os.name == 'nt', reason='Unicode paths are not supported on Windows')
        )
    ))
    def test_glob(self, pattern, matched, not_matched, tmp_path):
        for relpath in matched + not_matched:
            path = tmp_path.joinpath(relpath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()

        pattern = ant.Pattern(pattern).prepend(tmp_path)
        paths = pattern.glob()
        assert set(paths) == {tmp_path.joinpath(path) for path in matched}

    @pytest.mark.parametrize(('pattern', 'result'), (
        pytest.param('/foo/bar/baz', '/foo/bar/baz', marks=POSIX_ONLY),
        pytest.param('/foo/bar/baz/', '/foo/bar/baz', marks=POSIX_ONLY),
        pytest.param('/foo/bar/baz/*', '/foo/bar/baz', marks=POSIX_ONLY),
        pytest.param(u'тест/*/кек', u'тест', marks=POSIX_ONLY),
        pytest.param('C:\\foo\\bar\\baz', 'C:\\foo\\bar\\baz', marks=NT_ONLY),
        pytest.param('C:\\foo\\bar\\baz\\', 'C:\\foo\\bar\\baz', marks=NT_ONLY),
        pytest.param('C:\\foo\\bar\\baz\\*', 'C:\\foo\\bar\\baz', marks=NT_ONLY),
        pytest.param(u'тест\\*\\кек', u'тест', marks=NT_ONLY),
    ))
    def test_constant_part(self, pattern, result):
        pattern = ant.Pattern(pattern)
        assert pattern.constant_part() == result

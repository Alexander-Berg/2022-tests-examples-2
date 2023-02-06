import pytest
from sandbox.projects.sandbox_ci.utils.process import format_args_for_run_process, format_options


class TestsFormatArgs(object):
    def test_simple(self):
        """
        Should return simple list of args
        """
        expect = ['node', 'run.js', 'a', 'b', 'c']
        actual = format_args_for_run_process(('node', 'run.js', 'a', 'b', 'c'))
        assert expect == actual

    def test_opts(self):
        """
        Should return simple list of args
        """
        expect = ['node', 'run.js', '--opt1 \'some\'', '--opt2 \'some\'']
        actual = format_args_for_run_process(('node', 'run.js', {'opt1': 'some', 'opt2': 'some'}))
        assert expect == actual

    def test_no_supported_type(self):
        expect_msg = '<type \'tuple\'> is not supported type'
        with pytest.raises(Exception) as error:
            format_args_for_run_process(('node', 'run.js', (1, 2, 3)))
        assert error.value.message == expect_msg


class TestsFormatDictArgs(object):
    def test_boolean(self):
        """
        Should work with boolean args
        """
        expect = ['--opt1']
        actual = format_options(dict(opt1=True))
        assert expect == actual

    def test_short(self):
        expect = ['-a \'some\'', '-b \'other\'']
        actual = format_options(dict(a='some', b='other'))
        assert expect == actual

    def test_simple(self):
        expect = ['--opt1 \'some\'', '--opt2 \'other\'']
        actual = format_options(dict(opt1='some', opt2='other'))
        assert expect == actual

    def test_boolean_false(self):
        expect = ['--opt1 \'some\'']
        actual = format_options(dict(opt1='some', opt2=False))
        assert expect == actual

    def test_single_qoute(self):
        expect = ["--opt1 'som'\\''e'"]
        actual = format_options(dict(opt1='som\'e', opt2=False))
        assert expect == actual

    def test_equal_delimeter(self):
        expect = ["--opt1='some'"]
        actual = format_options(dict(opt1='some', opt2=False), use_equal=True)
        assert expect == actual

    def test_list_opt(self):
        expect = ["--opt1 'some'", "--opt1 'other'"]
        actual = format_options(dict(opt1=('some', 'other')))
        assert expect == actual

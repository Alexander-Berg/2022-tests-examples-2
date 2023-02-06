from collections import defaultdict
from io import StringIO

import mock

from dmp_suite.maintenance import ecook
from dmp_suite.maintenance.ecook import cmd
from test_dmp_suite.maintenance.ecook.utils import (
    WITH_DEFAULT_SETTINGS,
    assert_system_exit,
    patch_parser,
    path_to_module_name_mock)


NO_DEFAULT_SETTINGS = {
        'ecook': {'source_prefix': None, 'target_ttl_days': 1},
        'yt': {'layout': defaultdict(lambda: None)},
    }


@ecook.recipe
def dummy_recipe(_):
    pass


@mock.patch('dmp_suite.maintenance.ecook.cmd.path_to_module_name',
            path_to_module_name_mock)
class TestArgParser(object):

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_base_args(self):
        recipe, args = cmd.parse_args(['foo/bar.py'])
        assert 'foo/bar.py' == args.recipe_path
        assert 'foo.bar' in args.recipe_module
        assert args.recipe_name is None
        assert not args.dry_run
        assert recipe is dummy_recipe

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_invalid_recipe_paths(self):
        with assert_system_exit():
            cmd.parse_args('/dummy.py')

    @patch_parser(WITH_DEFAULT_SETTINGS)
    def test_hook(self, extract_recipe_mock):
        recipe_ = mock.MagicMock()
        hook = mock.MagicMock()
        hook.add_cmd_args.return_value = None
        recipe_.hooks = (hook,)
        extract_recipe_mock.return_value = recipe_

        recipe, args = cmd.parse_args(['foo/bar.py'])
        assert 'foo/bar.py' == args.recipe_path
        assert 'foo.bar' in args.recipe_module
        assert args.recipe_name is None
        assert not args.dry_run
        hook.add_cmd_args.assert_called()

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_sysargv_args(self):
        with mock.patch('sys.argv',
                        ['script', 'foo/bar.py']):
            recipe, args = cmd.parse_args()
            assert 'foo/bar.py' == args.recipe_path
            assert 'foo.bar' in args.recipe_module
            assert args.recipe_name is None
            assert not args.dry_run
            assert recipe is dummy_recipe

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_optional_args(self):
        with assert_system_exit():
            cmd.parse_args(['foo/bar.py', '--foo', 'bar', '--dry-run'])

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_sysargv_optional_args(self):
        with mock.patch('sys.argv',
                        ['script', 'foo/bar.py', '--foo', 'bar']):
            with assert_system_exit():
                cmd.parse_args()

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_empty_optional_args(self):
        with assert_system_exit():
            cmd.parse_args(['foo/bar.py', '--foo'])

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_recipe_name(self):
        recipe, args = cmd.parse_args(['foo/bar.py::name'])
        assert 'foo/bar.py::name' == args.recipe_path
        assert 'foo.bar' in args.recipe_module
        assert 'name' == args.recipe_name

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_recipe_complex_name(self):
        recipe, args = cmd.parse_args(['foo/bar.py::first::last'])
        assert 'foo/bar.py::first::last' == args.recipe_path
        assert 'foo.bar' in args.recipe_module
        assert 'first::last' == args.recipe_name

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_help(self):
        out = StringIO()
        with assert_system_exit('sys.stdout', out):
            cmd.parse_args(['-h'])
        assert out.getvalue()

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_help_before_args(self):
        out = StringIO()
        with assert_system_exit('sys.stdout', out):
            cmd.parse_args(['-h', 'foo/bar.py'])
        assert out.getvalue()
        assert 'foo/bar.py' not in out.getvalue()

    @patch_parser(WITH_DEFAULT_SETTINGS, dummy_recipe)
    def test_help_after_args(self):
        out = StringIO()
        with assert_system_exit('sys.stdout', out):
            cmd.parse_args(['foo/bar.py', '-h'])
        assert 'ecook foo/bar.py' in out.getvalue()

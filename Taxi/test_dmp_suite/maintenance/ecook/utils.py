# coding: utf-8
import contextlib
import functools
from collections import defaultdict
from io import StringIO

import mock
import pytest

WITH_DEFAULT_SETTINGS = {
    'ecook': {
        'source_layout_prefix': defaultdict(lambda: '//source/'),
        'target_ttl_days': 1
    }
}


def use_settings_mock(mock_dict):
    def settings(key, *args, **kwargs):
        keys = key.split('.')
        val = mock_dict
        for k in keys:
            val = val[k]
        return val
    return settings


@contextlib.contextmanager
def assert_system_exit(patched='sys.stderr', value=None):
    with pytest.raises(SystemExit):
        # hack prevent to print usage message to stderr
        with mock.patch(patched, value or StringIO()):
            yield


def patch_parser(settings_dict, recipe=None):
    def decorator(fn):
        if recipe:
            extract_recipe_kwargs = dict(
                new=mock.MagicMock(return_value=recipe))
        else:
            extract_recipe_kwargs = dict()

        @mock.patch('dmp_suite.maintenance.ecook.cmd.extract_recipe',
                    **extract_recipe_kwargs)
        @mock.patch('dmp_suite.maintenance.ecook.paths.settings',
                    use_settings_mock(settings_dict))
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            return fn(*args, **kwargs)

        return decorated

    return decorator


def path_to_module_name_mock(module):
    if module.endswith('foo/bar.py'):
        return 'foo.bar'
    else:
        raise ValueError()


def simplify_hnhm_attr_meta(table_list):
    """
    TableMeta для атрибутов генерируется динамически,
    то при совпадении всех полей - классы не совпадают.
    Думаю, в данном случае будет достаточно сранвить только поля
    """
    for el in table_list:
        el.source['meta'] = list(el.source['meta']().fields())

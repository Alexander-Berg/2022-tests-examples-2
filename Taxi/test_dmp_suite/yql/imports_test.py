import inspect
import modulefinder
import os.path
import pytest

from dmp_suite.yql import YQL_ALLOWED_MODULES


def check_module_imports(module):
    finder = modulefinder.ModuleFinder()
    finder.run_script(module)

    # based on https://github.com/jackmaney/python-stdlib-list/blob/master/stdlib_list/lists/2.7.txt
    #      and https://github.com/jackmaney/python-stdlib-list/blob/master/stdlib_list/lists/3.7.txt
    # but some modules are missing there and were added manually.
    # Probably it will be unnecessary if somebody will solve this issue:
    # https://github.com/jackmaney/python-stdlib-list/issues/7
    filename = 'stdlib-py3.txt'

    whitelist_path = os.path.join(os.path.dirname(__file__), filename)
    whitelist = set(line.strip() for line in open(whitelist_path))

    # known installed on cluster
    whitelist.add('cyson')
    # TODO: check if six is available too
    whitelist.add('six')

    modules = set(finder.modules)
    bad_modules = modules - whitelist

    if bad_modules:
        raise ValueError('Modules not in YQL: {}'.format(', '.join(bad_modules)))


@pytest.mark.parametrize(
    'module', YQL_ALLOWED_MODULES,
    ids=lambda mod: mod.__name__
)
def test_imports(module):
    filename = inspect.getfile(module).replace('.pyc', '.py')
    check_module_imports(filename)

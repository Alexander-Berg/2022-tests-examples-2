import os

import pytest

from replication_core import load
from replication_core.utils import yaml_utils

pytest_plugins = [
    'replication_core.pytest_plugins',
]

_TEST_RULES_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'replication_core',
    'replication_core_test_rules',
))
_MAIN_TEST_RULES_DIR = os.path.join(_TEST_RULES_DIR, 'core_test_rule_scopes')
_PARTIAL_TEST_RULES_DIR = os.path.join(_TEST_RULES_DIR, 'core_test_partial')


@pytest.fixture(scope='session')
def replication_core_rules():
    _cache = {}

    def loader(*, main=False, partial=False):
        args = (main, partial)
        if args not in _cache:
            if partial:
                partial_rules = load.load_rule_scopes(
                    _PARTIAL_TEST_RULES_DIR, validate=True,
                )
            if main:
                rules = load.load_rule_scopes(
                    _MAIN_TEST_RULES_DIR, validate=True,
                )
                if partial:
                    rules = rules.evolve(partial_rules, tolerate_errors=True)
            else:
                if not partial:
                    raise RuntimeError('Choose one of main/partial')
                rules = partial_rules

            _cache[args] = rules
        return _cache[args]

    class CoreTestRules:
        load = loader

        @staticmethod
        def make_main_path(path):
            return os.path.join(_MAIN_TEST_RULES_DIR, path)

        @staticmethod
        def make_partial_path(path):
            return os.path.join(_PARTIAL_TEST_RULES_DIR, path)

    return CoreTestRules


@pytest.fixture
def load_core_rules_yaml():
    def loader(path, main=True):
        if main:
            prefix = _MAIN_TEST_RULES_DIR
        else:
            prefix = _PARTIAL_TEST_RULES_DIR
        full_path = os.path.join(prefix, path) + '.yaml'
        return yaml_utils.load_file(full_path)
    return loader

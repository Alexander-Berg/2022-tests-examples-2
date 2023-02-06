import pathlib

import freezegun
import pytest

from replication import core_context
from replication import data_context
from replication import replication_yaml as replication_yaml_module
from replication import settings
from replication.replication import classes


pytest_plugins = [
    'testsuite.pytest_plugin',
    'replication_core.pytest_plugins.mappers',
]


class DummyConfig:
    REPLICATION_SERVICE_CTL: dict = {}
    REPLICATION_RULES_PARSE_ERRORS: dict = {}


class DummyMongoDb:
    replication_state = NotImplemented
    replication_settings = NotImplemented


# TODO: move it out of here
_SECDIST = {
    'settings_override': {
        'YT_PHONE_HASH_SECRET': 'secret1',
        'YT_PHONE_HASH_SECRET_2': 'secret2',
    },
}


MAPPING_PARAMS = data_context.get_mapping_params(_SECDIST)

TEST_ENV_TESTSUITE = 'testsuite'
TEST_ENV_DMP_RULES = 'dmp'


def _parametrize_test_env(*, testsuite=False, dmp=False):
    options = []
    if testsuite:
        options.append(TEST_ENV_TESTSUITE)
    if dmp and settings.HAS_ENV_DMP_INSTALL_DIR:
        options.append(TEST_ENV_DMP_RULES)
    return pytest.mark.parametrize(
        'replication_ctx', options, indirect=['replication_ctx'],
    )


# pylint: disable=invalid-name
any_rules = _parametrize_test_env(testsuite=True, dmp=True)
dmp_rules_only = _parametrize_test_env(dmp=True)


@pytest.fixture
def replication_ctx(monkeypatch, _replication_core_cache, request):
    env = request.param
    if env == TEST_ENV_TESTSUITE:
        replication_yaml_path = pathlib.Path(settings.ROOT_DIR).joinpath(
            'test_replication/schemas/replication_testsuite.yaml',
        )
        monkeypatch.setattr(settings, 'SKIP_EXAMPLE_RULES', True)
    else:
        replication_yaml_path = settings.REPLICATION_YAML_PATH
        monkeypatch.setattr(settings, 'SKIP_EXAMPLE_RULES', False)

    if env not in _replication_core_cache:
        core = core_context.make_local_minimal(
            mongo_db=DummyMongoDb(), config_service=DummyConfig(), secdist={},
        )
        replication_yaml = replication_yaml_module.load(
            path=replication_yaml_path,
        )
        master_rules = data_context.get_master_rules(
            core.pluggy_deps.source_definitions, replication_yaml, strict=True,
        )
        rule_keeper_depends = core_context.RuleKeeperDepends(
            map_context_params=MAPPING_PARAMS,
            master_rules=master_rules,
            replication_yaml=replication_yaml,
        )
        rule_keeper = core_context.RuleKeeper(rule_keeper_depends)
        core.rule_keeper = rule_keeper

        # TODO: better call on_startup?
        rule_keeper.shared_deps = core.shared_deps
        rule_keeper.pluggy_deps = core.pluggy_deps
        rule_keeper.states_wrapper = data_context.get_states_wrapper(
            core.db, rule_keeper,
        )
        rule_keeper.staging_db = None
        rule_keeper.confirm_map = None
        rule_keeper.rules_storage = classes.RulesStorage(
            core.rule_keeper, fail_at_load_rules=True, imitate_secrets=True,
        )
        rule_keeper.rules_storage._init()  # pylint: disable=protected-access
        _replication_core_cache[env] = core

    return _replication_core_cache[env]


# workaround to disable replication's autouse fixture
@pytest.fixture
def entry_point():
    pass


@pytest.fixture
def freeze_time(now):
    with freezegun.freeze_time(now, ignore=['']) as frozen:
        yield frozen


@pytest.fixture(scope='session')
def _replication_core_cache():
    return {}

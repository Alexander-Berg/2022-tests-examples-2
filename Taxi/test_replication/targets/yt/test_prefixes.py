# pylint: disable=redefined-outer-name
import pytest

from replication import settings
from replication.common.yt_tools import utils as yt_utils
from replication.targets.yt import prefixes


@pytest.mark.nofilldb
@pytest.mark.parametrize('is_force_environment', [False, True])
@pytest.mark.parametrize(
    'prefix_alias, environment, expected',
    [
        (None, None, '//home/taxi/unittests/'),
        (None, 'testing', '//home/taxi/testing/'),
        (None, 'unittests', '//home/taxi/unittests/'),
        (None, 'production', '//home/taxi/production/'),
        (None, 'development', '//home/taxi/development/'),
        ('allowed', None, '//allowed/unittests/data/'),
        ('allowed', 'testing', '//allowed/testing/data/'),
        ('allowed', 'unittests', '//allowed/unittests/data/'),
        ('allowed', 'production', '//allowed/production/data/'),
        ('allowed', 'development', '//allowed/production/data/'),
    ],
)
def test_prefixes(
        monkeypatch,
        prefix_alias,
        is_force_environment,
        environment,
        expected,
        yt_entity,
):
    force_environment = None
    if environment is not None:
        if is_force_environment:
            force_environment = environment
        else:
            monkeypatch.setattr(settings, 'ENVIRONMENT', environment)
    assert yt_entity.get_prefix(prefix_alias, force_environment) == expected


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'prefix_alias, client_name, expected',
    [
        (None, 'seneca-vla', None),
        ('allowed', 'seneca-man', 'senecabundle'),
        ('allowed', 'hahn', 'hahnbundle'),
        ('allowed', 'arni', None),
    ],
)
def test_get_bundle(yt_entity, prefix_alias, client_name, expected):
    yt_client_names = yt_utils.gel_all_client_names()
    assert client_name in yt_client_names
    assert yt_entity.get_prefix_bundle(prefix_alias, client_name) == expected


@pytest.fixture
def yt_entity(replication_ctx):
    config = None
    for master_rule in replication_ctx.rule_keeper.master_rules.values():
        for source_core, _ in master_rule.iter_replication_cores():
            config = source_core.flaky_config
            break
        break
    return prefixes.load_yt_entity(config)

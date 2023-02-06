import pytest

from replication.common.pytest import env_util
from replication.common.pytest import replication_rules


@env_util.parametrize_test_env(testsuite=True, dmp=False)
def test_states_base_source(replication_ctx):
    replication_rules.run_test_states_base_source(replication_ctx)


@env_util.parametrize_test_env(testsuite=True, dmp=False)
@pytest.mark.nofilldb
def test_api_sources(replication_app):
    replication_rules.run_test_api_sources(replication_app)

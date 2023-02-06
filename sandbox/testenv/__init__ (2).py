from sandbox import sdk2


class TESTENV_CI_BACKEND_PACKAGE(sdk2.resource.AbstractResource):
    """
        testenv-ci-backend package
    """
    releasable = True
    any_arch = True
    auto_backup = True
    releasers = ["CI"]
    ttl = 'inf'


class TEST_ENVIRONMENT_CORE_PACKAGE(sdk2.resource.AbstractResource):
    """
        testenv-core package
    """
    auto_backup = True
    any_arch = True


class TESTENV_CORE(sdk2.resource.AbstractResource):
    """
        testenv-core package
    """
    releasable = True
    auto_backup = True
    any_arch = True
    releasers = ["CI"]
    ttl = "inf"


class CLICKHOUSE_PACKAGE(sdk2.resource.AbstractResource):
    """
        clickhouse package
    """
    any_arch = False
    executable = True
    releasers = ["CI"]
    ttl = 'inf'


class TESTENV_SOLOMON_AGENT_PACKAGE(sdk2.resource.AbstractResource):
    """
        solomon/agent/bin package for samogon
    """
    any_arch = False
    executable = True

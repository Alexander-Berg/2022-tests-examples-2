from functools import wraps
from multiprocessing.dummy import Pool as ThreadPool
from typing import Dict

import pytest
import urllib3

from ..core import exceptions
from ..helpers.testenv_helpers import _TestEnv

# Disable annoying ssl certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


ABC_SERVICE = "slb"

# Services with testing fsm
PROD_SVC_FQDN = "l3manager-agent-successful-integration-test.yandex.net"
TEST_ENV_SVC_FQDN_SUCCESS_TEST = "l3manager-agent-successful-integration-test.yandex.net"
TEST_ENV_SVC_FQDN_FAILURE_TEST = "l3manager-agent-failure-integration-test.yandex.net"

# Services with testing+deployment fsm
PROD_SVC_FQDN_FSM = "l3manager-machine-successful-integration-test.yandex.net"
TEST_ENV_SVC_FQDN_SUCCESS_TEST_FSM = "l3manager-machine-successful-integration-test.yandex.net"
TEST_ENV_SVC_FQDN_FAILURE_TEST_FSM = "l3manager-machine-failure-integration-test.yandex.net"


# TEST_LB = "sas-1testenv-test-lb0aa.yndx.net"
SERVICE_LB = "sas-1testenv-lb0bb.yndx.net"
SERVICE_LB_FSM = "sas-1testenv-lb0ab.yndx.net"

LBS = [SERVICE_LB, SERVICE_LB_FSM]

UNREACHABLE_PORT = {"config-CONNECT_PORT": 9998}
UNREACHABLE_IP_PORT: Dict = {**UNREACHABLE_PORT, **{"ip": "2a02:6b8:0:3400:0:43c:0:9999"}}
UNREACHABLE_IP_PORT_FSM: Dict = {**UNREACHABLE_PORT, **{"ip": "2a02:6b8:0:3400:0:43c:1:0"}}


def named(foo):
    """
    Adding function name argument to a decorated function
    """

    @wraps(foo)
    def _(*args, **kwargs):
        return foo(foo.__name__, *args, **kwargs)

    return _


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_SUCCESS_TEST)
@named
def test_config_testing_workflow_success(name=None):
    with _TestEnv(
        ABC_SERVICE,
        prod_svc_fqdn=PROD_SVC_FQDN,
        test_svc_fqdn=TEST_ENV_SVC_FQDN_SUCCESS_TEST,
        lb_fqdns=LBS,
        message=" ".join(name.split("_")),
    ) as test_env:

        test_env.inject_test_task()

    assert test_env.is_task_succesfully_tested(wait_vs_announced=True, testing_timeout_override=600)


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_SUCCESS_TEST)
@named
def test_config_testing_workflow_failure(name=None):
    with _TestEnv(
        ABC_SERVICE,
        prod_svc_fqdn=PROD_SVC_FQDN,
        test_svc_fqdn=TEST_ENV_SVC_FQDN_SUCCESS_TEST,
        lb_fqdns=LBS,
        vs_config_field_override=UNREACHABLE_PORT,
        message=" ".join(name.split("_")),
    ) as test_env:

        test_env.inject_test_task()

        assert not test_env.is_task_succesfully_tested()


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_FAILURE_TEST)
@named
def test_never_announced_config(name=None):
    with _TestEnv(
        ABC_SERVICE,
        prod_svc_fqdn=PROD_SVC_FQDN,
        test_svc_fqdn=TEST_ENV_SVC_FQDN_FAILURE_TEST,
        lb_fqdns=LBS,
        vs_config_field_override=UNREACHABLE_IP_PORT,
        message=" ".join(name.split("_")),
    ) as test_env:

        test_env.inject_test_task()

        assert test_env.is_task_succesfully_tested()


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_FAILURE_TEST)
@named
def test_concurrent_deployments(name=None):
    with _TestEnv(
        ABC_SERVICE,
        prod_svc_fqdn=PROD_SVC_FQDN,
        test_svc_fqdn=TEST_ENV_SVC_FQDN_FAILURE_TEST,
        lb_fqdns=LBS,
        vs_config_field_override=UNREACHABLE_IP_PORT,
        message=" ".join(name.split("_")),
    ) as test_env:
        num_workers = 8

        with ThreadPool(num_workers) as pool:
            future_results = []
            for _ in range(num_workers):
                future_results.append(pool.apply_async(test_env.inject_test_task, args=()))
            for f in future_results:
                try:
                    f.get()
                except exceptions.CouldNotDeployConfigError as e:
                    if str(e) != 'L3 response: Code 409, Body {"result": "ERROR", "message": "Failed to change configuration state"}':
                        raise

        assert test_env.is_task_succesfully_tested(testing_timeout_override=600)


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_SUCCESS_TEST_FSM)
@named
def test_config_testing_workflow_success_fsm(name=None):
    with _TestEnv(
        ABC_SERVICE,
        prod_svc_fqdn=PROD_SVC_FQDN_FSM,
        test_svc_fqdn=TEST_ENV_SVC_FQDN_SUCCESS_TEST_FSM,
        lb_fqdns=LBS,
        message=" ".join(name.split("_")),
    ) as test_env:

        test_env.inject_test_task()

    assert test_env.is_task_succesfully_tested(
        # Uncomment when fms fixes VS state processing
        # wait_vs_announced=True,
        testing_timeout_override=600
    )


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_FAILURE_TEST_FSM)
@named
def test_config_testing_workflow_failure_fsm(name=None):
    with _TestEnv(
        ABC_SERVICE,
        prod_svc_fqdn=PROD_SVC_FQDN_FSM,
        test_svc_fqdn=TEST_ENV_SVC_FQDN_FAILURE_TEST_FSM,
        lb_fqdns=LBS,
        vs_config_field_override=UNREACHABLE_IP_PORT_FSM,
        message=" ".join(name.split("_")),
    ) as test_env:

        test_env.inject_test_task()

    assert test_env.is_task_succesfully_tested()

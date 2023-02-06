import urllib3
import copy
import requests
import pytest
from http import HTTPStatus

from ..core.client import L3mgrSimpleClient
from ..helpers.testenv_helpers import _TestEnv


# Disable annoying ssl certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ABC_SERVICE = "slb"
PROD_SVC_FQDN = "l3manager-agent-successful-integration-test.yandex.net"
TEST_ENV_SVC_FQDN_SUCCESS_TEST = "l3manager-agent-successful-integration-test.yandex.net"

SERVICE_LB = "sas-1testenv-lb0bb.yndx.net"
SERVICE_LB_FSM = "sas-1testenv-lb0ab.yndx.net"

LBS = [SERVICE_LB, SERVICE_LB_FSM]


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_SUCCESS_TEST)
def test_post_config_failure_case():
    """
    Creating a config and checking precondition that there is no other configs except `dummy_config` created
    The check should fail
    """

    dummy_config = 1

    test_env = _TestEnv(
        ABC_SERVICE, prod_svc_fqdn=PROD_SVC_FQDN, test_svc_fqdn=TEST_ENV_SVC_FQDN_SUCCESS_TEST, lb_fqdns=LBS
    )
    svc_id = test_env.client.svc_id

    configs = L3mgrSimpleClient.svc_configs(svc_id)

    if len(configs["objects"]) < 0:
        raise Exception("Cannot prepare test env for svc_id {svc_id}")

    most_recent_config_id = configs["objects"][0]["id"]

    headers = copy.deepcopy(L3mgrSimpleClient.HEADERS)
    headers["If-Match"] = f"cfg_id={dummy_config}"

    response = requests.post(
        L3mgrSimpleClient.api_path.service_config_by_id(svc_id, most_recent_config_id) + "/process",
        headers=headers,
        verify=False,
    )

    assert response.status_code == HTTPStatus.PRECONDITION_FAILED


@pytest.mark.xdist_group(name=TEST_ENV_SVC_FQDN_SUCCESS_TEST)
def test_post_config_success_case():
    """
    Creating a config and checking precondition that there is no other configs except the newly created config
    The check should succeed
    """

    test_env = _TestEnv(
        ABC_SERVICE, prod_svc_fqdn=PROD_SVC_FQDN, test_svc_fqdn=TEST_ENV_SVC_FQDN_SUCCESS_TEST, lb_fqdns=LBS
    )
    svc_id = test_env.client.svc_id

    configs = L3mgrSimpleClient.svc_configs(svc_id)

    if len(configs["objects"]) < 0:
        raise Exception("Cannot prepare test env for svc_id {svc_id}")

    most_recent_config_id = configs["objects"][0]["id"]

    headers = copy.deepcopy(L3mgrSimpleClient.HEADERS)
    headers["If-Match"] = f"cfg_id={most_recent_config_id}"

    response = requests.post(
        L3mgrSimpleClient.api_path.service_config_by_id(svc_id, most_recent_config_id) + "/process",
        headers=headers,
        verify=False,
    )

    assert response.status_code == HTTPStatus.ACCEPTED

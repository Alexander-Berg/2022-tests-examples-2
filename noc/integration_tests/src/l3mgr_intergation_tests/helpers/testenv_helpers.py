from time import time, sleep
import urllib3
import re
import json

import requests

from ..core.client import L3mgrSimpleClient, APIRoutes
from ..core.exceptions import UnexpectedConfigState, TestNotCompleteInExpectedTime
from ..definitions import APP_CONFIG

from typing import List

# Disable annoying ssl certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def session_attributes():
    return type("L3ClientSessionData", (), dict(cfg_id=None, vs_ids=set()))


class AgentTestenvBuilder:
    TEST_WAIT_TIMEOUT_SECONDS = 90

    # Config deployment states
    TESTING_NOT_COMPLETE = ["NEW", "PREPARED", "TEST_PENDING", "TESTING"]
    TEST_FAIL = "TEST_FAIL"
    ACTIVE_STATE = "ACTIVE"
    ANNOUNCED_STATE = "ANNOUNCED"
    TESTING_SUCCEED = [
        "TEST_SUCCESS",
        "PENDING",
        "VCS_PENDING",
        "VCS_UPDATING",
        "VCS_COMMITTED",
        "DEPLOYING",
        "DEPLOYED",
        ACTIVE_STATE,
    ]
    UNEXPECTED = ["FAIL", "INACTIVE"]

    def __init__(self, abc: str, prod_svc_fqdn: str, test_svc_fqdn: str, lb_fqdns: List[str]):
        self.converter = ProdConfigsConverter(prod_svc_fqdn)
        self.runtime = session_attributes()
        self.abc = abc
        self.svc_fqdn = test_svc_fqdn
        self.lb_fqdns = lb_fqdns

        self._svc_id = None
        self._lb_ids: List = []

    @property
    def svc_id(self):
        if self._svc_id:
            return self._svc_id

        return L3mgrSimpleClient.get_svc_id_by_fqdn(self.svc_fqdn)

    def add_svc_ignore_exist(self):
        L3mgrSimpleClient.add_svc_ignore_exist(self.svc_fqdn, self.abc)

        return self

    def delete_configs_if_possible(self):
        """
        Some configs cannot be deleted (like ACTIVE or INACTIVE)
        but it may be useful to delete configs stopping depoyment of a new config
        """
        result_limit = "?_limit=100"
        configs = L3mgrSimpleClient.svc_configs(self.svc_id, result_limit)

        for config in configs.get("objects", []):
            L3mgrSimpleClient.delete_config(self.svc_id, config["id"])

    def add_vs(self, vs_form_data):
        self.runtime.vs_ids.add(L3mgrSimpleClient.add_vs(self.svc_id, vs_form_data))

        return self

    def add_vss_from_prod(self, data_formatter=None):
        for vs_form_data in self.converter.prod_vs_configs_form_data:
            if data_formatter:
                vs_form_data = data_formatter(vs_form_data)
            self.add_vs(vs_form_data)

        return self

    def create_config(self, message):
        self.runtime.cfg_id = L3mgrSimpleClient.create_config(
            self.svc_id, list(self.runtime.vs_ids)[0], "Integ test" + f": {message}" or ""
        )

        return self

    def deploy(self):
        L3mgrSimpleClient.deploy(self.svc_id, self.runtime.cfg_id)

        return self

    @property
    def lb_ids(self):
        if self._lb_ids:
            return self._lb_ids

        self._lb_ids.extend(L3mgrSimpleClient.get_lb_ids_by_fqdns(self.lb_fqdns))

        return self._lb_ids

    def add_lbs_to_abc_service(self):
        L3mgrSimpleClient.add_lbs_to_abc_service(self.abc, self.lb_ids)

        return self

    def is_task_succesfully_tested(self, wait_vs_announced=None, testing_timeout_override=None):
        wait_timeout = testing_timeout_override or self.TEST_WAIT_TIMEOUT_SECONDS

        max_wait_time = time() + wait_timeout

        while max_wait_time > time():
            config_info = L3mgrSimpleClient.config_deployment_status(self.svc_id, self.runtime.cfg_id)
            state = config_info["state"]

            if state in self.TESTING_NOT_COMPLETE:
                sleep(1)
                continue
            elif state == self.TEST_FAIL:
                return False
            elif state in self.TESTING_SUCCEED and wait_vs_announced:
                return self.is_vs_announced(config_info, max_wait_time)
            elif state in self.TESTING_SUCCEED:
                return True
            else:
                raise UnexpectedConfigState(
                    f"Unexpected config state '{state}' during testing. Config info: {config_info}"
                )

        raise TestNotCompleteInExpectedTime(f"Testing wait time {wait_timeout}s exceed. Config info: {config_info}")

    def is_vs_announced(self, svc_config, max_wait_time):
        wait_timeout = int(max_wait_time - time())

        while max_wait_time > time():
            vs_states = []

            for vs_id in svc_config["vs_id"]:
                vs_config = L3mgrSimpleClient.get_vs_config(vs_id)
                vs_states += [status["state"] for status in vs_config["status"]]

                if self.ANNOUNCED_STATE in vs_states:
                    return True
            sleep(1)

        TestNotCompleteInExpectedTime(f"VS Announce wait time {wait_timeout}s exceed. Current VS states: {vs_states}")


class ProdConfigsConverter:
    ANNOUNCED_STATE = "ANNOUNCED"
    ACTIVE_STATE = "ACTIVE"

    # robot-ttmgmt-builder token
    PROD_L3MGR_READONLY_TOKEN = APP_CONFIG.api.prod.PROD_L3MGR_READONLY_TOKEN
    PROD_API_URL = APP_CONFIG.api.prod.PROD_API_URL

    # Headers
    OAUTH_HEADER = {"Authorization": f"OAuth {PROD_L3MGR_READONLY_TOKEN}"}
    HEADERS = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", **OAUTH_HEADER}

    def __init__(self, svc_fqdn):
        self.api_path = APIRoutes(self.PROD_API_URL)
        self.svc_fqdn = svc_fqdn
        self.runtime = session_attributes()

        self._svc_id = None

    @property
    def svc_id(self):
        if self._svc_id:
            return self._svc_id

        l3_response = requests.get(
            self.api_path.service_info_by_fqdn(self.svc_fqdn), headers=self.HEADERS, verify=False
        )

        if l3_response.json()["objects"]:
            self._svc_id = l3_response.json()["objects"][0]["id"]
            return self._svc_id

    def _active_config_data(self):
        active_config = "?state__exact=ACTIVE"

        l3_response = requests.get(
            self.api_path.service_by_id(self.svc_id, active_config), headers=self.HEADERS, verify=False
        )

        if l3_response.json()["objects"]:
            config_data = l3_response.json()["objects"][0]
            self.runtime.cfg_id = config_data["id"]
            self.runtime.vs_ids = config_data["vs_id"]

        return self.runtime

    def get_vss_for_active_config(self):
        vs_configs = []

        for vs_id in self._active_config_data().vs_ids:
            l3_response = requests.get(self.api_path.vs_config_by_id(vs_id), headers=self.HEADERS, verify=False)
            vs_configs.append(l3_response.json())

        return vs_configs

    @property
    def prod_vs_configs_form_data(self):
        """
        Collects active VSs and converts their configs to the form data, that can be used in API calls
        to deploy those VSs
        """

        vs_configs_converted = []
        for vs in self.get_vss_for_active_config():
            vs_configs_converted.append(self.convert_l3_api_response_to_vs_config_form_data(vs))

        return vs_configs_converted

    def convert_l3_api_response_to_vs_config_form_data(self, vs):
        form_data = ""
        AND_LITERAL = "&"

        for field in ["ip", "port", "protocol", "group"]:
            if field == "group":
                form_data += field + "=" + vs[field][0] + AND_LITERAL
            else:
                value = json.dumps(vs[field]) if not isinstance(vs[field], str) else vs[field]
                form_data += field + "=" + value + AND_LITERAL

        for field, value in vs["config"].items():
            if value is not None and value != "" and not field.startswith("WEIGHT"):
                value = json.dumps(value) if not isinstance(value, str) else value
                form_data += "config-" + field + "=" + value + AND_LITERAL

        return form_data.rstrip(AND_LITERAL)


class _TestEnv:
    def __init__(
        self, abc_service, prod_svc_fqdn, test_svc_fqdn, lb_fqdns, vs_config_field_override=None, message=None
    ):
        self.client = AgentTestenvBuilder(
            abc_service,
            prod_svc_fqdn=prod_svc_fqdn,
            test_svc_fqdn=test_svc_fqdn,
            lb_fqdns=lb_fqdns,
        )

        # Setup test env
        self.client.add_lbs_to_abc_service()
        self.client.add_svc_ignore_exist()
        self.client.add_vss_from_prod(self.data_formatter_setup(vs_config_field_override))
        self.client.create_config(message)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Maybe it makes sense to keep configs to see test result in UI
        # self.client.delete_configs_if_possible()
        pass

    def data_formatter_setup(self, field_override):
        def data_formatter(vs_form_data):
            if not field_override:
                return vs_form_data

            data_formatted = ""

            for field, value in field_override.items():
                replace_to = f"&{field}={value}&"
                pattern = re.compile(f"(&|^){field}=.*?(&|$)")

                data_formatted = re.sub(pattern, replace_to, data_formatted or vs_form_data)
            return data_formatted.strip("&")

        return data_formatter

    def inject_test_task(self):
        self.client.deploy()

    def is_task_succesfully_tested(self, wait_vs_announced=False, testing_timeout_override=None):
        return self.client.is_task_succesfully_tested(wait_vs_announced, testing_timeout_override)

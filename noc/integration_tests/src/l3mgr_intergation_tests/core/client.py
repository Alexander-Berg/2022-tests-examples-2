import http
import urllib3

import requests

from .exceptions import (
    CouldNotAddServiceError,
    CouldNotAddIPError,
    CouldNotCreateConfigError,
    CouldNotGetBalancerID,
    CouldNotGetIPError,
    CouldNotAddBalancerToABCError,
    CouldNotDeleteConfigError,
    CouldNotGetConfigError,
    CouldNotAddVSError,
    CouldNotDeployConfigError,
)

from ..definitions import APP_CONFIG

# Disable annoying ssl certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class APIRoutes:
    ABC = "/abc"
    SERVICE = "/service"
    IP = "/ip"
    VS = "/vs"
    CONFIG = "/config"
    BALANCER = "/balancer"

    def __init__(self, api_url):
        self.base_url = api_url

    @property
    def service_root(self):
        return self.base_url + self.SERVICE

    @property
    def abc_root(self):
        return self.base_url + self.ABC

    @property
    def config_root(self):
        return self.base_url + self.CONFIG

    @property
    def vs_root(self):
        return self.base_url + self.VS

    def balancer_root(self, search_params=None):
        return f"{self.base_url}{self.BALANCER}{search_params if search_params else ''}"

    def abc_by_id(self, abc_id):
        return f"{self.abc_root}/{abc_id}"

    def services(self, search_params=None):
        return f"{self.service_root}{search_params if search_params else ''}"

    def service_by_id(self, svc_id, search_params=None):
        return f"{self.service_root}/{svc_id}{self.CONFIG}{search_params if search_params else ''}"

    def service_config_by_id(self, svc_id, cfg_id):
        return f"{self.service_root}/{svc_id}{self.CONFIG}/{cfg_id}"

    def vs_config_by_id(self, vs_id):
        return f"{self.vs_root}/{vs_id}"

    def service_info_by_fqdn(self, fqdn):
        return f"{self.service_root}?fqdn__exact={fqdn}"

    def vs_by_svc_id(self, svc_id):
        return f"{self.service_root}/{svc_id}{self.VS}"

    def config_by_svc_id(self, svc_id):
        return f"{self.service_root}/{svc_id}{self.CONFIG}"


class L3mgrSimpleClient:
    L3_TEST_API = APP_CONFIG.api.test.TEST_API_URL
    TEST_ENV_L3MGR_TOKEN = APP_CONFIG.api.test.TEST_ENV_L3MGR_TOKEN

    api_path = APIRoutes(L3_TEST_API)

    # Headers
    OAUTH_HEADER = {"Authorization": f"OAuth {TEST_ENV_L3MGR_TOKEN}"}
    HEADERS = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", **OAUTH_HEADER}

    # L3 response statuses
    L3_OK_STATUS = "OK"
    SVC_ALREADY_EXISTS = "Service with this FQDN already exists."

    @classmethod
    def get_svc_id_by_fqdn(cls, svc_fqdn):
        fqdn_query = f"?fqdn__exact={svc_fqdn}"

        l3_response = requests.get(cls.api_path.services(search_params=fqdn_query), headers=cls.HEADERS, verify=False)

        if l3_response.json()["objects"]:
            svc_id = l3_response.json()["objects"][0]["id"]
            return svc_id

    @classmethod
    def add_svc_ignore_exist(cls, svc_fqdn, abc):
        body = f"fqdn={svc_fqdn}&abc={abc}"

        l3_response = requests.post(cls.api_path.services(), headers=cls.HEADERS, data=body, verify=False)

        if (
            l3_response.json()["result"] == cls.L3_OK_STATUS
            or l3_response.json().get("errors", {}).get("fqdn", [None])[0] == cls.SVC_ALREADY_EXISTS
        ):
            return
        else:
            raise CouldNotAddServiceError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

    @classmethod
    def svc_configs(cls, svc_id, search_params=None):
        l3_response = requests.get(cls.api_path.service_by_id(svc_id, search_params), headers=cls.HEADERS, verify=False)

        if l3_response.status_code != http.HTTPStatus.OK:
            raise CouldNotGetConfigError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

        return l3_response.json()

    @classmethod
    def delete_config(cls, svc_id, config_id):
        l3_response = requests.delete(
            cls.api_path.service_config_by_id(svc_id, config_id), headers=cls.HEADERS, verify=False
        )

        if l3_response.status_code not in [http.HTTPStatus.NO_CONTENT, http.HTTPStatus.FORBIDDEN]:
            raise CouldNotDeleteConfigError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

    @classmethod
    def add_vs(cls, svc_id, vs_form_data):
        l3_response = requests.post(
            cls.api_path.vs_by_svc_id(svc_id), headers=cls.HEADERS, data=vs_form_data, verify=False
        )

        if l3_response.json()["result"] == cls.L3_OK_STATUS:
            return l3_response.json()["object"]["id"]
        else:
            raise CouldNotAddVSError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

    @classmethod
    def create_config(cls, svc_id, vs_ids, comment):
        l3_response = requests.post(
            cls.api_path.config_by_svc_id(svc_id),
            headers=cls.HEADERS,
            data=f"vs={vs_ids}&comment={comment}",
            verify=False,
        )

        if l3_response.json()["result"] == cls.L3_OK_STATUS:
            return l3_response.json()["object"]["id"]
        else:
            raise CouldNotCreateConfigError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

    @classmethod
    def deploy(cls, svc_id, cfg_id):
        l3_response = requests.post(
            cls.api_path.service_config_by_id(svc_id, cfg_id) + "/process", headers=cls.HEADERS, verify=False
        )

        if l3_response.json()["result"] != cls.L3_OK_STATUS:
            raise CouldNotDeployConfigError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

    @classmethod
    def add_ip(cls, abc, ip):
        l3_response = requests.post(cls.api_path.abc_by_id(abc), headers=cls.HEADERS, data=f"ip={ip}", verify=False)

        if l3_response.json()["result"] != cls.L3_OK_STATUS:
            raise CouldNotAddIPError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

    @classmethod
    def get_ip(cls, abc):
        l3_response = requests.post(cls.api_path.abc_by_id(abc) + "/getip", headers=cls.HEADERS, verify=False)
        result = l3_response.json()

        if result["result"] != cls.L3_OK_STATUS:
            raise CouldNotGetIPError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

        return result

    @classmethod
    def get_lb_ids_by_fqdns(cls, lb_fqdns):
        lb_ids = []

        for fqdn in lb_fqdns:
            l3_response = requests.get(
                cls.api_path.balancer_root(f"?fqdn__exact={fqdn}"), headers=cls.HEADERS, verify=False
            )

            if l3_response.status_code == http.HTTPStatus.OK:
                lb_id = l3_response.json()["objects"][0]["id"]
                lb_ids.append(lb_id)
            else:
                raise CouldNotGetBalancerID(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

        return lb_ids

    @classmethod
    def add_lbs_to_abc_service(cls, abc, lb_ids):
        l3_response = requests.post(
            cls.api_path.abc_by_id(abc) + "/assignlbs",
            headers=cls.HEADERS,
            data="&".join([f"lb={_id}" for _id in lb_ids]),
            verify=False,
        )

        if l3_response.json()["result"] != cls.L3_OK_STATUS:
            raise CouldNotAddBalancerToABCError(f"L3 response: Code {l3_response.status_code}, Body {l3_response.text}")

    @classmethod
    def config_deployment_status(cls, svc_id, cfg_id):
        l3_response = requests.get(cls.api_path.service_config_by_id(svc_id, cfg_id), headers=cls.HEADERS, verify=False)

        return l3_response.json()

    @classmethod
    def get_vs_config(cls, vs_id):
        l3_response = requests.get(cls.api_path.vs_config_by_id(vs_id), headers=cls.HEADERS, verify=False)

        return l3_response.json()

    # TODO: Don't delete, can be used for API integ tests
    #     def get_svc_vss(self):
    #         fqdn_query = f"?fqdn__exact={self.svc_fqdn}"
    #
    #         l3_response = requests.get(
    #             self.L3_TEST_API + self.SERVICE_PATH + fqdn_query,
    #             headers=self.HEADERS,
    #             verify=False
    #         )
    #
    #         if l3_response.json()["objects"]:
    #             return l3_response.json()["objects"][0]["id"]

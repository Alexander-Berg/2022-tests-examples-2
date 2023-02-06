import os
import sys
import pytest
import requests
import http
import copy
import json
import urllib3
from datetime import datetime
from netaddr import IPNetwork
from itertools import chain

from netaddr import valid_ipv6

# TODO: remove after TRAFFIC-12138 has complete
# from rtnmgr2.tests.helpers import RSD
from rtnmgr2.tests.helpers import RSD_YANDEX_TEST
from rtnmgr2.tests.helpers import RSD_VIEWS_TEST as RSD
from rtnmgr2.core.config import ConfigGlobal
from rtnmgr2.operations.helpers import v4_ips, v4_mappings


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.verify = False

TEST_INSTANCE_NAME = "integ_test"
YANDEX_TEST_INSTANCE_NAME = "yandex_integ_test"

CONFIG_CLOBAL = ConfigGlobal()
OAUTH_HEADER = {"Authorization": f"OAuth {CONFIG_CLOBAL.auth_config.rtnmgr_robot_token}"}

FULL_HEADERS = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"OAuth {CONFIG_CLOBAL.auth_config.rtnmgr_robot_token}",
}

LB_TEST = "test-lb.yndx.net"
LB_UNKNOWN = "unknown-lb.yndx.net"
LB_APPLIED_STATUS = {"MODIFIED": True, "LB_APPLIED": True, "NS_APPLIED": False, "NEW_MAPPINGS": True}
NS_APPLIED_STATUS = {"MODIFIED": False, "LB_APPLIED": True, "NS_APPLIED": True, "NEW_MAPPINGS": True}


@pytest.fixture()
def http_headers():
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    headers.update(**OAUTH_HEADER)

    return headers


@pytest.fixture()
def rsd():
    """
    Create a copy of RSD to avoid unexpected mutations during test
    """
    return copy.deepcopy(RSD)


@pytest.fixture()
def upload_rsd():
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    headers.update(**OAUTH_HEADER)

    session.post(DOCUMENT_URL + "/force", headers=headers, data=json.dumps(copy.deepcopy(RSD)))


def upload_modified_rsd(rsd):
    return session.post(DOCUMENT_URL + "/force", headers=FULL_HEADERS, data=json.dumps(rsd))


def upload_modified_rsd_instances(rsd, instance=TEST_INSTANCE_NAME):
    return session.post(get_document_url(instance) + "/force", headers=FULL_HEADERS, data=json.dumps(rsd))


if CONFIG_CLOBAL.app_config.ssl_termination or os.environ.get("RTNMGR_ENV") != "development":
    BASE_URL = CONFIG_CLOBAL.app_config.url.replace("http", "https")
else:
    BASE_URL = CONFIG_CLOBAL.app_config.url


DOCUMENT_URL = (
    BASE_URL + ":" + str(CONFIG_CLOBAL.app_config.port) + "/api/v2.0/document/instances/" + TEST_INSTANCE_NAME
)


ROTATION_URL = (
    BASE_URL + ":" + str(CONFIG_CLOBAL.app_config.port) + "/api/v2.0/rotation/instances/" + TEST_INSTANCE_NAME
)


def get_document_url(instance_name):
    return BASE_URL + ":" + str(CONFIG_CLOBAL.app_config.port) + "/api/v2.0/document/instances/" + instance_name


def get_rotation_url(instance_name):
    return BASE_URL + ":" + str(CONFIG_CLOBAL.app_config.port) + "/api/v2.0/rotation/instances/" + instance_name

def _get_views_domains(views_data):
    found_domains = set()

    for _, ips in views_data.items():
        found_domains |= set(ips)

    return found_domains

class TestsRotationInstance:
    @pytest.mark.parametrize(
        "rsd_instance,instance",
        [(copy.deepcopy(RSD), TEST_INSTANCE_NAME), (copy.deepcopy(RSD_YANDEX_TEST), YANDEX_TEST_INSTANCE_NAME)],
    )
    def test_create_instance_success_case(self, rsd_instance, instance, http_headers):
        session.delete(get_document_url(instance), headers=OAUTH_HEADER)
        rtnmgr_response = session.post(
            get_document_url(instance) + "/force", headers=http_headers, data=json.dumps(rsd_instance)
        )

        assert rtnmgr_response.status_code == http.HTTPStatus.OK

    def test_list_instances(self, rsd, http_headers):
        instances = session.get(DOCUMENT_URL.replace("/" + TEST_INSTANCE_NAME, ""), headers=OAUTH_HEADER).json()[
            "data"
        ]["instances"]

        assert TEST_INSTANCE_NAME in instances

    def test_collect_instance_success_case(self, rsd, http_headers):
        collected_rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        del collected_rsd["version_id"]
        del rsd["version_id"]

        assert collected_rsd == rsd

    @pytest.mark.parametrize(
        "rsd,instance",
        [(copy.deepcopy(RSD), TEST_INSTANCE_NAME), (copy.deepcopy(RSD_YANDEX_TEST), YANDEX_TEST_INSTANCE_NAME)],
    )
    def test_update_rsd_correct_version_id(self, rsd, instance, http_headers):
        rsd["version_id"] = session.get(get_rotation_url(instance) + "/version_id", headers=OAUTH_HEADER).json()[
            "data"
        ]["version_id"]

        rtnmgr_response = session.post(get_document_url(instance), headers=http_headers, data=json.dumps(rsd))

        assert rtnmgr_response.status_code == http.HTTPStatus.OK

    def test_update_rsd_wrong_version_id(self, rsd, http_headers):
        rsd["version_id"] = 0
        rtnmgr_response = session.post(DOCUMENT_URL, headers=http_headers, data=json.dumps(rsd))

        assert rtnmgr_response.status_code == http.HTTPStatus.BAD_REQUEST

    def test_update_rotation_state(self, rsd, http_headers):
        rotation_state = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_state"]

        rtnmgr_response = session.put(
            DOCUMENT_URL + "/rotation-state", headers=http_headers, data=json.dumps(rotation_state)
        )
        assert rtnmgr_response.status_code == http.HTTPStatus.OK

    def test_update_settings(self, rsd, http_headers):
        settings = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["settings"]

        rtnmgr_response = session.put(DOCUMENT_URL + "/settings", headers=http_headers, data=json.dumps(settings))

        assert rtnmgr_response.status_code == http.HTTPStatus.OK

    def test_update_rotation_providers(self, rsd, http_headers):
        providers = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["providers"]

        rtnmgr_response = session.put(DOCUMENT_URL + "/providers", headers=http_headers, data=json.dumps(providers))

        assert rtnmgr_response.status_code == http.HTTPStatus.OK


class TestsRotationCycle:
    def submit_rotation(self, instance=TEST_INSTANCE_NAME):
        return session.put(get_rotation_url(instance) + "/submit", headers=FULL_HEADERS, data=json.dumps({}))

    @pytest.mark.parametrize(
        "rsd,instance",
        [(copy.deepcopy(RSD), TEST_INSTANCE_NAME), (copy.deepcopy(RSD_YANDEX_TEST), YANDEX_TEST_INSTANCE_NAME)],
    )
    def test_submit_rotation_success_case(self, rsd, instance, http_headers, upload_rsd):
        session.post(get_document_url(instance) + "/force", headers=http_headers, data=json.dumps(rsd))

        rsd_before_submit = session.get(get_document_url(instance), headers=OAUTH_HEADER).json()["data"]
        rtnmgr_response = session.put(get_rotation_url(instance) + "/submit", headers=http_headers, data=json.dumps({}))
        rsd_after_submit = session.get(get_document_url(instance), headers=OAUTH_HEADER).json()["data"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        # test rotation_id increased
        assert rsd_before_submit["rotation_id"] == rsd_after_submit["rotation_id"] - 1
        # test version_id increased
        assert datetime.fromtimestamp(rsd_before_submit["version_id"] / 1000000.0) < datetime.fromtimestamp(
            rsd_after_submit["version_id"] / 1000000.0
        )

        for pool, pool_data in rsd_before_submit["rotation_state"].items():
            for provider, mapping in pool_data["mappings"].get("current", {}).items():
                if rsd_after_submit["providers"][provider]["settings"]["rotate"]:
                    mapping != rsd_after_submit["rotation_state"][pool]["mappings"].get("current", {}).get(provider)
                else:
                    mapping == rsd_after_submit["rotation_state"][pool]["mappings"].get("current", {}).get(provider)

    @pytest.mark.parametrize(
        "rsd,instance,provider1,provider2,balancers",
        [
            (copy.deepcopy(RSD), TEST_INSTANCE_NAME, "cogent", "telia", ["kiv-lb1.yndx.net", "rad-lb1.yndx.net"]),
            (copy.deepcopy(RSD_YANDEX_TEST), YANDEX_TEST_INSTANCE_NAME, "pool1", "pool2", []),
        ],
    )
    def test_ips_allocated_to_not_rotating_pool_after_submiting_rotation(
        self, rsd, instance, provider1, provider2, balancers, http_headers, upload_rsd
    ):
        test_pool1 = {
            "test-pool1": {
                "views": {},
                "int_ips": {provider1: ["5.45.202.178", "5.45.202.179"], provider2: ["5.45.202.180", "5.45.202.181"]},
                "mappings": {},
                "settings": {"rotate": False, "ns_tracking": False},
                "lb_current_ext_ips": [],
                "ns_current_ext_ips": [],
            }
        }

        test_pool2 = {
            "test-pool2": {
                "views": {},
                "int_ips": {provider1: ["5.45.202.75"], provider2: ["5.45.202.74"]},
                "mappings": {
                    "static": {
                        provider1: {"5.45.202.75": {"ext_ip": "80.239.201.6", "timestamp": ""}},
                        provider2: {"5.45.202.74": {"ext_ip": "149.5.244.26", "timestamp": ""}},
                    },
                },
                "settings": {"rotate": False, "ns_tracking": True},
                "lb_current_ext_ips": [],
                "ns_current_ext_ips": [],
            }
        }

        rsd["rotation_state"].update(**test_pool1, **test_pool2)
        rsd["settings"]["ns_update"]["enabled"] = False

        session.delete(get_document_url(instance) + "/history/keep_records/0", headers=OAUTH_HEADER)
        self.do_rotation_cycles(
            rsd,
            number_of_cycles=2,
            http_headers=http_headers,
            instance=instance,
            lb_update_disabled=True if instance == YANDEX_TEST_INSTANCE_NAME else False,
            balancers=balancers,
        )

        rotation_history = session.get(get_document_url(instance) + "/history", headers=OAUTH_HEADER).json()["data"]

        assert rotation_history[0]["rsd"]["rotation_state"]["test-pool1"]["mappings"]["current"] and (
            rotation_history[0]["rsd"]["rotation_state"]["test-pool1"]["mappings"]["current"]
            == rotation_history[1]["rsd"]["rotation_state"]["test-pool1"]["mappings"]["current"]
        )

        assert not rotation_history[0]["rsd"]["rotation_state"]["test-pool2"]["mappings"].get("current") and (
            rotation_history[0]["rsd"]["rotation_state"]["test-pool2"]["mappings"].get("current")
            == rotation_history[1]["rsd"]["rotation_state"]["test-pool2"]["mappings"].get("current")
        )
        session.delete(get_document_url(instance) + "/history/keep_records/0", headers=OAUTH_HEADER)

    def test_lb_collect_mappings_lb_ignore(self):
        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = [LB_TEST]

        upload_modified_rsd(rsd)
        self.submit_rotation()
        response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER)

        assert response.status_code == http.HTTPStatus.FORBIDDEN
        assert response.json()["code"] == http.HTTPStatus.FORBIDDEN

    def test_lb_collect_mappings(self):
        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]

        upload_modified_rsd(rsd)
        self.submit_rotation()

        mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER)

        assert mappings_response.json()["data"]

        # assuming no mappings in history
        no_mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/last-applied", headers=OAUTH_HEADER)

        assert no_mappings_response.status_code == http.HTTPStatus.NOT_FOUND

        no_mappings_response = session.get(ROTATION_URL + "/lb/" + LB_UNKNOWN + "/new", headers=OAUTH_HEADER)

        assert no_mappings_response.status_code == http.HTTPStatus.NOT_FOUND

    def test_lb_update_time_exceed(self):
        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["settings"]["lb_update"]["lb_update_expected_time_minutes"] = 0.00001

        upload_modified_rsd(rsd)
        self.submit_rotation()

        no_mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER)
        assert no_mappings_response.status_code == http.HTTPStatus.FORBIDDEN

    def test_lb_collect_new_mappings_success(self):
        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["test"]["lb_apply_intention"] = []

        upload_modified_rsd(rsd)
        self.submit_rotation()

        mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER)
        rsd_response = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rotation_state = rsd_response["rotation_state"]

        ext_ips_for_lb = set()
        ext_ips_in_rsd = set()

        mappings_json = mappings_response.json()["data"]
        del mappings_json["rotation_id"]

        for _, mappings in mappings_json.items():
            for mapping in mappings:
                ext_ips_for_lb.add(mapping["ext_ip"])

        for _, pool_data in rotation_state.items():
            for _, mappings in pool_data["mappings"].items():
                if pool_data["int_ips"].get("telia") and mappings:
                    for _, ext_ip in mappings["telia"].items():
                        ext_ips_in_rsd.add(ext_ip["ext_ip"])

        assert mappings_response.status_code == http.HTTPStatus.OK
        assert ext_ips_for_lb == ext_ips_in_rsd

    def test_lb_send_confirmation_about_applied_mappings_at_new_mappings_stage(self, http_headers):
        """
        'http://rtnmgr-test.tt.yandex-team.ru:8888/api/v2.0/rotation/instances/integ_test/lb/test-lb.yndx.net/3'
        """
        expected_status_after_lb_applied = {
            "MODIFIED": True,
            "LB_APPLIED": True,
            "NS_APPLIED": False,
            "NEW_MAPPINGS": True,
        }

        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["test"]["lb_apply_intention"] = []
        rsd["providers"]["cogent"]["lb_apply_intention"] = []

        upload_modified_rsd(rsd)
        self.submit_rotation()

        mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER).json()["data"]

        rotation_id = str(mappings_response["rotation_id"])
        del mappings_response["rotation_id"]
        rtnmgr_response = session.put(
            ROTATION_URL + "/lb/" + LB_TEST + "/" + rotation_id,
            headers=http_headers,
            data=json.dumps(mappings_response),
        )

        rsd_updated = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_updated["status"] == expected_status_after_lb_applied
        assert rsd_updated["providers"]["telia"]["lb_apply_actual"] == [LB_TEST]

    def test_lb_send_confirmation_about_applied_mappings_at_lb_applied_stage(self, http_headers):
        """
        1. Check that new mappings are available for balancers that are already in "lb_apply_actual" list
        when LB_APPLIED in not set
        2. Check that new mappings are available for balancers when LB_APPLIED flag set but NS_APPLIED not yet set
        """
        expected_status_after_new_mapping_request = {
            "MODIFIED": True,
            "LB_APPLIED": True,
            "NS_APPLIED": False,
            "NEW_MAPPINGS": True,
        }

        new_mappings_status = {"MODIFIED": True, "LB_APPLIED": False, "NS_APPLIED": False, "NEW_MAPPINGS": True}

        fake_lb = "fake_lb"

        rsd = copy.deepcopy(RSD)
        rsd["status"] = new_mappings_status
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST, fake_lb]
        rsd["providers"]["test"]["lb_apply_intention"] = []
        rsd["providers"]["cogent"]["lb_apply_intention"] = []
        upload_modified_rsd(rsd)

        # make API add LB_TEST to lb_apply_actual list
        mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER).json()["data"]
        rotation_id = str(mappings_response["rotation_id"])
        del mappings_response["rotation_id"]

        session.put(
            ROTATION_URL + "/lb/" + LB_TEST + "/" + rotation_id,
            headers=http_headers,
            data=json.dumps(mappings_response),
        )

        # try to collect mappings again
        mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER).json()["data"]
        rotation_id = str(mappings_response["rotation_id"])
        del mappings_response["rotation_id"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/lb/" + LB_TEST + "/" + rotation_id,
            headers=http_headers,
            data=json.dumps(mappings_response),
        )

        rsd_updated = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_updated["status"] == new_mappings_status
        assert rsd_updated["providers"]["telia"]["lb_apply_actual"] == [LB_TEST]

        # make API add fake_lb to lb_apply_actual list
        mappings_response = session.get(ROTATION_URL + "/lb/" + fake_lb + "/new", headers=OAUTH_HEADER).json()["data"]
        rotation_id = str(mappings_response["rotation_id"])
        del mappings_response["rotation_id"]

        session.put(
            ROTATION_URL + "/lb/" + fake_lb + "/" + rotation_id,
            headers=http_headers,
            data=json.dumps(mappings_response),
        )

        # try to collect mappings again
        mappings_response = session.get(ROTATION_URL + "/lb/" + fake_lb + "/new", headers=OAUTH_HEADER).json()["data"]
        rotation_id = str(mappings_response["rotation_id"])
        del mappings_response["rotation_id"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/lb/" + fake_lb + "/" + rotation_id,
            headers=http_headers,
            data=json.dumps(mappings_response),
        )

        rsd_updated = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_updated["status"] == expected_status_after_new_mapping_request
        assert rsd_updated["providers"]["telia"]["lb_apply_actual"] == [LB_TEST, fake_lb]

    def test_lb_new_mapping_collection_and_confirmation_at_not_allowed_stages(self, http_headers):
        """
        'http://rtnmgr-test.tt.yandex-team.ru:8888/api/v2.0/rotation/instances/integ_test/lb/test-lb.yndx.net/3'
        """
        clear_flags_status = {"MODIFIED": False, "LB_APPLIED": False, "NS_APPLIED": False, "NEW_MAPPINGS": False}

        rsd = copy.deepcopy(RSD)

        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["test"]["lb_apply_intention"] = []
        rsd["providers"]["cogent"]["lb_apply_intention"] = []

        rsd["providers"]["telia"]["lb_apply_actual"] = [LB_TEST]

        for rsd_flags in [NS_APPLIED_STATUS, clear_flags_status]:
            rsd["status"] = NS_APPLIED_STATUS
            upload_modified_rsd(rsd)

            mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER)
            rtnmgr_response = session.put(
                ROTATION_URL + "/lb/" + LB_TEST + "/" + str(rsd["rotation_id"]),
                headers=http_headers,
            )
            rsd_flags = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["status"]

            assert mappings_response.status_code == mappings_response.json()["code"] == http.HTTPStatus.LOCKED
            assert rtnmgr_response.status_code == rtnmgr_response.json()["code"] == http.HTTPStatus.LOCKED
            assert rsd_flags == NS_APPLIED_STATUS

    def test_lb_collect_new_mappings_unknown_lb_name(self, http_headers):
        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["test"]["lb_apply_intention"] = []

        upload_modified_rsd(rsd)
        self.submit_rotation()
        rotation_id = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"]

        get_lb_update_response = session.get(ROTATION_URL + "/lb/unknown.yandex.net" + "/new", headers=OAUTH_HEADER)
        report_lb_update_response = session.put(
            ROTATION_URL + "/lb/unknown.yandex.net/" + str(rotation_id), headers=http_headers, data=json.dumps({})
        )

        assert get_lb_update_response.status_code == http.HTTPStatus.NOT_FOUND
        assert report_lb_update_response.status_code == http.HTTPStatus.NOT_FOUND

    def test_correct_rotation_status_lb_not_applied(self, http_headers):
        lb_apply_intention = [LB_TEST + "1", LB_TEST + "2"]
        lb_apply_actual = set()

        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["telia"]["lb_apply_intention"] = lb_apply_intention
        rsd["providers"]["test"]["lb_apply_intention"] = lb_apply_intention
        rsd["providers"]["cogent"]["lb_apply_intention"] = []

        upload_modified_rsd(rsd)
        self.submit_rotation()

        # no lbs have applied mappings
        assert set(session.get(ROTATION_URL + "/status", headers=OAUTH_HEADER).json()["data"]["lb_not_applied"]) == set(
            lb_apply_intention
        )

        for lb in lb_apply_intention:
            lb_apply_actual.add(lb)
            mappings_response = session.get(ROTATION_URL + "/lb/" + lb + "/new", headers=OAUTH_HEADER).json()["data"]

            rotation_id = str(mappings_response["rotation_id"])
            del mappings_response["rotation_id"]
            session.put(
                ROTATION_URL + "/lb/" + lb + "/" + rotation_id, headers=http_headers, data=json.dumps(mappings_response)
            )

            # lbs apply mappings one by one
            assert session.get(ROTATION_URL + "/status", headers=OAUTH_HEADER).json()["data"]["lb_not_applied"] == list(
                set(lb_apply_intention) - lb_apply_actual
            )

    def test_correct_rotation_status_lb_ignored_and_different_lbs_between_providers(self, http_headers):
        lb_apply_intention = ["lb_telia", "lb_cogent", LB_TEST]
        lb_ignore = ["lb_telia_2"]
        lb_apply_actual = set()

        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = lb_ignore
        rsd["providers"]["telia"]["lb_apply_intention"] = ["lb_telia", LB_TEST] + lb_ignore
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST] + lb_ignore
        rsd["providers"]["cogent"]["lb_apply_intention"] = ["lb_cogent", LB_TEST]

        upload_modified_rsd(rsd)
        self.submit_rotation()

        # no lbs have applied mappings
        assert set(session.get(ROTATION_URL + "/status", headers=OAUTH_HEADER).json()["data"]["lb_not_applied"]) == set(
            lb_apply_intention
        )

        for lb in lb_apply_intention + lb_ignore:
            lb_apply_actual.add(lb)
            mappings_response = session.get(ROTATION_URL + "/lb/" + lb + "/new", headers=OAUTH_HEADER).json()["data"]

            if mappings_response:
                rotation_id = str(mappings_response["rotation_id"])
                del mappings_response["rotation_id"]

            if rotation_id:
                session.put(
                    ROTATION_URL + "/lb/" + lb + "/" + rotation_id,
                    headers=http_headers,
                    data=json.dumps(mappings_response),
                )

            # lbs apply mappings one by one
            assert set(
                session.get(ROTATION_URL + "/status", headers=OAUTH_HEADER).json()["data"]["lb_not_applied"]
            ) == set(lb_apply_intention) - (set(lb_apply_actual) | set(lb_ignore))

    @pytest.mark.parametrize(
        "rsd,instance",
        [(copy.deepcopy(RSD), TEST_INSTANCE_NAME), (copy.deepcopy(RSD_YANDEX_TEST), YANDEX_TEST_INSTANCE_NAME)],
    )
    def test_ns_get_update(self, rsd, instance, http_headers):
        """"""
        session.delete(get_document_url(instance) + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd = copy.deepcopy(RSD)
        rsd["status"] = LB_APPLIED_STATUS
        upload_modified_rsd_instances(rsd, instance)

        mappings_response = session.get(get_rotation_url(instance) + "/ns/mappings", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()

        rsd = session.get(get_document_url(instance), headers=OAUTH_HEADER).json()["data"]
        rotation_state = rsd["rotation_state"]

        ext_ips_in_rsd = set()
        domains_in_rsd = set()

        for _, pool_data in rotation_state.items():
            for stage, mappings in pool_data["mappings"].items():
                if mappings and stage != "previous":
                    for provider, mapping in mappings.items():
                        if rsd["providers"][provider]["settings"]["show_to_ns"]:
                            domains_in_rsd |= set(pool_data.get("domains", [])) or _get_views_domains(
                                pool_data["views"]
                            )
                            for _, ext_ip in mapping.items():
                                ext_ips_in_rsd.add(ext_ip["ext_ip"])

        ext_ips_in_ns_update = set()
        domains_in_ns_update = set()

        for domain, mappings in mappings_response_data.items():
            ext_ips_in_ns_update |= set(mappings)
            domains_in_ns_update.add(domain)

        # IPv6 address may be filtered from NS update TRAFFIC-11777
        diff = ext_ips_in_rsd - ext_ips_in_ns_update
        assert not diff or all(valid_ipv6(ip) for ip in diff)
        if not diff:
            assert ext_ips_in_ns_update == ext_ips_in_rsd
        else:
            assert all(valid_ipv6(ip) for ip in diff)

        assert domains_in_ns_update == domains_in_rsd
        assert mappings_response.status_code == http.HTTPStatus.OK

    def test_ns_worker_not_updated_in_time_and_rotation_disabled(self, http_headers):
        rsd = copy.deepcopy(RSD)

        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["settings"]["ns_update"]["enabled"] = False
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["cogent"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["test"]["settings"]["rotate"] = True

        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        self.do_rotation_cycles(rsd, number_of_cycles=2, balancers=[LB_TEST], http_headers=http_headers)

        mappings_for_ns_before_lb_applied_stage = session.get(ROTATION_URL + "/ns/mappings", headers=OAUTH_HEADER)
        assert mappings_for_ns_before_lb_applied_stage.status_code == http.HTTPStatus.OK

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd["settings"]["ns_update"]["ns_update_expected_time_minutes"] = 0.000001
        rsd["settings"]["ns_update"]["enabled"] = True
        upload_modified_rsd(rsd)

        self.submit_rotation()
        mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/new", headers=OAUTH_HEADER).json()

        if not mappings_response["data"]:
            raise Exception(f"Could get lb mappings. data {mappings_response}")

        rotation_id = str(mappings_response["data"]["rotation_id"])
        del mappings_response["data"]["rotation_id"]

        session.put(
            ROTATION_URL + "/lb/" + LB_TEST + "/" + rotation_id,
            headers=http_headers,
            data=json.dumps(mappings_response["data"]),
        )

        mappings_for_ns_on_lb_applied_stage = session.get(ROTATION_URL + "/ns/mappings", headers=OAUTH_HEADER)
        assert mappings_for_ns_on_lb_applied_stage.status_code == http.HTTPStatus.OK

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        assert mappings_response.status_code == http.HTTPStatus.OK

        rtnmgr_response_disabled_rotation = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response.json()["data"]["rotation_id"]),
            headers=http_headers,
            data=json.dumps({}),
        )
        assert rtnmgr_response_disabled_rotation.status_code == http.HTTPStatus.FORBIDDEN

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        assert mappings_response.status_code == http.HTTPStatus.LOCKED

        mappings_for_ns_when_rotation_disabled = session.get(ROTATION_URL + "/ns/mappings", headers=OAUTH_HEADER)
        assert mappings_for_ns_when_rotation_disabled.status_code == http.HTTPStatus.OK
        assert (
            mappings_for_ns_before_lb_applied_stage.json()
            == mappings_for_ns_when_rotation_disabled.json()
            != mappings_for_ns_on_lb_applied_stage.json()
        )

    def test_ns_worker_get_update(self, http_headers):
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd["status"] = LB_APPLIED_STATUS
        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rotation_state = rsd["rotation_state"]

        ext_ips_in_rsd = set()
        domains_in_rsd = set()

        for _, pool_data in rotation_state.items():
            for stage, mappings in pool_data["mappings"].items():
                if mappings and stage != "previous":
                    for provider, mapping in mappings.items():
                        if rsd["providers"][provider]["settings"]["show_to_ns"]:
                            domains_in_rsd |= set(pool_data.get("domains", [])) or _get_views_domains(
                                pool_data["views"]
                            )
                            for _, ext_ip in mapping.items():
                                ext_ips_in_rsd.add(ext_ip["ext_ip"])

        ext_ips_in_ns_update = set()
        domains_in_ns_update = set()

        for domain, mappings in mappings_response_data["mappings"].items():
            ext_ips_in_ns_update |= set(mappings)
            domains_in_ns_update.add(domain)

        assert ext_ips_in_ns_update == ext_ips_in_rsd
        assert domains_in_ns_update == domains_in_rsd
        assert mappings_response.status_code == http.HTTPStatus.OK

    def test_ns_worker_update_report_incorrect_mappings(self, http_headers):
        rsd = copy.deepcopy(RSD)

        rsd["status"] = LB_APPLIED_STATUS
        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps({}),
        )

        assert rtnmgr_response.status_code == http.HTTPStatus.BAD_REQUEST

    def test_mappings_missing_in_ns_added_in_error_field(self, http_headers):
        rsd = copy.deepcopy(RSD)

        rsd["status"] = LB_APPLIED_STATUS
        rsd["settings"]["ns_update"]["ns_update_expected_time_minutes"] = 0.000001

        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]
        rotation_id = mappings_response_data["rotation_id"]
        mappings = mappings_response_data["mappings"]

        missing_mappings = {}

        [
            (missing_mappings.update(**{domain: ips}), mappings.pop(domain))
            for domain, ips in mappings.copy().items()
            if len(missing_mappings) < 3
        ]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(rotation_id), headers=http_headers, data=json.dumps(mappings)
        )

        assert (
            session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["error"]["data"]["missing_mappings"]
            == missing_mappings
        )
        assert (
            session.get(ROTATION_URL + "/status-monitor", headers=OAUTH_HEADER).json()["data"]["ns_not_applied"]
            == missing_mappings
        )
        assert rtnmgr_response.status_code == http.HTTPStatus.FORBIDDEN

        # Check that error has cleared after reset rotation states
        # (which is a regular procedure after NS mapping syncronization error)
        session.put(ROTATION_URL + "/reset", headers=OAUTH_HEADER).json()
        assert session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["error"]["data"] is None
        assert (
            session.get(ROTATION_URL + "/status-monitor", headers=OAUTH_HEADER).json()["data"]["ns_not_applied"] == {}
        )

    def test_error_field_updated_only_in_affected_instance(self, http_headers):
        session.delete(DOCUMENT_URL + "/history", headers=OAUTH_HEADER)
        session.delete(get_document_url(YANDEX_TEST_INSTANCE_NAME) + "/history", headers=OAUTH_HEADER)

        rsd = copy.deepcopy(RSD)

        rsd["status"] = LB_APPLIED_STATUS
        rsd["settings"]["ns_update"]["ns_update_expected_time_minutes"] = 0.000001

        upload_modified_rsd(rsd)
        upload_modified_rsd_instances(copy.deepcopy(RSD_YANDEX_TEST), YANDEX_TEST_INSTANCE_NAME)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]
        rotation_id = mappings_response_data["rotation_id"]
        mappings = mappings_response_data["mappings"]

        missing_mappings = {}

        [
            (missing_mappings.update(**{domain: ips}), mappings.pop(domain))
            for domain, ips in mappings.copy().items()
            if len(missing_mappings) < 3
        ]

        session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(rotation_id), headers=http_headers, data=json.dumps(mappings)
        )

        error_expected = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["error"]["data"]
        error_not_expected = session.get(get_document_url(YANDEX_TEST_INSTANCE_NAME), headers=OAUTH_HEADER).json()[
            "data"
        ]["error"]["data"]

        assert error_expected
        assert not error_not_expected

        # Check that error has cleared after reset rotation states
        # (which is a regular procedure after NS mapping syncronization error)

    def test_ns_worker_send_update_status_success(self, http_headers):
        rsd = copy.deepcopy(RSD)
        rsd["status"] = LB_APPLIED_STATUS
        rsd["rotation_id"] += 1
        upload_modified_rsd(rsd)

        session.delete(DOCUMENT_URL + "/history", headers=OAUTH_HEADER)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps(mappings_response_data["mappings"]),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_flags == NS_APPLIED_STATUS

    @pytest.mark.parametrize(
        "rsd_instance,instance,lb_update_disabled",
        [
            (copy.deepcopy(RSD), TEST_INSTANCE_NAME, False),
            (copy.deepcopy(RSD_YANDEX_TEST), YANDEX_TEST_INSTANCE_NAME, True),
        ],
    )
    def test_previous_mappings_taken_from_history(self, rsd_instance, instance, lb_update_disabled, http_headers):
        session.delete(get_document_url(instance) + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd_instance["settings"]["lb_update"]["lb_ignore"] = []
        rsd_instance["settings"]["ns_update"]["enabled"] = False

        if rsd_instance["providers"].get("telia"):
            rsd_instance["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]

        if rsd_instance["providers"].get("cogent"):
            rsd_instance["providers"]["cogent"]["lb_apply_intention"] = [LB_TEST]

        if rsd_instance["providers"].get("test"):
            rsd_instance["providers"]["test"]["settings"]["rotate"] = True
        rsd_instance["settings"]["lb_update"]["lb_update_expected_time_minutes"] = 1

        rsd_instance["rotation_id"] = (
            session.get(get_document_url(instance), headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1
        )
        # session.delete(get_document_url(instance) + "/history/keep_records/0", headers=OAUTH_HEADER)
        self.do_rotation_cycles(
            rsd_instance,
            number_of_cycles=2,
            balancers=[LB_TEST],
            http_headers=http_headers,
            lb_update_disabled=lb_update_disabled,
            instance=instance,
        )

        # to avoid saving rsd to history
        rsd_before_submit = session.get(get_document_url(instance), headers=OAUTH_HEADER).json()["data"]
        rsd_before_submit["settings"]["lb_update"]["enabled"] = True

        if instance == YANDEX_TEST_INSTANCE_NAME:
            rsd_before_submit["providers"]["pool1"]["lb_apply_intention"] = [LB_TEST]

        upload_modified_rsd_instances(rsd_before_submit, instance=instance)

        self.submit_rotation(instance=instance)

        rsd_from_history = session.get(get_document_url(instance) + "/history", headers=OAUTH_HEADER).json()["data"][0][
            "rsd"
        ]
        rsd_after_submit = session.get(get_document_url(instance), headers=OAUTH_HEADER).json()["data"]

        for pool, pool_data in rsd_from_history["rotation_state"].items():
            if pool_data["settings"]["rotate"]:

                assert (
                    pool_data["mappings"]["current"] == rsd_after_submit["rotation_state"][pool]["mappings"]["previous"]
                )
            else:
                assert (
                    pool_data["mappings"]["current"] == rsd_after_submit["rotation_state"][pool]["mappings"]["current"]
                )

    def test_ips_exhausted_for_network(self, http_headers):
        rsd = copy.deepcopy(RSD)
        rsd["rotation_id"] += 1
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["cogent"]["lb_apply_intention"] = [LB_TEST]
        rsd["settings"]["ns_update"]["enabled"] = False
        # clear allocated IPs
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd["settings"]["mappings_update"]["external_ip_cooldown_hours"] = 0.0001
        upload_modified_rsd(rsd)
        self.submit_rotation()

        small_network = "80.239.201.0/25"
        rsd["settings"]["mappings_update"]["external_ip_cooldown_hours"] = 1000
        rsd["providers"]["telia"]["networks"] = [small_network]

        amount_of_ips_needed_for_provider = 0
        amount_of_available_ips = 0
        amount_of_reserved_ips = 0
        # amount_of_reserved_not_rotating_ips = 0

        for _, pool_data in rsd["rotation_state"].items():
            ips = pool_data["int_ips"].get("telia", [])
            if pool_data["settings"]["rotate"]:
                amount_of_ips_needed_for_provider += max(len(ips) // 2, 1) if ips else 0
                # amount_of_reserved_ips += max(len(ips) // 2, 1) if ips else 0
                amount_of_reserved_ips += len(pool_data["mappings"].get("previous", {}).get("telia", {}))
            else:
                amount_of_reserved_ips += len(pool_data["mappings"].get("current", {}).get("telia", {}))
                amount_of_reserved_ips += len(pool_data["mappings"].get("previous", {}).get("telia", {}))
                # amount_of_reserved_not_rotating_ips += len(ips)

            amount_of_reserved_ips += len(pool_data["mappings"].get("static", {}).get("telia", {}))

        amount_of_available_ips += (
            IPNetwork(small_network).size
            - amount_of_reserved_ips
            - amount_of_ips_needed_for_provider
            # - amount_of_reserved_not_rotating_ips
        )

        expected_amount_of_rotation_cycles = amount_of_available_ips // amount_of_ips_needed_for_provider

        # expected_amount_of_rotation_cycles + 1 - because the history is empty and the first cycle is free
        self.do_rotation_cycles(rsd, number_of_cycles=expected_amount_of_rotation_cycles + 1, http_headers=http_headers)
        assert self.submit_rotation().status_code == http.HTTPStatus.CONFLICT

    def test_update_rsd_rotation_id_lower_than_rotation_id_in_history(self, rsd, http_headers):
        rsd["version_id"] = session.get(ROTATION_URL + "/version_id", headers=OAUTH_HEADER).json()["data"]["version_id"]
        rsd["rotation_id"] = 0

        rtnmgr_response = session.post(DOCUMENT_URL, headers=http_headers, data=json.dumps(rsd))

        assert rtnmgr_response.status_code == http.HTTPStatus.BAD_REQUEST

    @pytest.mark.parametrize(
        "in_ips,static_mappings,expected_status_code",
        [
            (
                # Valid case: 4 int ips for dynamic mapings, 2 int_ips for static mappings
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108", "5.45.202.109", "5.45.202.110"],
                {
                    "cogent": {
                        "5.45.202.109": {"ext_ip": "80.239.201.22", "timestamp": ""},
                        "5.45.202.110": {"ext_ip": "80.239.201.23", "timestamp": ""},
                    }
                },
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 4 int ips for dynamic mapings, 1 int_ip for static mappings
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108", "5.45.202.109"],
                {
                    "cogent": {"5.45.202.109": {"ext_ip": "80.239.201.22", "timestamp": ""}},
                },
                http.HTTPStatus.OK,
            ),
            (
                # Invalid case: 5 int ips for dynamic mapings - rtnmgr doesn't know how many mappings to create
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108", "5.45.202.109", "5.45.202.110"],
                {"cogent": {"5.45.202.109": {"ext_ip": "80.239.201.22", "timestamp": ""}}},
                http.HTTPStatus.BAD_REQUEST,
            ),
            (
                # Invalid case: 5 int ips for dynamic mapings - rtnmgr doesn't know how many mappings to create
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108", "5.45.202.109"],
                None,
                http.HTTPStatus.BAD_REQUEST,
            ),
            (
                # Valid case: 4 int ips for dynamic mapings - 2 mappings per rotation
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Invalid case: 3 int ips for dynamic mapings - rtnmgr doesn't know how many mappings to create
                ["5.45.202.158", "5.45.202.159", "5.45.202.157"],
                None,
                http.HTTPStatus.BAD_REQUEST,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings (one mapping per rotation), 1 int_ip for static mappings
                ["5.45.202.158", "5.45.202.159", "5.45.202.109"],
                {"cogent": {"5.45.202.109": {"ext_ip": "80.239.201.22", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Invalid case: 3 int ips for dynamic mapings, static mapping has unknown IP
                ["5.45.202.158", "5.45.202.159", "5.45.202.109"],
                {"cogent": {"5.45.202.110": {"ext_ip": "80.239.201.22", "timestamp": ""}}},
                http.HTTPStatus.BAD_REQUEST,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings (one mapping per rotation)
                ["5.45.202.158", "5.45.202.159"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                # and 1 int_ip for static mappings
                ["5.45.202.158", "5.45.202.159"],
                {"cogent": {"5.45.202.159": {"ext_ip": "80.239.201.22", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                ["5.45.202.158"],
                None,
                http.HTTPStatus.OK,
            ),
        ],
    )
    def test_internal_ips_not_overlapping_between_rotations(
        self, in_ips, static_mappings, expected_status_code, http_headers
    ):
        """
        Check that int IPs change every rotation
        """
        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["cogent"]["lb_apply_intention"] = [LB_TEST]
        rsd["settings"]["ns_update"]["enabled"] = False
        rsd["settings"]["mappings_update"]["external_ip_cooldown_hours"] = 0.001
        rsd["rotation_state"]["market.yandex.ua"]["int_ips"]["telia"] = ["5.45.202.167"]
        rsd["rotation_state"]["market.yandex.ua"]["int_ips"]["cogent"] = in_ips

        if static_mappings:
            rsd["rotation_state"]["market.yandex.ua"]["mappings"]["static"] = static_mappings

        rsd["rotation_id"] = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1

        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        if expected_status_code >= http.HTTPStatus.BAD_REQUEST:
            with pytest.raises(Exception) as excinfo:
                self.do_rotation_cycles(rsd, number_of_cycles=2, http_headers=http_headers)
                self.submit_rotation()

            assert expected_status_code == excinfo._excinfo[1].args[1]
            return

        self.do_rotation_cycles(rsd, number_of_cycles=2, http_headers=http_headers)
        self.submit_rotation()
        current_rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_state"]
        rsd_from_history = session.get(DOCUMENT_URL + "/history", headers=OAUTH_HEADER).json()["data"][:2]

        rsd_from_history_recent = rsd_from_history[0]["rsd"]["rotation_state"]
        rsd_from_history_before_recent = rsd_from_history[1]["rsd"]["rotation_state"]

        for pool, data in current_rsd.items():
            for provider, mappings in data["mappings"]["current"].items():
                if len(mappings) > 1:
                    current_int_ips = set(int_ip for int_ip, _ in mappings.items())
                    static_int_ips = set(
                        int_ip
                        for int_ip, _ in v4_mappings(current_rsd[pool]["mappings"].get("static", {}))
                        .get(provider, {})
                        .items()
                    )
                    previous_int_ips = set(
                        int_ip
                        for int_ip, _ in current_rsd[pool]["mappings"].get("previous", {}).get(provider, {}).items()
                    )

                    unexpected_matched_mapping = current_int_ips & (static_int_ips | previous_int_ips)
                    assert not unexpected_matched_mapping

                for int_ip, _ in mappings.items():
                    unexpected_matched_mapping = rsd_from_history_recent[pool]["mappings"]["current"][provider].get(
                        int_ip
                    ) or v4_mappings(current_rsd[pool]["mappings"].get("static", {})).get(provider, {}).get(int_ip)
                    if (
                        len(current_rsd[pool]["int_ips"][provider])
                        - len(v4_mappings(current_rsd[pool]["mappings"].get("static", {})).get(provider, {}))
                    ) > 1 and current_rsd[pool]["settings"]["rotate"]:
                        assert not unexpected_matched_mapping
                    else:
                        # If only 1 IP for provider, there is no int IP to replace
                        assert unexpected_matched_mapping

        for pool, data in rsd_from_history_recent.items():
            for provider, mappings in data["mappings"]["current"].items():
                if len(mappings) > 1:
                    current_int_ips = set(int_ip for int_ip, _ in mappings.items())
                    static_int_ips = set(
                        int_ip
                        for int_ip, _ in v4_mappings(rsd_from_history_recent[pool]["mappings"].get("static", {}))
                        .get(provider, {})
                        .items()
                    )
                    previous_int_ips = set(
                        int_ip
                        for int_ip, _ in rsd_from_history_recent[pool]["mappings"]
                        .get("previous", {})
                        .get(provider, {})
                        .items()
                    )

                    unexpected_matched_mapping = current_int_ips & (static_int_ips | previous_int_ips)
                    assert not unexpected_matched_mapping
                for int_ip, _ in mappings.items():
                    unexpected_matched_mapping = rsd_from_history_before_recent[pool]["mappings"]["current"][
                        provider
                    ].get(int_ip)
                    if (
                        len(current_rsd[pool]["int_ips"][provider])
                        - len(v4_mappings(current_rsd[pool]["mappings"].get("static", {})).get(provider, {}))
                    ) > 1 and current_rsd[pool]["settings"]["rotate"]:
                        assert not unexpected_matched_mapping
                    else:
                        # If only 1 IP for provider, there is no int IP to replace
                        assert unexpected_matched_mapping

    @pytest.mark.parametrize(
        "int_ips,static_mappings,expected_status_code",
        [
            (
                # Valid case: 4 int ips for dynamic mapings
                ["0.0.0.1", "0.0.0.2", "0.0.0.3", "0.0.0.4"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings
                ["0.0.0.1", "0.0.0.2"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Invalid case: 5 int ips for dynamic mapings - rtnmgr doesn't know how many mappings to create
                ["0.0.0.1", "0.0.0.2", "0.0.0.3", "0.0.0.4", "0.0.0.5"],
                None,
                http.HTTPStatus.BAD_REQUEST,
            ),
            (
                # Invalid case: 3 int ips for dynamic mapings - rtnmgr doesn't know how many mappings to create
                ["0.0.0.1", "0.0.0.2", "0.0.0.3"],
                None,
                http.HTTPStatus.BAD_REQUEST,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings (one mapping per rotation), 1 int_ip for static mappings
                ["0.0.0.1", "0.0.0.2", "0.0.0.100"],
                {"pool1": {"0.0.0.100": {"ext_ip": "5.255.255.77", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Invalid case: 3 int ips for dynamic mapings, static mapping has unknown IP
                ["0.0.0.1", "0.0.0.2", "0.0.0.100"],
                {"pool1": {"0.0.0.101": {"ext_ip": "5.255.255.77", "timestamp": ""}}},
                http.HTTPStatus.BAD_REQUEST,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                # and 1 int_ip for static mappings
                ["0.0.0.1", "0.0.0.2"],
                {"pool1": {"0.0.0.2": {"ext_ip": "5.255.255.77", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                ["0.0.0.1"],
                None,
                http.HTTPStatus.OK,
            ),
        ],
    )
    def test_internal_ips_not_overlapping_between_rotations_instance_yandex(
        self, int_ips, static_mappings, expected_status_code, http_headers
    ):
        """
        Check that int IPs change every rotation
        """
        rsd = copy.deepcopy(RSD_YANDEX_TEST)
        rsd["settings"]["mappings_update"]["external_ip_cooldown_hours"] = 0.00001
        rsd["rotation_state"]["yandex.ru"]["int_ips"]["pool1"] = int_ips

        if static_mappings:
            rsd["rotation_state"]["yandex.ru"]["mappings"]["static"] = static_mappings

        rsd["rotation_id"] = (
            session.get(get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME), headers=OAUTH_HEADER).json()["data"][
                "rotation_id"
            ]
            + 1
        )

        session.delete(
            get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME) + "/history/keep_records/0", headers=OAUTH_HEADER
        )

        if expected_status_code >= http.HTTPStatus.BAD_REQUEST:
            with pytest.raises(Exception) as excinfo:
                self.do_rotation_cycles(
                    rsd,
                    number_of_cycles=2,
                    http_headers=http_headers,
                    instance=YANDEX_TEST_INSTANCE_NAME,
                    lb_update_disabled=True,
                )
                self.submit_rotation(instance=YANDEX_TEST_INSTANCE_NAME)

            assert expected_status_code == excinfo._excinfo[1].args[1]
            return

        self.do_rotation_cycles(
            rsd,
            number_of_cycles=2,
            http_headers=http_headers,
            instance=YANDEX_TEST_INSTANCE_NAME,
            lb_update_disabled=True,
        )

        self.submit_rotation(instance=YANDEX_TEST_INSTANCE_NAME)

        current_rsd = session.get(
            get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME), headers=OAUTH_HEADER
        ).json()["data"]["rotation_state"]

        rsd_from_history = session.get(
            get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME) + "/history", headers=OAUTH_HEADER
        ).json()["data"][:3]

        rsd_from_history_first = rsd_from_history[0]["rsd"]["rotation_state"]

        assert current_rsd == rsd_from_history_first

        rsd_from_history_second = rsd_from_history[1]["rsd"]["rotation_state"]
        rsd_from_history_third = rsd_from_history[2]["rsd"]["rotation_state"]

        for pool, data in current_rsd.items():
            for provider, mappings in data["mappings"]["current"].items():
                if len(mappings) > 1:
                    current_int_ips = set(int_ip for int_ip, _ in mappings.items())
                    static_int_ips = set(
                        int_ip
                        for int_ip, _ in v4_mappings(current_rsd[pool]["mappings"].get("static", {}))
                        .get(provider, {})
                        .items()
                    )
                    previous_int_ips = set(
                        int_ip
                        for int_ip, _ in current_rsd[pool]["mappings"].get("previous", {}).get(provider, {}).items()
                    )

                    unexpected_matched_mapping = current_int_ips & (static_int_ips | previous_int_ips)
                    assert not unexpected_matched_mapping

                for int_ip, _ in mappings.items():
                    unexpected_matched_mapping = rsd_from_history_second[pool]["mappings"]["current"][provider].get(
                        int_ip
                    ) or v4_mappings(current_rsd[pool]["mappings"].get("static", {})).get(provider, {}).get(int_ip)
                    if (
                        len(current_rsd[pool]["int_ips"][provider])
                        - len(v4_mappings(current_rsd[pool]["mappings"].get("static", {})).get(provider, {}))
                    ) > 1 and current_rsd[pool]["settings"]["rotate"]:
                        assert not unexpected_matched_mapping
                    else:
                        # If only 1 IP for provider, there is no int IP to replace
                        assert unexpected_matched_mapping

        for pool, data in rsd_from_history_second.items():
            for provider, mappings in data["mappings"]["current"].items():
                if len(mappings) > 1:
                    current_int_ips = set(int_ip for int_ip, _ in mappings.items())
                    static_int_ips = set(
                        int_ip
                        for int_ip, _ in v4_mappings(rsd_from_history_second[pool]["mappings"].get("static", {}))
                        .get(provider, {})
                        .items()
                    )
                    previous_int_ips = set(
                        int_ip
                        for int_ip, _ in rsd_from_history_second[pool]["mappings"]
                        .get("previous", {})
                        .get(provider, {})
                        .items()
                    )

                    unexpected_matched_mapping = current_int_ips & (static_int_ips | previous_int_ips)
                    assert not unexpected_matched_mapping
                for int_ip, _ in mappings.items():
                    unexpected_matched_mapping = rsd_from_history_third[pool]["mappings"]["current"][provider].get(
                        int_ip
                    )
                    if (
                        len(current_rsd[pool]["int_ips"][provider])
                        - len(v4_mappings(current_rsd[pool]["mappings"].get("static", {})).get(provider, {}))
                    ) > 1 and current_rsd[pool]["settings"]["rotate"]:
                        assert not unexpected_matched_mapping
                    else:
                        # If only 1 IP for provider, there is no int IP to replace
                        assert unexpected_matched_mapping

    @pytest.mark.parametrize(
        "in_ips,static_mappings,expected_status_code",
        [
            (
                # Valid case: 4 int ips for dynamic mapings, 2 int_ips for static mappings
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108", "5.45.202.109", "5.45.202.110"],
                {
                    "cogent": {
                        "5.45.202.109": {"ext_ip": "80.239.201.22", "timestamp": ""},
                        "5.45.202.110": {"ext_ip": "80.239.201.23", "timestamp": ""},
                    }
                },
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 4 int ips for dynamic mapings, 1 int_ip for static mappings
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108", "5.45.202.109"],
                {
                    "cogent": {"5.45.202.109": {"ext_ip": "80.239.201.22", "timestamp": ""}},
                },
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 4 int ips for dynamic mapings - 2 mappings per rotation
                ["5.45.202.158", "5.45.202.159", "5.45.202.157", "5.45.202.108"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings (one mapping per rotation), 1 int_ip for static mappings
                ["5.45.202.158", "5.45.202.159", "5.45.202.109"],
                {"cogent": {"5.45.202.109": {"ext_ip": "80.239.201.22", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings (one mapping per rotation)
                ["5.45.202.158", "5.45.202.159"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                # and 1 int_ip for static mappings
                ["5.45.202.158", "5.45.202.159"],
                {"cogent": {"5.45.202.159": {"ext_ip": "80.239.201.22", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                ["5.45.202.158"],
                None,
                http.HTTPStatus.OK,
            ),
        ],
    )
    def test_external_ips_not_overlapping_between_rotations(
        self, in_ips, static_mappings, expected_status_code, http_headers
    ):
        """
        Check that int IPs change every rotation
        """
        pools_to_exclude = ["proxy.yandex.ua", "static.yandex.net", "front.kp.yandex.net"]
        current_ips_in_use = []
        previous_ips_in_use = []
        static_ips_in_use = []
        not_rotating_ips = []

        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["telia"]["lb_apply_intention"] = [LB_TEST]
        rsd["providers"]["cogent"]["lb_apply_intention"] = [LB_TEST]
        rsd["settings"]["ns_update"]["enabled"] = False
        rsd["settings"]["mappings_update"]["external_ip_cooldown_hours"] = 0.0001
        rsd["rotation_id"] = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1
        self.do_rotation_cycles(rsd, number_of_cycles=1, http_headers=http_headers)
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd["settings"]["mappings_update"]["external_ip_cooldown_hours"] = 1

        for pool in pools_to_exclude:
            del rsd["rotation_state"][pool]

        rsd["rotation_state"]["market.yandex.ua"]["int_ips"]["telia"] = ["5.45.202.167"]
        rsd["rotation_state"]["market.yandex.ua"]["int_ips"]["cogent"] = in_ips
        rsd["rotation_id"] = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1

        if static_mappings:
            rsd["rotation_state"]["market.yandex.ua"]["mappings"]["static"] = static_mappings

        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        self.do_rotation_cycles(rsd, number_of_cycles=3, http_headers=http_headers)
        self.submit_rotation()
        current_rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_from_history = session.get(DOCUMENT_URL + "/history", headers=OAUTH_HEADER).json()["data"][:2]

        rsd_from_history_recent = rsd_from_history[0]["rsd"]
        rsd_from_history_before_recent = rsd_from_history[1]["rsd"]

        for evaluated_rsd in [current_rsd, rsd_from_history_recent, rsd_from_history_before_recent]:
            for _, pool_state in evaluated_rsd["rotation_state"].items():
                current_mappings = pool_state["mappings"].get("current", {}).items()
                for provider_name, mappings in current_mappings:
                    if evaluated_rsd["providers"][provider_name]["settings"]["rotate"]:
                        for _, mapping in mappings.items():
                            current_ips_in_use.append(mapping["ext_ip"])
                    else:
                        for _, mapping in mappings.items():
                            not_rotating_ips.append(mapping["ext_ip"])
                previous_mappings = pool_state["mappings"].get("previous", {}).items()
                for provider_name, mappings in previous_mappings:
                    # if evaluated_rsd["providers"][provider_name]["settings"]["rotate"]:
                    for _, mapping in mappings.items():
                        previous_ips_in_use.append(mapping["ext_ip"])
                static_mappings = pool_state["mappings"].get("static", {}).items()
                for provider_name, mappings in static_mappings:
                    # if evaluated_rsd["providers"][provider_name]["settings"]["rotate"]:
                    for _, mapping in mappings.items():
                        static_ips_in_use.append(mapping["ext_ip"])

            # check that current IPs not duplicating
            assert len(current_ips_in_use) == len(set(current_ips_in_use))
            # check that previous IPs not duplicating
            assert len(previous_ips_in_use) == len(set(previous_ips_in_use))
            # check that current IPs not overlapping with previous IPs and static IPs
            assert not set(current_ips_in_use) & (set(previous_ips_in_use) | set(static_ips_in_use))
            # check that not rotating pool's IPs not overlapping with previous IPs and static IPs
            assert not set(not_rotating_ips) - (set(previous_ips_in_use) | set(static_ips_in_use))

            current_ips_in_use = []
            previous_ips_in_use = []
            static_ips_in_use = []
            not_rotating_ips = []

    @pytest.mark.parametrize(
        "int_ips,static_mappings,expected_status_code",
        [
            (
                # Valid case: 4 int ips for dynamic mapings
                ["0.0.0.1", "0.0.0.2", "0.0.0.3", "0.0.0.4"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings
                ["0.0.0.1", "0.0.0.2"],
                None,
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 2 int ips for dynamic mapings (one mapping per rotation), 1 int_ip for static mappings
                ["0.0.0.1", "0.0.0.2", "0.0.0.100"],
                {"pool1": {"0.0.0.100": {"ext_ip": "5.255.255.77", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                # and 1 int_ip for static mappings
                ["0.0.0.1", "0.0.0.2"],
                {"pool1": {"0.0.0.2": {"ext_ip": "5.255.255.77", "timestamp": ""}}},
                http.HTTPStatus.OK,
            ),
            (
                # Valid case: 1 int ips for dynamic mapings (the same mapping will be generated)
                ["0.0.0.1"],
                None,
                http.HTTPStatus.OK,
            ),
        ],
    )
    def test_external_ips_not_overlapping_between_rotations_instance_yandex(
        self, int_ips, static_mappings, expected_status_code, http_headers
    ):
        """
        Check that int IPs change every rotation
        """
        current_ips_in_use = []
        previous_ips_in_use = []
        static_ips_in_use = []
        not_rotating_ips = []

        rsd = copy.deepcopy(RSD_YANDEX_TEST)
        rsd["settings"]["mappings_update"]["external_ip_cooldown_hours"] = 0.0001
        rsd["rotation_state"]["yandex.ru"]["int_ips"]["pool1"] = int_ips

        if static_mappings:
            rsd["rotation_state"]["yandex.ru"]["mappings"]["static"] = static_mappings

        rsd["rotation_id"] = (
            session.get(get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME), headers=OAUTH_HEADER).json()["data"][
                "rotation_id"
            ]
            + 1
        )

        session.delete(
            get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME) + "/history/keep_records/0", headers=OAUTH_HEADER
        )

        self.do_rotation_cycles(
            rsd,
            number_of_cycles=3,
            http_headers=http_headers,
            instance=YANDEX_TEST_INSTANCE_NAME,
            lb_update_disabled=True,
        )
        current_rsd = session.get(
            get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME), headers=OAUTH_HEADER
        ).json()["data"]

        rsd_from_history = session.get(
            get_document_url(instance_name=YANDEX_TEST_INSTANCE_NAME) + "/history", headers=OAUTH_HEADER
        ).json()["data"][:3]

        rsd_from_history_first = rsd_from_history[0]["rsd"]

        assert current_rsd == rsd_from_history_first

        rsd_from_history_second = rsd_from_history[1]["rsd"]
        rsd_from_history_third = rsd_from_history[1]["rsd"]

        for evaluated_rsd in [current_rsd, rsd_from_history_second, rsd_from_history_third]:
            for _, pool_state in evaluated_rsd["rotation_state"].items():
                current_mappings = pool_state["mappings"].get("current", {}).items()
                for provider_name, mappings in current_mappings:
                    if evaluated_rsd["providers"][provider_name]["settings"]["rotate"]:
                        for _, mapping in mappings.items():
                            current_ips_in_use.append(mapping["ext_ip"])
                    else:
                        for _, mapping in mappings.items():
                            not_rotating_ips.append(mapping["ext_ip"])
                previous_mappings = pool_state["mappings"].get("previous", {}).items()
                for provider_name, mappings in previous_mappings:
                    # if evaluated_rsd["providers"][provider_name]["settings"]["rotate"]:
                    for _, mapping in mappings.items():
                        previous_ips_in_use.append(mapping["ext_ip"])
                static_mappings = pool_state["mappings"].get("static", {}).items()
                for provider_name, mappings in static_mappings:
                    # if evaluated_rsd["providers"][provider_name]["settings"]["rotate"]:
                    for _, mapping in mappings.items():
                        static_ips_in_use.append(mapping["ext_ip"])

            # check that current IPs not duplicating
            assert len(current_ips_in_use) == len(set(current_ips_in_use))
            # check that previous IPs not duplicating
            assert len(previous_ips_in_use) == len(set(previous_ips_in_use))
            # check that current IPs not overlapping with previous IPs and static IPs
            assert not set(current_ips_in_use) & (set(previous_ips_in_use) | set(static_ips_in_use))
            # check that not rotating pool's IPs not overlapping with previous IPs and static IPs
            assert not set(not_rotating_ips) - (set(previous_ips_in_use) | set(static_ips_in_use))

            current_ips_in_use = []
            previous_ips_in_use = []
            static_ips_in_use = []
            not_rotating_ips = []

    def test_lb_collect_last_applied(self, http_headers):
        """
        Test LB last-applied mappings interface
        """
        fake_lb = "fake_lb"

        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST, fake_lb]
        rsd["settings"]["ns_update"]["enabled"] = False
        rsd["providers"]["telia"]["lb_apply_intention"] = []
        rsd["providers"]["cogent"]["lb_apply_intention"] = []

        # test fake_lb is included in RSD, and wants to collect last applied mappings
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        self.do_rotation_cycles(
            rsd, number_of_cycles=1, http_headers=http_headers, balancers=rsd["providers"]["test"]["lb_apply_intention"]
        )
        mappings_response = session.get(ROTATION_URL + "/lb/" + LB_TEST + "/last-applied", headers=OAUTH_HEADER)

        assert mappings_response.status_code == http.HTTPStatus.OK
        assert mappings_response.json().get("data", {}).get("current")

        # test fake_lb not included in RSD, but wants to collect mappings
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST]
        rsd["rotation_id"] = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1
        self.do_rotation_cycles(rsd, number_of_cycles=1, http_headers=http_headers)
        no_mappings_response = session.get(ROTATION_URL + "/lb/" + fake_lb + "/last-applied", headers=OAUTH_HEADER)
        assert no_mappings_response.status_code == http.HTTPStatus.NOT_FOUND

        # test fake_lb was ignored when rotation had completed
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST, fake_lb]
        rsd["settings"]["lb_update"]["lb_ignore"] = [fake_lb]
        rsd["rotation_id"] = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1
        self.do_rotation_cycles(
            rsd, number_of_cycles=1, http_headers=http_headers, balancers=rsd["providers"]["test"]["lb_apply_intention"]
        )
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["rotation_id"] += 1
        upload_modified_rsd(rsd)
        no_mappings_response = session.get(ROTATION_URL + "/lb/" + fake_lb + "/last-applied", headers=OAUTH_HEADER)
        assert no_mappings_response.status_code == http.HTTPStatus.NOT_FOUND

        # test fake_lb is ignored now
        rsd["providers"]["test"]["lb_apply_intention"] = [LB_TEST, fake_lb]
        rsd["settings"]["lb_update"]["lb_ignore"] = []
        rsd["rotation_id"] = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1
        self.do_rotation_cycles(
            rsd, number_of_cycles=1, http_headers=http_headers, balancers=rsd["providers"]["test"]["lb_apply_intention"]
        )
        rsd["settings"]["lb_update"]["lb_ignore"] = [fake_lb]
        rsd["rotation_id"] = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]["rotation_id"] + 1
        upload_modified_rsd(rsd)
        no_mappings_response = session.get(ROTATION_URL + "/lb/" + fake_lb + "/last-applied", headers=OAUTH_HEADER)
        assert no_mappings_response.status_code == http.HTTPStatus.FORBIDDEN

    def test_clear_except_specific_ids(self, rsd, http_headers):
        current_history = session.get(DOCUMENT_URL + "/history/short", headers=OAUTH_HEADER).json()["data"]
        current_history = sorted(current_history, key=lambda item: item["rotation_id"], reverse=True)
        oldest_id = current_history.pop()["rotation_id"]
        keep_ids = [_id["rotation_id"] for _id in current_history]
        keep_ids_query = "&".join([f"keep_id={_id}" for _id in keep_ids])

        delete_response = session.delete(DOCUMENT_URL + "/history?" + keep_ids_query, headers=OAUTH_HEADER)
        cleared_history = session.get(DOCUMENT_URL + "/history", headers=OAUTH_HEADER).json()["data"]

        for history_record in cleared_history:
            kept_rotation_id = history_record["rotation_id"]
            assert kept_rotation_id in keep_ids
            assert kept_rotation_id != oldest_id
        assert delete_response.status_code == http.HTTPStatus.OK

    def test_cannot_clear_all_history_using_wildcard(self, rsd, http_headers):
        current_history = session.get(DOCUMENT_URL + "/history/short", headers=OAUTH_HEADER).json()["data"]
        current_history = sorted(current_history, key=lambda item: item["rotation_id"])
        recent_id = current_history.pop()["rotation_id"]

        delete_response = session.delete(DOCUMENT_URL + "/history", headers=OAUTH_HEADER)
        cleared_history = session.get(DOCUMENT_URL + "/history", headers=OAUTH_HEADER).json()["data"]

        for history_record in cleared_history:
            kept_rotation_id = history_record["rotation_id"]
            assert kept_rotation_id == recent_id
        assert delete_response.status_code == http.HTTPStatus.OK

    def test_clear_all_history(self, rsd, http_headers):
        delete_response = session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        cleared_history = session.get(DOCUMENT_URL + "/history", headers=OAUTH_HEADER).json()["data"]

        assert delete_response.status_code == http.HTTPStatus.OK
        assert cleared_history == []

    def test_delete_instance_success_case(self, rsd, http_headers):
        rsd = copy.deepcopy(RSD)
        rsd["rotation_id"] += 1
        upload_modified_rsd(rsd)
        rtnmgr_response = session.delete(DOCUMENT_URL, headers=OAUTH_HEADER)
        assert rtnmgr_response.status_code == http.HTTPStatus.OK

        rsd_request = session.get(DOCUMENT_URL, headers=OAUTH_HEADER)
        assert rsd_request.status_code == http.HTTPStatus.NOT_FOUND

    def do_rotation_cycles(
        self,
        rsd,
        number_of_cycles=2,
        http_headers=http_headers,
        balancers=[LB_TEST],
        lb_update_disabled=False,
        instance=TEST_INSTANCE_NAME,
    ):
        upload_result = upload_modified_rsd_instances(rsd, instance=instance)
        if upload_result.status_code != http.HTTPStatus.OK:
            raise Exception(
                f"Could not upload rsd. code {upload_result.status_code} data {upload_result.json()}",
                upload_result.status_code,
                upload_result.json(),
            )

        for _ in range(number_of_cycles):
            submit_result = self.submit_rotation(instance=instance)

            if submit_result.status_code != http.HTTPStatus.OK:
                raise Exception(
                    f"Could not submit rotation. code {submit_result.status_code} data {submit_result.json()}",
                    submit_result.status_code,
                    submit_result.json(),
                )

            if lb_update_disabled:
                continue

            for balancer in balancers:
                if balancer in rsd["settings"]["lb_update"]["lb_ignore"]:
                    continue
                mappings_response = session.get(ROTATION_URL + "/lb/" + balancer + "/new", headers=OAUTH_HEADER).json()

                if not mappings_response["data"]:
                    raise Exception(f"Could get lb mappings. data {mappings_response}", None, mappings_response.json())

                rotation_id = str(mappings_response["data"]["rotation_id"])
                del mappings_response["data"]["rotation_id"]

                session.put(
                    ROTATION_URL + "/lb/" + balancer + "/" + rotation_id,
                    headers=http_headers,
                    data=json.dumps(mappings_response["data"]),
                )


class TestsNSTrackingPerPool:
    def add_ns_tracking_option_in_rsd(self, rsd, track_ns_applied=True):
        for state in rsd["rotation_state"].values():
            state["settings"]["ns_tracking"] = track_ns_applied

        return rsd

    def customize_rsd_ns_tracking_fields(self, rsd, max_pools_to_set=sys.maxsize, max_applied=sys.maxsize):
        rsd["status"] = LB_APPLIED_STATUS
        rsd["rotation_id"] += 1

        rsd = self.add_ns_tracking_option_in_rsd(rsd, track_ns_applied=False)

        providers_hiding_mappings = set()

        for provider_name, provider_data in rsd["providers"].items():
            if not provider_data["settings"]["show_to_ns"]:
                providers_hiding_mappings.add(provider_name)

        ns_mappings = {}
        ns_mappings_not_applied = {}

        for pool_state in rsd["rotation_state"].values():
            i = len(ns_mappings.keys()) + len(ns_mappings_not_applied.keys())

            if i == max_pools_to_set:
                break

            pool_state["settings"]["ns_tracking"] = True

            ext_ips_for_pool = []

            current_mappings = pool_state["mappings"].get("current", {}).items()
            static_mappings = pool_state["mappings"].get("static", {}).items()

            for provider_name, rsd_mappings in chain(current_mappings, static_mappings):
                if provider_name in providers_hiding_mappings:
                    continue

                ext_ips_for_pool.extend([ext_ip["ext_ip"] for (int_ip, ext_ip) in rsd_mappings.items()])
                for domain in pool_state.get("domains") or _get_views_domains(pool_state["views"]):

                    if i < max_applied:
                        ns_mappings[domain] = ext_ips_for_pool
                    else:
                        ns_mappings_not_applied[domain] = ext_ips_for_pool

        return rsd, ns_mappings, ns_mappings_not_applied

    def test_ns_worker_send_update_status_success_tracking_disabled_for_all_pools(self, http_headers):
        """
        Set ignore tracking flag on every pool and check that worker NS_APPLIED succeeds for any worker request
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd["status"] = LB_APPLIED_STATUS
        rsd["rotation_id"] += 1
        upload_modified_rsd(self.add_ns_tracking_option_in_rsd(rsd, track_ns_applied=False))

        session.delete(DOCUMENT_URL + "/history", headers=OAUTH_HEADER)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps({}),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_flags == NS_APPLIED_STATUS

    def test_ns_worker_send_update_status_success_tracking_enabled_for_one_pool(self, http_headers):
        """
        Set NS tracking for one pool. Send mappings for that pool in NS worker update. Check successful result
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd, ns_mappings, _ = self.customize_rsd_ns_tracking_fields(rsd, max_pools_to_set=1)

        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps(ns_mappings),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_flags == NS_APPLIED_STATUS

    def test_ns_worker_send_update_status_failure_tracking_enabled_for_one_pool(self, http_headers):
        """
        Set NS tracking for one pool. Don't send mappings for that pool in NS worker update. Check failure result
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd, _, _ = self.customize_rsd_ns_tracking_fields(rsd)

        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps({}),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.BAD_REQUEST
        assert rsd_flags == LB_APPLIED_STATUS

    def test_ns_worker_send_update_status_success_tracking_enabled_for_multiple_pools(self, http_headers):
        """
        Set NS tracking for multiple pools. Send mappings for those pools in NS worker update. Check successful result
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd, ns_mappings, _ = self.customize_rsd_ns_tracking_fields(rsd, max_pools_to_set=3)

        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps(ns_mappings),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_flags == NS_APPLIED_STATUS

    def test_ns_worker_send_update_status_failure_tracking_enabled_for_multiple_pools(self, http_headers):
        """
        Set NS tracking for multiple pools. Send mappings for some pools in NS worker update. Check failure result
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd, ns_mappings, _ = self.customize_rsd_ns_tracking_fields(rsd, max_pools_to_set=3, max_applied=1)

        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps(ns_mappings),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.BAD_REQUEST
        assert rsd_flags == LB_APPLIED_STATUS

    def test_ns_worker_send_update_status_failure_tracking_enabled_for_all_pools(self, http_headers):
        """
        Set NS tracking for all pools. Send mappings for some (not all) pools in NS worker update. Check failure result
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd, ns_mappings, _ = self.customize_rsd_ns_tracking_fields(rsd, max_applied=1)

        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps(ns_mappings),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.BAD_REQUEST
        assert rsd_flags == LB_APPLIED_STATUS

    def test_ns_worker_send_update_status_success_tracking_enabled_for_all_pools(self, http_headers):
        """
        Set NS tracking for all pools. Send mappings for all pools in NS worker update. Check successful result
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)
        rsd = copy.deepcopy(RSD)

        rsd, ns_mappings, _ = self.customize_rsd_ns_tracking_fields(rsd)

        upload_modified_rsd(rsd)

        mappings_response = session.get(ROTATION_URL + "/ns/mappings/worker", headers=OAUTH_HEADER)
        mappings_response_data = mappings_response.json()["data"]

        rtnmgr_response = session.put(
            ROTATION_URL + "/ns/mappings/worker/" + str(mappings_response_data["rotation_id"]),
            headers=http_headers,
            data=json.dumps(ns_mappings),
        )

        rsd = session.get(DOCUMENT_URL, headers=OAUTH_HEADER).json()["data"]
        rsd_flags = rsd["status"]

        assert rtnmgr_response.status_code == http.HTTPStatus.OK
        assert rsd_flags == NS_APPLIED_STATUS


class TestsValidations:
    def test_hide_everything_from_ns_validation(self, http_headers):
        """
        Check that we cannot save rsd/settings if NS update is enabled and all providers hide mappings
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd = copy.deepcopy(RSD)
        rsd["settings"]["ns_update"]["enabled"] = True

        upload_result = upload_modified_rsd(rsd)

        for _, provider_settings in rsd["providers"].items():
            provider_settings["settings"]["show_to_ns"] = False

        rsd["version_id"] = session.get(
            get_rotation_url(TEST_INSTANCE_NAME) + "/version_id", headers=OAUTH_HEADER
        ).json()["data"]["version_id"]

        # Trying to upload full document with invalid settings
        upload_result = session.post(DOCUMENT_URL, headers=FULL_HEADERS, data=json.dumps(rsd))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

        # Trying to upload invalid providers settings
        upload_result = session.put(
            DOCUMENT_URL + "/providers", headers=FULL_HEADERS, data=json.dumps(rsd["providers"])
        )

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

        # Trying uploading valid document to prepare upload invalid settings assertion
        rsd["settings"]["ns_update"]["enabled"] = False

        upload_result = session.post(DOCUMENT_URL, headers=FULL_HEADERS, data=json.dumps(rsd))

        assert upload_result.status_code == http.HTTPStatus.OK

        # upload invalid settings
        rsd["settings"]["ns_update"]["enabled"] = True

        upload_result = session.put(DOCUMENT_URL + "/settings", headers=FULL_HEADERS, data=json.dumps(rsd["settings"]))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

    def test_exclude_all_balancers(self, http_headers):
        """
        Check that we cannot save rsd/settings if LB update is enabled and all balancers are in lb_ignore list
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd = copy.deepcopy(RSD)
        rsd["settings"]["lb_update"]["enabled"] = True

        upload_result = upload_modified_rsd(rsd)

        lbs = set()

        for _, provider_settings in rsd["providers"].items():
            for lb in provider_settings["lb_apply_intention"]:
                lbs.add(lb)

        rsd["settings"]["lb_update"]["lb_ignore"] = list(lbs)

        rsd["version_id"] = session.get(
            get_rotation_url(TEST_INSTANCE_NAME) + "/version_id", headers=OAUTH_HEADER
        ).json()["data"]["version_id"]

        # Trying to upload full document with invalid settings
        upload_result = session.post(DOCUMENT_URL, headers=FULL_HEADERS, data=json.dumps(rsd))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

        # Trying to upload invalid providers settings
        upload_result = session.put(DOCUMENT_URL + "/settings", headers=FULL_HEADERS, data=json.dumps(rsd["settings"]))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

        # Trying uploading valid document to prepare upload invalid settings assertion
        rsd["settings"]["lb_update"]["enabled"] = False

        upload_result = session.post(DOCUMENT_URL, headers=FULL_HEADERS, data=json.dumps(rsd))

        assert upload_result.status_code == http.HTTPStatus.OK

        # upload invalid settings
        rsd["settings"]["lb_update"]["enabled"] = True

        for _, provider_settings in rsd["providers"].items():
            provider_settings["lb_apply_intention"] = []

        upload_result = session.put(DOCUMENT_URL + "/providers", headers=FULL_HEADERS, data=json.dumps(rsd["settings"]))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

    def test_internal_ips_overlapping(self, http_headers):
        """
        Check that we cannot save rsd/settings if int IPs overlap after RSD editing
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd = copy.deepcopy(RSD)

        overlapping_ip = None
        break_loop = False

        for _, pool_settings in rsd["rotation_state"].items():
            for provider_name, _int_ips in pool_settings["int_ips"].items():
                if overlapping_ip:
                    pool_settings["int_ips"][provider_name].append(overlapping_ip)
                    break_loop = True
                    break
                else:
                    for ip in _int_ips:
                        overlapping_ip = ip
                        break
            if break_loop:
                break

        upload_result = upload_modified_rsd(rsd)

        rsd["version_id"] = session.get(
            get_rotation_url(TEST_INSTANCE_NAME) + "/version_id", headers=OAUTH_HEADER
        ).json()["data"]["version_id"]

        # Trying to upload full document with invalid settings
        upload_result = session.post(DOCUMENT_URL, headers=FULL_HEADERS, data=json.dumps(rsd))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

        # Trying to upload invalid providers settings
        upload_result = session.put(
            DOCUMENT_URL + "/rotation-state", headers=FULL_HEADERS, data=json.dumps(rsd["rotation_state"])
        )

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

    def test_external_ips_overlapping_between_dynamic_and_static_mappings(self, http_headers):
        """
        Check that we cannot save rsd/settings if ext IPs overlap after RSD editing between dynamic and static mappings
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd = copy.deepcopy(RSD)

        dynamic_ext_ip = None
        break_loop = False

        for _, pool_settings in rsd["rotation_state"].items():
            for mapping_type, provider_mappings in pool_settings["mappings"].items():
                for _, mappings in provider_mappings.items():
                    for _, ext_ip in mappings.items():
                        if mapping_type == "current":
                            dynamic_ext_ip = ext_ip["ext_ip"]
                            break
                        else:
                            ext_ip["ext_ip"] = dynamic_ext_ip
                            break_loop = True
                            break
                if break_loop:
                    break
            if break_loop:
                break

        upload_result = upload_modified_rsd(rsd)

        rsd["version_id"] = session.get(
            get_rotation_url(TEST_INSTANCE_NAME) + "/version_id", headers=OAUTH_HEADER
        ).json()["data"]["version_id"]

        # Trying to upload full document with invalid settings
        upload_result = session.post(DOCUMENT_URL, headers=FULL_HEADERS, data=json.dumps(rsd))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

        # Trying to upload invalid providers settings
        upload_result = session.put(
            DOCUMENT_URL + "/rotation-state", headers=FULL_HEADERS, data=json.dumps(rsd["rotation_state"])
        )

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

    def test_external_ips_overlapping_between_static_mappings(self, http_headers):
        """
        Check that we cannot save rsd/settings if ext IPs overlap after RSD editing between static mappings
        """
        session.delete(DOCUMENT_URL + "/history/keep_records/0", headers=OAUTH_HEADER)

        rsd = copy.deepcopy(RSD)

        static_ext_ip = None
        break_loop = False

        for _, pool_settings in rsd["rotation_state"].items():
            for mapping_type, provider_mappings in pool_settings["mappings"].items():
                for _, mappings in provider_mappings.items():
                    for _, ext_ip in mappings.items():
                        if mapping_type == "static" and not static_ext_ip:
                            static_ext_ip = ext_ip["ext_ip"]
                            break
                        elif mapping_type == "static":
                            ext_ip["ext_ip"] = static_ext_ip
                            break_loop = True
                            break
                if break_loop:
                    break
            if break_loop:
                break

        upload_result = upload_modified_rsd(rsd)

        rsd["version_id"] = session.get(
            get_rotation_url(TEST_INSTANCE_NAME) + "/version_id", headers=OAUTH_HEADER
        ).json()["data"]["version_id"]

        # Trying to upload full document with invalid settings
        upload_result = session.post(DOCUMENT_URL, headers=FULL_HEADERS, data=json.dumps(rsd))

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

        # Trying to upload invalid pool settings
        upload_result = session.put(
            DOCUMENT_URL + "/rotation-state", headers=FULL_HEADERS, data=json.dumps(rsd["rotation_state"])
        )

        assert upload_result.status_code == http.HTTPStatus.BAD_REQUEST

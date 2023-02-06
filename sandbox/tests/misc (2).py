import pytest

import requests

from sandbox import common
import sandbox.common.types.misc as ctm

from sandbox.yasandbox.api.json import misc
import sandbox.web.response


class TestMisc(object):

    def test_response_json_with_code(self):
        with pytest.raises(sandbox.web.response.HttpErrorResponse) as exc_info:
            misc.json_error(555, 'deadbeaf')
        assert exc_info.value.code == 555
        assert 'deadbeaf' in exc_info.value.msg

    @pytest.mark.usefixtures("resource_manager", "task_controller")
    def test_float_timeout(self, json_api_url):
        try:
            r = requests.get(json_api_url + "/task?limit=1", timeout=3.5, headers={"X-Request-Timeout": "3.5"})
            r.raise_for_status()
            r = requests.get(json_api_url + "/resource?limit=1", timeout=3.5, headers={"X-Request-Timeout": "3.5"})
            r.raise_for_status()
        except requests.HTTPError:
            pytest.fail("HTTP error on API requests with float timeout")

    def test__profiler(self, rest_su_session, rest_session):
        profiler_rest_su_session = rest_su_session << common.rest.Client.HEADERS({ctm.HTTPHeader.PROFILER: "2"})
        with pytest.raises(rest_su_session.HTTPError) as response:
            profiler_rest_su_session.service.status.server.read()
        assert response.value.status == requests.codes.I_AM_A_TEAPOT
        response = response.value.response.json()
        fields = ("profile", "legacy_profile", "result")
        for field in fields:
            assert field in response

        profiler_rest_session = rest_session << common.rest.Client.HEADERS({ctm.HTTPHeader.PROFILER: "2"})
        response = profiler_rest_session.service.status.server.read()
        for field in fields:
            assert field not in response

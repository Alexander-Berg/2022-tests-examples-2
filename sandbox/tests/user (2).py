import json
import httplib

import pytest
import requests

import sandbox.common.types.user as ctu
import sandbox.common.types.misc as ctm


class TestUser:
    @pytest.fixture(scope="function")
    def _login(self):
        return

    @pytest.mark.usefixtures("serviceq", "gui_su_session")
    def test__user_get(
        self, json_api_url, gui_session, gui_su_session, gui_session_login, gui_su_session_login
    ):
        ret = requests.get(json_api_url + "/user/current").json()
        assert ret["login"] == ctu.ANONYMOUS_LOGIN
        assert ret["role"] == ctu.Role.ANONYMOUS
        resp = requests.get(json_api_url + "/user/current", headers=gui_session)
        assert resp.status_code == httplib.OK
        ret = resp.json()
        assert ret["login"] == gui_session_login
        assert ret["role"] == ctu.Role.REGULAR
        headers = gui_su_session.copy()
        headers[ctm.HTTPHeader.CURRENT_USER] = gui_session_login
        resp = requests.get(json_api_url + "/user/current", headers=headers)
        assert resp.status_code == httplib.OK
        ret = resp.json()
        assert ret["login"] == gui_session_login
        assert ret["role"] == ctu.Role.REGULAR
        resp = requests.get(json_api_url + "/user/" + gui_session_login, headers=gui_session)
        assert resp.status_code == httplib.OK
        ret = resp.json()
        assert ret["login"] == gui_session_login
        resp = requests.get(json_api_url + "/user/" + gui_su_session_login)
        assert resp.status_code == httplib.OK
        ret = resp.json()
        assert ret["login"] == gui_su_session_login
        assert ret["role"] == ctu.Role.ADMINISTRATOR

    @pytest.mark.usefixtures("gui_su_session", "group_controller")
    def test__user_group(self, gui_su_session_login, json_api_url):
        prev = None
        for login in ("current", gui_su_session_login):
            resp = requests.get("/".join([json_api_url, "user", login, "groups"]))
            assert resp.status_code == httplib.OK
            data = resp.json()
            if prev:
                assert data == prev
            prev = data

        prev[0].pop("url")
        g = ctu.OTHERS_GROUP
        assert prev == [
            {
                "name": g.name,
                "priority_limits": {
                    "ui": dict(zip(("class", "subclass"), g.priority_limits.ui.__getstate__())),
                    "api": dict(zip(("class", "subclass"), g.priority_limits.api.__getstate__())),
                },
                "quota": {
                    "consumption": {
                        "real": 0,
                        "future": 0,
                    },
                    "limit": 0,
                    "pools": [],
                }
            }
        ]

    def test__preferences(self, json_api_url, gui_session, gui_su_session, gui_su_session_login, gui_session_login):
        node_url = "/".join([json_api_url, "user", "current", "preferences", "mynode"])
        resp = requests.get(node_url, headers=gui_session)
        assert resp.status_code == httplib.NOT_FOUND

        node_url = "/".join([json_api_url, "user", gui_su_session_login, "preferences", "mynode"])
        resp = requests.get(node_url, headers=gui_session)
        assert resp.status_code == httplib.FORBIDDEN

        node_url = "/".join([json_api_url, "user", "current", "preferences", "mynode"])
        data = {"mystr": "myvalue", "myint": 123, "mybool": True, "mylist": [1, "a", False], "mydict": {"k": "v"}}
        hdrs = gui_session.copy()
        hdrs["Content-Type"] = "application/json"
        resp = requests.put(
            node_url,
            data=json.dumps(data),
            headers=hdrs,
        )
        assert resp.status_code == httplib.CREATED, (resp.status_code, resp.reason, resp.text)
        assert resp.headers["Location"] == node_url

        resp = requests.get(node_url, headers=gui_su_session)
        assert resp.status_code == httplib.NOT_FOUND, (resp.status_code, resp.reason, resp.text)

        resp = requests.get(node_url, headers=gui_session)
        assert resp.status_code == httplib.OK, (resp.status_code, resp.reason, resp.text)
        assert resp.json() == data

        node_url = "/".join([json_api_url, "user", gui_session_login, "preferences", "mynode"])
        resp = requests.get(node_url, headers=gui_su_session)
        assert resp.status_code == httplib.OK, (resp.status_code, resp.reason, resp.text)
        assert resp.json() == data

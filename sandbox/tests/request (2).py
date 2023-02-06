import pytest

import mock
import uuid
import datetime as dt
import xmlrpclib

from sandbox import common
import sandbox.common.types.misc as ctm

import sandbox.yasandbox.controller.user as user_controller
from sandbox.yasandbox.database import mapping

import web.helpers
import web.controller
import web.server.request

from sandbox.yasandbox import manager
from sandbox.yasandbox.manager import tests as manager_tests


class TestRequestAuth(object):

    @staticmethod
    def __user(login):
        mapping.User(login=login).save()
        user_controller.User.validated(login)
        return login

    @staticmethod
    def tear_up(login):
        web.server.request.SandboxRequest.settings.auth = mock.MagicMock()
        web.server.request.SandboxRequest.settings.auth.enabled = True

    @pytest.mark.usefixtures("initialize")
    def test_auth_renew_session(self):
        login = self.__user("user")
        self.tear_up(login)
        path = "tasks/list"
        data = {"task_type": "TEST_TASK", "refresh_params": True}
        cookies = {"Session_id": uuid.uuid4().hex}
        req = web.server.request.SandboxRequest(
            "127.0.0.1", {ctm.HTTPHeader.CURRENT_USER: login}, ctm.RequestMethod.GET, path, target=("", ""),
            cookies=cookies, params=data,
        )
        web.controller.dispatch(path, req)
        del data["refresh_params"]
        assert user_controller.User.get_path_params(login, path) == data

    @pytest.mark.usefixtures("initialize")
    def test_auth_without_user_header(self):
        login = "user"
        self.tear_up(login)
        mapping.User(login=login).save()
        user_controller.User.validate_login = mock.MagicMock()
        user_controller.User.validate_login.return_value = None
        cookies = {"Session_id": uuid.uuid4().hex}
        request = web.server.request.SandboxRequest(
            "127.0.0.1", {}, ctm.RequestMethod.GET, "tasks/list", target=("", ""), cookies=cookies
        )
        assert not user_controller.User.validate_login.called
        assert request.user.login == "guest"

    @pytest.mark.usefixtures("initialize")
    def test_auth_login_was_validated(self):
        login = "user"
        self.tear_up(login)
        mapping.User(login=login, staff_validate_timestamp=(dt.datetime.utcnow() - dt.timedelta(days=2))).save()
        user_controller.User.validate_login = mock.MagicMock()
        user_controller.User.validate_login.return_value = user_controller.User.StaffInfo()
        cookies = {"Session_id": uuid.uuid4().hex}
        request = web.server.request.SandboxRequest(
            "127.0.0.1", {ctm.HTTPHeader.CURRENT_USER: login}, ctm.RequestMethod.GET, "tasks/list",
            target=("", ""), cookies=cookies,
        )
        assert not user_controller.User.validate_login.called
        assert request.user.login == login


class TestRequestXMLRPCParsing(object):
    def test__good_request(self, server, api_session):
        assert api_session.ping("Correct data") == "Correct data"

    def test__bad_request(self, server, api_session, monkeypatch):
        log = [None]
        monkeypatch.setattr(server.logger, "debug", lambda _, *args: log.__setitem__(0, args))
        body = "Incorrect data \010"
        with pytest.raises(xmlrpclib.ProtocolError) as exc:
            api_session.ping(body)
        assert "400 BAD REQUEST: ExpatError: not well-formed (invalid token): line 6, column 30>" in str(exc)
        assert log[0][1] == (
            "<?xml version='1.0'?>\n"
            "<methodCall>\n"
            "<methodName>ping</methodName>\n"
            "<params>\n"
            "<param>\n"
            "<value><string>{}</string></value>\n"
            "</param>\n"
            "</params>\n"
            "</methodCall>\n".format(body)
        )

    def test__large_xmlrpc_request(self, server, api_session, task_manager):
        task = manager_tests._create_task(task_manager)
        # This produces about 18Mb of a payload on the server side:
        # DataSizeError: Too large data size: 19730898
        task.ctx = {"Test": "a" * (common.process.InterProcessQueue.DATA_LIMIT / 2)}
        remote_task_manager = manager.ManagerDispatchWrapper(task_manager)
        with pytest.raises(xmlrpclib.Fault) as exc_info:
            remote_task_manager.update(task)

        assert "DataSizeError" in str(exc_info)
        # should be propagated to a user
        assert exc_info.value.faultCode == common.proxy.ReliableServerProxy.ErrorCodes.ERROR

import uuid
import pytest
import collections

from sandbox.common.types import task as ctt
from sandbox.common.types import database as ctd

from sandbox.taskbox.client import service as tb_service
from sandbox.yasandbox.database import mapping


pytest_plugins = (
    "sandbox.tests.common",
)


# Copy of sandbox.web.server.TaskSession
TaskSession = collections.namedtuple("TaskSession", ("client", "task", "vault", "token"))


class DummyRequest(object):
    def __init__(self, login, node_id):
        self.id = "SES_" + uuid.uuid4().hex[4:]
        self.source = ctt.RequestSource.TASK
        self.user = mapping.User(login=login)
        self.remote_ip = "1.1.1.1"
        self.session = TaskSession(client=node_id, task=123456, vault="", token="")
        self.headers = None
        self.cookies = None
        self.remote_ip = None
        self.client_address = None
        self.is_binary = None
        self.profid = None
        self.read_preference = ctd.ReadPreference.PRIMARY
        self.ctx = None


@pytest.fixture(scope="session")
def dispatcher(taskbox, host, taskbox_port):
    import sandbox.taskbox.config
    sandbox.taskbox.config.Registry().reload()
    return tb_service.Dispatcher(host=host, port=taskbox_port)


@pytest.fixture()
def request_env(request, rest_session_login, client_node_id):

    mapping.base.tls.request = DummyRequest(rest_session_login, client_node_id)

    def drop_request():
        mapping.base.tls.request = None
    request.addfinalizer(drop_request)

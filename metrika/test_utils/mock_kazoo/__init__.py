from zake.fake_client import FakeClient
from metrika.pylib.zkconnect import KazooClientMetrika


class FakeKazooClientMetrika(FakeClient):
    create_or_set = KazooClientMetrika.__dict__['create_or_set']
    client_state = 'CONNECTED'
    hosts = [('FakeHost', 8888)]


def get_zk(*args, **kwargs):
    # kazoo.client.KazooClient = FakeClient
    # from metrika.pylib.zkconnect import KazooClientMetrika
    # zk = KazooClientMetrika()
    zk = FakeKazooClientMetrika()
    return zk

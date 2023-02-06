from __future__ import absolute_import

import time
import functools as ft

import pytest
import zake.fake_client

from sandbox.serviceq import election

TIMEOUT = .1


@pytest.fixture()
def fake_contender():
    class FakeContender(election.Contender):
        __storage = zake.fake_client.FakeClient().storage

        def _create_zk_client(self):
            zk_client = zake.fake_client.FakeClient(storage=self.__storage)
            zk_client.start()
            return zk_client

    return ft.partial(FakeContender, "", "/test/node", do_fork=False, timeout=TIMEOUT)


# noinspection PyShadowingNames
class TestContender(object):
    def test__election(self, request, fake_contender):
        nodes = ["contender1", "contender2", "contender3"]
        contenders = [fake_contender(node).start() for node in nodes]
        contenders[0].contenders = nodes

        request.addfinalizer(lambda: [contender.stop() for contender in contenders])

        for contender in contenders:
            assert contender.primary(None) is None
            assert contender.primary(False) is None
            assert sorted(contender.contenders) == nodes

        assert contenders[0].primary(True) == nodes[0]
        for contender in contenders:
            if contender != contenders[0]:
                assert contender.primary(None) is None
            assert contender.primary(False) == nodes[0]

        contenders[0].restart()
        time.sleep(TIMEOUT)

        for contender in contenders:
            assert contender.primary(None) is None
            assert contender.primary(False) is None
            assert sorted(contender.contenders) == nodes

        assert contenders[1].primary(True) == nodes[1]
        assert contenders[0].primary(True) == nodes[1]
        assert contenders[2].primary(True) == nodes[1]

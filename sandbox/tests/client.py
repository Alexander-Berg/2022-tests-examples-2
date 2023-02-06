import mock
import time
import logging
import threading

from sandbox.agentr import client


def test__task_session_is_called_first_on_reconnect():
    s = client.Session("token", 1, 0, logging.getLogger())
    # imagine connection was already established
    s._sid = "b46465ed"

    task_session_created = threading.Event()
    should_throw = []  # in Python3 it can be replaced with nonlocal bool variable

    def mock_srv_call(name, *args, **kwargs):
        if name == "task_session":
            time.sleep(1)
            task_session_created.set()
        elif name == "resource_sync":
            # assert if task_session was not called before resource_sync
            if not task_session_created.isSet():
                should_throw.append(1)
        return mock.MagicMock()

    class MockReactor(object):
        def __init__(self, sid):
            self.sid = sid

    mock_srv_connect = mock.Mock(return_value=MockReactor("75adef59"))  # return sid which differs from initial s._sid
    with mock.patch.object(s._srv, "connect", mock_srv_connect):
        with mock.patch.object(s._srv, "call", new_callable=lambda: mock_srv_call):
            t1 = threading.Thread(target=lambda: s.__call__("resource_sync", 1))
            t2 = threading.Thread(target=lambda: s.__call__("resource_sync", 2))

            t1.start()
            t2.start()

            t1.join()
            t2.join()

            assert not should_throw, "task_session was not called before resource_sync"

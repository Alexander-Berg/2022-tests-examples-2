import time
import pytest

from sandbox import common

import sandbox.services.modules.client_availability_checker


@pytest.fixture
def client_availability_checker(server, rest_su_session):
    service = sandbox.services.modules.client_availability_checker.ClientAvailabilityChecker()
    service.load_service_state()
    service.rest = rest_su_session
    return service


class TestClientAvailabilityChecker(object):
    def test__dead_clients(self, client_availability_checker, client_manager):
        client_availability_checker.send_dead_clients_report = lambda *args: None
        dead_clients = [client_manager.create("test_client_{}".format(i)) for i in xrange(3)]
        update_ts = time.time()
        alive_clients = [
            client_manager.create("test_client_alive_{}".format(i), update_ts=update_ts)
            for i in xrange(3)
        ]

        dead = client_availability_checker.find_dead_clients()
        assert set(dead) == set(c.hostname for c in dead_clients)

        client_availability_checker._model.context["known"] = list(dead)
        new_dead = alive_clients[0]
        new_dead.update_ts = update_ts - common.config.Registry().server.web.mark_client_as_dead_after - 20
        new_dead.save()

        dead = client_availability_checker.find_dead_clients()
        assert set(dead) == set(c.hostname for c in (dead_clients + [new_dead]))

import time
import pytest
import logging
import requests
import threading
import metrika.pylib.pinger as mtpinger
import yatest.common.network as ycn


class RealCheck(mtpinger.Check):
    def do_check(self):
        pass

    def set_status(self, code, desc):
        self.check_status = (code, desc)


class TestPinger(mtpinger.Pinger):
    def __init__(self, config):
        super(TestPinger, self).__init__(
            name="TestPinger",
            checks=[
                {'name': 'check1', 'slave_class': RealCheck},
                {'name': 'check2', 'slave_class': RealCheck},
                {'name': 'check3', 'slave_class': RealCheck},
            ],
            config=config
        )


@pytest.fixture
def get_pinger(monkeypatch):
    with ycn.PortManager() as pm:
        port = pm.get_port()
        logging.debug("Port = %d", port)

        config = {
            'master': {
                'port': port,
                'sleep_timeout': 3,
                'logger_settings': {
                    'stdout': True,
                },
            },
            'check1': {
                'ttl': 60,
                'sleep_timeout': 2
            },
            'check2': {
                'ttl': 60,
                'sleep_timeout': 10,
            },
            'check3': {
                'ttl': 60,
                'sleep_timeout': 15,
            },
        }

        pinger = TestPinger(config=config)

        monkeypatch.setattr(pinger, 'start_juggler_sender', lambda: True)
        monkeypatch.setattr(pinger, 'start_graphite_sender', lambda: True)

        yield pinger, port


@pytest.fixture
def start_pinger(get_pinger):
    pinger = get_pinger[0]
    t = threading.Thread(target=lambda: pinger.start())
    t.daemon = True
    t.start()
    time.sleep(1)
    yield

    pinger.shutdown.set()


def test_ping(get_pinger, start_pinger):
    pinger, port = get_pinger
    url = "http://localhost:%d/ping" % port

    r = requests.get(url)

    assert r.status_code == 503
    assert "Didn't checked" in r.text

    pinger.slaves[0].set_status(0, 'OK')
    pinger.slaves[1].set_status(0, 'OK')
    pinger.slaves[2].set_status(0, 'OK')
    time.sleep(5)

    r = requests.get(url)

    assert r.status_code == 200
    assert 'OK' in r.text

    pinger.slaves[0].set_status(1, 'qwe 025 Gc')
    time.sleep(5)

    r = requests.get(url)

    assert r.status_code == 503
    assert 'qwe 025 Gc' in r.text

    pinger.slaves[0].set_status(0, 'qwe 025 Gc')
    time.sleep(5)

    r = requests.get(url)

    assert r.status_code == 200
    assert 'qwe 025 Gc' not in r.text

    time.sleep(50)

    r = requests.get(url)

    assert r.status_code == 503
    assert 'Current status is too old' in r.text

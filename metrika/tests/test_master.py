import os
import socket
import pytest


FAKE_FQDN = 'AWESOMEFQDN'


class MasterTestError(Exception):
    pass


def test_shutdown(master):
    assert master.shutdown is not None


def test_run_not_implemented(master):
    with pytest.raises(NotImplementedError):
        master.run()


def test_sighandler_initiate_stop(master, monkeypatch):
    def mock__initiate_stop(*args, **kwargs):
        raise MasterTestError

    monkeypatch.setattr(master, '_initiate_stop', mock__initiate_stop)

    with pytest.raises(MasterTestError):
        master._sigterm_handler(9, None)


def test_stop_on_exception(master, monkeypatch):
    def mock_run(*args, **kwargs):
        raise Exception("Exception")

    def mock__initiate_stop(*args, **kwargs):
        raise MasterTestError

    monkeypatch.setattr(master, 'run', mock_run)
    monkeypatch.setattr(master, '_initiate_stop', mock__initiate_stop)
    monkeypatch.setattr(master, 'start_daemon_services', lambda: True)

    with pytest.raises(MasterTestError):
        master.start()


def test_get_identifier(master, monkeypatch):
    def mock_getfqdn(*args, **kwargs):
        return FAKE_FQDN

    monkeypatch.setattr(socket, 'getfqdn', mock_getfqdn)

    # take from config file if specified
    assert master.get_identifier() == 'identity'

    # take from socket.getfqdn() if not specified in config
    # and no qloud variables in environ
    os.environ = {}
    master.master_config.identifier = None
    assert master.get_identifier() == FAKE_FQDN

    # build from qloud variables if exist
    os.environ = {
        'QLOUD_DISCOVERY_INSTANCE': 'DISCOVERY.INSTANCE',
    }
    identifier = 'DISCOVERY.INSTANCE'
    assert master.get_identifier() == identifier

    # build from deploy variables if exist
    os.environ = {
        'DEPLOY_PROJECT_ID': 'P',
        'DEPLOY_STAGE_ID': 'S',
        'DEPLOY_UNIT_ID': 'U',
        'DEPLOY_WORKLOAD_ID': 'W',
        'DEPLOY_POD_TRANSIENT_FQDN': 'F',
        'DEPLOY_POD_IP_0_ADDRESS': 'I',
    }
    identifier = 'P/S/U/W/F/I'
    assert master.get_identifier() == identifier

    # build ok if some variables are missed in deploy
    os.environ = {
        'DEPLOY_PROJECT_ID': 'P',
    }
    identifier = 'Failed to get indentifier: {}'.format(FAKE_FQDN)
    assert master.get_identifier() == identifier


def test_start_operations_order(master, monkeypatch):
    order = {}

    def mock_start_daemon_services(*args, **kwargs):
        order['start_daemon_services'] = len(order.keys())

    def mock_run(*args, **kwargs):
        order['run'] = len(order.keys())

    monkeypatch.setattr(master, 'start_daemon_services', mock_start_daemon_services)
    monkeypatch.setattr(master, 'run', mock_run)

    master.start()
    assert order['start_daemon_services'] < order['run']


def test__initiate_stop(master):
    master._initiate_stop()
    assert master.shutdown.is_set()


def test_load_config(master):
    assert master.config['awesome'] == 'config'


def test_load_config_master_section_is_removed(master):
    assert master.config.get('master') is None


def test_load_config_master_override(master):
    assert master.master_config['hidden_opts'] == ['whiskey', 'kukareku', 'super::puper::secret::key', 'super::unexisted::realy::key']


def test_load_config_master_append(master):
    assert master.master_config['awesome'] == 'master'


def test_status_hide_hidden_opts(master):
    status = master.status()
    assert status['config'].get('whiskey') == '*** HIDDEN ***'
    assert status['config'].get('kukareku') == '*** HIDDEN ***'
    assert status['config']['super']['puper']['secret']['key'] == '*** HIDDEN ***'
    assert status['config']['super']['puper']['nonsecret']['key'] == 'bong'
    assert status['config']['super']['unexisted']['key'] == 'value'

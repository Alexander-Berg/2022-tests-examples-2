import pytest
from unittest.mock import patch, Mock

from contextlib import contextmanager, closing
from netaddr import IPAddress
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.agent import AgentRequestHandler

from l3mgr.models import (
    VirtualServer,
    Configuration,
)
from l3mgr.tasks import _restart_fw
from l3.celery import app
from l3balancer.exceptions import BalancerCommunicationException


LB_ID = 35
CFG_ID = 104
IPS_ON_BALANCER = ["2a02:6b8:0:3400::2221", "2a02:6b8:0:3400::2221", "95.108.254.221", "95.108.254.221"]
VS_IDS = {112: "2a02:6b8:0:3400::2221", 111: "2a02:6b8:0:3400::2221", 109: "95.108.254.221", 108: "95.108.254.221"}


@pytest.fixture(scope="module")
def celery_app(request):
    """
    Avoid task scheduling
    """
    app.conf.update(CELERY_ALWAYS_EAGER=True)
    return app


def fake_make_ssh_chain(*args):
    """
    Use localhost for SSH connection
    """
    host, port, username = "localhost", 22, "piskunov-va"
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(
        host,
        port=port,
        username="piskunov-va",
        allow_agent=True,
        key_filename="/home/" + username + "/.ssh/id_rsa_test",
    )
    AgentRequestHandler(client.get_transport().open_session())

    return host, port, client


def add_ips_on_vss(lb, cfg_id, vs_ids_to_ips_map):
    """
    Setup DB fields for testing
    """

    def actual_call(lb=lb, cfg_id=cfg_id, vs_ids_to_ips_map=vs_ids_to_ips_map):
        Configuration.objects.filter(pk=cfg_id).update(vs_ids=list(vs_ids_to_ips_map.keys()))

        for vs_id, ip in vs_ids_to_ips_map.items():
            VirtualServer.objects.filter(id=vs_id).update(lb_ids=[lb], ip=ip)

    return actual_call


def delete_vss_for_config(cfg_id):
    """
    Setup DB fields for testing
    """

    def actual_call(cfg_id=cfg_id):
        Configuration.objects.filter(pk=cfg_id).update(vs_ids=[])

    return actual_call


def manage_dummy_interfaces(ips, action="add"):
    """
    Add/delete IPs on dummy interfaces
    """
    commands = []

    for n, ip in enumerate(ips):
        mask = 32 if IPAddress(ip).version == 4 else 128
        interaface_number = n + 10000
        link = "sudo ip link {} dummy{} type dummy".format(action, interaface_number)
        add_ip = "sudo ip address {} {}/{} dev dummy{}".format(action, ip, mask, interaface_number)
        commands.extend([link, add_ip]) if action == "add" else commands.extend([add_ip, link])

    return " && ".join(commands)


@contextmanager
def ssh():
    """
    Create SSH client
    """
    with closing(fake_make_ssh_chain()[2]) as client:
        yield client


@contextmanager
def manage_ips(ips):
    """
    Adding then auto-removing IPs on dummy interfaces after test is done
    """
    with ssh() as client:
        try:
            yield client.exec_command(manage_dummy_interfaces(ips))
        finally:
            client.exec_command(manage_dummy_interfaces(ips, action="del"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lb_id, cfg_id, vs_ids, ips, db_updator, expected_result",
    [
        # Success case - IPs on Balancer are the same as IPs on VSs in config
        (LB_ID, CFG_ID, VS_IDS, list(VS_IDS.values()), add_ips_on_vss(LB_ID, CFG_ID, VS_IDS), False),
        # Success case - no IPs to check
        (LB_ID, CFG_ID, VS_IDS, list(VS_IDS.values()), delete_vss_for_config(CFG_ID), False),
        # Failure case - some IPs on Balancer are missing
        (LB_ID, CFG_ID, VS_IDS, [list(VS_IDS.values())[0]], add_ips_on_vss(LB_ID, CFG_ID, VS_IDS), True),
    ],
)
@patch("l3balancer.utils._make_ssh_chain", new=fake_make_ssh_chain)
@patch("l3balancer.services.BalancerHost.restart_firewall")
def test__restart_fw(mocked_restart_firewall, lb_id, cfg_id, vs_ids, ips, db_updator, expected_result, celery_app):
    db_updator()

    with manage_ips(ips):
        result = _restart_fw.apply(args=(LB_ID, CFG_ID))

    assert result.result == expected_result
    if expected_result:
        assert mocked_restart_firewall.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lb_id, cfg_id, vs_ids, ips, db_updator, expected_result",
    [
        # Test exception result
        (
            LB_ID,
            CFG_ID,
            VS_IDS,
            [list(VS_IDS.values())[0]],
            add_ips_on_vss(LB_ID, CFG_ID, VS_IDS),
            "Could not check if FW has restarted",
        ),
    ],
)
@patch("l3balancer.utils._make_ssh_chain", new=fake_make_ssh_chain)
@patch(
    "l3balancer.services.BalancerHost.ips_installed_on_interfaces", Mock(side_effect=BalancerCommunicationException())
)
@patch("l3mgr.tasks.task_postrun_handler")
@patch("celery.signals.task_postrun")
@patch("l3balancer.services.BalancerHost.restart_firewall")
def test__restart_fw_exception_in_precheck(
    mocked_restart_firewall,
    mocked_task_postrun,
    mocked_task_postrun_handler,
    lb_id,
    cfg_id,
    vs_ids,
    ips,
    db_updator,
    expected_result,
    celery_app,
):
    db_updator()

    result = _restart_fw.apply(args=(LB_ID, CFG_ID))
    assert expected_result in result.result.__str__()

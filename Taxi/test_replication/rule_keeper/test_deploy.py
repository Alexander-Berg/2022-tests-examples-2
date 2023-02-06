import datetime

import attr
import pytest

from replication import core_context
from replication.rule_keeper import deploy

HOSTNAME = 'dummy_host'
RESOURCES = [
    deploy.DownloadedResourceInfo(package='pack', version='ver1'),
    deploy.DownloadedResourceInfo(package='pack', version='ver2'),
]
EXPECTED_HOST_INFO = deploy.RuleDeployInfo(
    hostname=HOSTNAME,
    last_release_time=datetime.datetime(2021, 1, 1, 1),
    metadata_cron_status=deploy.MetadataCronStatuses.WAITING,
    downloaded_resources=RESOURCES,
)
HOST_INFO = {'_id': HOSTNAME, 'host_alive': datetime.datetime(2021, 1, 1, 1)}


async def test_mark_host_downloaded_resources(
        monkeypatch, replication_ctx: core_context.TasksCoreData,
):
    monkeypatch.setattr(deploy, 'get_hostname', lambda: HOSTNAME)
    deploy_manager = replication_ctx.rules_deploy_manager

    host_info = await deploy_manager.get_host_rule_deploying_info()
    assert host_info is None

    await deploy_manager.mark_host_downloaded_resources(RESOURCES)

    host_info = await deploy_manager.get_host_rule_deploying_info()
    host_info = _patch_info(host_info)
    assert host_info == EXPECTED_HOST_INFO

    all_host_info = await deploy_manager.get_all_rule_deploying_info()
    assert len(all_host_info) == 1
    host_info = _patch_info(all_host_info[0])
    assert host_info == EXPECTED_HOST_INFO


@pytest.mark.config(
    REPLICATION_RULES_DEPLOY={
        'deploy_draft': {'host_alive_check_enable': True},
    },
)
async def test_get_host_rule_deploying_info(
        monkeypatch, replication_ctx: core_context.TasksCoreData,
):
    monkeypatch.setattr(deploy, 'get_hostname', lambda: HOSTNAME)
    deploy_manager = replication_ctx.rules_deploy_manager
    await deploy_manager.mark_host_downloaded_resources(RESOURCES)
    await deploy_manager.host_alive.update_host_alive()

    host_alive_threshold_dt = datetime.datetime.utcnow() - datetime.timedelta(
        600,
    )
    assert deploy_manager.host_alive.is_host_alive(
        HOST_INFO, host_alive_threshold_dt,
    )
    all_host_info = await deploy_manager.get_all_rule_deploying_info()
    assert len(all_host_info) == 1


def _patch_info(host_info):
    assert host_info is not None
    assert host_info.last_release_time
    return attr.evolve(
        host_info, last_release_time=datetime.datetime(2021, 1, 1, 1),
    )

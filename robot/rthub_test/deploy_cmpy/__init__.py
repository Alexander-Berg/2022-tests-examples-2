import json
import logging

from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.utils import read_token_from_file
from robot.cmpy.library.yt_tools import client

from sandbox.projects.common.nanny.client import NannyClient
from robot.library.python.sandbox.client import SandboxClient

from os.path import join as pj
from retrying import retry
from datetime import timedelta


def in_milliseconds(**kwargs):
    return timedelta(**kwargs).total_seconds() * 1000


@retry(
    stop_max_delay=in_milliseconds(minutes=10),
    wait_fixed=in_milliseconds(seconds=10))
def wait_deploy(nanny_client, service_id, snapshot_id):
    logging.info('Waiting for snapshot %s to be ACTIVE.', snapshot_id)
    current_state = nanny_client.get_service_current_state(service_id)
    logging.info(json.dumps(current_state, indent=4))

    for snapshot in current_state['content']['active_snapshots']:
        if snapshot['snapshot_id'] == snapshot_id:
            if snapshot['state'] == 'ACTIVE':
                return snapshot_id
            else:
                logging.info('Found snapshot %s, but it is %s', snapshot_id, snapshot['state'])

    raise Exception()


@cm_target
def build_cmpy(cfg):
    yt_client = client(cfg)
    sandbox = SandboxClient(token=read_token_from_file(cfg.SandboxTokenPath))

    build_task_id = sandbox.run_task(
        name="YA_MAKE_RELEASE_TO_NANNY",
        params={
            "checkout_arcadia_from_url": cfg.ArcadiaPath,
            "targets": "robot/rthub/packages/rthub_test_cmpy",
            "arts": "robot/rthub/packages/rthub_test_cmpy",
            "result_single_file": True,
            "use_aapi_fuse": True,
            "result_rt": "RTHUB_CMPY",
            "result_rd": "RTHub cmpy build",
            "clear_build": False,
            "ya_yt_proxy": "arnold.yt.yandex.net",
            "ya_yt_dir": "//home/kwyt-test/yamake_cache",
            "ya_yt_token_vault_owner": "RTHUB",
            "ya_yt_token_vault_name": "kwyt_test_yt_token",
            "ya_yt_put": True
        },
        description="Build scripts and binaries for RTHub test control CM instance.",
        disk_space=10 * 2 ** 30,
        wait_success=True,
        owner="RTHUB"
    )

    revision = sandbox.get_resource_info_by_task(
        resource_name="RTHUB_CMPY",
        task_id=build_task_id,
    )["attributes"]["arcadia_revision"]

    yt_client.set(
        pj(cfg.YtPrefix, "@cmpy_version"),
        {"branch": "trunk", "build_task_id": build_task_id, "revision": revision}
    )


@cm_target
def deploy_cmpy(cfg):
    yt_client = client(cfg)
    nanny_client = NannyClient(api_url=cfg.Nanny.ApiUrl, oauth_token=read_token_from_file(cfg.NannyTokenPath))
    nanny_response = nanny_client.update_service_sandbox_file(
        service_id=cfg.Nanny.ServiceId,
        task_type=cfg.Nanny.DeployTaskType,
        task_id=str(yt_client.get(pj(cfg.YtPrefix, "@cmpy_version", "build_task_id"))),
        deploy=True,
        recipe='default',
        skip_not_existing_resources=True,
        resource_types=["RTHUB_CMPY"]
    )
    logging.info('Nanny response was %s', json.dumps(nanny_response, indent=4))

    wait_deploy(nanny_client, cfg.Nanny.ServiceId, nanny_response['set_target_state']['snapshot_id'])

import os
import json
import shutil
import logging
from datetime import timedelta

from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.utils import read_token_from_file
from robot.cmpy.library.yt_tools import client

from robot.library.python.sandbox.client import SandboxClient
from robot.library.python.testenv.client import TestEnvClient, TestEnvFailedTestException

from os.path import join as pj


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
def cleanup_rthub_builds(cfg):
    for dst in cfg.Test.PagesRTHubDir, cfg.Test.HostsRTHubDir, cfg.Baseline.PagesRTHubDir, cfg.Baseline.HostsRTHubDir:
        if os.path.isdir(dst):
            shutil.rmtree(dst)
            os.mkdir(dst)


@cm_target
def get_rthub_task_id(cfg, target):
    subcfg = cfg[target]

    test_env_client = TestEnvClient()
    deploy_revision = test_env_client.last_test_results(subcfg.TeBaseName).get_head_revision()

    try:
        test_results = test_env_client.wait_revision_test_success(
            base=subcfg.TeBaseName,
            revision=deploy_revision,
            tests_to_check=("_BUILD__RTHUB__PAGES", "_BUILD__RTHUB__HOSTS", "_BUILD__RTHUB__APP_DOCS"),
            timeout=timedelta(hours=3)
        )
    except TestEnvFailedTestException as e:
        logging.exception(e)
        test_results = test_env_client.last_test_results(base=subcfg.TeBaseName)
        deploy_revision = test_results.get_last_successfull_revision(
            tests_to_check=("_BUILD__RTHUB__PAGES", "_BUILD__RTHUB__HOSTS", "_BUILD__RTHUB__APP_DOCS"))

    pages_build_task_id = str(test_results.get_task_id(deploy_revision, "_BUILD__RTHUB__PAGES"))
    logging.info("{} RTHub Pages build task Id: {}".format(target, pages_build_task_id))
    hosts_build_task_id = str(test_results.get_task_id(deploy_revision, "_BUILD__RTHUB__HOSTS"))
    logging.info("{} RTHub Hosts build task Id: {}".format(target, hosts_build_task_id))
    app_docs_build_task_id = str(test_results.get_task_id(deploy_revision, "_BUILD__RTHUB__APP_DOCS"))
    logging.info("{} RTHub AppDocs build task Id: {}".format(target, app_docs_build_task_id))

    token = os.getenv("SANDBOX_TOKEN") or read_token_from_file(cfg.SandboxTokenPath)
    sandbox = SandboxClient(token=token)
    pages_res_file_name = sandbox.get_resource_info_by_task(resource_name='RTHUB_PAGES_FULL_PACKAGE', task_id=pages_build_task_id)['file_name']
    hosts_res_file_name = sandbox.get_resource_info_by_task(resource_name='RTHUB_HOSTS_FULL_PACKAGE', task_id=hosts_build_task_id)['file_name']
    app_docs_res_file_name = sandbox.get_resource_info_by_task(resource_name='RTHUB_APP_DOCS_FULL_PACKAGE', task_id=app_docs_build_task_id)['file_name']

    yt_client = client(cfg)
    build_info = {
        "te_base": subcfg.TeBaseName,
        "pages_build_task_id": pages_build_task_id,
        "pages_res_file_name": pages_res_file_name,
        "hosts_build_task_id": hosts_build_task_id,
        "hosts_res_file_name": hosts_res_file_name,
        "app_docs_build_task_id": app_docs_build_task_id,
        "app_docs_res_file_name": app_docs_res_file_name,
        "revision": deploy_revision,
        "sample": yt_client.get(pj(cfg.YtPrefix, subcfg.YtAttribute, 'sample'))
    }
    if target == 'Baseline':
        build_info['skip_index'] = yt_client.get(pj(cfg.YtPrefix, subcfg.YtAttribute, 'skip_index'))
    else:
        build_info['sample'] = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))
    yt_client.set(
        pj(cfg.YtPrefix, subcfg.YtAttribute),
        build_info
    )


def download_rthub_build_resource(cfg, subcfg, id_attr, resource_name, dst_dir):
    yt_client = client(cfg)
    token = os.getenv("SANDBOX_TOKEN") or read_token_from_file(cfg.SandboxTokenPath)
    sandbox = SandboxClient(token=token)

    build_task_id = yt_client.get(pj(cfg.YtPrefix, subcfg.YtAttribute, id_attr))
    res_info = sandbox.get_resource_info_by_task(resource_name=resource_name, task_id=build_task_id)
    sandbox.download_resource(
        dst_dir=dst_dir,
        tmp_dir=cfg.TmpDir,
        resource_info=res_info,
        skynet=True
    )


@cm_target
def download_rthub_build(cfg, target):
    subcfg = cfg[target]

    download_rthub_build_resource(
        cfg, subcfg,
        id_attr="pages_build_task_id",
        resource_name="RTHUB_PAGES_FULL_PACKAGE",
        dst_dir=subcfg.PagesRTHubDir)

    download_rthub_build_resource(
        cfg, subcfg,
        id_attr="hosts_build_task_id",
        resource_name="RTHUB_HOSTS_FULL_PACKAGE",
        dst_dir=subcfg.HostsRTHubDir)

    download_rthub_build_resource(
        cfg, subcfg,
        id_attr="app_docs_build_task_id",
        resource_name="RTHUB_APP_DOCS_FULL_PACKAGE",
        dst_dir=subcfg.AppDocsRTHubDir)

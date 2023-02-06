from robot.cmpy.library.cmapi import CmApi
from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.yt_tools import client

from os.path import join as pj


# CM Targets


@cm_target
def run_deploy(cfg):
    cmapi = CmApi()
    cmapi.launch_target("deploy.finish", sync=True)


@cm_target
def run_sample(cfg):
    yt_client = client(cfg)
    sample_state = yt_client.get(pj(cfg.JupiterProdPrefix, '@jupiter_meta', 'sample_prev_state'))
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))
    if sample_state != current_sample_state:
        cmapi = CmApi()
        cmapi.launch_target("sample.finish", sync=True)


@cm_target
def run_cleanup(cfg):
    cmapi = CmApi()
    cmapi.launch_target("cleanup.finish", sync=True)


@cm_target
def run_2nd_cleanup(cfg):
    cmapi = CmApi()
    cmapi.launch_target("cleanup.finish", sync=True)


@cm_target
def run_index_data(cfg):
    cmapi = CmApi()
    cmapi.launch_target("index_data.finish", sync=True)


@cm_target
def update_cm_variables(cfg):
    yt_client = client(cfg)
    prod_jupiter_branch_num = yt_client.get(pj(cfg.JupiterProdPrefix, '@jupiter_current_deploy_version', 'yandex_bundle_tag')).split('-')[-2]
    rthub_test_cmapi = CmApi(server_address=cfg.RTHubTestCm)
    rthub_test_cmapi.setvar("Deploy.BranchNumber", prod_jupiter_branch_num)


@cm_target
def run_cm_deploy(cfg):
    rthub_test_cmapi = CmApi(server_address=cfg.RTHubTestCm)
    rthub_test_cmapi.forced_run("duty.run_full_deploy_to_last_tag", sync=True)


@cm_target
def update_delivery(cfg):
    yt_client = client(cfg)
    if yt_client.exists(pj(cfg.YtPrefix, 'delivery')):
        yt_client.remove(pj(cfg.YtPrefix, 'delivery'), recursive=True, force=True)
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))
    if yt_client.exists(pj(cfg.SampleDstDir, current_sample_state, 'delivery')):
        yt_client.copy(pj(cfg.SampleDstDir, current_sample_state, 'delivery'), pj(cfg.YtPrefix, 'delivery'))


@cm_target
def build_baseline(cfg):
    cmapi = CmApi()
    cmapi.launch_target("build_baseline.finish", sync=True)


@cm_target
def build_test(cfg):
    cmapi = CmApi()
    cmapi.launch_target("build_test.finish", sync=True)


@cm_target
def wait_quality_acceptance(cfg):
    cmapi = CmApi(server_address=cfg.RTHubTestCm)
    cmapi.wait_target("yandex_deploy.finish", strict=True)

# END CM Targets

from robot.cmpy.library.cmapi import CmApi
from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.yt_tools import client

from os.path import join as pj


# CM Targets


@cm_target
def copy_baseline_input_data(cfg):
    yt_client = client(cfg)
    yt_client.copy(
        pj(cfg.SampleDstDir, 'baseline', 'rthub--hosts'),
        pj(cfg.YtPrefix, 'kiwi_export/rthub/hosts', 'rthub--hosts')
    )
    for b in range(0, 32):
        yt_client.copy(
            pj(cfg.SampleDstDir, 'baseline', 'rthub--pages_{}'.format(str(b).zfill(3))),
            pj(cfg.YtPrefix, 'kiwi_export/rthub/jupiter', 'rthub--pages_{}'.format(str(b).zfill(3)))
        )


@cm_target
def run_baseline_spread_async(cfg):
    cmapi = CmApi(server_address=cfg.RTHubTestCm)
    cmapi.launch_target("spread_rthub_async.save_state", sync=True)


@cm_target
def build_baseline(cfg):
    yt_client = client(cfg)
    yt_client.remove(pj(cfg.YtPrefix, '@jupiter_meta', 'yandex_prev_state'), force=True)
    yt_client.remove(pj(cfg.YtPrefix, '@jupiter_meta', 'yandex_current_state'), force=True)
    yt_client.remove(pj(cfg.YtPrefix, '@jupiter_meta', 'production_current_state'), force=True)
    cmapi = CmApi(server_address=cfg.RTHubTestCm)
    cmapi.launch_target("yandex.save_state", sync=True)
    cmapi.reset_this_only("shards_prepare.run_meta.yandex_deploy")
    cmapi.wait_target("shards_prepare.run_statistics")
    cmapi.mark_success("shards_prepare.finish", sync=True)
    cmapi.reset_whole_path("yandex_deploy.finish")
    cmapi.launch_target("yandex_deploy.init", sync=True)
    cmapi.forced_run("yandex_deploy.save_state", sync=True)
    cmapi.forced_run("yandex_deploy.finish", sync=True)


# END CM Targets

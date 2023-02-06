from robot.cmpy.library.cmapi import CmApi
from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.yt_tools import client

from os.path import join as pj


# CM Targets


@cm_target
def copy_test_input_data(cfg):
    yt_client = client(cfg)
    yt_client.copy(
        pj(cfg.SampleDstDir, 'test', 'rthub--hosts'),
        pj(cfg.YtPrefix, 'kiwi_export/rthub/hosts', 'rthub--hosts')
    )
    for b in range(0, 32):
        yt_client.copy(
            pj(cfg.SampleDstDir, 'test', 'rthub--pages_{}'.format(str(b).zfill(3))),
            pj(cfg.YtPrefix, 'kiwi_export/rthub/jupiter', 'rthub--pages_{}'.format(str(b).zfill(3)))
        )


@cm_target
def run_test_spread_async(cfg):
    cmapi = CmApi(server_address=cfg.RTHubTestCm)
    cmapi.launch_target("spread_rthub_async.save_state", sync=True)


@cm_target
def build_test(cfg):
    yt_client = client(cfg)
    yt_client.remove(pj(cfg.YtPrefix, '@jupiter_meta', 'yandex_prev_state'))
    yt_client.remove(pj(cfg.YtPrefix, '@jupiter_meta', 'yandex_current_state'))
    cmapi = CmApi(server_address=cfg.RTHubTestCm)
    cmapi.launch_target("yandex.finish", sync=True)
    cmapi.wait_target("shards_prepare.finish")


# END CM Targets

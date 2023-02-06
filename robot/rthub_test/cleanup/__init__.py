from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.yt_tools import client

from os.path import join as pj


def clean_state(cfg, prefix, state):
    yt_client = client(cfg)
    dir_list = yt_client.list(prefix, absolute=True)
    for d in dir_list:
        if yt_client.get_type(d) == 'map_node':
            sub_dir_list = yt_client.list(d)
            if state in sub_dir_list:
                print "Removing {}".format(pj(d, state))
                yt_client.remove(pj(d, state), recursive=True)


# CM Targets


@cm_target
def remove_deploy_prev_prev_state(cfg):
    yt_client = client(cfg)
    deploy_prev_prev_state = yt_client.get(pj(cfg.YtPrefix, '@jupiter_meta', 'deploy_prev_prev_state'))
    clean_state(cfg, cfg.YtPrefix, deploy_prev_prev_state)


@cm_target
def remove_deploy_prev_state(cfg):
    yt_client = client(cfg)
    deploy_prev_state = yt_client.get(pj(cfg.YtPrefix, '@jupiter_meta', 'deploy_prev_state'))
    clean_state(cfg, cfg.YtPrefix, deploy_prev_state)


# END CM Targets

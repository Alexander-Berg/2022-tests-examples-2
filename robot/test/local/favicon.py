from robot.library.yuppie.modules.environment import Environment
from robot.jupiter.test.common import merge_kwargs
from robot.favicon.test.common import launch_local_favicon

import yatest.common

from os.path import join as pj
from time import sleep
import json


def test_local_favicon():
    env = Environment()
    config = {
        "working_dir": pj(env.arcadia, "favicon_working_dir"),
    }

    config_file = yatest.common.get_param("favicon_config", None)
    if config_file is not None:
        with open(config_file) as fd:
            config = merge_kwargs(json.load(fd), **config)

    with launch_local_favicon(env, **config):
        while True:
            sleep(100500)

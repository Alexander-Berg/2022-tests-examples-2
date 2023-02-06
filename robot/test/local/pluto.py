from robot.library.yuppie.modules.environment import Environment
from robot.pluto.test.common import launch_local_pluto

import yatest.common

from os.path import join as pj
from signal import pause
import json


def test_local_pluto():
    env = Environment()
    config = {
        "working_dir": pj(env.arcadia, "pluto_working_dir"),
        "res_dir": yatest.common.work_path()
    }

    config_file = yatest.common.get_param("pluto_config", None)
    if config_file is not None:
        with open(config_file) as fd:
            config.update(json.load(fd))

    with launch_local_pluto(env, **config):
        try:
            pause()
        except KeyboardInterrupt:
            pass

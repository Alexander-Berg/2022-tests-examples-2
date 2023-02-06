#!/usr/bin/env python

from time import sleep
import json

from robot.jupiter.test.common import launch_local_jupiter, merge_kwargs
import yatest.common
from robot.library.yuppie.modules.environment import Environment


def test_local_jupiter():
    defaults = {
        "testing": False,
        "working_dir": None,
        "disable_restart": True,
    }

    config_file = yatest.common.get_param('jupiter_config', None)
    if config_file is None:
        raise Exception("Parameter 'jupiter_config' is not set. See README.\n")

    with open(config_file) as fd:
        config = json.load(fd)
    config = merge_kwargs(config, **defaults)

    env = Environment(hang_test=True)
    with launch_local_jupiter(env, **config):
        while True:
            sleep(100500)

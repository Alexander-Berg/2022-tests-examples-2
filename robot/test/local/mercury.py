#!/usr/bin/env python

from time import sleep
import json
import logging
import yatest.common

from robot.library.python.common_test import merge_kwargs
from robot.library.yuppie.modules.environment import Environment
from robot.mercury.test.common import start_local_mercury


def test_local_mercury():
    defaults = {
        "cm_env": {"YT_USER": "root"},
        "run_cm": True,
        "testing": False,
        "working_dir": None,
    }

    config_file = yatest.common.get_param('mercury_config', None)
    if config_file is None:
        raise Exception("Parameter 'mercury_config' is not set. See README.\n")

    with open(config_file) as fd:
        config = json.load(fd)
    config = merge_kwargs(config, **defaults)

    env = Environment(hang_test=True)
    logging.info("Parameters read from config: %s", config)

    with start_local_mercury(
        env=env,
        skip_setup=True,
        **config
    ):
        while True:
            sleep(100500)

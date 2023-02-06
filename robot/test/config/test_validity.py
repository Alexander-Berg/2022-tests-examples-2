from favicon.config import load_config
from robot.jupiter.test.common import yatest_binary_path

import os


def test_validity():
    conf_dir = yatest_binary_path("robot/favicon/packages/cm_binaries")
    for filename in os.listdir(conf_dir):
        if filename.startswith("conf-"):
            load_config(os.path.join(conf_dir, filename))

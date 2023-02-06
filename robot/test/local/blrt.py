from robot.blrt.library.local_blrt import start_local_blrt
from robot.blrt.library.local_blrt.config.builder import LocalBlrtConfigBuilder
from robot.blrt.library.local_blrt.config.dev import (
    generate_local_blrt_config_for_current_dev_run_from_now,
    get_local_blrt_config_override_for_dev_local,
    get_local_blrt_config_override_for_dev_vanilla
)
from robot.blrt.library.local_blrt.dev import (
    try_cleanup_blrt_dev_user_prefix,
    patch_local_blrt_config_for_datacamp,
    import_input_tables,
    process_pocket
)
from robot.library.yuppie.modules.environment import Environment
from robot.library.yuppie.modules.sys_mod import Sys

import json
import logging
import os
import yatest.common


def read_local_blrt_config():
    local_blrt_config_path = yatest.common.get_param("blrt_config", None)
    if not local_blrt_config_path:
        return {}
    with open(os.path.realpath(local_blrt_config_path)) as local_blrt_config_file:
        return json.load(local_blrt_config_file)


def get_dev_config_override():
    dev_mode = yatest.common.get_param("dev", "none").strip().lower()
    if dev_mode == "local":
        return get_local_blrt_config_override_for_dev_local()
    if dev_mode == "vanilla":
        return get_local_blrt_config_override_for_dev_vanilla()
    return {}


def build_local_blrt_config():
    return LocalBlrtConfigBuilder() \
        .override_from_config(generate_local_blrt_config_for_current_dev_run_from_now()) \
        .override_from_config(get_dev_config_override()) \
        .override_from_config(read_local_blrt_config()) \
        .override_from_test_params() \
        .get_config()


def dump_local_blrt_config(local_blrt_config):
    local_blrt_config_dump_path = os.path.realpath(yatest.common.output_path("local_blrt_config.json"))
    logging.info("Dumping resulting local_blrt_config into {}".format(local_blrt_config_dump_path))
    with open(local_blrt_config_dump_path, "w") as local_blrt_config_dump_file:
        json.dump(local_blrt_config, local_blrt_config_dump_file, indent=4, sort_keys=True)


def test_local_blrt():
    Environment()

    input_tables = [it for it in yatest.common.get_param("input", "").split(",") if it]
    is_datacamp_processing = yatest.common.get_param("datacamp", "false").lower() == "true"

    local_blrt_config = build_local_blrt_config()
    if is_datacamp_processing:
        patch_local_blrt_config_for_datacamp(local_blrt_config, input_tables)
    dump_local_blrt_config(local_blrt_config)

    logging.info("Starting local blrt with YT cluster = {} and prefix = {}".format(local_blrt_config["yt"]["cluster"], local_blrt_config["yt"]["prefix"]))
    with start_local_blrt(local_blrt_config) as local_blrt:
        try_cleanup_blrt_dev_user_prefix(local_blrt)
        if input_tables:
            import_input_tables(local_blrt, input_tables, is_datacamp_processing)

        if input_tables and not is_datacamp_processing:
            process_pocket(local_blrt)
        else:
            with local_blrt.run_workers():
                Sys.hang()

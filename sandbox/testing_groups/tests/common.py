# -*- coding: utf-8 -*-
import json
import os

import yaml


def load_config(config_file):
    import yatest.common
    dir_name = os.path.dirname(yatest.common.test_source_path())
    path = os.path.join(dir_name, config_file)
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def load_json_schema(schema_file):
    import yatest.common
    path = yatest.common.test_source_path(schema_file)
    with open(path, 'r') as f:
        return json.load(f)

# -*- coding: utf-8 -*-
import jsonschema

from sandbox.projects.browser.autotests_qa_tools.configs.testing_groups.tests import common


def test_config_is_valid():
    config = common.load_config('testing_groups.yaml')
    schema = common.load_json_schema('testing_groups_schema.json')
    jsonschema.validate(config, schema)

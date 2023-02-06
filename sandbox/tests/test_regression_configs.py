# -*- coding: utf-8 -*-
import jsonschema

from sandbox.projects.browser.autotests.regression.conf import tests


def test_config_is_valid():
    config = tests.load_config('testing_groups.yaml')
    schema = tests.load_json_schema('testing_groups_schema.json')
    jsonschema.validate(config, schema)

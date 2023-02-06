import itertools

import jsonschema
import pytest

from sandbox.projects.browser.autotests.regression.conf import tests


TESTED_CONFIGS = (
    'testing_groups.yaml',
    'testing_groups_mobile.yaml',
)


def _load_tracker_sanitizers_groups(config_file):
    raw_config = tests.load_config(config_file)
    return {group_name: group for group_name, group in raw_config.iteritems()
            if 'tracker_sanitizers' in group.get('activity', [])}


@pytest.mark.parametrize('config_file', TESTED_CONFIGS)
def test_config_schema(config_file):
    config = tests.load_config(config_file)
    schema = tests.load_json_schema('tracker_sanitizers_testing_groups_schema.json')
    jsonschema.validate(config, schema)


@pytest.mark.parametrize('config_file', TESTED_CONFIGS)
def test_config_components(config_file):
    config = _load_tracker_sanitizers_groups(config_file)

    def key_func(group):
        return group.get('startrek_queue', '')

    groups = sorted(config.values(), key=key_func)
    for queue, groups in itertools.groupby(groups, key=key_func):
        used_components = set()
        for group in groups:
            group_components = set(group['components'])
            duplicated_components = used_components & group_components
            assert not duplicated_components, (
                "Duplicated components for queue '{}'".format(queue))
            used_components |= group_components

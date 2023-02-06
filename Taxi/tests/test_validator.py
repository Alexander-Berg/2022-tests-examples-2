import os

import pytest

from taxi_dashboards import validator


def parametrize_test_case():
    parameters = []
    if 'GRAPHS_DIR' in os.environ:
        for dir_path, _, file_names in os.walk(os.environ['GRAPHS_DIR']):
            for file_name in file_names:
                if file_name.endswith('.yaml'):
                    parameters.append(os.path.join(dir_path, file_name))

    return pytest.mark.parametrize('file_path', parameters)


@parametrize_test_case()
def test_configs(file_path):
    config_validator = validator.ConfigValidator()
    validator.validate_one(file_path, validator=config_validator)

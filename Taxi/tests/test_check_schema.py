import os
import yaml

from jsonschema import validate

PATH_TO_SCHEMA = 'models_autodeploy/snapshots/schemas/snapshot.yaml'
PATH_TO_CONFIGS = 'models_autodeploy/snapshots/configs'


def test_check_schemas():
    with open(PATH_TO_SCHEMA) as schema_file:
        schema = yaml.safe_load(schema_file)

    for file_name in os.listdir(PATH_TO_CONFIGS):
        with open(os.path.join(PATH_TO_CONFIGS, file_name)) as config_file:
            validate(instance=yaml.safe_load(config_file), schema=schema)

import os

import pytest

from taxi.internal.data_manager import loader_utils
from taxi.internal.yt_tools import table_rotate
from taxi.internal.yt_tools.table_rotate import schema
import helpers


@pytest.mark.asyncenv('blocking')
def test_rotation_json_schema():
    schema_path = os.path.join(
        schema.STATIC_BASEDIR, 'yt_rotation_schema.yaml'
    )
    rotation_schema = loader_utils.load_yaml(schema_path)
    helpers.validate_objects_in_dir(schema.RULES_PATH, rotation_schema)


@pytest.mark.asyncenv('blocking')
def test_load_rules_schema():
    schema.load_rules(fail=True)


@pytest.mark.asyncenv('blocking')
def test_load_rules():
    table_rotate.load_rules()

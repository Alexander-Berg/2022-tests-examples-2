import os.path

import jsonschema
import pytest

from taxi_schemas import consts
from taxi_schemas import utils

LOGBROKER_SCHEMAS_DIR = os.path.join(consts.SCHEMAS_DIR, 'logbroker')


@pytest.mark.parametrize(
    'path', utils.get_all_schemas_paths(LOGBROKER_SCHEMAS_DIR),
)
@pytest.mark.nofilldb
def test_schemas(path):
    schema = utils.load_yaml(path)
    jsonschema.Draft4Validator.check_schema(schema=schema)

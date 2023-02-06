from __future__ import unicode_literals
from __future__ import print_function

import pytest
from contextlib import contextmanager
import json
from jsonschema import ValidationError
from sandbox.projects.yabs.partner_share.lib.config.inspect_functions.inspect_functions import (
    validate_config_functions,
    FunctionNotFound
)
from sandbox.projects.yabs.partner_share.lib.config.config import (
    validate_config,
    StateNotFound,
    OperationNotFound,
    PathNotFound,
    StageNotFound,
    QueueNotFound,
    TaskTypeNotFound,
)
from sandbox.common import fs

EXCEPTIONS = {
    "ValidationError": ValidationError,
    "StateNotFound": StateNotFound,
    "OperationNotFound": OperationNotFound,
    "PathNotFound": PathNotFound,
    "FunctionNotFound": FunctionNotFound,
    "StageNotFound": StageNotFound,
    "QueueNotFound": QueueNotFound,
    "TaskTypeNotFound": TaskTypeNotFound,
}


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    'case',
    json.loads(fs.read_file('test_configs.json').decode('utf-8'))
)
def test_config_validation(case):
    if case['error']:
        expectation = pytest.raises(EXCEPTIONS[case['error']])
    else:
        expectation = does_not_raise()
    with expectation:
        validate_config(case['input'])
        validate_config_functions(case['input'])

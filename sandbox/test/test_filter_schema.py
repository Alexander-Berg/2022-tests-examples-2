from __future__ import unicode_literals
from __future__ import print_function

import pytest
from contextlib import contextmanager
import json
from jsonschema import ValidationError
from sandbox.projects.yabs.partner_share.lib.fast_changes.filter_schema.filter_schema import validate_filter_schema
from sandbox.common import fs


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    'case',
    json.loads(fs.read_file('test_filters.json').decode('utf-8'))
)
def test_filters(case):
    if case['error']:
        expectation = pytest.raises(ValidationError)
    else:
        expectation = does_not_raise()
    with expectation:
        validate_filter_schema(
            {
                'filters': case['input']
            }
        )

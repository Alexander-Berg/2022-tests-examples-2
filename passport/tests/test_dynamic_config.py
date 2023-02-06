# -*- coding: utf-8 -*-
import json
from unittest import TestCase

import mock
from passport.backend.core.dynamic_config import (
    load_json,
    load_plaintext,
)
from passport.backend.core.test.test_utils import OPEN_PATCH_TARGET
import six


def mock_builtin_open(return_value):
    mock_open = mock.MagicMock()
    mock_open.return_value.__enter__.return_value = return_value
    return mock_open


class TestLoadJsonFunc(TestCase):
    def test_load(self):
        mock_open = mock_builtin_open(six.StringIO(
            json.dumps([
                {
                    'field1': 'value1',
                    'field2': 'value2',
                },
                {},
            ]),
        ))
        with mock.patch(OPEN_PATCH_TARGET, mock_open, create=True):
            json_ = load_json('some filename')
            assert json_ == [{'field1': 'value1', 'field2': 'value2'}, {}]


class TestLoadPlaintextFunc(TestCase):
    def test_load(self):
        mock_open = mock_builtin_open(six.StringIO('test_data'))
        with mock.patch(OPEN_PATCH_TARGET, mock_open, create=True):
            data = load_plaintext('some filename')
            assert data == 'test_data'

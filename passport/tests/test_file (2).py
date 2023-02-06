# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.test.test_utils import iterdiff
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.types.file import File
from passport.backend.core.validators import (
    FileUploadSchemaValidator,
    Invalid,
    SingleFileUploadValidator,
    State,
)
from six import StringIO


class TestSingleFile(unittest.TestCase):
    def setUp(self):
        self.not_empty_validator = SingleFileUploadValidator(not_empty=True)

    def test_ok(self):
        stream = StringIO('data')
        file1 = File(filename='file1.JPG', stream=stream)
        file2 = File(filename='file2.png', stream=stream)
        validators = (
            SingleFileUploadValidator(allowed_ext=['JPG'], max_size=4),
            SingleFileUploadValidator(not_empty=True),
            SingleFileUploadValidator(if_empty=123),
        )
        params = (
            (file1,),
            (file2, file1),
            (),
        )
        results = (
            file1,
            file2,
            123,
        )
        for validator, p, r in zip(validators, params, results):
            iterdiff(eq_)(validator.to_python(p), r)

    @raises(Invalid)
    def test_bad_extension(self):
        SingleFileUploadValidator(allowed_ext=['PNG']).to_python(
            (File(filename='a.jpg', stream=StringIO('data')),)
        )

    @raises(Invalid)
    def test_no_extension(self):
        SingleFileUploadValidator(allowed_ext=['PNG']).to_python(
            (File(filename='ajpg', stream=StringIO('data')),)
        )

    @raises(Invalid)
    def test_too_large(self):
        SingleFileUploadValidator(max_size=4).to_python(
            (File(filename='ajpg', stream=StringIO('data2')),)
        )

    @raises(Invalid)
    def test_empty_fails(self):
        self.not_empty_validator.to_python(())

    @raises(ValueError)
    def test_not_a_tuple(self):
        self.not_empty_validator.to_python(
            object,
        )

    @raises(ValueError)
    def test_not_a_file(self):
        self.not_empty_validator.to_python(
            (object,),
        )


class TestMultipleFiles(unittest.TestCase):
    def setUp(self):
        self.state = State(mock_env())
        stream = StringIO('data')
        self.file1 = File(filename='file1', stream=stream)
        self.file2 = File(filename='file2.jpg', stream=stream)
        self.state.files = dict(
            attach=(self.file1,),
            file=(self.file2, self.file1),
            omg=None,
        )
        self.file_schema = FileUploadSchemaValidator(
            attach=SingleFileUploadValidator(),
            file=SingleFileUploadValidator(max_size=4),
        )

    def tearDown(self):
        del self.state

    def test_ok(self):
        iterdiff(eq_)(
            self.file_schema.to_python({}, self.state),
            dict(attach=self.file1, file=self.file2),
        )

    @raises(Invalid)
    def test_nested_validator_fails(self):
        self.file2.stream = StringIO('large file data')
        self.file_schema.to_python({}, self.state)

    @raises(ValueError)
    def test_field_exists(self):
        self.file_schema.to_python(dict(attach='Another attach'), self.state)

    @raises(ValueError)
    def test_bad_single_validator(self):
        FileUploadSchemaValidator(attach=object())

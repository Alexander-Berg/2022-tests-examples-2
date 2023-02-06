# -*- coding: utf-8 -*-
from unittest import TestCase

from passport.backend.library.nginx_config_generator.utils import camel_case_to_snake_case


class TestCamelCaseToSnakeCase(TestCase):
    def test_ok(self):
        for from_, to_ in (
            ('Abc', 'abc'),
            ('ClassName', 'class_name'),
            ('AmazonS3CoolFeature', 'amazon_s3_cool_feature'),
        ):
            assert camel_case_to_snake_case(from_) == to_

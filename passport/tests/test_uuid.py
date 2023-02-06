# -*- coding: utf-8 -*-

import unittest

from nose_parameterized import parameterized
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import Uuid


class TestUuid(unittest.TestCase):
    @parameterized.expand([
        ('01430d73-25de-4955-980a-8aba4e09e7e2',),
        ('288c387f-e480-4cde-8dea-cc1a818a4925',),
        ('e77a745a-9172-45f5-857d-b36a719ee11d',),
        ('605f40dd-dff5-4c99-9e92-0840b5cdb228',),
        ('d6a6cf42-dcda-4cd4-b20e-bd305b264f92',),
        ('7c075ad7-199b-4428-addd-f0bf939202dc',),
        ('d594175b-3e69-4825-af43-30a3ab839257',),
        ('bdc4a98c-f0c8-4728-8caa-971dfac8e7a6',),
        ('6f6843fb-fec3-4e7d-99e4-8fd6ed937857',),
        ('bb9bddc8-f9ec-405a-a846-3783511e2964',),
    ])
    def test_uuid_ok(self, valid_uuid):
        check_equality(Uuid(), (valid_uuid, valid_uuid))

    @parameterized.expand([
        ('1430d73-25de-4955-980a-8aba4e09e7e2',),
        ('288c387fe480-4cde-8dea-cc1a818a4925',),
        ('e77a745a-172-45f5-857d-b36a719ee11d',),
        ('605f40dd-dff54c99-9e92-0840b5cdb228',),
        ('d6a6cf42-dcda-cd4-b20e-bd305b264f92',),
        ('7c075ad7-199b-4428addd-f0bf939202dc',),
        ('d594175b-3e69-4825-f43-30a3ab839257',),
        ('bdc4a98c-f0c8-4728-8caa971dfac8e7a6',),
        ('6f6843fb-fec3-4e7d-99e4-fd6ed937857',),
        ('101430d73-25de-4955-980a-8aba4e09e7e2',),
        ('288c387f-1e480-4cde-8dea-cc1a818a4925',),
        ('e77a745a-9172-415f5-857d-b36a719ee11d',),
        ('605f40dd-dff5-4c99-91e92-0840b5cdb228',),
        ('d6a6cf42-dcda-4cd4-b20e-b1d305b264f92',),
        ('7',),
        ('b',),
        ('-',),
        ('bz9bddc8-f9ec-405a-a846-3783511e2964',),
        ('bd9bddc8-f9ec-405a-a846-3783511/2964',),
    ])
    def test_wrong_uid(self, wrong_uid):
        check_raise_error(Uuid(), wrong_uid)

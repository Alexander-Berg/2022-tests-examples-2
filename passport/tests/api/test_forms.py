# -*- coding: utf-8 -*-
from passport.backend.oauth.core.api.forms import (
    UidMixin,
    UidOptionalMixin,
)
from passport.backend.oauth.core.test.framework import FormTestCase


class TestUidMixin(FormTestCase):
    form = UidMixin
    invalid_params = [
        ({}, {'uid': ['missing']}),
        ({'uid': ''}, {'uid': ['missing']}),
        ({'uid': 'abc'}, {'uid': ['invalid']}),
        ({'uid': '0'}, {'uid': ['invalid']}),
    ]
    valid_params = [
        ({'uid': '1'}, {'uid': 1}),
        ({'uid': '1130000000000001'}, {'uid': 1130000000000001}),
    ]


class TestUidOptionalMixin(FormTestCase):
    form = UidOptionalMixin
    invalid_params = [
        ({'uid': 'abc'}, {'uid': ['invalid']}),
        ({'uid': '0'}, {'uid': ['invalid']}),
    ]
    valid_params = [
        ({}, {'uid': None}),
        ({'uid': ''}, {'uid': None}),
        ({'uid': '1'}, {'uid': 1}),
        ({'uid': '1130000000000001'}, {'uid': 1130000000000001}),
    ]

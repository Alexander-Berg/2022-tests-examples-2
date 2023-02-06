# -*- coding: utf-8 -*-
from passport.backend.core import validators


class TestForm(validators.Schema):
    field = validators.Int(max=10)

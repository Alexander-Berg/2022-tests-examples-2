# -*- coding: utf-8 -*-
from passport.backend.core.test import test_utils
from passport.backend.perimeter import settings


def with_settings(*args, **kwargs):
    return test_utils.with_settings(*args, real_settings=settings, **kwargs)


def settings_context(*args, **kwargs):
    return test_utils.settings_context(*args, real_settings=settings, **kwargs)

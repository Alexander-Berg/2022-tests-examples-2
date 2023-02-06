# -*- coding: utf-8 -*-

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.adm_api import settings
from passport.backend.adm_api.common.exceptions import ValidationFailedError
from passport.backend.core.test.test_utils import utils
from passport.backend.core.test.test_utils.form_utils import check_equality
from passport.backend.core.validators import Invalid
import yatest.common as yc


def _get_default_settings_patches():
    return {
        'GEOBASE_LOOKUP_FILE': yc.work_path('test_data/geodata4.bin'),
        'IPREG_LOOKUP_FILE': yc.work_path('test_data/layout-passport-ipreg.json'),
    }


def with_settings_hosts(*args, **kwargs):
    kwargs = dict(_get_default_settings_patches(), **kwargs)
    return utils.with_settings_hosts(*args, real_settings=settings, **kwargs)


def with_settings(*args, **kwargs):
    kwargs = dict(_get_default_settings_patches(), **kwargs)
    return utils.with_settings(*args, real_settings=settings, **kwargs)


def check_form(form, invalid_params, valid_params, state=None):
    for invalid_params, expected_errors in invalid_params:
        try:
            form.to_python(invalid_params, state)
            ok_(
                False,
                'Form (%s) validation expected to fail with params: %s' %
                (form.__class__.__name__, repr(invalid_params)),
            )
        except Invalid as e:
            vf = ValidationFailedError(e)
            eq_(sorted(vf.errors), sorted(expected_errors))

    for p in valid_params:
        check_equality(form, p, state)

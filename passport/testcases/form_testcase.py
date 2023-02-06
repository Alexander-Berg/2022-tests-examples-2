# -*- coding: utf-8 -*-
from django.utils.datastructures import MultiValueDict
from nose.tools import (
    assert_false,
    ok_,
)
from passport.backend.oauth.core.test.framework.testcases.base import BaseTestCase
from passport.backend.oauth.core.test.utils import iter_eq


def to_multi_value_dict(params):
    # Честно эмулируем передачу в форму MultiValueDict
    return MultiValueDict({
        key: value if isinstance(value, (list, tuple)) else [value]
        for key, value in params.items()
    })


class FormTestCase(BaseTestCase):
    form = None
    form_args = []
    invalid_params = []
    valid_params = []

    def test_form(self):
        for (invalid_params, expected_errors) in self.invalid_params:
            form_instance = self.form(*self.form_args, data=to_multi_value_dict(invalid_params))
            assert_false(
                form_instance.is_valid(),
                msg=(
                    'Form "%s" validation expected to fail with params: %s' %
                    (self.form.__name__, repr(invalid_params)),
                ),
            )
            iter_eq(
                dict(form_instance.errors),
                expected_errors,
                msg='Form "%s" with params: %s produced incorrect errors: ' % (
                    self.form.__name__,
                    repr(invalid_params),
                ),
            )

        for valid_params, expected_values in self.valid_params:
            form_instance = self.form(*self.form_args, data=to_multi_value_dict(valid_params))
            ok_(
                form_instance.is_valid(),
                msg=(
                    'Form "%s" validation expected to succeed with params: %s, but produced errors: %s' %
                    (self.form.__name__, repr(valid_params), dict(form_instance.errors)),
                ),
            )
            iter_eq(
                form_instance.cleaned_data,
                expected_values,
                msg='Data mismatch in form "%s": ' % self.form.__name__,
            )

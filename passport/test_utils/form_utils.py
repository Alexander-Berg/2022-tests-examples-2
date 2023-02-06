# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.test.test_utils import iterdiff
from passport.backend.core.validators.base import Invalid
from six import (
    iteritems,
    string_types,
)


@raises(Invalid)
def check_raise_error(form, args, state=None):
    form.to_python(args, state)


def check_equality(form, args, state=None):
    params, result = args
    iterdiff(eq_)(form.to_python(params, state), result)


def check_error_codes(form, args, expected_codes, state=None):
    try:
        form.to_python(args, state)
        ok_(False, "Form (values: %s) expected to fail with codes: %s" % (args, expected_codes,))
    except Invalid as e:
        expected_codes = dict(expected_codes)
        for field, codes in iteritems(expected_codes):
            if isinstance(codes, string_types):
                expected_codes[field] = [codes]
            else:
                expected_codes[field] = sorted(codes)
        actual_codes = {}
        for field, error in iteritems(e.error_dict):
            if error.error_list:
                actual_codes[field] = sorted(e.code for e in error.error_list)
            else:
                actual_codes[field] = [error.code]
        eq_(actual_codes, expected_codes)

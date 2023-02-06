# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.views.bundle.exceptions import ValidationFailedError
from passport.backend.core.test.test_utils.form_utils import check_equality
from passport.backend.core.test.test_utils.utils import iterdiff
from passport.backend.core.validators import Invalid
from passport.backend.core.validators.jsonschema_adapter import validate_jsonschema_form
from six import string_types


eq_ = iterdiff(eq_)


def assert_errors(response_errors, expected_codes):
    if isinstance(expected_codes, (string_types, dict)):
        expected_codes = [expected_codes]
    eq_(sorted({e['field']: e['code']} for e in response_errors), sorted(expected_codes))
    # Был случай, что message случались списками, но не строками.
    # Это неверно и надо ловить, чтобы в будущем не наступить на эти грабли снова.
    for e in response_errors:
        ok_(isinstance(e['message'], string_types), "error['message'] must be string, got %s instead" % type(e['message']))


def check_bundle_form(form, invalid_tests, valid_tests, state=None):
    for invalid_params, expected_errors in invalid_tests:
        try:
            form.to_python(invalid_params, state)
            ok_(
                False,
                'Form (%s) validation expected to fail with params: %s' %
                (form.__class__.__name__, repr(invalid_params)),
            )
        except Invalid as e:
            validation_failed_error = ValidationFailedError.from_invalid(e)
            eq_(sorted(validation_failed_error.errors), sorted(expected_errors))

    for p in valid_tests:
        check_equality(form, p, state)


def check_jsonschema_form(schema, invalid_tests, valid_tests):
    for invalid_params, expected_errors in invalid_tests:
        errors = validate_jsonschema_form(schema, invalid_params)
        ok_(
            errors,
            'JSON schema validation expected to fail with params: %s' % repr(invalid_params),
        )
        eq_(sorted(errors), sorted(expected_errors))

    for valid_params, expected_results in valid_tests:
        errors = validate_jsonschema_form(schema, valid_params)
        ok_(
            not errors,
            'JSON schema validation failed with errors: %s (params %s)' % (errors, repr(valid_params)),
        )
        eq_(valid_params, expected_results)

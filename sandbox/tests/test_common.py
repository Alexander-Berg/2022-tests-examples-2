# coding=utf-8

import jsonschema
import pytest

from sandbox.projects.browser.booking import common


@pytest.mark.parametrize('params', [
    {},
    {'readonly': 'yes'},
    {'readonly': 'no'},
])
def test_booking_params_readonly_correct(params):
    jsonschema.validate(params, common.BookingParams._BOOKING_PARAMS_SCHEMA)


@pytest.mark.parametrize('params', [
    {'readonly': []},
    {'readonly': {}},
    {'readonly': None},
    {'readonly': 'unknown'},
])
def test_booking_params_readonly_wrong(params):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(params, common.BookingParams._BOOKING_PARAMS_SCHEMA)

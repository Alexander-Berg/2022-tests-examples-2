# -*- coding: utf-8 -*-
import json
import pytest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils.utils import iterdiff
from passport.backend.core.validators import Invalid
from passport.infra.daemons.yasmsapi.api.forms import (
    form_encode_invalid_to_field_and_code,
    RoutingForm,
    SendSmsForm,
)

from .test_data import (
    TEST_DEFAULT_ROUTE,
    TEST_FROM_UID,
    TEST_GSM_TEXT,
    TEST_LONG_TEXT,
    TEST_OTHER_PHONE,
    TEST_PHONE,
    TEST_ROUTE_ACTION,
    TEST_SENDER,
    TEST_TAXI_SENDER,
    TEST_UID,
    TEST_UNICODE16_LONG_TEXT,
    TEST_UNICODE16_TEXT,
    TEST_TEMPLATE_PARAMS,
)


def assert_invalid(form, invalid_params, expected_error):
    try:
        form.to_python(invalid_params, None)
        ok_(  # pragma: no cover
            False,
            'Form (%s) validation expected to fail with params: %s' % (form.__class__.__name__, repr(invalid_params)),
        )
    except Invalid as e:
        error = form_encode_invalid_to_field_and_code(e)
        eq_(error, expected_error)


@pytest.mark.parametrize(
    ('params', 'expected_result'),
    [
        (
            # Test by phone
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1',
                'scenario': 'testing_something_1',
                'device_id': 'ca2c4cfc56ed4465861356647d76865b',
                'request_path': '/2/bundle/phone/confirm_and_bind_secure/submit/',
            },
            {
                'uid': None,
                'from_uid': None,
                'phone': '+79201654534',
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': [1],
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': 'testing_something_1',
                'device_id': 'ca2c4cfc56ed4465861356647d76865b',
                'request_path': '/2/bundle/phone/confirm_and_bind_secure/submit/',
            },
        ),
        (
            # Test by UID
            {
                'uid': 1,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            {
                'uid': 1,
                'from_uid': None,
                'phone': None,
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': None,
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # Test both phone and UID
            {
                'uid': '1',
                'phone': '89201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1,2',
            },
            {
                'uid': 1,
                'from_uid': None,
                'phone': '+79201654534',
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': [1, 2],
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # Test by number
            {
                'number': TEST_OTHER_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '2,1',
            },
            {
                'uid': None,
                'from_uid': None,
                'phone': TEST_OTHER_PHONE,
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': [2, 1],
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # Test choose phone over number
            {
                'phone': TEST_PHONE,
                'number': TEST_OTHER_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            {
                'uid': None,
                'from_uid': None,
                'phone': TEST_PHONE,
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': None,
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # Test utf16 text
            {
                'phone': TEST_PHONE,
                'text': TEST_UNICODE16_TEXT,
                'sender': TEST_SENDER,
                'gate_id': '1',
            },
            {
                'uid': None,
                'from_uid': None,
                'phone': TEST_PHONE,
                'phone_id': None,
                'text': TEST_UNICODE16_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': 1,
                'previous_gates': None,
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # Route empty
            {
                'uid': '123',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': '  ',
            },
            {
                'uid': 123,
                'from_uid': None,
                'phone': None,
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': None,
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # UID + number
            {
                'uid': TEST_UID,
                'number': TEST_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            {
                'uid': TEST_UID,
                'from_uid': None,
                'phone': TEST_PHONE,
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': None,
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # Long number (20 digits)
            {
                'number': '+38001010101121315162',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            {
                'uid': None,
                'from_uid': None,
                'phone': '+38001010101121315162',
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': None,
                'caller': None,
                'identity': None,
                'text_template_params': None,
                'allow_unused_text_params': False,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
        (
            # With template
            {
                'number': '+38001010101121315162',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'text_template_params': TEST_TEMPLATE_PARAMS,
                'allow_unused_text_params': 'true',
            },
            {
                'uid': None,
                'from_uid': None,
                'phone': '+38001010101121315162',
                'phone_id': None,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'route': TEST_DEFAULT_ROUTE,
                'gate_id': None,
                'previous_gates': None,
                'caller': None,
                'identity': None,
                'text_template_params': json.loads(TEST_TEMPLATE_PARAMS),
                'allow_unused_text_params': True,
                'scenario': None,
                'device_id': None,
                'request_path': None,
            },
        ),
    ],
)
def test_send_sms_form(params, expected_result):
    form = SendSmsForm()

    iterdiff(eq_)(form.to_python(params, None), expected_result)


@pytest.mark.parametrize(
    ('invalid_params', 'expected_error'),
    [
        (
            # FROM_UID invalid
            {
                'from_uid': 'abc',
                'number': TEST_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('from_uid', u'integer'),
        ),
        (
            # FROM_UID invalid
            {
                'from_uid': -1000,
                'number': TEST_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('from_uid', u'tooLow'),
        ),
        (
            # Gate ID not integer
            {
                'uid': '123',
                'sender': TEST_SENDER,
                'text': TEST_UNICODE16_TEXT,
                'gate_id': 'gate123',
            },
            ('gate_id', u'integer'),
        ),
        (
            # Empty phone
            {
                'phone': '',
                'number': '',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('phone', u'empty'),
        ),
        (
            # Bad phone even with good number
            {
                'phone': 'None',
                'number': TEST_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('phone', u'badPhone'),
        ),
        (
            # Long phone (21 digits)
            {
                'phone': '+380010101011213151620',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('phone', u'badPhone'),
        ),
        (
            # Sender empty
            {
                'uid': '123',
                'text': TEST_GSM_TEXT,
                'sender': '',
            },
            ('sender', u'empty'),
        ),
        (
            # Sender missing
            {
                'uid': '123',
                'text': TEST_GSM_TEXT,
            },
            ('sender', u'missingValue'),
        ),
        (
            # GSM Text long
            {
                'uid': '123',
                'sender': TEST_SENDER,
                'text': TEST_LONG_TEXT,
            },
            ('text', u'tooLarge'),
        ),
        (
            # UTF16 Text long
            {
                'uid': '123',
                'sender': TEST_SENDER,
                'text': TEST_UNICODE16_LONG_TEXT,
            },
            ('text', u'tooLarge'),
        ),
        (
            # Text empty
            {
                'uid': '123',
                'sender': TEST_SENDER,
                'text': '\t\n',
            },
            ('text', u'empty'),
        ),
        (
            # Text missing
            {
                'uid': '123',
                'sender': TEST_SENDER,
            },
            ('text', u'missingValue'),
        ),
        (
            # Bad UID
            {
                'uid': 'abc',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('uid', u'integer'),
        ),
        (
            # Bad UID
            {
                'uid': '',
                'from_uid': TEST_FROM_UID,
                'number': TEST_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('uid', u'empty'),
        ),
        (
            # Bad UID
            {
                'uid': -1,
                'from_uid': TEST_FROM_UID,
                'number': TEST_PHONE,
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('uid', u'tooLow'),
        ),
        (
            # Neither UID nor phone
            {
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
            },
            ('uid', u'empty'),
        ),
        (
            # Previous gates empty
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '',
            },
            ('previous_gates', u'empty'),
        ),
        (
            # Previous gates one empty
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1,,3',
            },
            ('previous_gates', u'badvalues'),
        ),
        (
            # Previous gates one zero
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1,0,2',
            },
            ('previous_gates', u'badvalues'),
        ),
        (
            # Malformed json
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1',
                'text_template_params': '{{}',
            },
            ('text_template_params', u'badjson'),
        ),
        (
            # Invalid json
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1',
                'text_template_params': '[]',
            },
            ('text_template_params', u'badjson'),
        ),
        (
            # Invalid json
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1',
                'text_template_params': '{"a":1}',
            },
            ('text_template_params', u'badjson'),
        ),
        (
            # Invalid json
            {
                'phone': '79201654534',
                'text': TEST_GSM_TEXT,
                'sender': TEST_SENDER,
                'previous_gates': '1',
                'text_template_params': '{"a":{"b":"asdf"}}',
            },
            ('text_template_params', u'badjson'),
        ),
    ],
)
def test_send_sms_form_invalid(invalid_params, expected_error):
    form = SendSmsForm()

    assert_invalid(form, invalid_params, expected_error)


@pytest.mark.parametrize(
    ('params', 'expected_result'),
    [
        (
            {
                'sender': TEST_SENDER,
                'action': TEST_ROUTE_ACTION,
                'number': TEST_PHONE,
                'route': TEST_DEFAULT_ROUTE,
            },
            {
                'sender': TEST_SENDER,
                'action': TEST_ROUTE_ACTION,
                'number': TEST_PHONE,
                'route': TEST_DEFAULT_ROUTE,
            },
        ),
        (
            {
                'sender': TEST_SENDER,
                'action': ' ',
                'route': ' \t\n',
                'number': '',
            },
            {
                'sender': TEST_SENDER,
                'action': '',
                'number': None,
                'route': None,
            },
        ),
        (
            {
                'sender': TEST_SENDER,
            },
            {
                'sender': TEST_SENDER,
                'action': None,
                'number': None,
                'route': None,
            },
        ),
    ],
)
def test_routing_form(params, expected_result):
    form = RoutingForm()

    iterdiff(eq_)(form.to_python(params, None), expected_result)


@pytest.mark.parametrize(
    ('invalid_params', 'expected_error'),
    [
        (
            # No sender
            {
                'action': TEST_ROUTE_ACTION,
                'number': TEST_PHONE,
                'route': TEST_DEFAULT_ROUTE,
            },
            ('sender', u'missingValue'),
        ),
        (
            # Empty sender
            {
                'sender': ' ',
                'action': TEST_ROUTE_ACTION,
                'number': TEST_PHONE,
                'route': TEST_DEFAULT_ROUTE,
            },
            ('sender', u'empty'),
        ),
        (
            # Bad number
            {
                'sender': TEST_TAXI_SENDER,
                'number': 'hello',
            },
            ('number', u'badPhone'),
        ),
    ],
)
def test_routing_form_invalid(invalid_params, expected_error):
    form = RoutingForm()

    assert_invalid(form, invalid_params, expected_error)

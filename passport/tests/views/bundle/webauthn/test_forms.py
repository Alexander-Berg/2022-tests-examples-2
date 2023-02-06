# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.webauthn.forms import (
    WebauthnAddCredentialCommitForm,
    WebauthnVerifyCommitForm,
)

from .base import (
    TEST_ATTESTATION_OBJECT_BASE64,
    TEST_AUTH_DATA_BASE64,
    TEST_CLIENT_DATA_CREATE_BASE64,
    TEST_CLIENT_DATA_GET_BASE64,
    TEST_CREDENTIAL_EXTERNAL_ID,
    TEST_DEVICE_NAME,
    TEST_ORIGIN,
    TEST_SIGNATURE_HEX,
    TEST_UID,
)


class TestForms(unittest.TestCase):
    def test_add_credential_commit_form(self):
        invalid_params = [
            (
                {},
                [
                    'attestation_object.empty',
                    'client_data.empty',
                    'origin.empty',
                ],
            ),
            (
                {
                    'attestation_object': '=',
                    'client_data': '=',
                    'device_name': ' ',
                    'origin': TEST_ORIGIN,
                },
                [
                    'attestation_object.invalid',
                    'client_data.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'attestation_object': TEST_ATTESTATION_OBJECT_BASE64,
                    'client_data': TEST_CLIENT_DATA_CREATE_BASE64,
                    'origin': TEST_ORIGIN,
                },
                {
                    'attestation_object': TEST_ATTESTATION_OBJECT_BASE64,
                    'client_data': TEST_CLIENT_DATA_CREATE_BASE64,
                    'device_name': None,
                    'origin': TEST_ORIGIN,
                },
            ),
            (
                {
                    'attestation_object': TEST_ATTESTATION_OBJECT_BASE64,
                    'client_data': TEST_CLIENT_DATA_CREATE_BASE64,
                    'device_name': TEST_DEVICE_NAME,
                    'origin': TEST_ORIGIN,
                },
                {
                    'attestation_object': TEST_ATTESTATION_OBJECT_BASE64,
                    'client_data': TEST_CLIENT_DATA_CREATE_BASE64,
                    'device_name': TEST_DEVICE_NAME,
                    'origin': TEST_ORIGIN,
                },
            ),
        ]

        check_form(WebauthnAddCredentialCommitForm(), invalid_params, valid_params, None)

    def test_verify_commit_form(self):
        invalid_params = [
            (
                {},
                [
                    'auth_data.empty',
                    'client_data.empty',
                    'credential_external_id.empty',
                    'origin.empty',
                    'signature.empty',
                ],
            ),
            (
                {
                    'auth_data': '=',
                    'client_data': '=',
                    'signature': 'g',
                },
                [
                    'auth_data.invalid',
                    'client_data.invalid',
                    'credential_external_id.empty',
                    'origin.empty',
                    'signature.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'auth_data': TEST_AUTH_DATA_BASE64,
                    'client_data': TEST_CLIENT_DATA_GET_BASE64,
                    'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    'origin': TEST_ORIGIN,
                    'signature': TEST_SIGNATURE_HEX,
                },
                {
                    'auth_data': TEST_AUTH_DATA_BASE64,
                    'client_data': TEST_CLIENT_DATA_GET_BASE64,
                    'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    'origin': TEST_ORIGIN,
                    'signature': TEST_SIGNATURE_HEX,
                    'uid': None,
                },
            ),
            (
                {
                    'auth_data': TEST_AUTH_DATA_BASE64,
                    'client_data': TEST_CLIENT_DATA_GET_BASE64,
                    'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    'origin': TEST_ORIGIN,
                    'signature': TEST_SIGNATURE_HEX,
                    'uid': TEST_UID,
                },
                {
                    'auth_data': TEST_AUTH_DATA_BASE64,
                    'client_data': TEST_CLIENT_DATA_GET_BASE64,
                    'credential_external_id': TEST_CREDENTIAL_EXTERNAL_ID,
                    'origin': TEST_ORIGIN,
                    'signature': TEST_SIGNATURE_HEX,
                    'uid': TEST_UID,
                },
            ),
        ]

        check_form(WebauthnVerifyCommitForm(), invalid_params, valid_params, None)

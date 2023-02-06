# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.takeout.forms import (
    DeleteExtractResultForm,
    FinishExtractForm,
    GetExtractResultForm,
    RequestExtractForm,
    UserInfoForm,
)
from passport.backend.utils.time import unixtime_to_datetime


class TestForms(unittest.TestCase):
    def test_user_info_form(self):
        invalid_params = [
            (
                {},
                [
                    'uid.empty',
                    'unixtime.empty',
                ],
            ),
            (
                {
                    'uid': '',
                    'unixtime': '',
                },
                [
                    'uid.empty',
                    'unixtime.empty',
                ],
            ),
            (
                {
                    'uid': 'foo',
                    'unixtime': 'bar',
                },
                [
                    'uid.invalid',
                    'unixtime.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'uid': '123',
                    'unixtime': '1',
                },
                {
                    'uid': 123,
                    'unixtime': unixtime_to_datetime(1),
                },
            ),
        ]

        check_form(UserInfoForm(), invalid_params, valid_params, None)

    def test_request_extract_form(self):
        invalid_params = [
            (
                {
                    'uid': '',
                },
                [
                    'uid.empty',
                ],
            ),
            (
                {
                    'uid': 'foo',
                },
                [
                    'uid.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {},
                {
                    'uid': None,
                },
            ),
            (
                {
                    'uid': '123',
                },
                {
                    'uid': 123,
                },
            ),
        ]

        check_form(RequestExtractForm(), invalid_params, valid_params, None)

    def test_finish_extract_form(self):
        invalid_params = [
            (
                {},
                [
                    'uid.empty',
                    'archive_s3_key.empty',
                ],
            ),
            (
                {
                    'uid': '',
                    'archive_s3_key': '',
                },
                [
                    'uid.empty',
                    'archive_s3_key.empty',
                ],
            ),
            (
                {
                    'uid': 'foo',
                    'archive_s3_key': 'bar',
                },
                [
                    'uid.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'uid': '123',
                    'archive_s3_key': 'url',
                },
                {
                    'uid': 123,
                    'archive_s3_key': 'url',
                    'archive_password': None,
                },
            ),
            (
                {
                    'uid': '123',
                    'archive_s3_key': 'url',
                    'archive_password': 'password',
                },
                {
                    'uid': 123,
                    'archive_s3_key': 'url',
                    'archive_password': 'password',
                },
            ),
        ]

        check_form(FinishExtractForm(), invalid_params, valid_params, None)

    def test_get_extract_result_form(self):
        invalid_params = [
            (
                {
                    'uid': 'foo',
                },
                [
                    'uid.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {},
                {
                    'uid': None,
                },
            ),
            (
                {
                    'uid': '123',
                },
                {
                    'uid': 123,
                },
            ),
        ]

        check_form(GetExtractResultForm(), invalid_params, valid_params, None)

    def test_delete_extract_result_form(self):
        invalid_params = [
            (
                {},
                [
                    'uid.empty',
                ],
            ),
            (
                {
                    'uid': '',
                },
                [
                    'uid.empty',
                ],
            ),
            (
                {
                    'uid': 'foo',
                },
                [
                    'uid.invalid',
                ],
            ),
        ]

        valid_params = [
            (
                {
                    'uid': '123',
                },
                {
                    'uid': 123,
                },
            ),
        ]

        check_form(DeleteExtractResultForm(), invalid_params, valid_params, None)

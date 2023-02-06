# -*- coding: utf-8 -*-
from passport.backend.perimeter_api.tests.views.base import (
    BaseViewsTestCase,
    IDMAuthTests,
)


class TestGetAllRoles(BaseViewsTestCase, IDMAuthTests):
    default_url = '/dostup/get-all-roles/'
    http_method = 'GET'
    fixtures = ['default.json']

    def test_ok(self):
        response = self.make_request()
        self.assert_response_ok(
            response,
            {
                'code': 0,
                'users': [
                    {
                        'login': 'vasya',
                        'roles': [
                            {'role': 'long'},
                            {'role': 'mdm'},
                        ],
                    },
                    {
                        'login': 'petya',
                        'roles': [
                            {'role': 'motp'},
                        ],
                    },
                    {
                        'login': 'kolya',
                        'roles': [
                            {'role': 'totp'},
                        ],
                    },
                ],
            },
        )

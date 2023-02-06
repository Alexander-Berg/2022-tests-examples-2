# -*- coding: utf-8 -*-
from passport.backend.perimeter_api.tests.views.base import (
    BaseViewsTestCase,
    IDMAuthTests,
)


class TestInfo(BaseViewsTestCase, IDMAuthTests):
    default_url = '/dostup/info/'
    http_method = 'GET'

    def test_ok(self):
        response = self.make_request()
        self.assert_response_ok(
            response,
            {
                'code': 0,
                'roles': {
                    'slug': 'role',
                    'name': 'роль',
                    'values': {
                        'long': 'Длинный пароль',
                        'mdm': 'Пароль для iOS',
                        'motp': 'Одноразовый пароль (MOTP)',
                        'totp': 'Одноразовый пароль (TOTP)',
                    },
                },
            },
        )

# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.idm.base import (
    BaseIDMTestCase,
    CommonIDMTests,
)


class IDMInfoTestCase(BaseIDMTestCase, CommonIDMTests):
    default_url = '/1/bundle/idm/info/'

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok_response(
            rv,
            roles={
                'slug': 'mail',
                'name': u'Корпоративная почта',
                'values': {
                    'cloudil': {
                        'name': {
                            'ru': u'В домене cloudil.co.il',
                            'en': u'At cloudil.co.il',
                        },
                    },
                    'ext': {
                        'name': {
                            'ru': u'В домене ext.yandex.ru',
                            'en': u'At ext.yandex.ru'
                        },
                    },
                    'k50': {
                        'name': {
                            'ru': u'В домене k50.ru',
                            'en': u'At k50.ru'
                        },
                    },
                    'meteum': {
                        'name': {
                            'ru': u'В домене meteum.ai',
                            'en': u'At meteum.ai',
                        },
                    },
                    'openyard': {
                        'name': {
                            'ru': u'В домене openyard.ru',
                            'en': u'At openyard.ru'
                        },
                    },
                    'srb.tech': {
                        'name': {
                            'ru': u'В домене srb.tech',
                            'en': u'At srb.tech',
                        },
                    },
                    'yango': {
                        'name': {
                            'ru': u'В домене yango.com',
                            'en': u'At yango.com',
                        },
                    },
                    'userver.tech': {
                        'name': {
                            'ru': u'В домене userver.tech',
                            'en': u'At userver.tech',
                        },
                    },
                    'legal.direct': {
                        'name': {
                            'ru': u'В домене legal.direct',
                            'en': u'At legal.direct',
                        },
                    },
                },
            },
        )

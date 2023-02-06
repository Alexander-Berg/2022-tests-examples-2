# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.oauth.api.api.old.utils import (
    format_response,
    get_format,
    is_passport_domain,
    strip_to_yandex_domain,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


class FormatResponseTestCase(BaseTestCase):
    def setUp(self):
        super(FormatResponseTestCase, self).setUp()
        self.data = {
            'status': 'ok',
        }
        self.data_to_convert = {
            'null': None,
            'empty': '',
            'zero': 0,
            'bool': False,
        }

    def test_json(self):
        eq_(
            format_response(self.data, format_='json'),
            ('application/json', '{"status": "ok"}'),
        )

    def test_form(self):
        eq_(
            format_response(self.data, format_='form'),
            ('application/x-www-form-urlencoded', 'status=ok'),
        )

    def test_xml(self):
        eq_(
            format_response(self.data, format_='xml'),
            ('application/xml', '<?xml version="1.0" encoding="utf-8"?>\n<OAuth>\n\t<status>ok</status>\n</OAuth>\n'),
        )

    def test_default_format(self):
        eq_(
            format_response(self.data, format_=None),
            ('application/json', '{"status": "ok"}'),
        )

    @raises(ValueError)
    def test_unknown_format(self):
        format_response(data=self.data, format_='unknown')

    def test_empty_values_json(self):
        eq_(
            format_response(self.data_to_convert, format_='json'),
            ('application/json', '{"bool": false, "empty": "", "null": null, "zero": 0}'),
        )

    def test_empty_values_xml(self):
        eq_(
            format_response(self.data_to_convert, format_='xml'),
            (
                'application/xml',
                (
                    '<?xml version="1.0" encoding="utf-8"?>\n'
                    '<OAuth>\n'
                    '\t<bool>false</bool>\n'
                    '\t<empty></empty>\n'
                    '\t<null></null>\n'
                    '\t<zero>0</zero>\n'
                    '</OAuth>\n'
                )
            ),
        )

    def test_invalid_chars_xml(self):
        eq_(
            format_response(dict(self.data, invalid='12\x0034\x0F56'), format_='xml'),
            (
                'application/xml',
                (
                    '<?xml version="1.0" encoding="utf-8"?>\n'
                    '<OAuth>\n'
                    '\t<invalid>12\x0034\x0F56</invalid>\n'
                    '\t<status>ok</status>\n'
                    '</OAuth>\n'
                )
            ),
        )


class GetFormatTestCase(BaseTestCase):
    def setUp(self):
        super(GetFormatTestCase, self).setUp()
        self.request = mock.Mock()
        self.request.GET = {}
        self.request.POST = {}

    def test_json_get(self):
        self.request.GET['format'] = 'json'
        eq_(
            get_format(self.request),
            'json',
        )

    def test_json_post(self):
        self.request.POST['format'] = 'json'
        eq_(
            get_format(self.request),
            'json',
        )

    def test_form_get(self):
        self.request.GET['format'] = 'form'
        eq_(
            get_format(self.request),
            'form',
        )

    def test_form_post(self):
        self.request.POST['format'] = 'form'
        eq_(
            get_format(self.request),
            'form',
        )

    def test_xml_get(self):
        self.request.GET['format'] = 'xml'
        eq_(
            get_format(self.request),
            'xml',
        )

    def test_xml_post(self):
        self.request.POST['format'] = 'xml'
        eq_(
            get_format(self.request),
            'xml',
        )

    def test_post_and_get_differ(self):
        self.request.GET['format'] = 'xml'
        self.request.POST['format'] = 'json'
        eq_(
            get_format(self.request),
            'xml',
        )

    def test_default_format(self):
        eq_(
            get_format(self.request),
            'json',
        )

    def test_unknown_format(self):
        self.request.GET['format'] = 'unknown'
        eq_(
            get_format(self.request),
            'json',
        )


class StripToYandexDomainTestCase(BaseTestCase):
    def test_ok(self):
        for from_, to_ in (
            ('yandex.ru', 'yandex.ru'),
            ('yandex.com.tr', 'yandex.com.tr'),
            ('yandex-team.ru', 'yandex-team.ru'),
            ('passport.yandex.ru', 'yandex.ru'),
            ('passport.yandex.com.tr', 'yandex.com.tr'),
            ('passport.yandex-team.ru', 'yandex-team.ru'),
            ('mail.yandex.ru', 'yandex.ru'),
            ('mail.yandex.com.tr', 'yandex.com.tr'),
            ('mail.yandex-team.ru', 'yandex-team.ru'),
            ('google.com', 'google.com'),
            ('mail.google.com', 'mail.google.com'),
        ):
            eq_(strip_to_yandex_domain(from_), to_)


class IsPassportDomainTestCase(BaseTestCase):
    def test_true(self):
        for host in (
            'passport.yandex.ru',
            'passport.yandex.com.tr',
            'passport.yandex-team.ru',
            'smth.passport.yandex.ru',
        ):
            ok_(is_passport_domain(host))

    def test_false(self):
        for host in (
            'yandex.ru',
            'passport.yandex.smth.yandex.ru',
            'passport.ru',
            'google.com',
            'mail.google.com',
        ):
            ok_(not is_passport_domain(host))

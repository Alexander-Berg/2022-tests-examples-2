# -*- coding: utf-8 -*-

from functools import partial

from flask import request
from nose.tools import eq_
from passport.backend.api.common.decorators import (
    get_request_files,
    get_request_values,
    secure_filename,
)
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.file import File
from six import BytesIO


@with_settings_hosts()
class TestGetFormParams(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env

    def test_empty_values(self):
        params = [
            {'path': '/1/questions/', 'method': 'GET'},
            {'path': '/1/questions/', 'method': 'POST'},
            {'path': '/1/questions/', 'method': 'PUT'},
            {'path': '/1/questions/', 'method': 'DELETE'},
        ]

        for p in params:
            with self.env.client.application.test_request_context(**p):
                eq_(get_request_values(), {})

    def test_methods(self):
        params = [
            ({'path': '/1/questions/?consumer=dev', 'method': 'GET'},
             {'consumer': 'dev'}),
            ({'path': '/1/questions/', 'method': 'GET', 'query_string': 'consumer=dev'},
             {'consumer': 'dev'}),
            ({'path': '/1/questions/', 'method': 'GET',
              'data': {'consumer': 'dev', 'test': 'test'}},
             {}),
            ({'path': '/1/account/?consumer=dev', 'method': 'POST'},
             {'consumer': 'dev'}),
            ({'path': '/1/account/', 'method': 'POST', 'query_string': 'consumer=dev'},
             {'consumer': 'dev'}),
            ({'path': '/1/account/', 'method': 'POST', 'data': {'consumer': 'dev'}},
             {}),
            ({'path': '/1/account/?consumer=dev', 'method': 'POST', 'data': {'consumer': 'mail'}},
             {'consumer': 'dev'}),
            ({'path': '/1/questions/', 'method': 'DELETE',
              'data': {'consumer': 'dev', 'test': 'test'},
              'query_string': 'test2=test2'},
             {'test2': 'test2'}),
        ]
        for p, result in params:
            with self.env.client.application.test_request_context(**p):
                eq_(request.method, p['method'])
                values = get_request_values()
                eq_(values, result, [values, result, p])

    def test_files(self):
        params = [
            ({'method': 'GET',
              'data': {}},
             {}),
            ({'method': 'GET',
              'data': {'file': (BytesIO(b'data'), 'filename')}},
             {}),
            ({'method': 'POST',
              'data': {}},
             {}),
            ({'method': 'POST',
              'data': {'file': (BytesIO(b'data'), 'filename')}},
             {'file': (File('filename', BytesIO(b'data')),)}),
            ({'method': 'POST',
              'data': {'file1': (BytesIO(b'data'), 'filename'),
                       'file2': (BytesIO(b'data2'), 'filename2')}},
             {'file1': (File('filename', BytesIO(b'data')),),
              'file2': (File('filename2', BytesIO(b'data2')),)}),
            ({'method': 'DELETE',
              'data': {}},
             {}),
            ({'method': 'DELETE',
              'data': {'file': (BytesIO(b'data'), 'filename')}},
             {}),
        ]
        for p, result in params:
            with self.env.client.application.test_request_context(**p):
                files = get_request_files()
                eq_(files, result, [files, result, p])


def test_secure_filename():
    secure_utf8 = partial(secure_filename, file_system_encoding=u'utf-8')

    eq_(secure_utf8(u'My cool movie.mov'), u'My_cool_movie.mov')
    eq_(secure_utf8(u'../../../etc/passwd'), u'etc_passwd')
    eq_(
        secure_utf8(u'i contain cool \xfcml\xe4uts.txt'),
        u'i_contain_cool_umlauts.txt',
    )
    eq_(secure_utf8(u'привет.jpg'), u'привет.jpg')
    eq_(secure_utf8(u'../.././/привет/паспорт.jpg'), u'привет_паспорт.jpg')

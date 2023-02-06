# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestRetPathValidation(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'retpath': ['validate']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def retpath_validation_request(self, data):
        return self.env.client.post('/1/validation/retpath/?consumer=dev', data=data)

    def test_bad_request(self):
        response = self.retpath_validation_request({})
        eq_(response.status_code, 400)

    def test_ok(self):
        rv = self.retpath_validation_request({'retpath': '//yandex.ru'})
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'retpath': '//yandex.ru'})

    def test_notin(self):
        rv = self.retpath_validation_request({'retpath': '//tut_yandexa.net'})
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'retpath',
                'message': 'Url "//tut_yandexa.net" is not in allowed hosts range',
                'code': 'notin',
            }]
        )

    def test_nohost(self):
        rv = self.retpath_validation_request({'retpath': 'yandex.ru'})
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'retpath',
                'message': 'Can\'t find hostname after "//" in "yandex.ru"',
                'code': 'nohost',
            }]
        )

    def test_track_valid_data(self):
        self.retpath_validation_request({
            'retpath': 'https://yandex.ru',
            'track_id': self.track_id,
        })
        rv = self.retpath_validation_request({
            'retpath': 'https://yandex.ru',
            'track_id': self.track_id,
        })

        eq_(json.loads(rv.data), {'status': 'ok', 'retpath': 'https://yandex.ru'})

        track = self.track_manager.read(self.track_id)
        eq_(track.retpath, 'https://yandex.ru')
        eq_(track.retpath_validation_count.get(), 2)

    def test_track_invalid_data(self):
        self.retpath_validation_request({
            'retpath': 'https://blabla.ru',
            'track_id': self.track_id,
        })
        rv = self.retpath_validation_request({
            'retpath': 'https://blabla.ru',
            'track_id': self.track_id,
        })

        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'retpath',
                'message': 'Url "https://blabla.ru" is not in allowed hosts range',
                'code': 'notin',
            }]
        )

        track = self.track_manager.read(self.track_id)
        ok_(track.retpath is None)
        eq_(track.retpath_validation_count.get(), 2)

    @parameterized.expand([
        ('morda://yandex.ru', 'morda://yandex.ru'),
        ('viewport://?text=foo', 'viewport:?text=foo'),
        ('yandexmusic://profile', 'yandexmusic://profile'),
        ('ya-search-app-open://smth', 'ya-search-app-open://smth'),
        ('yamb://smth', 'yamb://smth'),
    ])
    def test_additional_scheme(self, retpath_in, retpath_out):
        rv = self.retpath_validation_request({'retpath': retpath_in})
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'retpath': retpath_out})

# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestHintValidation(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'hint': ['validate']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def hint_request(self, **kwargs):
        return self.env.client.post(
            '/1/validation/hint/?consumer=dev', **kwargs
        )

    def test_bad_request(self):
        response = self.hint_request()
        eq_(response.status_code, 400)

    def test_ok(self):
        rv = self.hint_request(
            data={
                'hint_question': u'Я' * 37,
                'hint_answer': u'Я' * 30,
            },
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'hint_question': u'Я' * 37,
                'hint_answer': u'Я' * 30,
            },
        )

    def test_ok_by_id(self):
        rv = self.hint_request(
            data={
                'hint_question_id': u'1',
                'hint_answer': u'Я' * 30,
            },
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'hint_question_id': 1,
                'hint_answer': u'Я' * 30,
            },
        )

    def test_ok_only_answer(self):
        rv = self.hint_request(
            data={
                'hint_answer': u'Я' * 30,
            },
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'hint_answer': u'Я' * 30,
            },
        )

    def test_ok_only_question(self):
        rv = self.hint_request(
            data={
                'hint_question': u'Я' * 37,
            },
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'hint_question': u'Я' * 37,
            },
        )

    def test_ok_only_question_id(self):
        rv = self.hint_request(
            data={
                'hint_question_id': u'1',
            },
        )
        eq_(rv.status_code, 200)
        eq_(
            json.loads(rv.data),
            {
                'status': 'ok',
                'hint_question_id': 1,
            },
        )

    def test_bad_question_toolong(self):
        rv = self.hint_request(
            data={
                'hint_question': 'X' * 38,
                'hint_answer': u'Я' * 30,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'hint_question',
                'message': 'Enter a value not more than 37 characters long',
                'code': 'toolong',
            }],
        )

    def test_bad_question_empty(self):
        rv = self.hint_request(
            data={
                'hint_question': '',
                'hint_answer': u'Я' * 30,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'hint_question',
                'message': 'Please enter a value',
                'code': 'empty',
            }],
        )

    def test_bad_question_id_toohigh(self):
        rv = self.hint_request(
            data={
                'hint_question_id': '99',
                'hint_answer': u'Я' * 30,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'hint_question_id',
                'message': 'Please enter a number that is 19 or smaller',
                'code': 'toohigh',
            }],
        )

    def test_bad_question_id_toolow(self):
        rv = self.hint_request(
            data={
                'hint_question_id': '0',
                'hint_answer': u'Я' * 30,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'hint_question_id',
                'message': 'Please enter a number that is 1 or greater',
                'code': 'toolow',
            }],
        )

    def test_bad_answer_toolong(self):
        rv = self.hint_request(
            data={
                'hint_question_id': '1',
                'hint_answer': u'Я' * 31,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'hint_answer',
                'message': 'Enter a value not more than 30 characters long',
                'code': 'toolong',
            }],
        )

    def test_bad_answer_empty(self):
        rv = self.hint_request(
            data={
                'hint_question_id': '1',
                'hint_answer': '',
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(
            response['validation_errors'],
            [{
                'field': 'hint_answer',
                'message': 'Please enter a value',
                'code': 'empty',
            }],
        )

    def test_track_content(self):
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            for _ in range(5):
                track.hint_validation_count.incr()

        rv = self.hint_request(
            data={
                'hint_question': u'Я' * 37,
                'hint_answer': u'Я' * 30,
                'track_id': self.track_id,
            },
        )

        eq_(rv.status_code, 200)

        track = self.track_manager.read(self.track_id)
        eq_(track.hint_validation_count.get(), 6)

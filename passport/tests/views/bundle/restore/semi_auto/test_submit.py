# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.api.tests.views.bundle.restore.semi_auto.base.test_base import BaseTestRestoreSemiAutoView
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import (
    PhoneNumber,
    TEST_APP_ID,
    TEST_DEFAULT_HINT_ANSWER,
    TEST_DEFAULT_HINT_QUESTION,
    TEST_DEFAULT_LOGIN,
    TEST_EMAIL,
    TEST_PHONE,
    TEST_REQUEST_SOURCE,
)
from passport.backend.api.views.bundle.restore.semi_auto.base import MULTISTEP_FORM_VERSION
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from six import string_types


eq_ = iterdiff(eq_)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
)
class TestRestoreSemiAutoSubmitView(BaseTestRestoreSemiAutoView):
    def setUp(self):
        super(TestRestoreSemiAutoSubmitView, self).setUp()
        self.env.statbox.bind_entry(
            'track_created',
            action='track_created',
            _exclude=['uid'],
            version=MULTISTEP_FORM_VERSION,
        )

        self.default_url = '/1/bundle/restore/semi_auto/submit/?consumer=dev'
        track = self.track_manager.read(self.track_id)
        self.orig_track = track.snapshot()

    def tearDown(self):
        del self.orig_track
        super(TestRestoreSemiAutoSubmitView, self).tearDown()

    def assert_track_ok(self, **params):
        """Трек заполнен полностью и корректно"""
        track = self.track_manager.read(self.track_id)
        for attr_name, value in params.items():
            actual_value = getattr(track, attr_name)
            expected_value = str(value) if not isinstance(value, (string_types, bool)) else value
            eq_(actual_value, expected_value, [attr_name, actual_value, expected_value])

    def test_submit_works(self):
        """Проверяем создание трека и возврат track_id"""
        resp = self.make_request(
            dict(
                login=TEST_DEFAULT_LOGIN,
                email=TEST_EMAIL,
                phone_number=TEST_PHONE,
                question=TEST_DEFAULT_HINT_QUESTION,
                answer=TEST_DEFAULT_HINT_ANSWER,
            ),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            user_entered_email=TEST_EMAIL,
            user_entered_question=TEST_DEFAULT_HINT_QUESTION,
            user_entered_answer=TEST_DEFAULT_HINT_ANSWER,
            user_entered_phone_number=PhoneNumber.parse(TEST_PHONE),
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_for_learning=False,
        )
        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'track_created',
                request_source=TEST_REQUEST_SOURCE,
                is_for_learning='0',
            ),
        ])

    def test_submit_works_with_cyrillic(self):
        resp = self.make_request(
            dict(
                login=TEST_DEFAULT_LOGIN,
                email=TEST_EMAIL,
                phone_number=TEST_PHONE,
                question=u'99:вопрос',
                answer=u'ответ',
            ),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            user_entered_email=TEST_EMAIL,
            user_entered_question=u'99:вопрос',
            user_entered_answer=u'ответ',
            user_entered_phone_number=PhoneNumber.parse(TEST_PHONE),
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_for_learning=False,
        )

    def test_submit_works_with_app_id(self):
        resp = self.make_request(
            dict(
                login=TEST_DEFAULT_LOGIN,
                email=TEST_EMAIL,
                phone_number=TEST_PHONE,
                question=TEST_DEFAULT_HINT_QUESTION,
                answer=TEST_DEFAULT_HINT_ANSWER,
                app_id=TEST_APP_ID,
            ),
            self.get_headers(),
        )

        self.assert_ok_response(resp, track_id=self.track_id)

        self.assert_track_ok(
            user_entered_login=TEST_DEFAULT_LOGIN,
            user_entered_email=TEST_EMAIL,
            user_entered_question=TEST_DEFAULT_HINT_QUESTION,
            user_entered_answer=TEST_DEFAULT_HINT_ANSWER,
            user_entered_phone_number=PhoneNumber.parse(TEST_PHONE),
            request_source=TEST_REQUEST_SOURCE,
            version=MULTISTEP_FORM_VERSION,
            is_for_learning=False,
            device_application=TEST_APP_ID,
        )

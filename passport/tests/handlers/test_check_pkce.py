# -*- coding: utf-8 -*-

import json

from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.pkce import (
    PKCE_METHOD_PLAIN,
    PKCE_METHOD_S256,
    s256,
)
from passport.backend.social.common.task import (
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_NAME1,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    PKCE_CODE_CHALLENGE1,
    PKCE_CODE_CHALLENGE2,
    PKCE_CODE_VERIFIER1,
    TASK_ID1,
    TASK_ID2,
)


CONF_APPLICATIONS = [
    dict(
        application_id=APPLICATION_ID1,
        application_name=APPLICATION_NAME1,
        provider_client_id=EXTERNAL_APPLICATION_ID1,
    ),
]


class TestCheckPkce(TestCase):
    def setUp(self):
        super(TestCheckPkce, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['check-pkce'])

    def build_settings(self):
        conf = super(TestCheckPkce, self).build_settings()
        conf.update(
            dict(
                applications=CONF_APPLICATIONS,
            ),
        )
        return conf

    DEFAULT_TASK_APPLICATION = Application(identifier=APPLICATION_ID1, name=APPLICATION_NAME1)

    def _build_task(self,
                    application=DEFAULT_TASK_APPLICATION,
                    task_id=TASK_ID1,
                    code_challenge=PKCE_CODE_CHALLENGE1,
                    code_challenge_method=PKCE_METHOD_PLAIN):
        task = Task()
        task.application = application
        task.access_token = {}

        task.created = 1.0
        task.finished = now.f()
        task.task_id = task_id
        task.code_challenge = code_challenge
        task.code_challenge_method = code_challenge_method
        return task

    def _setup_task(self, task):
        save_task_to_redis(self._fake_redis, task.task_id, task)

    def _make_request(self, task_id=TASK_ID1, code_verifier=PKCE_CODE_VERIFIER1):
        return self._client.post(
            '/check_pkce',
            data=dict(
                task_id=task_id,
                code_verifier=code_verifier,
                consumer=CONSUMER1,
            ),
            headers={'X-Real-Ip': CONSUMER_IP1},
        )

    def _assert_ok_response(self, rv, expected=None):
        self.assertEqual(rv.status_code, 200)

        expected = build_dict_from_standard(
            standard=dict(status='ok'),
            values=expected or dict(),
        )

        rv = json.loads(rv.data)
        self.assertEqual(rv, expected)

    def _assert_error_response(self, rv, expected):
        rv = json.loads(rv.data)

        self.assertIn('error', rv)
        self.assertEqual(rv['error']['code'], expected[0])

    def test_task_id_invalid(self):
        self._setup_task(self._build_task())

        rv = self._make_request(task_id='a' * 200)
        self._assert_error_response(rv, ['TaskIdInvalidError'])

    def test_task_not_found(self):
        self._setup_task(self._build_task())

        rv = self._make_request(task_id=TASK_ID2)
        self._assert_error_response(rv, ['TaskNotFoundError'])

    def test_code_verifier_too_long(self):
        self._setup_task(
            self._build_task(
                code_challenge='1' * 129,
                code_challenge_method=PKCE_METHOD_PLAIN,
            ),
        )

        rv = self._make_request(code_verifier='1' * 129)

        self._assert_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_not_required(self):
        self._setup_task(
            self._build_task(
                code_challenge='',
                code_challenge_method='',
            ),
        )

        rv = self._make_request(code_verifier=None)
        self._assert_ok_response(rv)

    def test_code_verifier_not_required_but_passed(self):
        self._setup_task(
            self._build_task(
                code_challenge='',
                code_challenge_method='',
            ),
        )

        rv = self._make_request(code_verifier=PKCE_CODE_CHALLENGE1)
        self._assert_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_required_but_missing(self):
        self._setup_task(self._build_task())

        rv = self._make_request(code_verifier=None)
        self._assert_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_plain_invalid(self):
        self._setup_task(
            self._build_task(
                code_challenge=PKCE_CODE_CHALLENGE1,
                code_challenge_method=PKCE_METHOD_PLAIN,
            ),
        )

        rv = self._make_request(code_verifier=PKCE_CODE_CHALLENGE2)

        self._assert_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_plain_valid(self):
        self._setup_task(
            self._build_task(
                code_challenge=PKCE_CODE_CHALLENGE1,
                code_challenge_method=PKCE_METHOD_PLAIN,
            ),
        )

        rv = self._make_request(code_verifier=PKCE_CODE_CHALLENGE1)

        self._assert_ok_response(rv)

    def test_code_verifier_s256_invalid(self):
        self._setup_task(
            self._build_task(
                code_challenge=s256(PKCE_CODE_CHALLENGE2),
                code_challenge_method=PKCE_METHOD_S256,
            ),
        )

        rv = self._make_request(code_verifier=PKCE_CODE_CHALLENGE1)

        self._assert_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_s256_valid(self):
        self._setup_task(
            self._build_task(
                code_challenge=s256(PKCE_CODE_CHALLENGE2),
                code_challenge_method=PKCE_METHOD_S256,
            ),
        )

        rv = self._make_request(code_verifier=PKCE_CODE_CHALLENGE2)

        self._assert_ok_response(rv)

# -*- coding: utf-8 -*-

import json

import mock
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_UID1
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts(
    ACCOUNT_DELETER_PATH='/usr/bin/account_deleter',
)
class TestFinishAccountDeletion(BaseBundleTestViews):
    def setUp(self):
        super(TestFinishAccountDeletion, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value({
            'dev': {
                'networks': ['127.0.0.1'],
                'grants': {'internal': ['finish_account_deletion']},
            },
        })

        self._subprocess_patch = mock.patch('passport.backend.api.views.bundle.internal.controllers.subprocess')
        fake_subprocess = self._subprocess_patch.start()

        self._path_patch = mock.patch('passport.backend.api.views.bundle.internal.controllers.path')
        self._fake_path = self._path_patch.start()

        self._fake_process = fake_subprocess.Popen.return_value
        self._fake_process.communicate.return_value = (json.dumps([]), '')
        self._fake_process.returncode = 0

        self._fake_path.exists.return_value = True

    def tearDown(self):
        self._path_patch.stop()
        self._subprocess_patch.stop()
        self.env.stop()
        del self._path_patch
        del self._subprocess_patch
        del self._fake_path
        del self._fake_process
        del self.env
        super(TestFinishAccountDeletion, self).tearDown()

    def _make_request(self, uid=TEST_UID1):
        return self.env.client.post(
            '/1/bundle/test/finish_account_deletion/',
            query_string={'consumer': 'dev'},
            data={'uid': uid},
        )

    def test_ok(self):
        self._fake_process.communicate.return_value = (
            json.dumps([{'status': 'deleted', 'uid': TEST_UID1}]),
            '',
        )
        rv = self._make_request()
        self.assert_ok_response(rv, uids=[{'status': 'deleted', 'uid': TEST_UID1}])

    def test_fail(self):
        self._fake_process.returncode = 1
        rv = self._make_request()
        self.assert_error_response(rv, ['account_deletion.failed'])

    def test_temporary_error(self):
        self._fake_process.communicate.return_value = (
            '',
            'some-output',
        )
        rv = self._make_request()
        self.assert_error_response(rv, ['account_deletion.temporary_error'])

    def test_no_uid(self):
        rv = self._make_request(uid=None)
        self.assert_error_response(rv, ['uid.empty'])

    def test_deleter_not_found(self):
        self._fake_path.exists.return_value = False
        rv = self._make_request()
        self.assert_error_response(rv, ['account_deletion.failed'])

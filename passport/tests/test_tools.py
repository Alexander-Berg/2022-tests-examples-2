# -*- coding: utf-8 -*-
import os
import time

import mock
from nose.tools import raises, eq_, ok_
from django.test import TestCase

from passport_grants_configurator.apps.core.exceptions import SubprocessTimedOut
from passport_grants_configurator.apps.core.tools.cvs import cvs_checkout

TEST_URL = 'http://localhost/'
TEST_DIR = '/tmp'
TEST_TIMEOUT = 1
TEST_RETURN_CODE = 0


def fake_select(*args):
    time.sleep(TEST_TIMEOUT + 1)
    return [], [], []


class ProcessWithTimeoutTestCase(TestCase):

    import_path = 'passport_grants_configurator.apps.core.tools.cvs.%s'

    def setUp(self):
        self.stdout = os.tmpfile()
        self.stderr = os.tmpfile()

        self.popen_mock = mock.Mock(
            stdout=self.stdout,
            stderr=self.stderr,
            poll=mock.Mock(return_value=TEST_RETURN_CODE),
        )

        self.popen_patch = mock.patch(
            self.import_path % 'subprocess.Popen',
            mock.Mock(return_value=self.popen_mock),
        )
        self.popen_patch.start()

    def tearDown(self):
        self.popen_patch.stop()

        self.stdout.close()
        self.stderr.close()

    def setup_stdout_and_stderr(self):
        self.popen_mock.stdout = open('/dev/null')
        self.popen_mock.stderr = open('/dev/null')

    def assert_process_terminated(self):
        ok_(self.popen_mock.kill.called)
        ok_(self.popen_mock.wait.called)

    def test_ok(self):
        """Хороший сценарий - подпроцесс что-то ответил и завершился с каким-то кодом"""
        self.setup_stdout_and_stderr()

        with self.settings(ENABLE_CVS_CHECKOUT=True):
            out, err = cvs_checkout(TEST_URL, TEST_DIR, timeout=TEST_TIMEOUT)

        # Это прочитали из /dev/null
        eq_(out, '')
        eq_(err, '')

    def test_timed_out(self):
        """Плохой сценарий - подпроцесс не отвечает за указанное время - завершаем его"""
        self.popen_mock.poll = mock.Mock(return_value=None)
        select_patch = mock.patch(
            self.import_path % 'select.select',
            mock.Mock(side_effect=fake_select),
        )

        with self.settings(ENABLE_CVS_CHECKOUT=True), select_patch:
            self.assertRaises(
                SubprocessTimedOut,
                cvs_checkout,
                TEST_URL,
                TEST_DIR,
                timeout=TEST_TIMEOUT,
            )

        self.assert_process_terminated()

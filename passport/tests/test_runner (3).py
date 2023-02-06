# -*- coding: utf-8 -*-
import mock
from passport.backend.core.test.test_utils import PassportTestCase
from passport.backend.logbroker_client.core.run import (
    Runner,
    TEST_MESSAGE_DELIMITER,
)


class TestRunner(PassportTestCase):
    def setUp(self):
        self.patches = []

        self._config = {}
        self.patches.append(mock.patch.object(Runner, 'config', self._config))

        self._handler = mock.Mock()
        self.patches.append(mock.patch.object(
            Runner,
            'instantiate_handler',
            lambda _: self._handler,
        ))

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()

    def get_runner(self):
        return Runner(None)

    def gen_lines(self, *lines):
        return (line + '\n' for line in lines)

    def test_run_tests__in_file__ok(self):
        in_file = self.gen_lines(
            TEST_MESSAGE_DELIMITER,
            'str1',
            'строка2',
            '',
            'str3',
            TEST_MESSAGE_DELIMITER,
            'str4',
            TEST_MESSAGE_DELIMITER + 'str5',
            'str6' + TEST_MESSAGE_DELIMITER,
            'str7',
            TEST_MESSAGE_DELIMITER,
        )
        self.get_runner().run_test_mode(in_file, None)
        self.assertEqual(self._handler.test_data.call_count, 3)
        self._handler.test_data.assert_has_calls([
            mock.call(''),
            mock.call('str1\nстрока2\n\nstr3\n'),
            mock.call(
                'str4\n' + TEST_MESSAGE_DELIMITER + 'str5\nstr6' +
                TEST_MESSAGE_DELIMITER + '\nstr7\n'
            ),
        ])

    def test_run_tests__stdin__ok(self):
        stdin = self.gen_lines('str1')
        with mock.patch(
            'passport.backend.logbroker_client.core.run.sys', mock.Mock(stdin=stdin),
        ):
            self.get_runner().run_test_mode(None, None)
        self._handler.test_data.assert_called_once_with('str1\n')

    def test_run_tests__data__ok(self):
        self.get_runner().run_test_mode(None, 'some_data')
        self._handler.test_data.assert_called_once_with('some_data')

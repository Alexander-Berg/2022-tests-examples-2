import json
import os
from time import time

import mock
from passport.backend.tvm_keyring import settings
from passport.backend.tvm_keyring.test.base import BaseTestCase
from passport.backend.tvm_keyring.test.base_test_data import (
    TEST_CONFIG_1_CONTENTS,
    TEST_CONFIG_1_NAME,
    TEST_CONFIG_2_CONTENTS,
    TEST_CONFIG_2_NAME,
    TEST_JUNK_RESULT_FILENAME,
    TEST_KEYS_FILENAME,
    TEST_RESULT_1,
    TEST_RESULT_1_FILENAME,
    TEST_RESULT_2,
    TEST_RESULT_2_FILENAME,
    TEST_TVM_KEYS,
)
from passport.backend.tvm_keyring.test.fake_tvm import tvm_ticket_response
from passport.backend.tvm_keyring.validate import validate


TEST_SUCCESSFUL_RESPONSE = '0;OK'


class ValidateTestCase(BaseTestCase):
    def setUp(self):
        super(ValidateTestCase, self).setUp()
        self.fake_fs.create_dir(settings.RESULT_PATH)
        self.fake_fs.create_file(
            os.path.join(settings.CONFIG_PATH, TEST_CONFIG_1_NAME),
            contents=json.dumps(TEST_CONFIG_1_CONTENTS),
        )
        self.fake_fs.create_file(
            os.path.join(settings.CONFIG_PATH, TEST_CONFIG_2_NAME),
            contents=json.dumps(TEST_CONFIG_2_CONTENTS),
        )
        self.fake_fs.create_file(
            TEST_KEYS_FILENAME,
            contents=TEST_TVM_KEYS,
        )
        self.fake_fs.create_file(
            TEST_RESULT_1_FILENAME,
            contents=TEST_RESULT_1,
        )
        self.fake_fs.create_file(
            TEST_RESULT_2_FILENAME,
            contents=TEST_RESULT_2,
        )
        self.fake_fs.create_file(
            TEST_JUNK_RESULT_FILENAME,
            contents='{}',
        )

    def test_ok(self):
        assert validate() == TEST_SUCCESSFUL_RESPONSE

    def test_secret_missing_ok(self):
        with open(TEST_RESULT_1_FILENAME, 'w') as f:
            json.dump({'client_id': 1}, f)
        assert validate() == TEST_SUCCESSFUL_RESPONSE

    def test_keys_not_found(self):
        self.fake_fs.remove_object(TEST_KEYS_FILENAME)
        assert validate() == '2;Cannot read keys: [Errno 2] No such file or directory in the fake filesystem: \'%s\'' % (
            TEST_KEYS_FILENAME,
        )

    def test_keys_invalid(self):
        with open(TEST_KEYS_FILENAME, 'w') as f:
            f.write('keys')
        assert validate() == '2;Failed to create context with downloaded keys: Malformed TVM keys'

    def test_keys_expire_soon(self):
        os.utime(TEST_KEYS_FILENAME, (0, time() - settings.MAX_KEYS_AGE_WARN - 100))
        assert validate() == '1;Keys are to expire soon'

    def test_keys_outdated(self):
        os.utime(TEST_KEYS_FILENAME, (0, time() - settings.MAX_KEYS_AGE_CRIT - 100))
        assert validate() == '2;Keys outdated'

    def test_tickets_not_found(self):
        self.fake_fs.remove_object(TEST_RESULT_1_FILENAME)
        actual = validate()
        expected = '2;[%s] Cannot read tickets: [Errno 2] No such file or directory in the fake filesystem: \'%s\'' % (
            TEST_CONFIG_1_NAME,
            TEST_RESULT_1_FILENAME,
        )
        assert actual == expected

    def test_tickets_malformed(self):
        with open(TEST_RESULT_1_FILENAME, 'w') as f:
            f.write('not-a-json')
        actual = validate()
        expected = '2;[%s] Bad JSON in tickets: Expecting value: line 1 column 1 (char 0)' % TEST_CONFIG_1_NAME
        assert actual == expected

    def test_tickets_expire_soon(self):
        os.utime(TEST_RESULT_1_FILENAME, (0, time() - settings.MAX_TICKETS_AGE_WARN - 100))
        assert validate() == '1;[%s] Tickets are to expire soon' % TEST_CONFIG_1_NAME

    def test_tickets_outdated(self):
        os.utime(TEST_RESULT_1_FILENAME, (0, time() - settings.MAX_TICKETS_AGE_CRIT - 100))
        assert validate() == '2;[%s] Tickets outdated' % TEST_CONFIG_1_NAME

    def test_client_credentials_missing(self):
        result = json.loads(TEST_RESULT_1)
        result.pop('client_secret')
        with open(TEST_RESULT_1_FILENAME, 'w') as f:
            json.dump(result, f)

        assert validate() == '2;[%s] Client credentials missing in result' % TEST_CONFIG_1_NAME

    def test_ticket_missing(self):
        result = json.loads(TEST_RESULT_1)
        result['tickets'] = json.loads(tvm_ticket_response({}, dst_to_error={'2': 'segfault'}))
        with open(TEST_RESULT_1_FILENAME, 'w') as f:
            json.dump(result, f)

        assert validate() == '2;[%s] Ticket missing for dst=2: segfault' % TEST_CONFIG_1_NAME

    def test_unhandled_error(self):
        self.fake_fs.pause()
        with mock.patch('builtins.open', mock.Mock(side_effect=RuntimeError('GC segfault'))):
            assert validate() == '2;Unhandled error: GC segfault'

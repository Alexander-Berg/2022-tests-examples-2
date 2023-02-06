from io import StringIO
import json
import os
import sys

import mock
from passport.backend.tvm_keyring import settings
from passport.backend.tvm_keyring.main import main
from passport.backend.tvm_keyring.test.base import BaseTestCase
from passport.backend.tvm_keyring.test.base_test_data import (
    TEST_CONFIG_1_CONTENTS,
    TEST_CONFIG_1_NAME,
    TEST_CONFIG_2_CONTENTS,
    TEST_CONFIG_2_NAME,
    TEST_TVM_KEYS,
)
from passport.backend.tvm_keyring.test.fake_tvm import tvm_ticket_response


class IntegrationalTestCase(BaseTestCase):
    def setUp(self):
        super(IntegrationalTestCase, self).setUp()
        self.fake_fs.create_dir(settings.RESULT_PATH)

        # подстилка для ci.yandex-team.ru
        # там LOG_PATH не пустой, а на ноутбуке или на девмашине - пустой
        if settings.LOG_PATH:
            self.fake_fs.create_dir(settings.LOG_PATH)

        self.fake_fs.create_file(
            os.path.join(settings.CONFIG_PATH, TEST_CONFIG_1_NAME),
            contents=json.dumps(TEST_CONFIG_1_CONTENTS),
        )
        self.fake_fs.create_file(
            os.path.join(settings.CONFIG_PATH, TEST_CONFIG_2_NAME),
            contents=json.dumps(TEST_CONFIG_2_CONTENTS),
        )

        self.fake_tvm.set_response_side_effect([
            TEST_TVM_KEYS,
            tvm_ticket_response({'2': 'ticket2'}),
            tvm_ticket_response({'1': 'ticket1', '3': 'ticket3', '4': 'ticket4'}),
        ])

    def test_ok(self):
        with mock.patch.object(sys, 'stdout', new=StringIO()) as fake_output:
            with mock.patch.object(sys, 'argv', ['__main__', 'update']):
                main()
            with mock.patch.object(sys, 'argv', ['__main__', 'validate']):
                main()
        assert fake_output.getvalue().strip() == '0;OK'

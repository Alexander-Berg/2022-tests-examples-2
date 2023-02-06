import json
import os
import stat
from time import time

import mock
from passport.backend.tvm_keyring import settings
from passport.backend.tvm_keyring.exceptions import TVMPermanentError
from passport.backend.tvm_keyring.test.base import BaseTestCase
from passport.backend.tvm_keyring.test.base_test_data import (
    TEST_CONFIG_1_CONTENTS,
    TEST_CONFIG_1_NAME,
    TEST_CONFIG_2_CONTENTS,
    TEST_CONFIG_2_NAME,
    TEST_JUNK_RESULT_FILENAME,
    TEST_JUNK_RESULT_NAME,
    TEST_KEYS_FILENAME,
    TEST_RESULT_1,
    TEST_RESULT_1_FILENAME,
    TEST_RESULT_2,
    TEST_RESULT_2_FILENAME,
    TEST_TVM_KEYS,
)
from passport.backend.tvm_keyring.test.fake_tvm import tvm_ticket_response
from passport.backend.tvm_keyring.update import update


class UpdateTestCase(BaseTestCase):
    def setUp(self):
        super(UpdateTestCase, self).setUp()
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
            TEST_JUNK_RESULT_FILENAME,
            contents='{}',
        )

        self.fake_tvm.set_response_side_effect([
            TEST_TVM_KEYS,
            tvm_ticket_response({'2': 'ticket2'}),
            tvm_ticket_response({'1': 'ticket1', '3': 'ticket3', '4': 'ticket4'}),
        ])

    def _assert_result_filenames_equal(self, filenames):
        assert set(os.listdir(settings.RESULT_PATH)) == set(filenames)

    def _check_permissions(self, filename, expected_permissions):
        # по 3 бита на стандартные юниксовые права all, group и other
        # итого 9 бит, или 0o777, что одно и то же
        file_permissions = os.stat(filename)[stat.ST_MODE] & 0o777
        assert oct(file_permissions) == oct(expected_permissions)

    def _check_change_file_owner_call(self, owner, group, call_index=0):
        assert self.getpwnam_mock.call_args_list[call_index][0] == (owner, )
        assert self.getgrnam_mock.call_args_list[call_index][0] == (group, )

    def check_ok(self, keys_content=TEST_TVM_KEYS.decode('utf-8'), result_1_content=TEST_RESULT_1, result_2_content=TEST_RESULT_2,
                 junk_left=False, result_owner=None, result_group=None, result_permissions=None, tvm_call_count=3,
                 change_file_owner_call_count=3):
        expected_filenames = []
        if keys_content is not None:
            expected_filenames.append('tvm.keys')
        if result_1_content is not None:
            expected_filenames.append('%s.tickets' % TEST_CONFIG_1_NAME)
        if result_2_content is not None:
            expected_filenames.append('%s.tickets' % TEST_CONFIG_2_NAME)
        if junk_left:
            expected_filenames.append(TEST_JUNK_RESULT_NAME)
        if result_owner is None:
            result_owner = settings.RESULT_TICKETS_DEFAULT_OWNER
        if result_group is None:
            result_group = settings.RESULT_TICKETS_DEFAULT_GROUP
        if result_permissions is None:
            result_permissions = settings.RESULT_TICKETS_DEFAULT_PERMISSIONS

        self._assert_result_filenames_equal(expected_filenames)

        if keys_content is not None:
            with open(TEST_KEYS_FILENAME) as f:
                assert f.read() == keys_content
            self._check_permissions(
                TEST_KEYS_FILENAME,
                expected_permissions=settings.RESULT_KEYS_PERMISSIONS,
            )
            if change_file_owner_call_count >= 1:
                self._check_change_file_owner_call(
                    owner=settings.RESULT_KEYS_OWNER,
                    group=settings.RESULT_KEYS_GROUP,
                    call_index=0,
                )
        else:
            assert not os.path.exists(TEST_KEYS_FILENAME)

        if result_1_content is not None:
            with open(TEST_RESULT_1_FILENAME) as f:
                assert f.read() == result_1_content
            self._check_permissions(
                TEST_RESULT_1_FILENAME,
                expected_permissions=result_permissions,
            )
            if change_file_owner_call_count >= 2:
                self._check_change_file_owner_call(
                    owner=result_owner,
                    group=result_group,
                    call_index=1,
                )
        else:
            assert not os.path.exists(TEST_RESULT_1_FILENAME)

        if result_2_content is not None:
            with open(TEST_RESULT_2_FILENAME) as f:
                assert f.read() == result_2_content
            self._check_permissions(
                TEST_RESULT_2_FILENAME,
                expected_permissions=result_permissions,
            )
            call_index = 2 if result_1_content else 1
            if change_file_owner_call_count >= call_index + 1:
                self._check_change_file_owner_call(
                    owner=result_owner,
                    group=result_group,
                    call_index=call_index,
                )
        else:
            assert not os.path.exists(TEST_RESULT_2_FILENAME)

        assert self.fake_tvm._mock.call_count == tvm_call_count

    def test_ok(self):
        assert update()
        self.check_ok()

    def test_results_already_actual(self):
        self.fake_fs.create_file(
            TEST_KEYS_FILENAME,
            contents='keys',
            st_mode=settings.RESULT_KEYS_PERMISSIONS,
        )
        self.fake_fs.create_file(
            TEST_RESULT_1_FILENAME,
            contents='1',
            st_mode=settings.RESULT_TICKETS_DEFAULT_PERMISSIONS,
        )
        self.fake_fs.create_file(
            TEST_RESULT_2_FILENAME,
            contents='2',
            st_mode=settings.RESULT_TICKETS_DEFAULT_PERMISSIONS,
        )

        assert update()

        self.check_ok(
            keys_content='keys',
            result_1_content='1',
            result_2_content='2',
            tvm_call_count=0,
            change_file_owner_call_count=0,
        )

    def test_forced_update(self):
        self.fake_fs.create_file(
            TEST_KEYS_FILENAME,
            contents=TEST_TVM_KEYS,
            st_mode=settings.RESULT_KEYS_PERMISSIONS,
        )
        self.fake_fs.create_file(
            TEST_RESULT_1_FILENAME,
            contents='1',
            st_mode=settings.RESULT_TICKETS_DEFAULT_PERMISSIONS,
        )
        self.fake_fs.create_file(
            TEST_RESULT_2_FILENAME,
            contents='2',
            st_mode=settings.RESULT_TICKETS_DEFAULT_PERMISSIONS,
        )
        self.fake_tvm.set_response_side_effect([
            tvm_ticket_response({'2': 'ticket2'}),
            tvm_ticket_response({'1': 'ticket1', '3': 'ticket3', '4': 'ticket4'}),
        ])

        assert update(force=True)

        self.check_ok(tvm_call_count=2, change_file_owner_call_count=2)

    def test_configs_changed_after_creating_results(self):
        self.fake_fs.create_file(
            TEST_KEYS_FILENAME,
            contents=TEST_TVM_KEYS,
            st_mode=settings.RESULT_KEYS_PERMISSIONS,
        )
        self.fake_fs.create_file(
            TEST_RESULT_1_FILENAME,
            contents='1',
            st_mode=settings.RESULT_TICKETS_DEFAULT_PERMISSIONS,
        )
        self.fake_fs.create_file(
            TEST_RESULT_2_FILENAME,
            contents='2',
            st_mode=settings.RESULT_TICKETS_DEFAULT_PERMISSIONS,
        )
        os.utime(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_2_NAME), (0, time() + 1))

        self.fake_tvm.set_response_side_effect([
            tvm_ticket_response({'1': 'ticket1', '3': 'ticket3', '4': 'ticket4'}),
        ])

        assert update()

        self.check_ok(
            keys_content=TEST_TVM_KEYS.decode('utf-8'),
            result_1_content='1',
            tvm_call_count=1,
            change_file_owner_call_count=1,
        )

    def test_no_destinations_ok(self):
        self.fake_fs.remove_object(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_1_NAME))
        with open(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_2_NAME), 'w') as f:
            json.dump(dict(TEST_CONFIG_2_CONTENTS.items(), destinations=[]), f)

        assert update()

        expected_result = json.dumps(
            dict(json.loads(TEST_RESULT_2).items(), tickets={}),
            indent=2,
        )
        self.check_ok(
            result_1_content=None,
            result_2_content=expected_result,
            tvm_call_count=1,
            change_file_owner_call_count=1,
        )

    def test_no_secret_ok(self):
        self.fake_fs.remove_object(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_1_NAME))
        with open(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_2_NAME), 'w') as f:
            json.dump({'client_id': 2}, f)

        assert update()

        expected_result = json.dumps(
            dict(client_id=2, client_secret=None, tickets={}),
            indent=2,
        )
        self.check_ok(
            result_1_content=None,
            result_2_content=expected_result,
            tvm_call_count=1,
            change_file_owner_call_count=1,
        )

    def test_custom_result_properties_ok(self):
        self.fake_fs.remove_object(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_2_NAME))
        with open(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_1_NAME), 'w') as f:
            json.dump(
                dict(
                    TEST_CONFIG_1_CONTENTS.items(),
                    result={'owner': 'root', 'group': 'root', 'permissions': '777'},
                ),
                f,
            )

        with mock.patch('passport.backend.tvm_keyring.update.get_current_user', mock.Mock(return_value='root')):
            assert update()

        self.check_ok(
            result_1_content=TEST_RESULT_1,
            result_2_content=None,
            tvm_call_count=2,
            change_file_owner_call_count=2,
            result_owner='root',
            result_group='root',
            result_permissions=0o777,
        )

    def test_failed_to_get_keys(self):
        self.fake_tvm.set_response_side_effect(TVMPermanentError())

        assert not update()

        self.check_ok(
            keys_content=None,
            result_1_content=None,
            result_2_content=None,
            junk_left=True,
            tvm_call_count=1,
            change_file_owner_call_count=1,
        )

    def test_got_invalid_keys(self):
        self.fake_tvm.set_response_side_effect(['keys'])

        assert not update()

        self.check_ok(
            keys_content=None,
            result_1_content=None,
            result_2_content=None,
            junk_left=True,
            tvm_call_count=1,
            change_file_owner_call_count=1,
        )

    def test_failed_to_get_keys_but_old_present(self):
        self.fake_tvm.set_response_side_effect([
            TVMPermanentError(),
            tvm_ticket_response({'2': 'ticket2'}),
            tvm_ticket_response({'1': 'ticket1', '3': 'ticket3', '4': 'ticket4'}),
        ])
        self.fake_fs.create_file(
            TEST_KEYS_FILENAME,
            contents=TEST_TVM_KEYS,
            st_mode=settings.RESULT_KEYS_PERMISSIONS,
        )
        os.utime(TEST_KEYS_FILENAME, (0, time() - settings.KEYS_UPDATE_INTERVAL - 10))

        assert update()

        self.check_ok(change_file_owner_call_count=0)

    def test_got_invalid_keys_but_old_present(self):
        self.fake_tvm.set_response_side_effect([
            b'keys',
            tvm_ticket_response({'2': 'ticket2'}),
            tvm_ticket_response({'1': 'ticket1', '3': 'ticket3', '4': 'ticket4'}),
        ])
        self.fake_fs.create_file(
            TEST_KEYS_FILENAME,
            contents=TEST_TVM_KEYS,
            st_mode=settings.RESULT_KEYS_PERMISSIONS,
        )
        os.utime(TEST_KEYS_FILENAME, (0, time() - settings.KEYS_UPDATE_INTERVAL - 10))

        assert update()

        self.check_ok(change_file_owner_call_count=0)

    def test_failed_to_get_some_tickets(self):
        self.fake_tvm.set_response_side_effect([
            TEST_TVM_KEYS,
            TVMPermanentError(),
            tvm_ticket_response({'1': 'ticket1', '3': 'ticket3', '4': 'ticket4'}),
        ])

        assert update()

        self.check_ok(result_1_content=None)

    def test_some_configs_invalid(self):
        with open(os.path.join(settings.CONFIG_PATH, TEST_CONFIG_2_NAME), 'w') as f:
            f.write('corrupt json')

        assert update()

        self.check_ok(result_2_content=None, tvm_call_count=2, change_file_owner_call_count=2)

    def test_failed_to_delete_junk(self):
        # Кидаем OSError только для TEST_JUNK_RESULT_FILENAME
        # Остальные файлы удаляются корректно
        from os import remove as original_os_remove
        with mock.patch.object(os, 'remove') as os_remove_mock:
            def broken_remove(filename):
                if filename == TEST_JUNK_RESULT_FILENAME:
                    raise OSError()
                else:
                    original_os_remove(filename)
            os_remove_mock.side_effect = broken_remove

            assert update()

        self.check_ok(junk_left=True)

    def test_unhandled_error(self):
        self.fake_tvm.set_response_side_effect(NameError)

        assert not update()

        self.check_ok(
            keys_content=None,
            result_1_content=None,
            result_2_content=None,
            junk_left=True,
            tvm_call_count=1,
            change_file_owner_call_count=1,
        )

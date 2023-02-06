import json
import os
from time import time

from passport.backend.tvm_keyring import settings
from passport.backend.tvm_keyring.exceptions import ConfigInvalidError
from passport.backend.tvm_keyring.test.base import BaseTestCase
from passport.backend.tvm_keyring.test.base_test_data import (
    TEST_CLIENT_SECRET,
    TEST_CONFIG_1_CONTENTS,
    TEST_CONFIG_2_CONTENTS,
)
from passport.backend.tvm_keyring.utils import (
    get_config_names,
    is_up_to_date,
    parse_and_validate_config,
)
import pytest


TEST_CONFIG_NAME = 'some-config-123'
TEST_CONFIG_FILENAME = os.path.join(settings.CONFIG_PATH, TEST_CONFIG_NAME)
TEST_SECRET_CONFIG_FILENAME = os.path.join(settings.SECRET_CONFIG_PATH, TEST_CONFIG_NAME)
TEST_OTHER_CONFIG_NAME = 'other-config'
TEST_OTHER_CONFIG_FILENAME = os.path.join(settings.CONFIG_PATH, TEST_OTHER_CONFIG_NAME)
TEST_USER = 'www-data'
TEST_GROUPS = ['www-data']


class ParseAndValidateConfigTestCase(BaseTestCase):
    def setUp(self):
        super(ParseAndValidateConfigTestCase, self).setUp()
        for path in (settings.CONFIG_PATH, settings.SECRET_CONFIG_PATH):
            self.fake_fs.create_dir(path)

    def test_ok(self):
        for content in (
            {
                'client_id': 1,
            },
            {
                'client_id': 1,
                'client_secret': TEST_CLIENT_SECRET,
                'destinations': [],
            },
            {
                'client_id': 1,
                'client_secret': TEST_CLIENT_SECRET,
                'destinations': [
                    {'client_id': 2, 'alias': 'a'},
                ],
            },
            {
                'client_id': 1,
                'client_secret': TEST_CLIENT_SECRET,
                'destinations': [
                    {'client_id': 2, 'alias': 'a'},
                    {'client_id': 3, 'alias': 'b', 'scopes': ['foo']},
                ],
            },
            {
                'client_id': 1,
                'client_secret': TEST_CLIENT_SECRET,
                'destinations': [
                    {'client_id': 2, 'alias': 'a'},
                    {'client_id': 3, 'alias': 'b', 'scopes': ['foo']},
                ],
                'result': {
                    'owner': 'www-data',
                    'group': 'www-data',
                    'permissions': '644',
                },
            },
            TEST_CONFIG_1_CONTENTS,
            TEST_CONFIG_2_CONTENTS,
        ):
            with open(TEST_CONFIG_FILENAME, 'w') as f:
                json.dump(content, f)
            with open(TEST_SECRET_CONFIG_FILENAME, 'w') as f:
                f.write('not-a-json')  # убедимся, что этот файл не читаем
            assert parse_and_validate_config(TEST_CONFIG_NAME, TEST_USER, TEST_GROUPS) == content

    def test_custom_owner_ok(self):
        content = {
            'client_id': 1,
            'result': {
                'owner': 'root',
                'group': 'root',
                'permissions': '644',
            },
        }
        with open(TEST_CONFIG_FILENAME, 'w') as f:
            json.dump(content, f)
        assert parse_and_validate_config(TEST_CONFIG_NAME, 'root', ['root']) == content

    def test_file_inaccessible(self):
        with pytest.raises(ConfigInvalidError) as context:
            parse_and_validate_config(TEST_OTHER_CONFIG_NAME, TEST_USER, TEST_GROUPS)

        actual = str(context.value)
        expected = '[%s] %s' % (
            TEST_OTHER_CONFIG_NAME,
            'Cannot read config: [Errno 2] No such file or directory in the fake filesystem: \'%s\'' % (
                TEST_OTHER_CONFIG_FILENAME,
            ),
        )
        assert actual == expected

    def test_config_invalid(self):
        for raw_content, error_message in (
            # всякий мусор
            (
                '',
                'Bad JSON in config: Expecting value: line 1 column 1 (char 0)',
            ),
            (
                '}',
                'Bad JSON in config: Expecting value: line 1 column 1 (char 0)',
            ),
            (
                '""',
                'Invalid config: \'\' is not of type \'object\'',
            ),
            # нехватка обязательных полей
            (
                '{}',
                'Invalid config: \'client_id\' is a required property',
            ),
            (
                '{"client_id": 1, "destinations": [{"client_id": 2, "alias": "a"}]}',
                'Invalid config: either \'client_secret\' or extra file with secret is required when destinations are present',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{}]}' % TEST_CLIENT_SECRET,
                'Invalid config: \'client_id\' is a required property',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a", "scopes": []}]}' % TEST_CLIENT_SECRET,
                'Invalid config: [] is too short',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2}]}' % TEST_CLIENT_SECRET,
                'Invalid config: \'alias\' is a required property',
            ),
            # невалидные значения полей
            (
                '{"client_id": "foo", "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a"}]}' % TEST_CLIENT_SECRET,
                'Invalid config: \'foo\' is not of type \'integer\'',
            ),
            (
                '{"client_id": "1", "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a"}]}' % TEST_CLIENT_SECRET,
                'Invalid config: \'1\' is not of type \'integer\'',
            ),
            (
                '{"client_id": 1, "client_secret": "foo", "destinations": [{"client_id": 2, "alias": "a"}]}',
                'Invalid config: \'foo\' is too short',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a"}]}' % ('a' * 30),
                'Invalid config: \'%s\' is too long' % ('a' * 30),
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": "2", "alias": "a"}]}' % TEST_CLIENT_SECRET,
                'Invalid config: \'2\' is not of type \'integer\'',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a", "scopes": [""]}]}' % TEST_CLIENT_SECRET,
                'Invalid config: \'\' is too short',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": ""}]}' % TEST_CLIENT_SECRET,
                'Invalid config: \'\' is too short',
            ),
            # дублирующиеся элементы
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a"}, {"client_id": 2, "alias": "a"}]}' % TEST_CLIENT_SECRET,
                'Invalid config: [{\'client_id\': 2, \'alias\': \'a\'}, {\'client_id\': 2, \'alias\': \'a\'}] has non-unique elements',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a", "scopes": ["foo", "foo"]}]}' % TEST_CLIENT_SECRET,
                'Invalid config: [\'foo\', \'foo\'] has non-unique elements',
            ),
            # дублирующиеся алиасы
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a"}, {"client_id": 3, "alias": "a"}]}' % TEST_CLIENT_SECRET,
                'Duplicate aliases: a',
            ),
            # неизвестные поля
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a"}], "some": "other"}' % TEST_CLIENT_SECRET,
                'Invalid config: Additional properties are not allowed (\'some\' was unexpected)',
            ),
            (
                '{"client_id": 1, "client_secret": "%s", "destinations": [{"client_id": 2, "alias": "a", "some2": "other2"}]}' % TEST_CLIENT_SECRET,
                'Invalid config: Additional properties are not allowed (\'some2\' was unexpected)',
            ),
            (
                '{"client_id": 1, "result": {"permissions": "888"}}',
                'Invalid config: \'888\' does not match \'^[0-7]{3}$\'',
            ),
            (
                '{"client_id": 1, "result": {"some2": "other2"}}',
                'Invalid config: Additional properties are not allowed (\'some2\' was unexpected)',
            ),
            # запуск не от того пользователя
            (
                '{"client_id": 1, "result": {"owner": "root"}}',
                'Insufficient rights: unable to chown to \'root\' while running as `www-data`',
            ),
            (
                '{"client_id": 1, "result": {"group": "root"}}',
                'Insufficient rights: unable to chgrp to \'root\' while running as `www-data`',
            ),
        ):
            with open(TEST_CONFIG_FILENAME, 'w') as f:
                f.write(raw_content)
            with pytest.raises(ConfigInvalidError) as context:
                parse_and_validate_config(TEST_CONFIG_NAME, TEST_USER, TEST_GROUPS)

            assert str(context.value) == '[%s] %s' % (TEST_CONFIG_NAME, error_message)

    def test_secret_config_ok(self):
        with open(TEST_CONFIG_FILENAME, 'w') as f:
            json.dump(
                {
                    'client_id': 1,
                    'destinations': [
                        {'client_id': 2, 'alias': 'a'},
                    ],
                },
                f,
            )
        with open(TEST_SECRET_CONFIG_FILENAME, 'w') as f:
            json.dump(
                {
                    'client_id': 1,
                    'client_secret': TEST_CLIENT_SECRET,
                },
                f,
            )
        assert parse_and_validate_config(TEST_CONFIG_NAME, TEST_USER, TEST_GROUPS) == {
            'client_id': 1,
            'client_secret': TEST_CLIENT_SECRET,
            'destinations': [
                {'client_id': 2, 'alias': 'a'},
            ],
        }

    def test_secret_config_invalid(self):
        with open(TEST_CONFIG_FILENAME, 'w') as f:
            json.dump(
                {
                    'client_id': 1,
                    'destinations': [
                        {'client_id': 2, 'alias': 'a'},
                    ],
                },
                f,
            )

        for raw_content, error_message in (
            # всякий мусор
            (
                '',
                'Bad JSON in config: Expecting value: line 1 column 1 (char 0)',
            ),
            # нехватка обязательных полей
            (
                '{}',
                'Invalid config: \'client_id\' is a required property',
            ),
            # несовпадение client_id
            (
                '{"client_id": 2, "client_secret": "%s"}' % TEST_CLIENT_SECRET,
                'Invalid config: \'client_id\' from %s and %s do not match' % (TEST_CONFIG_FILENAME, TEST_SECRET_CONFIG_FILENAME),
            ),
            # неизвестные поля
            (
                '{"client_id": 1, "client_secret": "%s", "some": "other"}' % TEST_CLIENT_SECRET,
                'Invalid config: Additional properties are not allowed (\'some\' was unexpected)',
            ),
        ):
            with open(TEST_SECRET_CONFIG_FILENAME, 'w') as f:
                f.write(raw_content)

            with pytest.raises(ConfigInvalidError) as context:
                parse_and_validate_config(TEST_CONFIG_NAME, TEST_USER, TEST_GROUPS)

            assert str(context.value) == '[%s] %s' % (TEST_CONFIG_NAME, error_message)


class GetConfigsTestCase(BaseTestCase):
    def setUp(self):
        super(GetConfigsTestCase, self).setUp()
        self.fake_fs.create_file(TEST_CONFIG_FILENAME)
        self.fake_fs.create_file(TEST_SECRET_CONFIG_FILENAME)
        self.fake_fs.create_file(TEST_OTHER_CONFIG_FILENAME)

    def test_ok(self):
        assert list(get_config_names()) == [TEST_OTHER_CONFIG_NAME, TEST_CONFIG_NAME]


class IsUpToDateTestCase(BaseTestCase):
    def setUp(self):
        super(IsUpToDateTestCase, self).setUp()
        self.fake_fs.create_file(TEST_CONFIG_FILENAME)
        os.utime(TEST_CONFIG_FILENAME, (0, time() - 100))

    def test_ok(self):
        assert is_up_to_date(TEST_CONFIG_FILENAME, 110)

    def test_expired(self):
        assert not is_up_to_date(TEST_CONFIG_FILENAME, 90)

    def test_file_inaccessible(self):
        assert not is_up_to_date(TEST_OTHER_CONFIG_FILENAME, 110)

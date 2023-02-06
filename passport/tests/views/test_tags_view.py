# -*- coding: utf-8 -*-

from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.db import get_db
from passport.backend.vault.api.models.tags import Tag
from passport.backend.vault.api.test.base_test_class import BaseTestClass
from passport.backend.vault.api.test.permissions_mock import PermissionsMock
from passport.backend.vault.api.test.uuid_mock import UuidMock


class BaseTestTagsView(BaseTestClass):
    fill_database = False
    send_user_ticket = True

    def setUp(self):
        super(BaseTestTagsView, self).setUp()

        with self.app.app_context():
            test_tags = [
                'one',
                'two',
                'three four',
                'five',
                'none',
                'test',
                'vault',
                u'навохудоноср',
            ]
            with UuidMock(base_value=1000000):
                Tag.create_tags(test_tags, created_by=100)
                get_db().session.commit()


class TestTagsView(BaseTestTagsView):
    fill_database = True

    def fill_secrets(self):
        self.fixture.fill_abc()
        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                with UuidMock(base_value=2000000):
                    self.client.create_complete_secret(
                        'tagged_secret_1',
                        secret_version={
                            'value': {'name': 'ppodolsky', 'password': '12345'},
                        },
                        tags='one, two',
                        roles=[
                            {'uid': 101, 'role': 'OWNER'},
                            {'abc_id': 14, 'role': 'READER'},
                            {'staff_id': 38098, 'role': 'READER'},
                        ],
                    )
                    self.client.create_complete_secret(
                        'tagged_secret_2',
                        secret_version={
                            'value': {'name': 'arhibot', 'password': '23456'},
                        },
                        tags='навохудоноср',
                        roles=[
                            {'uid': 102, 'role': 'OWNER'},
                            {'abc_id': 14, 'role': 'READER'},
                            {'staff_id': 2, 'role': 'READER'},
                        ],
                    )
                    self.client.create_complete_secret(
                        'tagged_secret_3',
                        secret_version={
                            'value': {'name': 'staff', 'password': '34567'},
                        },
                        tags='three, none, five',
                        roles=[
                            {'uid': 102, 'role': 'OWNER'},
                            {'abc_id': 14, 'role': 'READER'},
                            {'staff_id': 38098, 'role': 'READER'},
                        ],
                    )

                    hidden_secret = self.client.create_complete_secret(
                        'hidden_secret',
                        secret_version={
                            'value': {'name': 'staff', 'password': '34567'},
                        },
                        tags='five, hidden',
                        roles=[
                            {'uid': 102, 'role': 'OWNER'},
                            {'abc_id': 14, 'role': 'READER'},
                            {'staff_id': 38098, 'role': 'READER'},
                        ],
                    )['uuid']
                    self.client.update_secret(hidden_secret, state='hidden')

    def test_tags_ok(self):
        self.fill_secrets()

        with PermissionsMock(uid=100):
            with TimeMock(offset=15):
                r = self.client.get_tags(
                    return_raw=True,
                )
                self.assertResponseEqual(r, {
                    'status': 'ok',
                    'tags': list(sorted(['five', 'none', 'one', 'three', 'two', u'навохудоноср'])),
                })

        with PermissionsMock(uid=101):
            with TimeMock(offset=15):
                r = self.client.get_tags(
                    return_raw=True,
                )
                self.assertResponseEqual(r, {
                    'status': 'ok',
                    'tags': ['one', 'two', u'навохудоноср'],
                })

        with PermissionsMock(uid=102):
            with TimeMock(offset=15):
                r = self.client.get_tags(
                    return_raw=True,
                )
                self.assertResponseEqual(r, {
                    'status': 'ok',
                    'tags': ['five', 'none', 'three', u'навохудоноср'],
                })


class TestTagsSuggestView(BaseTestTagsView):
    def test_suggest(self):
        r = self.client.suggest_tags(
            text='one',
            return_raw=True,
        )
        self.assertResponseEqual(r, {
            'page': 0,
            'page_size': 50,
            'status': 'ok',
            'tags': [
                'none',
                'one',
            ],
            'text': 'one',
        })

        r = self.client.suggest_tags(
            text='fo',
        )
        self.assertEqual(r, ['three four'])

        r = self.client.suggest_tags(
            text=u'наво',
        )
        self.assertEqual(r, [u'навохудоноср'])

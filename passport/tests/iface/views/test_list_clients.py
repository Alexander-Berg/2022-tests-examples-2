# -*- coding: utf-8 -*-
from datetime import datetime

from django.test.utils import override_settings
from django.urls import reverse_lazy
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.oauth.api.api.iface.utils import (
    client_to_response,
    scopes_to_response,
)
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseClientTestCase,
    BaseIfaceApiTestCase,
    CommonCookieTests,
    TEST_AVATARS_BASE_URL,
    TEST_TURBOAPP_BASE_URL,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    UPDATE,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.base_test_data import (
    TEST_LOGIN,
    TEST_OTHER_UID,
    TEST_UID,
)
from passport.backend.oauth.core.test.utils import iter_eq


class TestListOwnedClients(BaseIfaceApiTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_list_owned_clients')

    def setUp(self):
        super(TestListOwnedClients, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'language': 'ru',
        }

    def test_ok(self):
        with CREATE(
            Client.create(
                uid=TEST_OTHER_UID,
                scopes=[Scope.by_keyword('test:ttl_refreshable')],
                default_title='Another',
            )
        ) as another_client:
            another_client.owner_uids = [TEST_UID]

        with UPDATE(self.test_client):
            self.test_client.owner_uids = [TEST_UID]  # и создатель, и владелец одновременно

        rv = self.make_request()
        self.assert_status_ok(rv)
        eq_(
            rv['created_clients'],
            [
                client_to_response(self.test_client, 'ru', for_creator=True, add_token_ttl=True),
            ],
        )
        eq_(
            rv['owned_clients'],
            [
                client_to_response(another_client, 'ru', for_creator=True, add_token_ttl=True),
            ],
        )

    def test_no_clients(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_ok(rv)
        eq_(rv['created_clients'], [])
        eq_(rv['owned_clients'], [])


@override_settings(AVATARS_READ_URL=TEST_AVATARS_BASE_URL)
class TestClientInfo(BaseClientTestCase):
    default_url = reverse_lazy('iface_client_info')

    def setUp(self):
        super(TestClientInfo, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        params = super(TestClientInfo, self).default_params()
        params.update(uid=TEST_UID)
        return params

    def test_ok_for_creator(self):
        with UPDATE(self.test_client) as client:
            client.contact_email = 'abacaba@test.ru'

        rv = self.make_request()
        self.assert_response_ok(
            rv,
            client=dict(
                self.base_client_info(),
                **{
                    'secret': self.test_client.secret,
                    'approval_status': self.test_client.approval_status,
                    'blocked': self.test_client.is_blocked,
                    'owners': [],
                    'owner_groups': [],
                    'contact_email': 'abacaba@test.ru',
                }
            ),
            viewed_by_owner=True,
            can_be_edited=True,
            extra_visible_scopes={},
            token_ttl=None,
        )

    def test_ok_for_owner(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_OTHER_UID, id=TEST_OTHER_UID, login=TEST_LOGIN),
        )

        with UPDATE(self.test_client) as client:
            client.owner_uids = [TEST_OTHER_UID]
            client.contact_email = 'abacaba@test.ru'

        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_response_ok(
            rv,
            client=dict(
                self.base_client_info(),
                **{
                    'secret': self.test_client.secret,
                    'approval_status': self.test_client.approval_status,
                    'blocked': self.test_client.is_blocked,
                    'owners': [
                        {
                            'uid': TEST_OTHER_UID,
                            'login': TEST_LOGIN,
                        },
                    ],
                    'owner_groups': [],
                    'contact_email': 'abacaba@test.ru',
                }
            ),
            viewed_by_owner=True,
            can_be_edited=True,
            extra_visible_scopes={},
            token_ttl=None,
        )

    def test_ok_with_extra_visible_scopes(self):
        with UPDATE(self.test_client) as client:
            client.set_extra_visible_scopes([Scope.by_keyword('test:invisible')])

        rv = self.make_request()
        eq_(
            rv['extra_visible_scopes'],
            scopes_to_response([Scope.by_keyword('test:invisible')]),
        )

    def test_ok_with_extra_visible_scopes_for_intranet(self):
        with UPDATE(self.test_client) as client:
            client.set_extra_visible_scopes([Scope.by_keyword('test:invisible')])

        with mock.patch(
            'passport.backend.oauth.api.api.iface.views.is_yandex_ip',
            mock.Mock(return_value=True),
        ):
            rv = self.make_request()
        eq_(
            rv['extra_visible_scopes'],
            scopes_to_response([Scope.by_keyword('test:invisible')], with_slugs=True),
        )

    def test_ok_with_extra_visible_scopes_for_intranet_force_no_slugs(self):
        with UPDATE(self.test_client) as client:
            client.set_extra_visible_scopes([Scope.by_keyword('test:invisible')])

        with mock.patch(
            'passport.backend.oauth.api.api.iface.views.is_yandex_ip',
            mock.Mock(return_value=True),
        ):
            rv = self.make_request(force_no_slugs=True)
        eq_(
            rv['extra_visible_scopes'],
            scopes_to_response([Scope.by_keyword('test:invisible')]),
        )

    def test_ok_for_turboapp(self):
        with UPDATE(self.test_client) as client:
            client.turboapp_base_url = TEST_TURBOAPP_BASE_URL

        rv = self.make_request()
        eq_(
            rv['extra_visible_scopes'],
            scopes_to_response([Scope.by_keyword('test:default_phone')]),
        )

    def test_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_not_owner(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_response_ok(
            rv,
            client=self.base_client_info(),
            viewed_by_owner=False,
            can_be_edited=False,
            token_ttl=None,
        )

    def test_with_ttl(self):
        with UPDATE(self.test_client) as client:
            client.set_scopes([Scope.by_keyword('test:ttl_refreshable')])

        rv = self.make_request(uid=TEST_OTHER_UID)
        eq_(rv['token_ttl'], 300)
        ok_(rv['is_ttl_refreshable'])

    def test_localized(self):
        rv = self.make_request(language='en')
        self.assert_status_ok(rv)

        iter_eq(
            rv['client'],
            dict(
                self.base_client_info(),
                **{
                    'scopes': {
                        'OAuth test': {
                            'test:foo': {
                                'title': 'foo',
                                'requires_approval': False,
                                'ttl': None,
                                'is_ttl_refreshable': False,
                            },
                            'test:bar': {
                                'title': 'bar',
                                'requires_approval': False,
                                'ttl': None,
                                'is_ttl_refreshable': False,
                            },
                        },
                    },
                    'owners': [],
                    'owner_groups': [],
                    'secret': self.test_client.secret,
                    'approval_status': self.test_client.approval_status,
                    'blocked': self.test_client.is_blocked,
                    'contact_email': None,
                }
            ),
        )

    def test_no_session_cookie(self):
        rv = self.make_request(headers=self.default_headers(cookie='yandexuid=yu'))
        self.assert_response_ok(
            rv,
            client=self.base_client_info(),
            viewed_by_owner=False,
            can_be_edited=False,
            token_ttl=None,
        )

    def test_blackbox_sessionid_failed(self):
        self.fake_blackbox.set_response_side_effect(
            'sessionid',
            BlackboxTemporaryError,
        )
        rv = self.make_request()
        self.assert_response_ok(
            rv,
            client=self.base_client_info(),
            viewed_by_owner=False,
            can_be_edited=False,
            token_ttl=None,
        )


@override_settings(AVATARS_READ_URL=TEST_AVATARS_BASE_URL)
class TestClientsInfo(BaseClientTestCase):
    default_url = reverse_lazy('iface_clients_info')

    def test_ok(self):
        rv = self.make_request(
            client_id=[
                self.test_client.display_id,
                'gone_client_id',
            ],
        )
        self.assert_status_ok(rv)
        iter_eq(
            rv['clients'],
            {
                self.test_client.display_id: self.base_client_info(),
                'gone_client_id': None,
            },
        )

    def test_ok_for_deleted_client(self):
        with UPDATE(self.test_client) as client:
            client.deleted = datetime.now()

        rv = self.make_request(
            client_id=[
                self.test_client.display_id,
                'gone_client_id',
            ],
        )
        self.assert_status_ok(rv)
        iter_eq(
            rv['clients'],
            {
                self.test_client.display_id: dict(
                    self.base_client_info(),
                    is_deleted=True,
                ),
                'gone_client_id': None,
            },
        )

    def test_params_missing(self):
        rv = self.make_request(language='', client_id=' ')
        self.assert_status_error(rv, ['client_id.missing', 'language.missing'])

    def test_another_language(self):
        rv = self.make_request(language='en', client_id=[self.test_client.display_id])
        self.assert_status_ok(rv)
        clients_info = self.base_client_info()
        clients_info['scopes'] = {
            'OAuth test': {
                'test:foo': {
                    'title': 'foo',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                },
                'test:bar': {
                    'title': 'bar',
                    'requires_approval': False,
                    'ttl': None,
                    'is_ttl_refreshable': False,
                },
            },
        }
        iter_eq(
            rv['clients'],
            {self.test_client.display_id: clients_info},
        )

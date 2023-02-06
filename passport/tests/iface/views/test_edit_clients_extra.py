# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseIfaceApiTestCase,
    CommonCookieTests,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    EntityNotFoundError,
    UPDATE,
)
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_GRANT_TYPE,
    TEST_OTHER_UID,
    TEST_UID,
    TEST_YANDEX_IP,
)


class TestClientSecret(BaseIfaceApiTestCase, CommonCookieTests):
    http_method = 'POST'
    url_new = reverse_lazy('iface_new_client_secret')
    url_undo = reverse_lazy('iface_undo_new_client_secret')
    default_url = url_new

    def setUp(self):
        super(TestClientSecret, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'client_id': self.test_client.display_id,
        }

    def test_ok(self):
        old_secret = self.test_client.secret

        rv = self.make_request(url=self.url_new)
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        eq_(client.secret, rv['secret'])
        eq_(client.modified, DatetimeNow())
        self.assertNotEqual(client.secret, old_secret)

        rv = self.make_request(url=self.url_undo)
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        eq_(client.secret, rv['secret'])
        eq_(client.secret, old_secret)
        eq_(client.modified, DatetimeNow())

    def test_yandex_client_destructive_action(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request(
            url=self.url_new,
            headers=self.default_headers(user_ip=TEST_YANDEX_IP),
        )
        self.assert_status_error(
            rv,
            [
                'yandex_client.destructive_action',
            ],
        )

        rv = self.make_request(
            url=self.url_undo,
            headers=self.default_headers(user_ip=TEST_YANDEX_IP),
        )
        self.assert_status_error(
            rv,
            [
                'yandex_client.destructive_action',
            ],
        )

    def test_yandex_client_not_editable_outside_intranet(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request(url=self.url_new)
        self.assert_status_error(
            rv,
            [
                'client.not_editable',
            ],
        )
        rv = self.make_request(url=self.url_undo)
        self.assert_status_error(
            rv,
            [
                'client.not_editable',
            ],
        )

    def test_double_undo_ok(self):
        old_secret = self.test_client.secret

        rv = self.make_request(url=self.url_new)
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        self.assertEqual(client.secret, rv['secret'])
        self.assertNotEqual(client.secret, old_secret)

        rv = self.make_request(url=self.url_undo)
        self.assert_status_ok(rv)

        rv = self.make_request(url=self.url_undo)
        self.assert_status_ok(rv)

        client = Client.by_id(self.test_client.id)
        self.assertEqual(client.secret, rv['secret'])
        self.assertEqual(client.secret, old_secret)

    def test_client_not_found(self):
        rv = self.make_request(url=self.url_new, client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

        rv = self.make_request(url=self.url_undo, client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_not_creator(self):
        old_secret = self.test_client.secret

        rv = self.make_request(url=self.url_new, uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['client.creator_required'])
        client = Client.by_id(self.test_client.id)
        eq_(client.secret, old_secret)

        rv = self.make_request(url=self.url_undo, uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['client.creator_required'])
        client = Client.by_id(self.test_client.id)
        eq_(client.secret, old_secret)

    def test_password_not_entered(self):
        self.setup_blackbox_response(age=-1)

        rv = self.make_request(url=self.url_new)
        self.assert_status_error(rv, ['password.required'])

        rv = self.make_request(url=self.url_undo)
        self.assert_status_error(rv, ['password.required'])

    def test_password_not_entered_recently(self):
        self.setup_blackbox_response(age=100500)

        rv = self.make_request(url=self.url_new)
        self.assert_status_error(rv, ['password.required'])

        rv = self.make_request(url=self.url_undo)
        self.assert_status_error(rv, ['password.required'])


class TestDeleteClient(BaseIfaceApiTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_delete_client')
    http_method = 'POST'

    def setUp(self):
        super(TestDeleteClient, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'client_id': self.test_client.display_id,
        }

    def test_ok(self):
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request()
        self.assert_status_ok(rv)

        with assert_raises(EntityNotFoundError):
            Client.by_id(self.test_client.id)
        ok_(Client.by_id(self.test_client.id, allow_deleted=True))  # физически приложение не удаляем

        self.assertNotEqual(list_tokens_by_uid(TEST_UID), [])  # токены не удаляем, они инвалидируются сами
        self.check_statbox_entry(
            {
                'mode': 'delete_client',
                'status': 'ok',
                'client_id': self.test_client.display_id,
            },
            entry_index=-1,
        )
        self.check_historydb_event_entry(
            {
                'action': 'delete',
                'target': 'client',
                'client_id': self.test_client.display_id,
                'scopes': 'test:foo,test:bar',
            },
            entry_index=-1,
        )

    def test_yandex_client_destructive_action(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request(headers=self.default_headers(user_ip=TEST_YANDEX_IP))
        self.assert_status_error(
            rv,
            [
                'yandex_client.destructive_action',
            ],
        )

    def test_yandex_client_not_editable_outside_intranet(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request()
        self.assert_status_error(
            rv,
            [
                'client.not_editable',
            ],
        )
        ok_(Client.by_id(self.test_client.id))

    def test_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_not_creator(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['client.creator_required'])
        ok_(Client.by_id(self.test_client.id))

    def test_password_not_entered(self):
        self.setup_blackbox_response(age=-1)
        rv = self.make_request()
        self.assert_status_error(rv, ['password.required'])

    def test_password_not_entered_recently(self):
        self.setup_blackbox_response(age=100500)
        rv = self.make_request()
        self.assert_status_error(rv, ['password.required'])


class TestGlogoutClient(BaseIfaceApiTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_glogout_client')
    http_method = 'POST'

    def setUp(self):
        super(TestGlogoutClient, self).setUp()
        self.setup_blackbox_response()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'client_id': self.test_client.display_id,
        }

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        client = Client.by_id(self.test_client.id)
        eq_(client.glogouted, DatetimeNow())
        eq_(client.modified, DatetimeNow())

    def test_yandex_client_destructive_action(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request(headers=self.default_headers(user_ip=TEST_YANDEX_IP))
        self.assert_status_error(
            rv,
            [
                'yandex_client.destructive_action',
            ],
        )

    def test_yandex_client_not_editable_outside_intranet(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request()
        self.assert_status_error(
            rv,
            [
                'client.not_editable',
            ],
        )
        ok_(Client.by_id(self.test_client.id))

    def test_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_not_creator(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['client.creator_required'])
        ok_(Client.by_id(self.test_client.id))

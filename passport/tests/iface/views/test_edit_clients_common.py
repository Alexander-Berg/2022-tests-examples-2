# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.urls import reverse_lazy
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.avatars_mds_api.faker import avatars_mds_api_upload_ok_response
from passport.backend.core.builders.passport import PassportPermanentError
from passport.backend.core.builders.passport.faker import passport_ok_response
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.api.tests.iface.views.base import (
    BaseIfaceApiTestCase,
    CommonCookieTests,
    TEST_ANDROID_APPSTORE_URL,
    TEST_ANDROID_FINGERPRINT,
    TEST_ANDROID_PACKAGE_NAME,
    TEST_ANDROID_PACKAGE_NAME_OTHER,
    TEST_COOKIE,
    TEST_HOST,
    TEST_IOS_APP_ID,
    TEST_IOS_APP_ID_OTHER,
    TEST_IOS_APPSTORE_URL,
    TEST_NEW_CLIENT_ICON_ID_PREFIX,
    TEST_TURBOAPP_BASE_URL,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_GRANT_TYPE,
    TEST_GROUP,
    TEST_OTHER_UID,
    TEST_TVM_TICKET,
    TEST_UID,
    TEST_USER_IP,
    TEST_YANDEX_IP,
)


@override_settings(
    REQUIRE_DESCRIPTION_FOR_CLIENTS_WAITING_FOR_APPROVAL=True,
)
class TestCreateClient(BaseIfaceApiTestCase, CommonCookieTests):
    default_url = reverse_lazy('iface_create_client')
    http_method = 'POST'

    def setUp(self):
        super(TestCreateClient, self).setUp()
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            avatars_mds_api_upload_ok_response(),
        )
        self.setup_blackbox_response(
            attributes={
                settings.BB_ATTR_ACCOUNT_IS_CORPORATE: '1',
            },
        )
        self.is_yandex_ip_mock = mock.Mock(return_value=True)
        self.is_yandex_ip_patch = mock.patch(
            'passport.backend.oauth.api.api.iface.views.is_yandex_ip',
            self.is_yandex_ip_mock,
        )
        self.is_yandex_ip_patch.start()

    def tearDown(self):
        self.is_yandex_ip_patch.stop()
        super(TestCreateClient, self).tearDown()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'title': 'client',
            'description': 'Test client',
            'scopes': ['test:foo', 'test:bar'],
            'icon': 'http://home.ru/icon',
            'homepage': 'http://home.ru',
            'platforms': ['web'],
            'redirect_uri': ['http://test'],
            'is_yandex': '1',
            'icon_file': SimpleUploadedFile('cool_icon.jpg', b'file_content'),
            'contact_email': 'test@test.ru',
        }

    def assert_statbox_ok(self, client_id, redirect_uris=None):
        self.check_statbox_entry(
            {
                'mode': 'create_client',
                'status': 'ok',
                'client_id': client_id,
                'creator_uid': str(TEST_UID),
                'client_title': 'client',
                'client_description': 'Test client',
                'client_scopes': 'test:foo,test:bar',
                'client_redirect_uris': redirect_uris or 'http://test',
            },
            entry_index=-1,
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        ok_('client_id' in rv)
        client = Client.by_display_id(rv['client_id'])
        eq_(client.uid, TEST_UID)
        eq_(client.default_title, 'client')
        eq_(client.default_description, 'Test client')
        eq_(sorted([s.keyword for s in client.scopes]), sorted(['test:foo', 'test:bar']))
        eq_(client.icon, 'http://home.ru/icon')
        ok_(client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % rv['client_id']), client.icon_id)
        eq_(client.homepage, 'http://home.ru')
        eq_(client.redirect_uris, ['http://test'])
        ok_(not client._callback)
        ok_(client.is_yandex)
        eq_(client.contact_email, 'test@test.ru')
        self.assert_statbox_ok(rv['client_id'])

    def test_is_yandex_forbidden_by_ip(self):
        self.is_yandex_ip_mock.return_value = False
        rv = self.make_request()
        self.assert_status_ok(rv)
        client = Client.by_display_id(rv['client_id'])
        ok_(not client.is_yandex)
        self.assert_statbox_ok(rv['client_id'])

    def test_icon_upload_error(self):
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            '{"error": "crit"}',
            status=500,
        )
        rv = self.make_request()
        self.assert_status_error(
            rv,
            [
                'backend.failed',
            ],
        )

    def test_icon_bad_format(self):
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            '{"description": "cannot process image"}',
            status=400,
        )
        rv = self.make_request()
        self.assert_status_error(
            rv,
            [
                'icon.bad_format',
            ],
        )

    def test_icon_required(self):
        rv = self.make_request(is_yandex='1', exclude=['icon_file'])
        self.assert_status_error(
            rv,
            [
                'icon.required',
            ],
        )

    def test_icon_too_large(self):
        rv = self.make_request(
            is_yandex='1',
            icon_file=SimpleUploadedFile('cool_icon.jpg', b'a' * 2 * 1024 * 1024),
        )
        self.assert_status_error(
            rv,
            [
                'icon_file.too_large',
            ],
        )

    def test_scope_forbidden(self):
        rv = self.make_request(
            scopes=['test:invisible'],
        )
        self.assert_status_error(
            rv,
            [
                'scopes.invalid',
            ],
        )
        ok_('client_id' not in rv)

    def test_description_required_for_premoderated_scope(self):
        rv = self.make_request(scopes=['test:premoderate'], description='')
        self.assert_status_error(rv, ['description.missing'])

    def test_invalid_form(self):
        rv = self.make_request(
            title='a' * 101,
            description='a' * 251,
            scopes='money:frawd',
            contact_email='not_an_email'
        )
        self.assert_status_error(
            rv,
            [
                'description.too_long',
                'title.too_long',
                'scopes.invalid',
                'contact_email.invalid',
            ],
        )
        ok_('client_id' not in rv)

    def test_ok_with_several_redirect_uris(self):
        rv = self.make_request(redirect_uri=['http://test', 'https://prod'])
        self.assert_status_ok(rv)
        ok_('client_id' in rv)
        client = Client.by_display_id(rv['client_id'])
        eq_(client.uid, TEST_UID)
        eq_(client.default_title, 'client')
        eq_(client.default_description, 'Test client')
        eq_(sorted([s.keyword for s in client.scopes]), sorted(['test:foo', 'test:bar']))
        eq_(client.icon, 'http://home.ru/icon')
        ok_(client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % rv['client_id']), client.icon_id)
        eq_(client.homepage, 'http://home.ru')
        eq_(client.redirect_uris, ['http://test', 'https://prod'])
        ok_(not client._callback)
        ok_(client.is_yandex)
        self.assert_statbox_ok(rv['client_id'], redirect_uris='http://test, https://prod')

    def test_ok_with_platforms(self):
        rv = self.make_request(
            platforms=['ios', 'android', 'turboapp', 'web'],
            ios_app_id=[TEST_IOS_APP_ID, TEST_IOS_APP_ID_OTHER],
            ios_appstore_url=TEST_IOS_APPSTORE_URL,
            android_package_name=[TEST_ANDROID_PACKAGE_NAME, TEST_ANDROID_PACKAGE_NAME_OTHER],
            android_cert_fingerprints=[TEST_ANDROID_FINGERPRINT],
            android_appstore_url=TEST_ANDROID_APPSTORE_URL,
            turboapp_base_url=TEST_TURBOAPP_BASE_URL,
        )
        self.assert_status_ok(rv)
        ok_('client_id' in rv)
        client = Client.by_display_id(rv['client_id'])
        eq_(client.platforms, {'ios', 'android', 'turboapp', 'web'})

        eq_(client.ios_appstore_url, TEST_IOS_APPSTORE_URL)
        eq_(client.ios_default_app_id, TEST_IOS_APP_ID)
        eq_(client.ios_extra_app_ids, [TEST_IOS_APP_ID_OTHER])
        eq_(client.ios_app_ids, [TEST_IOS_APP_ID, TEST_IOS_APP_ID_OTHER])

        eq_(client.android_appstore_url, TEST_ANDROID_APPSTORE_URL)
        eq_(client.android_default_package_name, TEST_ANDROID_PACKAGE_NAME)
        eq_(client.android_extra_package_names, [TEST_ANDROID_PACKAGE_NAME_OTHER])
        eq_(client.android_package_names, [TEST_ANDROID_PACKAGE_NAME, TEST_ANDROID_PACKAGE_NAME_OTHER])

        eq_(client.turboapp_base_url, TEST_TURBOAPP_BASE_URL)

    def test_ok_with_owners(self):
        rv = self.make_request(owner_uids=[TEST_OTHER_UID], owner_groups=[TEST_GROUP])
        self.assert_status_ok(rv)
        ok_('client_id' in rv)
        client = Client.by_display_id(rv['client_id'])
        eq_(client.uid, TEST_UID)
        eq_(client.owner_uids, [TEST_OTHER_UID])
        eq_(client.owner_groups, [TEST_GROUP])

    def test_is_yandex_forbidden_by_account_type(self):
        self.setup_blackbox_response(attributes={})
        rv = self.make_request()
        self.assert_status_ok(rv)
        client = Client.by_display_id(rv['client_id'])
        ok_(not client.is_yandex)
        self.assert_statbox_ok(rv['client_id'])


@override_settings(
    REQUIRE_DESCRIPTION_FOR_CLIENTS_WAITING_FOR_APPROVAL=True,
)
class TestEditClient(BaseIfaceApiTestCase):
    default_url = reverse_lazy('iface_edit_client')
    http_method = 'POST'

    def setUp(self):
        super(TestEditClient, self).setUp()
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            avatars_mds_api_upload_ok_response(),
        )
        self.fake_avatars_mds_api.set_response_value(
            'delete',
            '{}',
        )
        self.fake_passport.set_response_value(
            'oauth_client_edited_send_notifications',
            passport_ok_response(),
        )
        self.setup_blackbox_response(
            attributes={
                settings.BB_ATTR_ACCOUNT_IS_CORPORATE: '1',
            },
        )
        self.is_yandex_ip_mock = mock.Mock(return_value=True)
        self.is_yandex_ip_patch = mock.patch(
            'passport.backend.oauth.api.api.iface.views.is_yandex_ip',
            self.is_yandex_ip_mock,
        )
        self.is_yandex_ip_patch.start()

    def tearDown(self):
        self.is_yandex_ip_patch.stop()
        super(TestEditClient, self).tearDown()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'client_id': self.test_client.display_id,
            'title': 'client',
            'description': 'Test client',
            'scopes': ['test:foo', 'lunapark:use'],
            'icon': 'http://home.ru/icon',
            'homepage': 'http://home.ru',
            'platforms': ['web'],
            'redirect_uri': 'http://test',
            'is_yandex': '1',
            'icon_file': SimpleUploadedFile('cool_icon.jpg', b'file_content'),
            'icon_id': 'client_id/some_new_icon_id',
            'contact_email': 'new_test@test.ru',
        }

    def assert_statbox_ok(self, scopes=None, redirect_uris=None):
        self.check_statbox_entry(
            {
                'mode': 'edit_client',
                'status': 'ok',
                'client_id': self.test_client.display_id,
                'client_title': 'client',
                'client_description': 'Test client',
                'client_scopes': scopes or 'test:foo,lunapark:use',
                'client_redirect_uris': redirect_uris or 'http://test',
            },
            entry_index=-2,
        )

    def assert_email_sent(self, scopes_changed=True):
        eq_(len(self.fake_passport.requests), 1)
        self.fake_passport.requests[0].assert_properties_equal(
            post_args={
                'uid': TEST_UID,
                'client_id': self.test_client.display_id,
                'client_title': 'Тестовое приложение',
                'redirect_uris_changed': 1,
                'scopes_changed': int(bool(scopes_changed)),
            },
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET,
                'Ya-Consumer-Client-Ip': TEST_USER_IP,
                'Ya-Client-Cookie': TEST_COOKIE,
                'Ya-Client-Host': TEST_HOST,
            },
        )

    def assert_email_not_sent(self):
        ok_(not self.fake_passport.requests)

    def assert_tokens_invalidated(self):
        for token in list_tokens_by_uid(TEST_UID):
            ok_(token.is_invalidated_by_client_glogout(client=token.get_client()))

        self.check_statbox_entry(
            {
                'mode': 'invalidate_tokens',
                'target': 'client',
                'status': 'ok',
                'client_id': self.test_client.display_id,
            },
            entry_index=-1,
        )

    def assert_tokens_not_invalidated(self):
        for token in list_tokens_by_uid(TEST_UID):
            ok_(not token.is_invalidated_by_client_glogout(client=token.get_client()))

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        eq_(client.uid, TEST_UID)
        eq_(client.default_title, 'client')
        eq_(client.default_description, 'Test client')
        eq_(sorted([s.keyword for s in client.scopes]), sorted(['test:foo', 'lunapark:use']))
        eq_(client.icon, 'http://home.ru/icon')
        ok_(client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % self.test_client.display_id), client.icon_id)
        eq_(client.homepage, 'http://home.ru')
        eq_(client.redirect_uris, ['http://test'])
        eq_(client.modified, DatetimeNow())
        ok_(not client._callback)
        ok_(client.is_yandex)
        eq_(client.contact_email, 'new_test@test.ru')
        self.assert_statbox_ok()

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

    def test_yandex_client_without_token_invalidation_ok(self):
        with UPDATE(self.test_client) as client:
            client.is_yandex = True

        rv = self.make_request(
            headers=self.default_headers(user_ip=TEST_YANDEX_IP),
            scopes=['test:foo', 'test:bar'],
            redirect_uri='https://callback',
        )
        self.assert_status_ok(rv)

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

    def test_is_yandex_forbidden_by_ip(self):
        self.is_yandex_ip_mock.return_value = False
        rv = self.make_request()
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        ok_(not client.is_yandex)
        self.assert_statbox_ok()

    def test_icon_upload_error(self):
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            '{"error": "crit"}',
            status=500,
        )
        rv = self.make_request()
        self.assert_status_error(
            rv,
            [
                'backend.failed',
            ],
        )

    def test_icon_bad_format(self):
        self.fake_avatars_mds_api.set_response_value(
            'upload_from_file',
            '{"description": "cannot process image"}',
            status=400,
        )
        rv = self.make_request()
        self.assert_status_error(
            rv,
            [
                'icon.bad_format',
            ],
        )

    def test_icon_required(self):
        rv = self.make_request(is_yandex='1', exclude=['icon_file', 'icon_id'])
        self.assert_status_error(
            rv,
            [
                'icon.required',
            ],
        )

    def test_icon_cleanup_failed(self):
        self.fake_avatars_mds_api.set_response_value(
            'delete',
            '{"error": "crit"}',
            status=500,
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        ok_(client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % self.test_client.display_id), client.icon_id)

    def test_file_not_uploaded(self):
        rv = self.make_request(exclude=['icon_file'])
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        eq_(client.icon_id, 'client_id/some_new_icon_id')

    def test_description_required_for_premoderated_scope(self):
        rv = self.make_request(scopes=['test:premoderate'], description='')
        self.assert_status_error(rv, ['description.missing'])

    def test_tokens_not_invalidated(self):
        token = issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request(scopes=['test:foo', 'test:bar'], redirect_uri='https://callback')
        self.assert_status_ok(rv)
        eq_(list_tokens_by_uid(TEST_UID), [token])

    def test_invalid_form(self):
        rv = self.make_request(
            title='a' * 101,
            description='a' * 251,
            scopes=['money:frawd'],
            icon='http://ya.ru/42.gif',
            contact_email='not_an_email',
        )
        eq_(rv['status'], 'error')
        self.assert_status_error(
            rv,
            [
                'description.too_long',
                'title.too_long',
                'scopes.invalid',
                'contact_email.invalid',
            ],
        )
        client = Client.by_id(self.test_client.id)
        eq_(client.default_title, self.test_client.default_title)
        eq_(client.icon, self.test_client.icon)
        eq_(client.homepage, self.test_client.homepage)
        eq_(client.redirect_uris, self.test_client.redirect_uris)
        eq_(client.scopes, self.test_client.scopes)

    def test_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_not_creator(self):
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_error(rv, ['client.creator_required'])
        client = Client.by_id(self.test_client.id)
        eq_(client.default_title, self.test_client.default_title)
        eq_(client.icon, self.test_client.icon)
        eq_(client.homepage, self.test_client.homepage)
        eq_(client.redirect_uris, self.test_client.redirect_uris)
        eq_(client.scopes, self.test_client.scopes)

    def test_ok_with_several_redirect_uris(self):
        rv = self.make_request(redirect_uri=['http://test', 'https://prod'])
        self.assert_response_ok(rv, redirect_uris_added=True, invalidate_tokens=True, will_require_approval=False)
        client = Client.by_id(self.test_client.id)
        eq_(client.uid, TEST_UID)
        eq_(client.default_title, 'client')
        eq_(client.default_description, 'Test client')
        eq_(sorted([s.keyword for s in client.scopes]), sorted(['test:foo', 'lunapark:use']))
        eq_(client.icon, 'http://home.ru/icon')
        ok_(client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % self.test_client.display_id), client.icon_id)
        eq_(client.homepage, 'http://home.ru')
        eq_(client.redirect_uris, ['http://test', 'https://prod'])
        ok_(not client._callback)
        ok_(client.is_yandex)
        self.assert_statbox_ok(redirect_uris='http://test, https://prod')
        self.assert_email_sent()

    def test_ok_with_platforms(self):
        rv = self.make_request(
            platforms=['ios', 'android', 'turboapp', 'web'],
            ios_app_id=[TEST_IOS_APP_ID, TEST_IOS_APP_ID_OTHER],
            ios_appstore_url=TEST_IOS_APPSTORE_URL,
            android_package_name=[TEST_ANDROID_PACKAGE_NAME, TEST_ANDROID_PACKAGE_NAME_OTHER],
            android_cert_fingerprints=[TEST_ANDROID_FINGERPRINT],
            android_appstore_url=TEST_ANDROID_APPSTORE_URL,
            turboapp_base_url=TEST_TURBOAPP_BASE_URL,
        )
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        eq_(client.platforms, {'ios', 'android', 'turboapp', 'web'})

        eq_(client.ios_appstore_url, TEST_IOS_APPSTORE_URL)
        eq_(client.ios_default_app_id, TEST_IOS_APP_ID)
        eq_(client.ios_extra_app_ids, [TEST_IOS_APP_ID_OTHER])
        eq_(client.ios_app_ids, [TEST_IOS_APP_ID, TEST_IOS_APP_ID_OTHER])

        eq_(client.android_appstore_url, TEST_ANDROID_APPSTORE_URL)
        eq_(client.android_default_package_name, TEST_ANDROID_PACKAGE_NAME)
        eq_(client.android_extra_package_names, [TEST_ANDROID_PACKAGE_NAME_OTHER])
        eq_(client.android_package_names, [TEST_ANDROID_PACKAGE_NAME, TEST_ANDROID_PACKAGE_NAME_OTHER])

        eq_(client.turboapp_base_url, TEST_TURBOAPP_BASE_URL)

    def test_ok_with_owners(self):
        rv = self.make_request(owner_uids=[TEST_OTHER_UID], owner_groups=[TEST_GROUP])
        self.assert_response_ok(rv, redirect_uris_added=True, invalidate_tokens=True, will_require_approval=False)
        client = Client.by_id(self.test_client.id)
        eq_(client.uid, TEST_UID)
        eq_(client.owner_uids, [TEST_OTHER_UID])
        eq_(client.owner_groups, [TEST_GROUP])

    def test_ok_but_failed_to_send_email(self):
        self.fake_passport.set_response_side_effect(
            'oauth_client_edited_send_notifications',
            PassportPermanentError(),
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
        self.assert_statbox_ok()

    def test_callback_changed_tokens_not_invalidated(self):
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request(scopes=['test:foo', 'test:bar'])
        self.assert_response_ok(rv, redirect_uris_added=True, invalidate_tokens=False, will_require_approval=False)
        self.assert_tokens_not_invalidated()
        self.assert_email_sent(scopes_changed=False)

    def test_scope_changed_tokens_invalidated(self):
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request(redirect_uri='https://callback')
        self.assert_response_ok(rv, redirect_uris_added=False, invalidate_tokens=True, will_require_approval=False)
        self.assert_tokens_invalidated()
        self.check_historydb_event_entry(
            {
                'action': 'change',
                'target': 'client',
                'client_id': self.test_client.display_id,
                'old_scopes': 'test:foo,test:bar',
                'new_scopes': 'test:foo,lunapark:use',
                'old_redirect_uris': 'https://callback',
                'new_redirect_uris': 'https://callback',
            },
            entry_index=-1,
        )
        self.assert_email_not_sent()  # пока не шлём письмо, если поменялись только скоупы

    def test_scope_and_redirect_uris_changed_tokens_not_invalidated(self):
        issue_token(uid=TEST_UID, client=self.test_client, grant_type=TEST_GRANT_TYPE, env=self.env)
        rv = self.make_request(
            platforms=[],
            redirect_uri=[],
            scopes=['test:foo', 'test:bar', 'test:ttl'],
        )
        self.assert_response_ok(rv, redirect_uris_added=False, invalidate_tokens=False, will_require_approval=False)
        self.assert_tokens_not_invalidated()
        self.assert_email_not_sent()

    def test_is_yandex_forbidden_by_account_type(self):
        self.setup_blackbox_response(attributes={})
        rv = self.make_request()
        self.assert_status_ok(rv)
        client = Client.by_id(self.test_client.id)
        ok_(not client.is_yandex)
        self.assert_statbox_ok()

    def test_ok_with_hidden_scope(self):
        with UPDATE(self.test_client) as client:
            client.set_extra_visible_scopes([Scope.by_keyword('test:invisible')])

        rv = self.make_request(scopes=['test:invisible'])
        self.assert_response_ok(rv, redirect_uris_added=True, invalidate_tokens=True, will_require_approval=False)
        client = Client.by_id(self.test_client.id)
        eq_(client.uid, TEST_UID)
        eq_(client.scopes, set([Scope.by_keyword('test:invisible')]))

    def test_ok_with_turboapp_and_phone_scope(self):
        with UPDATE(self.test_client) as client:
            client.turboapp_base_url = TEST_TURBOAPP_BASE_URL

        rv = self.make_request(scopes=['test:default_phone'])
        self.assert_response_ok(rv, redirect_uris_added=True, invalidate_tokens=True, will_require_approval=False)
        client = Client.by_id(self.test_client.id)
        eq_(client.uid, TEST_UID)
        eq_(client.scopes, set([Scope.by_keyword('test:default_phone')]))


@override_settings(
    REQUIRE_DESCRIPTION_FOR_CLIENTS_WAITING_FOR_APPROVAL=True,
)
class TestValidateClientChanges(BaseIfaceApiTestCase):
    default_url = reverse_lazy('iface_validate_client')
    http_method = 'POST'

    def setUp(self):
        super(TestValidateClientChanges, self).setUp()
        self.setup_blackbox_response(
            attributes={
                settings.BB_ATTR_ACCOUNT_IS_CORPORATE: '1',
            },
        )
        self.is_yandex_ip_mock = mock.Mock(return_value=True)
        self.is_yandex_ip_patch = mock.patch(
            'passport.backend.oauth.api.api.iface.views.is_yandex_ip',
            self.is_yandex_ip_mock,
        )
        self.is_yandex_ip_patch.start()

    def tearDown(self):
        self.is_yandex_ip_patch.stop()
        super(TestValidateClientChanges, self).tearDown()

    def default_params(self):
        return {
            'consumer': 'oauth_frontend',
            'title': 'client',
            'description': 'Test client',
            'scopes': ['test:foo', 'lunapark:use'],
            'icon': 'http://home.ru/icon',
            'homepage': 'http://home.ru',
            'platforms': ['web'],
            'redirect_uri': 'http://test',
            'is_yandex': '1',
            'icon_file': SimpleUploadedFile('cool_icon.jpg', b'file_content'),
            'icon_id': 'client_id/some_new_icon_id',
            'contact_email': 'test@test.ru',
        }

    def test_ok_for_new(self):
        rv = self.make_request(scopes=['test:foo', 'test:bar'])
        self.assert_response_ok(
            rv,
            token_ttl=None,
            will_require_approval=False,
        )

    def test_ok_for_limited_ttl(self):
        rv = self.make_request(scopes=['test:ttl'])
        self.assert_response_ok(
            rv,
            token_ttl=60,
            is_ttl_refreshable=False,
            will_require_approval=False,
        )

    def test_ok_for_refreshable_ttl(self):
        rv = self.make_request(scopes=['test:ttl_refreshable'])
        self.assert_response_ok(
            rv,
            token_ttl=300,
            is_ttl_refreshable=True,
            will_require_approval=False,
        )

    def test_ok_for_premoderated_scope(self):
        rv = self.make_request(scopes=['test:premoderate'])
        self.assert_response_ok(
            rv,
            token_ttl=None,
            will_require_approval=True,
        )

    def test_description_required_for_premoderated_scope(self):
        rv = self.make_request(scopes=['test:premoderate'], description='')
        self.assert_status_error(rv, ['description.missing'])

    def test_callback_changed_tokens_not_invalidated(self):
        rv = self.make_request(client_id=self.test_client.display_id, scopes=['test:foo', 'test:bar'])
        self.assert_response_ok(
            rv,
            redirect_uris_added=True,
            invalidate_tokens=False,
            token_ttl=None,
            will_require_approval=False,
        )

    def test_scope_changed_tokens_invalidated(self):
        rv = self.make_request(client_id=self.test_client.display_id, redirect_uri='https://callback')
        self.assert_response_ok(
            rv,
            redirect_uris_added=False,
            invalidate_tokens=True,
            token_ttl=None,
            will_require_approval=False,
        )

    def test_platform_ios_added_tokens_not_invalidated(self):
        rv = self.make_request(
            platforms=['ios', 'web'],
            client_id=self.test_client.display_id,
            scopes=['test:foo', 'test:bar'],
            ios_app_id=TEST_IOS_APP_ID,
        )
        self.assert_response_ok(
            rv,
            redirect_uris_added=True,
            invalidate_tokens=False,
            token_ttl=None,
            will_require_approval=False,
        )

    def test_platform_android_added_tokens_not_invalidated(self):
        rv = self.make_request(
            platforms=['android', 'web'],
            client_id=self.test_client.display_id,
            scopes=['test:foo', 'test:bar'],
            android_package_name=TEST_ANDROID_PACKAGE_NAME,
            android_cert_fingerprints=[TEST_ANDROID_FINGERPRINT],
        )
        self.assert_response_ok(
            rv,
            redirect_uris_added=True,
            invalidate_tokens=False,
            token_ttl=None,
            will_require_approval=False,
        )

    def test_platform_turboapp_added_tokens_not_invalidated(self):
        rv = self.make_request(
            platforms=['turboapp', 'web'],
            client_id=self.test_client.display_id,
            scopes=['test:foo', 'test:bar'],
            turboapp_base_url=TEST_TURBOAPP_BASE_URL,
        )
        self.assert_response_ok(
            rv,
            redirect_uris_added=True,
            invalidate_tokens=False,
            token_ttl=None,
            will_require_approval=False,
        )

    def test_scope_and_redirect_uris_changed_tokens_not_invalidated(self):
        rv = self.make_request(
            platforms=[],
            client_id=self.test_client.display_id,
            redirect_uri=[],
            scopes=['test:foo', 'test:bar', 'test:ttl'],
        )
        self.assert_response_ok(
            rv,
            redirect_uris_added=False,
            invalidate_tokens=False,
            token_ttl=60,
            is_ttl_refreshable=False,
            will_require_approval=False,
        )

# -*- coding: utf-8 -*-
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.urls import reverse_lazy
from passport.backend.core.builders.avatars_mds_api.faker import avatars_mds_api_upload_ok_response
from passport.backend.core.builders.blackbox import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_userinfo_response,
)
from passport.backend.oauth.core.db.client import (
    Client,
    PLATFORM_WEB,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


TEST_TITLE = 'test-title'
TEST_DESCRIPTION = 'test-description'
TEST_UID = 123

TEST_NEW_CLIENT_ICON_ID_PREFIX = '1234/%s-'  # сюда подставится client_id


@override_settings(
    EXTERNAL_MANAGE_CLIENT_SCOPES=['test:foo'],
    OAUTH_MANAGE_CLIENTS_SCOPE_KEYWORD='oauth:manage_clients',
    CLIENT_ID_TO_DOMAIN={'fake_clid': 'test_domain'},
)
class CreateClientExternalTestcase(BundleApiTestCase):
    default_url = reverse_lazy('api_create_client_external')
    http_method = 'POST'
    require_grants = False
    require_consumer = False

    def setUp(self):
        super(CreateClientExternalTestcase, self).setUp()

        self.fake_avatars_mds_api.set_response_value('upload_from_file', avatars_mds_api_upload_ok_response())

        self.setup_blackbox_response()

    def setup_blackbox_response(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(has_user_in_token=False, scope='oauth:manage_clients'),
        )
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_UID,
                login='test_login@test_domain',
                aliases={
                    'pdd': 'test_login@test_domain',
                },
            ),
        )

    def default_headers(self):
        return {'HTTP_AUTHORIZATION': 'OAuth test_token'}

    def default_params(self):
        return {
            'title': TEST_TITLE,
            'description': TEST_DESCRIPTION,
            'owner_login': 'test_login@test_domain',
            'scopes': ['test:foo'],
            'redirect_uris': ['http://test.ru/test1', 'http://test.ru/test2'],
            'homepage': 'test.ru',
            'icon_file': SimpleUploadedFile('test_icon.jpg', b'test_file_content'),
        }

    def assert_statbox_ok(self, client_id, **kwargs):
        expected_entry = {
            'mode': 'create_client',
            'type': 'external_web',
            'status': 'ok',
            'client_id': client_id,
            'creator_uid': str(TEST_UID),
            'client_title': TEST_TITLE,
            'client_description': TEST_DESCRIPTION,
            'client_scopes': 'test:foo',
            'client_redirect_uris': 'http://test.ru/test1, http://test.ru/test2',
        }
        expected_entry.update(kwargs)
        self.check_statbox_entries([expected_entry])

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        assert 'client_id' in rv
        assert 'client_secret' in rv

        client = Client.by_display_id(rv['client_id'])
        assert client.uid == TEST_UID
        assert client.default_title == TEST_TITLE
        assert client.default_description == TEST_DESCRIPTION
        assert client.homepage == 'http://test.ru'
        assert sorted([s.keyword for s in client.scopes]) == sorted(['test:foo'])
        assert client.redirect_uris == ['http://test.ru/test1', 'http://test.ru/test2']
        assert client.platforms == {PLATFORM_WEB}
        assert client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % rv['client_id'])
        assert not client.is_yandex

        self.assert_statbox_ok(rv['client_id'])

    def test_token_invalid_error(self):
        self.fake_blackbox.set_response_value('oauth', blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS))
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_token_no_scope_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(has_user_in_token=False, scope='oauth:not_manage_clients'),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_token_not_2_legged_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(scope='oauth:manage_clients'),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_domain_invalid_error(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_UID,
                login='test_login@test_domain_not_in_config',
                aliases={
                    'pdd': 'test_login@test_domain_not_in_config',
                },
            ),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['domain.invalid'])

    def test_user_not_found_error(self):
        self.fake_blackbox.set_response_value('userinfo', blackbox_userinfo_response(None))
        rv = self.make_request()
        self.assert_status_error(rv, ['user.not_found'])

    def test_scope_not_allowed_error(self):
        rv = self.make_request(scopes=['test:bar'])
        self.assert_status_error(rv, ['scope.not_allowed'])


@override_settings(
    EXTERNAL_MANAGE_CLIENT_SCOPES=['test:foo'],
    EXTERNAL_MANAGE_DEFAULT_PHONES_ALLOWED_CLIENT_ID=['fake_clid'],
    DEFAULT_PHONE_SCOPE_KEYWORD='test:default_phone',
    OAUTH_MANAGE_CLIENTS_SCOPE_KEYWORD='oauth:manage_clients',
    CLIENT_ID_TO_DOMAIN={
        'fake_clid': 'test_domain',
        'fake_clid2': 'test_domain2',
    },
)
class EditClientExternalWebAuthTestcase(BundleApiTestCase):
    default_url = reverse_lazy('api_edit_client_external')
    http_method = 'POST'
    require_grants = False
    require_consumer = False

    def setUp(self):
        super(EditClientExternalWebAuthTestcase, self).setUp()

        self.fake_avatars_mds_api.set_response_value('upload_from_file', avatars_mds_api_upload_ok_response())

        self.setup_blackbox_response()

    def setup_blackbox_response(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(has_user_in_token=False, scope='oauth:manage_clients'),
        )
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_UID,
                login='test_login@test_domain',
                aliases={
                    'pdd': 'test_login@test_domain',
                },
            ),
        )

    def default_headers(self):
        return {'HTTP_AUTHORIZATION': 'OAuth test_token'}

    def default_params(self):
        return {
            'title': TEST_TITLE,
            'description': TEST_DESCRIPTION,
            'client_id': self.test_client.display_id,
            'scopes': ['test:foo', 'test:default_phone'],
            'redirect_uris': ['http://test.ru/test1', 'http://test.ru/test2'],
            'homepage': 'test.ru',
            'icon_file': SimpleUploadedFile('test_icon.jpg', b'test_file_content'),
        }

    def assert_statbox_ok(self, client_id, **kwargs):
        expected_entry = {
            'mode': 'edit_client',
            'type': 'external_web',
            'status': 'ok',
            'client_id': client_id,
            'creator_uid': '1',
            'client_title': TEST_TITLE,
            'client_description': TEST_DESCRIPTION,
            'client_scopes': 'test:foo,test:default_phone',
            'client_redirect_uris': 'http://test.ru/test1, http://test.ru/test2',
        }
        expected_entry.update(kwargs)
        self.check_statbox_entries([expected_entry])

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        client = Client.by_display_id(self.test_client.display_id)
        assert client.uid == 1
        assert client.default_title == TEST_TITLE
        assert client.default_description == TEST_DESCRIPTION
        assert client.homepage == 'http://test.ru'
        assert sorted([s.keyword for s in client.scopes]) == sorted(['test:foo', 'test:default_phone'])
        assert client.redirect_uris == ['http://test.ru/test1', 'http://test.ru/test2']
        assert client.platforms == {PLATFORM_WEB}
        assert client.icon_id.startswith(TEST_NEW_CLIENT_ICON_ID_PREFIX % self.test_client.display_id)
        assert not client.is_yandex

        self.assert_statbox_ok(self.test_client.display_id)

    def test_token_invalid_error(self):
        self.fake_blackbox.set_response_value('oauth', blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS))
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_token_no_scope_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(has_user_in_token=False, scope='oauth:not_manage_clients'),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_token_not_2_legged_error(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(scope='oauth:manage_clients'),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['oauth_token.invalid'])

    def test_domain_not_in_config(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_UID,
                login='test_login@test_domain_not_in_config',
                aliases={
                    'pdd': 'test_login@test_domain_not_in_config',
                },
            ),
        )
        rv = self.make_request(domain='not_in_config_domain')
        self.assert_status_error(rv, ['client_id.not_allowed'])

    def test_user_not_found_error(self):
        self.fake_blackbox.set_response_value('userinfo', blackbox_userinfo_response(None))
        rv = self.make_request()
        self.assert_status_error(rv, ['user.not_found'])

    def test_scope_not_allowed_error(self):
        rv = self.make_request(scopes=['test:bar'])
        self.assert_status_error(rv, ['scope.not_allowed'])

    def test_client_id_not_allowed_error(self):
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_UID,
                login='test_login@test_domain_2',
                aliases={
                    'pdd': 'test_login@test_domain_2',
                },
            ),
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['client_id.not_allowed'])

    def test_client_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_default_phone_not_allowed(self):
        self.fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(has_user_in_token=False, scope='oauth:manage_clients', client_id='fake_clid2'),
        )
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                TEST_UID,
                login='test_login@test_domain2',
                aliases={
                    'pdd': 'test_login@test_domain2',
                },
            ),
        )
        rv = self.make_request(scopes=['test:default_phone'])
        self.assert_status_error(rv, ['scope.not_allowed'])

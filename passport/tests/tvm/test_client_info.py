# -*- coding: utf-8 -*-
from django.conf import settings
from django.test.utils import override_settings
from django.urls import reverse_lazy
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.oauth.core.common.utils import now
from passport.backend.oauth.core.db.eav import (
    CREATE,
    UPDATE,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ABC_SERVICE_ID,
    TEST_CIPHER_KEYS,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase
from passport.backend.oauth.core.test.utils import iter_eq
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient


@override_settings(ATTRIBUTE_CIPHER_KEYS=TEST_CIPHER_KEYS)
class ClientInfoTestcase(BundleApiTestCase):
    default_url = reverse_lazy('tvm_client_info')
    http_method = 'GET'
    require_grants = False

    def setUp(self):
        super(ClientInfoTestcase, self).setUp()
        with CREATE(TVMClient.create(
            creator_uid=TEST_UID,
            name='Test Client',
        )) as client:
            client.add_new_secret_key()
            client.add_new_secret_key()
            self.test_client = client

    def default_params(self):
        return dict(
            consumer='nginx',
            client_id=self.test_client.id,
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        iter_eq(
            rv,
            {
                'status': 'ok',
                'id': 1,
                'name': 'Test Client',
                'create_time': TimeNow(),
                'modification_time': TimeNow(),
                'creator_uid': TEST_UID,
                'abc_service_id': None,
            },
        )

    def test_ok_for_abc_client(self):
        with UPDATE(self.test_client) as client:
            client.abc_service_id = TEST_ABC_SERVICE_ID
            client.vault_secret_uuid = 'secret_uuid'
            client.vault_version_uuid = 'version_uuid'

        rv = self.make_request()
        self.assert_status_ok(rv)

        iter_eq(
            rv,
            {
                'status': 'ok',
                'id': 1,
                'name': 'Test Client',
                'create_time': TimeNow(),
                'modification_time': TimeNow(),
                'creator_uid': TEST_UID,
                'abc_service_id': TEST_ABC_SERVICE_ID,
                'vault_link': settings.VAULT_SECRET_LINK_TEMPLATE.format(
                    secret_uuid='secret_uuid',
                    version_uuid='version_uuid',
                ),
            },
        )

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])

    def test_client_deleted(self):
        with UPDATE(self.test_client) as client:
            client.deleted = now()
        rv = self.make_request()
        self.assert_status_error(rv, ['client.not_found'])

    def test_client_deleted_with_param(self):
        with UPDATE(self.test_client) as client:
            client.deleted = now()
        rv = self.make_request(with_deleted=True)
        self.assert_status_ok(rv)

        iter_eq(
            rv,
            {
                'status': 'ok',
                'id': 1,
                'name': 'Test Client',
                'create_time': TimeNow(),
                'modification_time': TimeNow(),
                'deletion_time': TimeNow(),
                'creator_uid': TEST_UID,
                'abc_service_id': None,
            },
        )

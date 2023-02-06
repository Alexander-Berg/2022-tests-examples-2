# -*- coding: utf-8 -*-

from nose.tools import (
    assert_not_equal,
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_CONSUMER1,
    TEST_CONSUMER_IP1,
    TEST_USER_IP1,
)
from passport.backend.core.builders.blackbox.constants import BLACKBOX_GET_DEVICE_PUBLIC_KEY_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_device_signature_response,
    blackbox_get_device_public_key_response,
)
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.device_public_key import insert_device_public_key
from passport.backend.core.models.device_public_key import DevicePublicKey
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.useragent.sync import RequestError


DEVICE_ID1 = '0' * 32
OWNER1 = 'device_owner1'
OWNER2 = 'device_owner2'
PUBLIC_KEY1 = 'key1'
PUBLIC_KEY2 = 'key2'
NONCE1 = 'nonce1'
NONCE_SIGN_SPACE1 = 'nonce_sign_space1'
SIGNATURE1 = 'signature1'


class BaseDevicePublicTestCase(BaseBundleTestViews):
    def setUp(self):
        super(BaseDevicePublicTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.setup_statbox_templates()
        self.assign_grants()

    def tearDown(self):
        self.env.stop()
        del self.env
        super(BaseDevicePublicTestCase, self).tearDown()

    def assign_grants(self, owner=OWNER1):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'device_public_key_create': [owner],
                        'device_public_key_update': [owner],
                        'device_public_key_delete': [owner],
                    },
                ),
            },
        )

    def assign_no_grants(self):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(),
            },
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base_action',
            device_id=DEVICE_ID1,
            owner=OWNER1,
            consumer=TEST_CONSUMER1,
        )
        self.env.statbox.bind_entry(
            'create_device_public_key_ok',
            _inherit_from=['base_action'],
            action='create_device_public_key',
            status='ok',
        )
        self.env.statbox.bind_entry(
            'create_device_public_key_error',
            _inherit_from=['base_action'],
            action='create_device_public_key',
            status='error',
        )
        self.env.statbox.bind_entry(
            'update_device_public_key_ok',
            _inherit_from=['base_action'],
            action='update_device_public_key',
            status='ok',
        )
        self.env.statbox.bind_entry(
            'update_device_public_key_error',
            _inherit_from=['base_action'],
            action='update_device_public_key',
            status='error',
        )
        self.env.statbox.bind_entry(
            'delete_device_public_key_ok',
            _inherit_from=['base_action'],
            action='delete_device_public_key',
            status='ok',
        )
        self.env.statbox.bind_entry(
            'delete_device_public_key_error',
            _inherit_from=['base_action'],
            action='delete_device_public_key',
            status='error',
        )

    def build_device_public_key(self, public_key=PUBLIC_KEY1, owner_id=1):
        return dict(
            public_key=public_key,
            owner_id=owner_id,
            version=1,
            device_id=DEVICE_ID1,
        )

    def find_device_public_key(self, device_id=DEVICE_ID1):
        rels = self.env.db.select(
            table_name='device_public_key',
            db='passportdbcentral',
            device_id=device_id,
        )
        ok_(len(rels) <= 1)
        return None if not rels else dict(rels[0])

    def save_device_public_key(self, key):
        key = DevicePublicKey(
            device_id=key['device_id'],
            owner_id=key['owner_id'],
            public_key=key['public_key'],
            version=key['version'],
        )
        insert_device_public_key(key)

    def assert_device_public_key_not_saved(self, device_id=DEVICE_ID1):
        key = self.find_device_public_key(device_id)
        ok_(key is None)

    def setup_blackbox(self):
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(),
            ],
        )

    def assert_check_device_signature_requested(
        self,
        request,
        public_key=PUBLIC_KEY1,
        nonce_sign_space=NONCE_SIGN_SPACE1,
    ):
        request.assert_properties_equal(
            method='POST',
            url='https://blackbox/blackbox/',
            post_args={
                'method': 'check_device_signature',
                'format': 'json',
                'device_id': DEVICE_ID1,
                'nonce': NONCE1,
                'nonce_sign_space': nonce_sign_space,
                'public_key': public_key,
                'signature': SIGNATURE1,
                'version': '1',
            },
        )


class BaseCreateDriveDevicePublicKeyTestCase(BaseDevicePublicTestCase):
    def assign_grants(self, owner=OWNER1):
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'device_public_key_create': [owner],
                    },
                ),
                'drive_device': dict(
                    networks=[TEST_USER_IP1],
                    grants={
                        'auth_forward_drive': ['public_access'],
                    },
                ),
            },
        )

    def assert_check_device_signature_requested(
        self,
        request,
        public_key=PUBLIC_KEY1,
    ):
        super(BaseCreateDriveDevicePublicKeyTestCase, self).assert_check_device_signature_requested(
            request,
            public_key=public_key,
            nonce_sign_space='auto_head_unit',
        )

    def assert_get_device_public_key_requested(self, request):
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('https://blackbox/blackbox/?')
        request.assert_query_equals(
            {
                'method': 'get_device_public_key',
                'format': 'json',
                'device_id': DEVICE_ID1,
            },
        )

    def setup_blackbox(self, device_public_key=None):
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(),
            ],
        )
        if device_public_key is None:
            response = blackbox_get_device_public_key_response(status=BLACKBOX_GET_DEVICE_PUBLIC_KEY_STATUS.PUBLIC_KEY_NOT_FOUND)
        else:
            self.save_device_public_key(device_public_key)
            response = blackbox_get_device_public_key_response(
                value=device_public_key['public_key'],
                version=device_public_key['version'],
                owner_id=device_public_key['owner_id'],
            )
        self.env.blackbox.set_response_side_effect('get_device_public_key', [response])

    def setup_kolmogor(self, total=0, rps=0):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rps),
                str(total),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK', 'OK'])

    def assert_kolmogor_get_rps_requested(self, request):
        self.assert_kolmogor_get_requested(
            request,
            'device_public_key_short',
            ['drive_create_key_rps'],
        )

    def assert_kolmogor_inc_rps_requested(self, request):
        self.assert_kolmogor_inc_requested(
            request,
            'device_public_key_short',
            ['drive_create_key_rps'],
        )

    def assert_kolmogor_get_rpd_requested(self, request):
        self.assert_kolmogor_get_requested(request, 'device_public_key', ['drive_create_key'])

    def assert_kolmogor_inc_rpd_requested(self, request):
        self.assert_kolmogor_inc_requested(request, 'device_public_key', ['drive_create_key'])

    def assert_kolmogor_get_requested(self, request, space, keys):
        request.assert_properties_equal(method='GET')
        request.assert_url_starts_with('http://kolmogor/get?')
        request.assert_query_equals(
            {
                'keys': ','.join(keys),
                'space': space,
            },
        )

    def assert_kolmogor_inc_requested(self, request, space, keys):
        request.assert_properties_equal(
            method='POST',
            url='http://kolmogor/inc',
            post_args={
                'keys': ','.join(keys),
                'space': space,
            },
        )


@with_settings_hosts(
    BLACKBOX_RETRIES=1,
    BLACKBOX_URL='https://blackbox',
    DEVICE_PUBLIC_KEY_KOLMOGOR_KEY_SPACE='device_public_key',
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={
        OWNER1: 1,
        OWNER2: 2,
    },
    DEVICE_PUBLIC_KEY_SHORT_KOLMOGOR_KEY_SPACE='device_public_key_short',
    DRIVE_PRODUCTION_PUBLIC_KEY_OWNER_ID=1,
    DRIVE_DEVICE_PUBLIC_KEY_API_ENABLED=True,
    DRIVE_NONCE_SIGN_SPACE='auto_head_unit',
    KOLMOGOR_URL='http://kolmogor',
    KOLMOGOR_RETRIES=1,
    **mock_counters(
        DRIVE_CREATE_DEVICE_PUBLIC_KEY_RPD_COUNTER=10,
        DRIVE_CREATE_DEVICE_PUBLIC_KEY_RPS_COUNTER=5,
    )
)
class TestCreateDriveDevicePublicKey(BaseCreateDriveDevicePublicKeyTestCase):
    default_url = '/1/bundle/drive_device_public_key/create/'
    http_method = 'POST'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_ip': TEST_USER_IP1,
    }
    http_query_args = {
        'device_id': DEVICE_ID1,
        'owner': OWNER1,
        'public_key': PUBLIC_KEY1,
        'check_nonce': NONCE1,
        'check_signature': SIGNATURE1,
    }
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(TestCreateDriveDevicePublicKey, self).setUp()
        self.assign_grants()
        self.setup_blackbox()
        self.setup_kolmogor()

    def test_new_public_key(self):
        rv = self.make_request()

        self.assert_ok_response(rv)

        key = self.build_device_public_key()
        saved_key = self.find_device_public_key()
        eq_(saved_key, key)

        eq_(len(self.env.blackbox.requests), 2)
        self.assert_check_device_signature_requested(self.env.blackbox.requests[0])
        self.assert_get_device_public_key_requested(self.env.blackbox.requests[1])

        eq_(len(self.env.kolmogor.requests), 4)
        self.assert_kolmogor_get_rps_requested(self.env.kolmogor.requests[0])
        self.assert_kolmogor_get_rpd_requested(self.env.kolmogor.requests[1])
        self.assert_kolmogor_inc_rps_requested(self.env.kolmogor.requests[2])
        self.assert_kolmogor_inc_rpd_requested(self.env.kolmogor.requests[3])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_ok'),
            ],
        )

    def test_public_key_exists(self):
        old_key = self.build_device_public_key()
        self.setup_blackbox(device_public_key=old_key)

        rv = self.make_request(query_args={'public_key': PUBLIC_KEY2})

        self.assert_error_response(rv, ['device_public_key.conflict'])

        saved_key = self.find_device_public_key()
        eq_(saved_key, old_key)

        new_key = self.build_device_public_key(public_key=PUBLIC_KEY2)
        assert_not_equal(saved_key, new_key)

        eq_(len(self.env.blackbox.requests), 2)
        self.assert_check_device_signature_requested(
            self.env.blackbox.requests[0],
            public_key=PUBLIC_KEY2,
        )
        self.assert_get_device_public_key_requested(self.env.blackbox.requests[1])

        eq_(len(self.env.kolmogor.requests), 2)
        self.assert_kolmogor_get_rps_requested(self.env.kolmogor.requests[0])
        self.assert_kolmogor_get_rpd_requested(self.env.kolmogor.requests[1])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_error'),
            ],
        )

    def test_public_key_for_another_owner_exists(self):
        old_key = self.build_device_public_key(owner_id=2)
        self.setup_blackbox(device_public_key=old_key)

        rv = self.make_request(query_args={'owner': OWNER1})

        self.assert_error_response(rv, ['device_public_key.conflict'])

    def test_same_public_exists(self):
        old_key = self.build_device_public_key()
        self.setup_blackbox(device_public_key=old_key)

        rv = self.make_request()

        self.assert_ok_response(rv)

        saved_key = self.find_device_public_key()
        eq_(saved_key, old_key)

        eq_(len(self.env.blackbox.requests), 2)
        self.assert_check_device_signature_requested(self.env.blackbox.requests[0])
        self.assert_get_device_public_key_requested(self.env.blackbox.requests[1])

        eq_(len(self.env.kolmogor.requests), 4)
        self.assert_kolmogor_get_rps_requested(self.env.kolmogor.requests[0])
        self.assert_kolmogor_get_rpd_requested(self.env.kolmogor.requests[1])
        self.assert_kolmogor_inc_rps_requested(self.env.kolmogor.requests[2])
        self.assert_kolmogor_inc_rpd_requested(self.env.kolmogor.requests[3])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_ok'),
            ],
        )

    def test_unknown_owner(self):
        self.assign_grants(owner='unknown')

        rv = self.make_request(query_args={'owner': 'unknown'})

        self.assert_error_response(rv, ['device_public_key.owner_invalid'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'create_device_public_key_error',
                    owner='unknown',
                ),
            ],
        )

    def test_no_grants(self):
        self.assign_no_grants()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['access.denied'],
            status_code=403,
        )
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_error'),
            ],
        )

    def test_not_granted_owner(self):
        rv = self.make_request(query_args={'owner': OWNER2})

        self.assert_error_response(
            rv,
            ['access.denied'],
            status_code=403,
        )
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'create_device_public_key_error',
                    owner=OWNER2,
                ),
            ],
        )

    def test_check_not_passed(self):
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(
                    status='SIGNATURE.INVALID',
                    error='your password',
                ),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['internal.permanent'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_error'),
            ],
        )

    def test_blackbox_check_device_signature_timeout(self):
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                RequestError(),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_error'),
            ],
        )

    def test_blackbox_get_device_public_key_timeout(self):
        self.env.blackbox.set_response_side_effect(
            'get_device_public_key',
            [
                RequestError(),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_error'),
            ],
        )

    def test_total_limit_exceeded(self):
        self.setup_kolmogor(total=10)

        rv = self.make_request()

        self.assert_error_response(rv, ['rate.limit_exceeded'])
        self.assert_device_public_key_not_saved()

        eq_(len(self.env.kolmogor.requests), 2)
        self.assert_kolmogor_get_rps_requested(self.env.kolmogor.requests[0])
        self.assert_kolmogor_get_rpd_requested(self.env.kolmogor.requests[1])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_error'),
            ],
        )

    def test_kolmogor_get_timeout(self):
        self.env.kolmogor.set_response_side_effect('get', [RequestError()])

        rv = self.make_request()

        self.assert_ok_response(rv)

        key = self.build_device_public_key()
        saved_key = self.find_device_public_key()
        eq_(saved_key, key)

        eq_(len(self.env.kolmogor.requests), 1)
        self.assert_kolmogor_get_rps_requested(self.env.kolmogor.requests[0])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_ok'),
            ],
        )

    def test_kolmogor_inc_timeout(self):
        self.env.kolmogor.set_response_side_effect('inc', [RequestError()])

        rv = self.make_request()

        self.assert_ok_response(rv)

        key = self.build_device_public_key()
        saved_key = self.find_device_public_key()
        eq_(saved_key, key)

        eq_(len(self.env.kolmogor.requests), 3)
        self.assert_kolmogor_get_rps_requested(self.env.kolmogor.requests[0])
        self.assert_kolmogor_get_rpd_requested(self.env.kolmogor.requests[1])
        self.assert_kolmogor_inc_rps_requested(self.env.kolmogor.requests[2])

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_ok'),
            ],
        )

    def test_database_failed(self):
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.try_again'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('create_device_public_key_error'),
            ],
        )

    def test_forbidden_user_ip(self):
        rv = self.make_request(headers={'user_ip': TEST_CONSUMER_IP1})
        self.assert_error_response(rv, ['access.denied'], status_code=403)

    def test_not_restricted_owner_and_forbidden_user_ip(self):
        self.assign_grants(OWNER2)

        rv = self.make_request(
            headers={'user_ip': TEST_CONSUMER_IP1},
            query_args={'owner': OWNER2},
        )

        self.assert_ok_response(rv)


@with_settings_hosts(
    DRIVE_DEVICE_PUBLIC_KEY_API_ENABLED=False,
)
class TestCreateDriveDevicePublicKeyApiDisabled(BaseCreateDriveDevicePublicKeyTestCase):
    default_url = '/1/bundle/drive_device_public_key/create/'
    http_method = 'POST'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
        'user_ip': TEST_USER_IP1,
    }
    http_query_args = {
        'device_id': DEVICE_ID1,
        'owner': OWNER1,
        'public_key': PUBLIC_KEY1,
        'check_nonce': NONCE1,
        'check_signature': SIGNATURE1,
    }
    consumer = TEST_CONSUMER1

    def test_new_public_key(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['internal.permanent'])

        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'create_device_public_key_error',
                    _exclude=['device_id', 'owner'],
                ),
            ],
        )


@with_settings_hosts(
    BLACKBOX_RETRIES=1,
    BLACKBOX_URL='https://blackbox',
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={
        OWNER1: 1,
        OWNER2: 2,
    },
    DRIVE_NONCE_SIGN_SPACE='auto_head_unit',
)
class TestUpdateDevicePublicKey(BaseDevicePublicTestCase):
    default_url = '/1/bundle/device_public_key/update/'
    http_method = 'POST'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
    }
    http_query_args = {
        'device_id': DEVICE_ID1,
        'owner': OWNER1,
        'public_key': PUBLIC_KEY1,
        'check_nonce': NONCE1,
        'check_nonce_sign_space': NONCE_SIGN_SPACE1,
        'check_signature': SIGNATURE1,
    }
    consumer = TEST_CONSUMER1

    def setUp(self):
        super(TestUpdateDevicePublicKey, self).setUp()
        self.setup_blackbox()

    def test_public_key_exists(self):
        old_key = self.build_device_public_key()
        self.save_device_public_key(old_key)

        rv = self.make_request(query_args={'public_key': PUBLIC_KEY2})

        self.assert_ok_response(rv)

        saved_key = self.find_device_public_key(DEVICE_ID1)
        new_key = self.build_device_public_key(PUBLIC_KEY2)
        eq_(saved_key, new_key)
        assert_not_equal(saved_key, old_key)

        eq_(len(self.env.blackbox.requests), 1)
        self.assert_check_device_signature_requested(
            self.env.blackbox.requests[0],
            public_key=PUBLIC_KEY2,
        )

        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('update_device_public_key_ok'),
            ],
        )

    def test_public_key_not_exist(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['device_public_key.not_found'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('update_device_public_key_error'),
            ],
        )

    def test_public_key_belongs_other_owner(self):
        old_key = self.build_device_public_key()
        self.save_device_public_key(old_key)
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'device_public_key_update': [OWNER1, OWNER2],
                    },
                ),
            },
        )

        rv = self.make_request(query_args={'owner': OWNER2})

        self.assert_error_response(rv, ['device_public_key.not_found'])
        saved_key = self.find_device_public_key(DEVICE_ID1)
        eq_(saved_key, old_key)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'update_device_public_key_error',
                    owner=OWNER2,
                ),
            ],
        )

    def test_unknown_owner(self):
        self.assign_grants(owner='unknown')

        rv = self.make_request(query_args={'owner': 'unknown'})

        self.assert_error_response(rv, ['device_public_key.owner_invalid'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'update_device_public_key_error',
                    owner='unknown',
                ),
            ],
        )

    def test_no_grants(self):
        self.assign_no_grants()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['access.denied'],
            status_code=403,
        )
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('update_device_public_key_error'),
            ],
        )

    def test_not_granted_owner(self):
        rv = self.make_request(query_args={'owner': OWNER2})

        self.assert_error_response(
            rv,
            ['access.denied'],
            status_code=403,
        )
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'update_device_public_key_error',
                    owner=OWNER2,
                ),
            ],
        )

    def test_check_not_passed(self):
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                blackbox_check_device_signature_response(
                    status='SIGNATURE.INVALID',
                    error='your password',
                ),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['device_public_key.check_failed'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('update_device_public_key_error'),
            ],
        )

    def test_blackbox_timeout(self):
        self.env.blackbox.set_response_side_effect(
            'check_device_signature',
            [
                RequestError(),
            ],
        )

        rv = self.make_request()

        self.assert_error_response(rv, ['backend.blackbox_failed'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('update_device_public_key_error'),
            ],
        )


@with_settings_hosts(
    DEVICE_PUBLIC_KEY_OWNER_TO_OWNER_ID={
        OWNER1: 1,
        OWNER2: 2,
    },
)
class TestDeleteDevicePublicKey(BaseDevicePublicTestCase):
    default_url = '/1/bundle/device_public_key/delete/'
    http_method = 'POST'
    http_headers = {
        'consumer_ip': TEST_CONSUMER_IP1,
    }
    http_query_args = {
        'device_id': DEVICE_ID1,
        'owner': OWNER1,
    }
    consumer = TEST_CONSUMER1

    def test_public_key_exists(self):
        old_key = self.build_device_public_key()
        self.save_device_public_key(old_key)

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('delete_device_public_key_ok'),
            ],
        )

    def test_public_key_not_exist(self):
        rv = self.make_request()

        self.assert_error_response(rv, ['device_public_key.not_found'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('delete_device_public_key_error'),
            ],
        )

    def test_public_key_belongs_other_owner(self):
        old_key = self.build_device_public_key()
        self.save_device_public_key(old_key)
        self.env.grants.set_grants_return_value(
            {
                TEST_CONSUMER1: dict(
                    networks=[TEST_CONSUMER_IP1],
                    grants={
                        'device_public_key_delete': [OWNER1, OWNER2],
                    },
                ),
            },
        )

        rv = self.make_request(query_args={'owner': OWNER2})

        self.assert_error_response(rv, ['device_public_key.not_found'])
        saved_key = self.find_device_public_key(DEVICE_ID1)
        eq_(saved_key, old_key)
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'delete_device_public_key_error',
                    owner=OWNER2,
                ),
            ],
        )

    def test_unknown_owner(self):
        self.assign_grants(owner='unknown')

        rv = self.make_request(query_args={'owner': 'unknown'})

        self.assert_error_response(rv, ['device_public_key.owner_invalid'])
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'delete_device_public_key_error',
                    owner='unknown',
                ),
            ],
        )

    def test_no_grants(self):
        self.assign_no_grants()

        rv = self.make_request()

        self.assert_error_response(
            rv,
            ['access.denied'],
            status_code=403,
        )
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry('delete_device_public_key_error'),
            ],
        )

    def test_not_granted_owner(self):
        rv = self.make_request(query_args={'owner': OWNER2})

        self.assert_error_response(
            rv,
            ['access.denied'],
            status_code=403,
        )
        self.assert_device_public_key_not_saved()
        self.env.statbox.assert_equals(
            [
                self.env.statbox.entry(
                    'delete_device_public_key_error',
                    owner=OWNER2,
                ),
            ],
        )

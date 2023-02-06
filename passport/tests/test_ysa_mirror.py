# -*- coding: utf-8 -*-

import base64
import json

from nose_parameterized import parameterized
from passport.backend.core.builders.ysa_mirror import (
    YsaMirrorAPI,
    YsaMirrorPermanentError,
    YsaMirrorResolution,
    YsaMirrorTemporaryError,
)
from passport.backend.core.builders.ysa_mirror.faker.ysa_mirror import (
    FakeYsaMirrorAPI,
    TEST_YSA_MIRROR_RESOLUTION1,
    ysa_mirror_no_resolution_response,
    ysa_mirror_ok_resolution_response,
)
from passport.backend.core.test.consts import TEST_REQUEST_ID1
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.types.ip.ip import IP


MOBILEPROXY_INTERNAL_HOST = 'mobileproxy-internal.passport.yandex.net'
TEST_IPV4_ADDRESS1 = IP('127.0.0.1')


@with_settings(
    YSA_MIRROR_API_TIMEOUT=2,
    YSA_MIRROR_API_RETRIES=1,
    MOBILEPROXY_INTERNAL_HOST=MOBILEPROXY_INTERNAL_HOST,
)
class TestYsaMirror(PassportTestCase):
    def setUp(self):
        self.ysa_mirror_api = YsaMirrorAPI()
        self.fake_ysa_mirror = FakeYsaMirrorAPI()
        self.fake_ysa_mirror.start()

    def tearDown(self):
        self.fake_ysa_mirror.stop()
        del self.fake_ysa_mirror

    @parameterized.expand([
        (TEST_IPV4_ADDRESS1,),
        (IP('2a02:6b8:b040:1600:225:90ff:feeb:90e8'),),
    ])
    def test_check_client_by_requestid_v2_ok(self, remote_addr):
        self.fake_ysa_mirror.set_response_value('check_client_by_requestid_v2', ysa_mirror_ok_resolution_response())

        assert self.ysa_mirror_api.check_client_by_requestid_v2(remote_addr, TEST_REQUEST_ID1) == TEST_YSA_MIRROR_RESOLUTION1

        request = self.fake_ysa_mirror.requests[0]
        request.assert_url_starts_with('http://%s/_check_client/fingerprint?' % remote_addr.as_url())
        request.assert_headers_contain({'Host': MOBILEPROXY_INTERNAL_HOST})
        request.assert_query_contains({'request_id': TEST_REQUEST_ID1})

    def test_check_client_by_requestid_v2_no_resolution(self):
        self.fake_ysa_mirror.set_response_value('check_client_by_requestid_v2', ysa_mirror_no_resolution_response())

        assert self.ysa_mirror_api.check_client_by_requestid_v2(TEST_IPV4_ADDRESS1, TEST_REQUEST_ID1) is None

    def test_check_client_by_requestid_v2_status_500(self):
        self.fake_ysa_mirror.set_response_value('check_client_by_requestid_v2', b'', status=500)

        with self.assertRaises(YsaMirrorTemporaryError):
            self.ysa_mirror_api.check_client_by_requestid_v2(TEST_IPV4_ADDRESS1, TEST_REQUEST_ID1)

    def test_check_client_by_requestid_v2_status_400(self):
        self.fake_ysa_mirror.set_response_value(
            'check_client_by_requestid_v2',
            json.dumps(dict(error='err')),
            status=400,
        )

        with self.assertRaises(YsaMirrorPermanentError):
            self.ysa_mirror_api.check_client_by_requestid_v2(TEST_IPV4_ADDRESS1, TEST_REQUEST_ID1)


@with_settings()
class TestYsaMirrorResolution(PassportTestCase):
    def setUp(self):
        super(TestYsaMirrorResolution, self).setUp()
        self.ymr_bytes = b'123'
        self.ymr = YsaMirrorResolution.from_bytes(self.ymr_bytes)

    def test_to_bytes(self):
        assert self.ymr.to_bytes() == self.ymr_bytes

    def test_to_base64(self):
        assert self.ymr.to_base64() == base64.standard_b64encode(self.ymr_bytes).decode('utf8')

    def test_eq(self):
        assert self.ymr == YsaMirrorResolution.from_bytes(self.ymr.to_bytes())
        assert self.ymr != YsaMirrorResolution.from_bytes(b'456')
        assert not (self.ymr == 0)
        assert self.ymr != 0

    def test_hash(self):
        # Для быстродействия планирую сделать объект мутабельным
        with self.assertRaises(TypeError) as assertion:
            hash(self.ymr)
        assert str(assertion.exception) == "unhashable type: '%s'" % YsaMirrorResolution.__name__

    def test_repr(self):
        assert repr(self.ymr) == 'YsaMirrorResolution.from_base64(%s)' % self.ymr.to_base64()

    def test_from_base64(self):
        assert YsaMirrorResolution.from_base64(self.ymr.to_base64()) == self.ymr

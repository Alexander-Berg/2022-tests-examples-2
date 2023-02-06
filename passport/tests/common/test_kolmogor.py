# -*- coding: utf-8 -*-
from passport.backend.oauth.core.common.kolmogor import get_kolmogor
from passport.backend.oauth.core.test.framework import (
    BaseTestCase,
    PatchesMixin,
    TEST_TVM_TICKET,
)


TEST_SPACE = 'space'


class KolmogorTestcase(BaseTestCase, PatchesMixin):
    def setUp(self):
        super(KolmogorTestcase, self).setUp()
        self.patch_environment()
        self.patch_tvm_credentials_manager()

    def tearDown(self):
        self.stop_patches()
        super(KolmogorTestcase, self).tearDown()

    def test_tvm_used(self):
        get_kolmogor().get(TEST_SPACE, ['key1', 'key2'])
        self.fake_kolmogor.requests[0].assert_properties_equal(
            headers={'X-Ya-Service-Ticket': TEST_TVM_TICKET},
        )

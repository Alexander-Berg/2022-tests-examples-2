# -*- coding: utf-8 -*-
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import BaseViewTestCase
from passport.backend.adm_api.tests.views.account.base_test_attribute_toggle import BaseAccountAttributeToggleTestCase


@with_settings_hosts()
class SetTakeoutSubsciptionViewTestCase(BaseAccountAttributeToggleTestCase, BaseViewTestCase):
    path = '/1/account/set_takeout_delete_subscription/'
    param_name = 'takeout_delete_subscription'

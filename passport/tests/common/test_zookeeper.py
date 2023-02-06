# -*- coding: utf-8 -*-
from nose.tools import eq_
from passport.backend.oauth.core.common.zookeeper.zookeeper_utils import build_full_lock_name
from passport.backend.oauth.core.test.framework import BaseTestCase
import yenv


class TestZookeeper(BaseTestCase):
    # TODO: написать полноценные тесты на все ветки
    def test_make_full_lock_name(self):
        eq_(
            build_full_lock_name('/custom/lock/name'),
            '/{}/{}/custom/lock/name'.format(yenv.name, yenv.type),
        )

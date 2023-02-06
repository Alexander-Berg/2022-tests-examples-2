# -*- coding: utf-8 -*-
from passport.backend.takeout.common.conf import get_config
from passport.backend.takeout.test_utils.base import BaseTestCase


class TestGraphiteFormat(BaseTestCase):
    def test_tab_is_there(self):
        conf = get_config()
        assert '\t' in conf['logging']['formatters']['graphite']['format']

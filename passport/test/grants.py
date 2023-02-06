# -*- coding: utf-8 -*-

import mock
from passport.backend.core.lazy_loader import LazyLoader


class FakeGrantsLoader(object):
    def __init__(self):
        self._mock = mock.Mock()
        self._patch_roles_json = mock.patch(
            'passport.backend.adm_api.common.grants.GrantsLoader._roles_json',
            self._mock,
        )

    def start(self):
        self._patch_roles_json.start()
        LazyLoader.flush(instance_name='GrantsLoader')

    def stop(self):
        self._patch_roles_json.stop()

    def set_grants_json(self, value):
        self._mock.return_value = value

    def set_grants_side_effect(self, fn):
        self._mock.side_effect = fn

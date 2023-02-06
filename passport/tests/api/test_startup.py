# -*- coding: utf-8 -*-
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.oauth.core.api.startup import prepare_environment
from passport.backend.oauth.core.test.framework import (
    BaseTestCase,
    PatchesMixin,
)
from passport.backend.oauth.core.test.utils import iter_eq


COMMON_LOADED_INSTANCES = {
    'ClientLists',
    'Grants',
    'DeviceNamesMapping',
    'LoginToUidMapping',
    'Scopes',
    'Scope translations',
    'Scope short translations',
    'Service translations',
    'TokenParams',
    'TvmCredentialsManager',
    'UserAgent',
}
ALL_LOADED_INSTANCES = COMMON_LOADED_INSTANCES | {
    'Geobase',
    'IPReg',
}


class PrepareEnvironmentTestCase(BaseTestCase, PatchesMixin):
    def setUp(self):
        super(PrepareEnvironmentTestCase, self).setUp()
        self.patch_db()
        self.patch_grants()
        self.patch_tvm_credentials_manager()
        self.patch_device_names_mapping()
        self.patch_login_to_uid_mapping()
        self.patch_scopes()
        self.patch_token_params()
        self.patch_client_lists()

        LazyLoader.flush()
        # Геобаза и IPReg по умолчанию не флашатся, приходится это делать явно
        LazyLoader.flush('Geobase')
        LazyLoader.flush('IPReg')

    def tearDown(self):
        self.stop_patches()
        super(PrepareEnvironmentTestCase, self).tearDown()

    @property
    def loaded_instances(self):
        return set([
            instance_name
            for instance_name, instance in LazyLoader._instances.items()
            if instance._instance is not None
        ])

    def test_not_prepared(self):
        iter_eq(self.loaded_instances, set())

    def test_ok(self):
        prepare_environment()
        iter_eq(self.loaded_instances, ALL_LOADED_INSTANCES)

    def test_ok_without_geodata(self):
        prepare_environment(skip_geodata=True)
        iter_eq(self.loaded_instances, COMMON_LOADED_INSTANCES)

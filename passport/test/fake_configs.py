# -*- coding: utf-8 -*-
import mock
from passport.backend.core.lazy_loader import (
    InstanceNotRegisteredError,
    LazyLoader,
)


class BaseFakeConfig(object):
    mocked_class = None
    instance_name = None
    mocked_method = 'read_config_file'

    def __init__(self):
        self._mock = mock.Mock(return_value={})
        self._patch_scopes_load = mock.patch(
            self.mocked_class + '.' + self.mocked_method,
            self._mock,
        )

    def _update_lazy_loader_instance(self):
        try:
            LazyLoader.flush(instance_name=self.instance_name)
        except InstanceNotRegisteredError:  # pragma: no cover
            # при запуске одного теста могут использоваться не все lazy-loadable инстансы
            pass  # pragma: no cover

    def start(self):
        self._patch_scopes_load.start()
        self._update_lazy_loader_instance()

    def stop(self):
        self._patch_scopes_load.stop()

    def set_data(self, value):
        self._mock.return_value = value
        self._update_lazy_loader_instance()


class FakeScopes(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.scopes.ScopesConfig'
    instance_name = 'Scopes'


class FakeScopeTranslations(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.translations.ScopeTranslationsConfig'
    instance_name = 'Scope translations'


class FakeScopeShortTranslations(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.translations.ScopeShortTranslationsConfig'
    instance_name = 'Scope short translations'


class FakeServiceTranslations(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.translations.ServiceTranslationsConfig'
    instance_name = 'Service translations'


class FakeScopeGrants(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.grants_config.GrantsConfig'
    instance_name = 'Grants'
    mocked_method = 'read_config_file'


class FakeAclGrants(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.acl.AclConfig'
    instance_name = 'ACL'


class FakeLoginToUidMapping(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.login_to_uid_mapping.LoginToUidMapping'
    instance_name = 'LoginToUidMapping'


class FakeDeviceNamesMapping(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.device_names_mapping.DeviceNamesMapping'
    instance_name = 'DeviceNamesMapping'


class FakeTokenParams(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.token_params.TokenParams'
    instance_name = 'TokenParams'


class FakeClientLists(BaseFakeConfig):
    mocked_class = 'passport.backend.oauth.core.db.config.client_lists.ClientLists'
    instance_name = 'ClientLists'


def mock_grants(grants, networks=None):
    return {
        'grants': grants,
        'networks': ['0.0.0.0/0', '::0/0'] if networks is None else networks,
    }


def mock_scope_grant(grant_types=None, client_ids=None, networks=None):
    return mock_grants(
        grants={
            'grant_type': ['*'] if grant_types is None else grant_types,
            'client': ['*'] if client_ids is None else client_ids,
        },
        networks=networks,
    )

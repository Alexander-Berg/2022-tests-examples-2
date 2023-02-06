# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.exceptions import HeadersEmptyError
from passport.backend.core.grants.grants_config import extract_entity_grant
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.track_manager import create_track_id


TEST_UID = 123


@with_settings_hosts()
class TestBundleGrants(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={}))

        self.track_id = create_track_id()

        bundle_views = [(key, value) for key, value in self.env.client.application.view_functions.items() if 'bundle_api' in key]

        self.apis = []

        for name, view_func in bundle_views:
            rule = self.env.client.application.url_map._rules_by_endpoint.get(name)
            if rule:
                rule = rule[0]

                # удаляем методы, зачем-то добавленные flask-ом/werkzeug-ом
                if 'OPTIONS' in rule.methods:
                    rule.methods.remove('OPTIONS')
                if 'HEAD' in rule.methods:
                    rule.methods.remove('HEAD')

                # (имя бандла, view_class, url, methods)
                # имя бандла: строка
                # view_class: класс данного бандла
                # url: строка
                # methods: set из http методов
                self.apis.append(
                    (name, view_func.view_class(), rule.rule, rule.methods),
                )

    def tearDown(self):
        self.env.stop()
        del self.env

    def bundle_request(self, method, params, consumer=None, possible_url_params=None):
        if consumer:
            params.setdefault('query_string', {}).update({'consumer': '%s' % consumer})
        if possible_url_params and 'path' in params:
            params['path'] = self.substitute_url_params(params['path'], possible_url_params)
        return getattr(self.env.client, method)(**params)

    @staticmethod
    def substitute_url_params(url, params):
        # Функция заменяет параметры в урле, например <int:uid>
        new_url = []
        for path_part in url.split('/'):
            if path_part.startswith('<') and ':' in path_part and path_part.endswith('>'):
                param = path_part.strip('<>').split(':')[-1]
                new_url.append(str(params[param]))
            else:
                new_url.append(path_part)
        return '/'.join(new_url)

    def get_required_grants_from_view(self, view_class):
        grants = dict()
        if not view_class.required_grants:
            return grants
        for grant_and_action in view_class.required_grants:
            grant, action = extract_entity_grant(grant_and_action)
            if action is None:
                action = '*'
            grants.setdefault(grant, [])
            grants[grant].append(action)
        return grants

    def test_trailing_slash(self):
        for _bundle_name, _view_class, path, _methods in self.apis:
            ok_(path.endswith('/'), "API end-point {} must end with a trailing slash.".format(repr(path)))

    def test_without_grants(self):
        self.env.grants.set_grants_return_value({'dev': {}})

        url_params = {'uid': TEST_UID}

        for bundle_name, view_class, path, methods in self.apis:
            if not view_class.required_grants:
                continue

            if bundle_name.startswith('bundle_api.IDM'):
                # В этих ручках специфическая логика проверки грантов, она проверяется в тестах бандла idm
                continue

            for method in methods:
                method = method.lower()
                params = {'path': path}

                if view_class.require_track:
                    if method == 'post':
                        params.update({'data': {'track_id': self.track_id}})
                    if method in ('get', 'delete'):
                        params.update({'query_string': {'track_id': self.track_id}})

                rv = self.bundle_request(method, params, consumer='dev', possible_url_params=url_params)
                eq_(rv.status_code, 403, [rv.data, bundle_name])
                response = json.loads(rv.data)
                if bundle_name == 'bundle_api.UserInfoView' and 'takeout' in path:
                    # В этой ручке кастомный формат выдачи ошибок
                    eq_(response['error'], 'access.denied')
                else:
                    eq_(response['errors'], ['access.denied'])
                # Поскольку гранты приводятся к сету (core.grants.grants.py),
                # сделаем то же и здесь, чтобы не зависеть от их порядка
                # в списке required_grants.
                message = 'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: %r' % (
                    list(set(view_class.required_grants)),
                )
                eq_(
                    response['error_message'],
                    message,
                    [rv.data, message, bundle_name],
                )

    def test_need_headers(self):
        url_params = {'uid': TEST_UID}

        for bundle_name, view_class, path, methods in self.apis:
            if not view_class.required_headers:
                continue

            required_grants = self.get_required_grants_from_view(view_class)
            # Грантовая конфигурация -- это синглтон, который перечитывает
            # замоканные гранты, только когда протухает кеш. Т.к. нам нужно
            # менять конфигурацию грантов чаще, здесь следует либо
            # инвалидировать кеш, либо совсем удалять синглтон.
            LazyLoader.flush(instance_name='GrantsConfig')
            self.env.grants.set_grants_return_value(mock_grants(grants=required_grants))

            for method in methods:
                method = method.lower()
                params = {'path': path}
                required_headers = view_class.required_headers

                if view_class.require_track:
                    if method == 'post':
                        params.update({'data': {'track_id': self.track_id}})
                    if method in ('get', 'delete'):
                        params.update({'query_string': {'track_id': self.track_id}})

                rv = self.bundle_request(method, params, consumer='dev', possible_url_params=url_params)
                eq_(rv.status_code, 200, [rv.data, bundle_name])
                response = json.loads(rv.data)
                eq_(
                    response['errors'],
                    HeadersEmptyError(
                        [h.code_for_error for h in required_headers],
                    ).errors,
                    [rv.data, bundle_name],
                )

    def test_need_track(self):
        self.env.grants.set_grants_return_value(mock_grants())

        for bundle_name, view_class, path, methods in self.apis:
            if view_class.require_track:
                for method in methods:
                    params = {'path': path}
                    rv = self.bundle_request(method.lower(), params, consumer='dev')
                    eq_(rv.status_code, 200, [rv.data, bundle_name])
                    response = json.loads(rv.data)
                    eq_(response['errors'], ['track_id.empty'], [rv.data, bundle_name])

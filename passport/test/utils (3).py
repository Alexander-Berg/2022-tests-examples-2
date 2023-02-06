# -*- coding: utf-8 -*-
import re
from urllib import urlencode
from urlparse import urlparse
from contextlib import contextmanager
from operator import __or__ as OR
from shutil import rmtree
from tempfile import (
    mkdtemp,
    NamedTemporaryFile,
)

from django.db.models import Q
from mock import Mock, patch

from ..models import Namespace


@contextmanager
def create_temp_test_file():
    _temp_dir_path = mkdtemp()
    try:
        with NamedTemporaryFile(dir=_temp_dir_path) as temp_file:
            yield temp_file
    finally:
        rmtree(_temp_dir_path)


def _requests_get_side_effect(responses):
    """Подготавливаем ответы от requests.get()"""

    def wrap(url, *args, **kwargs):
        """Функция, которая будет работать вместо requests.get()"""
        # Парсим переданный url
        scheme, netloc, path, params, query, fragment = urlparse(url)
        params_encoded = urlencode(kwargs.get('params', {}))
        # Находим подготовленные ответы для вызванного хоста
        options = responses.get(netloc, [])
        # Пройдемся по всем подготовленным вариантам
        for qs_re, value in options:
            # Проверим, что регулярка матчится на querystring
            if qs_re is not None and re.search(qs_re, query + '&' + params_encoded):
                # Отдаем подготовленный ответ как если бы это был requests.Response
                return Mock(text=value, json=value)

    return wrap


class MockRequests(object):
    """
    Подменяет ВСЮ библиотеку requests и позволяет подготовить желаемые ответы при вызовах
      * get()
    """

    import_path = 'passport_grants_configurator.apps.core.utils.requests'
    internal_bitbucket_hostname = 'bb.yandex-team.ru'

    def __init__(self):
        self.responses = dict()
        self.response = Mock()
        self.raise_for_status = Mock()
        self.response.raise_for_status = self.raise_for_status
        self.mock_get = Mock(return_value=self.response)
        self.patch = patch(self.import_path, Mock(get=self.mock_get))

    def set_response_value_for_host(self, host, value, qs_re=''):
        """
        Подготовим заглушку. При запросе на указанный хост, будем отдавать указанную строку.
        Дополнительно примем условие для поиска в строке параметров
        :param host: Имя узла, запросы на который будут имитироваться
        :param value: Желаемый ответ библиотеки requests
        :param qs_re: Регулярное выражение для поиска в строке запроса вызываемого url
        """
        self.responses.setdefault(host, list())
        item = qs_re, value
        self.responses[host].append(item)

        self.mock_get.side_effect = _requests_get_side_effect(self.responses)

    def setup_bitbucket_last_commit_info(self):
        self.set_response_value_for_host(
            self.internal_bitbucket_hostname,
            '[{"id": "fake-commit-hash"}]',  # отдаем json-список из одного коммита с его хэшем
        )

    def start(self):
        self.patch.start()

    def stop(self):
        self.patch.stop()


class MockUserPermissions(object):
    def __init__(self, object_location='passport_grants_configurator.apps.core.permissions'):
        self.UserPermissions = Mock(**{
            'have_all.return_value': True,
            'do_not_have.return_value': [],
            'intersect_grouped.side_effect': lambda namespaces: ((n, list(n.environments.all())) for n in namespaces),
            'get_q.return_value': reduce(
                OR,
                [Q(namespace=n, environment__in=n.environments.all()) for n in Namespace.objects.all()] or [Q(), Q()],
            ),
        })

        self._patch = patch(object_location, Mock(return_value=self.UserPermissions))

        @contextmanager
        def context_manager():
            self._patch.start()
            yield
            self._patch.stop()

        self.context_manager = context_manager()

    def __enter__(self, *args, **kwargs):
        self.context_manager.__enter__(*args, **kwargs)

    def __exit__(self, *args, **kwargs):
        self.context_manager.__exit__(*args, **kwargs)

    def start(self):
        self._patch.start()

    def stop(self):
        self._patch.stop()


class MockRedis(object):
    import_path = 'passport_grants_configurator.apps.core.caching.redis_connection'

    def __init__(self):
        self.cache = {}
        self.mock = Mock()
        self.mock.get.side_effect = lambda key: self.cache.get(key)
        self.mock.setex.side_effect = lambda key, value, _: self.cache.__setitem__(key, value)
        self.patch = patch(self.import_path, self.mock)

    def start(self):
        self.patch.start()

    def stop(self):
        self.patch.stop()


class MockNetworkApi(object):
    """Позволяет подготовить ответы функций раскрытия сетевых объектов"""
    import_path_base = 'passport_grants_configurator.apps.core.network_apis.%s'

    def __init__(self):
        self.patches = list()
        self.maps = {
            'getipsfromaddr': {},
            'get_conductor_group_hosts': {},
            'expand_firewall_macro': {},
        }
        self.mocks = {}

    def start(self):
        for name, patch, mock in self.patches:
            patch.start()

    def stop(self):
        for name, patch, mock in self.patches:
            patch.stop()

    def setup_response(self, function_name, values, response=None):
        self.maps[function_name].update(values)

        map_ = self.maps[function_name].copy()

        def side_effect(key):
            value = map_.get(key)
            if isinstance(value, Exception):
                raise value

            return value

        new_mock = Mock(return_value=response, side_effect=side_effect)
        new_patch = patch(self.import_path_base % function_name, new_mock)
        new_patch.start()

        item = function_name, new_patch, new_mock
        self.mocks[function_name] = new_mock
        self.patches.append(item)


class MockGit(object):
    """Изолируем вызовы git"""
    import_path_template = 'passport_grants_configurator.apps.core.export_utils.git_%s'

    def __init__(self, mock_push=True, mock_pull=True):
        self.mock_push = mock_push
        self.mock_pull = mock_pull

        if self.mock_push:
            self.push = Mock()
            self.push_patch = patch(self.import_path_template % 'push', self.push)
        if self.mock_pull:
            self.pull = Mock()
            self.pull_patch = patch(self.import_path_template % 'pull', self.pull)

    def start(self):
        if self.mock_push:
            self.push_patch.start()
        if self.mock_pull:
            self.pull_patch.start()

    def stop(self):
        if self.mock_push:
            self.push_patch.stop()
        if self.mock_pull:
            self.pull_patch.stop()

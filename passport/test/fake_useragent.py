# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from furl import furl
import mock
from passport.backend.social.common.useragent import Url
from werkzeug.urls import url_decode


class _BaseFakeUseragent(object):
    def __init__(self):
        self._pool_manager_class = mock.Mock(name='PoolManager')

        pool_manager = self._pool_manager_class.return_value = mock.Mock(name='pool_manager')
        pool_manager.urlopen.side_effect = self._urlopen

        self._urlopen_method = mock.Mock(name='urlopen')
        self._urlopen_method.side_effect = UseragentResponseNotMocked()
        self.requests = []

    def start(self):
        self._patch.start()
        return self

    def stop(self):
        self._patch.stop()

    def _urlopen(self, method, url, **kwargs):
        url = Url(url)
        data = kwargs.get('body')
        if isinstance(data, basestring):
            data = url_decode(data)
            data = data.to_dict()
        request = FakeRequest(
            method=method,
            url=url.paramless,
            headers=kwargs.get('headers'),
            query=url.params,
            data=data,
        )
        self.requests.append(request)

        return self._urlopen_method()

    def set_response_value(self, response_value):
        self.set_response_values([response_value])

    def set_response_values(self, responses):
        self._urlopen_method.side_effect = responses

    def reset(self):
        self.requests[:] = []
        self._urlopen_method.side_effect = UseragentResponseNotMocked()


class FakeUseragent(_BaseFakeUseragent):
    def __init__(self):
        super(FakeUseragent, self).__init__()
        self._patch = mock.patch('passport.backend.social.common.useragent.PoolManager', self._pool_manager_class)


class FakeZoraUseragent(_BaseFakeUseragent):
    def __init__(self):
        super(FakeZoraUseragent, self).__init__()
        self._patch = mock.patch('passport.backend.social.common.useragent.ProxyManager', self._pool_manager_class)


class FakeRequest(object):
    def __init__(self, method, url, query=None, data=None, headers=None):
        base_url, _query = self._split_url(url)
        _query.update(query or dict())
        query = _query

        self.method = method
        self.url = base_url
        self.query = query
        self.data = data or dict()
        self.headers = headers or dict()

        self.fields = dict()
        self.fields.update(self.query)
        self.fields.update(self.data)

    def _split_url(self, url):
        url = furl(url)
        return url.origin + str(url.path), url.args

    def to_dict(self):
        return dict(
            method=self.method.upper(),
            url=Url(self.url, self.query).to_dict(),
            headers=self.headers,
            data=self.data,
            timeout=None,
            retries=1,
            not_quotable_params=set(),
        )


class UseragentResponseNotMocked(Exception):
    pass

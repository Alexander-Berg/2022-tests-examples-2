# -*- coding: utf-8 -*-

from flask.testing import FlaskClient


class FlaskTestClient(FlaskClient):
    def __init__(self, application, response_wrapper=None, use_cookies=True, allow_subdomain_redirects=False):
        super(FlaskTestClient, self).__init__(application, response_wrapper, use_cookies, allow_subdomain_redirects)
        self._context = {'query_string': {}, 'data': {}}

    def _prepare_args_kwargs(self, args, kwargs):
        query_string = self._context['query_string'].copy()
        query_string.update(kwargs.pop('query_string', {}))
        kwargs['query_string'] = query_string

        data = self._context['data'].copy()
        data.update(kwargs.pop('data', {}))
        kwargs['data'] = data

        kwargs['environ_base'] = {'REMOTE_ADDR': kwargs.pop('remote_addr', '127.0.0.1')}
        return args, kwargs

    def set_context(self, query_string=None, data=None):
        if query_string is None:
            query_string = {}
        if data is None:
            data = {}
        self._context = {'query_string': query_string, 'data': data}

    def get(self, *args, **kwargs):
        args, kwargs = self._prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        args, kwargs = self._prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        args, kwargs = self._prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).delete(*args, **kwargs)

    def put(self, *args, **kwargs):
        args, kwargs = self._prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).put(*args, **kwargs)

# -*- coding: utf-8 -*-
from flask.testing import FlaskClient


class FlaskTestClient(FlaskClient):

    def __init__(self, application, response_wrapper=None, use_cookies=True, allow_subdomain_redirects=False):
        super(FlaskTestClient, self).__init__(application, response_wrapper, use_cookies, allow_subdomain_redirects)

    def prepare_args_kwargs(self, args, kwargs):
        kwargs['environ_base'] = {
            'REMOTE_ADDR': kwargs.pop('remote_addr', '127.0.0.1'),
            'HTTP_USER_AGENT': 'curl',
        }
        return args, kwargs

    def get(self, *args, **kwargs):
        args, kwargs = self.prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        args, kwargs = self.prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).post(*args, **kwargs)

    def put(self, *args, **kwargs):
        args, kwargs = self.prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        args, kwargs = self.prepare_args_kwargs(args, kwargs)
        return super(FlaskTestClient, self).delete(*args, **kwargs)

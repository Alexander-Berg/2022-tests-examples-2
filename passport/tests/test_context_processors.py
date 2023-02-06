# -*- coding: utf-8 -*
from django.http import HttpRequest
from nose.tools import eq_
from passport.backend.oauth.admin.admin.context_processors import (
    env_name,
    request_full_path,
)
from passport.backend.oauth.core.test.framework import BaseTestCase


class ContextProcessorsTestcase(BaseTestCase):
    def setUp(self):
        super(ContextProcessorsTestcase, self).setUp()
        self.request = HttpRequest()
        self.request.path = '/production/clients/'

    def test_request_full_path(self):
        eq_(
            request_full_path(self.request),
            {
                'request_full_path': '/production/clients/',
            },
        )

    def test_env_name(self):
        eq_(
            env_name(self.request),
            {
                'env_name': 'production',
                'available_envs': {
                    'production': 'Большая админка',
                    'intranet': 'Ятимная админка',
                },
            },
        )

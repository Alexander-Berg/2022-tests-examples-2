# -*- coding: utf-8 -*-
from contextlib import contextmanager

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.restore.test.base_test_data import *
from passport.backend.api.views.bundle.base import BaseBundleView
from passport.backend.api.views.bundle.restore.factors import CalculateFactorsMixin
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.logging_utils.loggers.statbox import StatboxLogger
from passport.backend.core.models.account import Account
from passport.backend.core.test.test_utils.utils import iterdiff
from passport.backend.core.utils.decorators import cached_property
from passport.backend.utils.common import merge_dicts
from werkzeug.datastructures import Headers


eq_ = iterdiff(eq_)


class BundleViewWithFactors(BaseBundleView, CalculateFactorsMixin):
    """
    View для тестирования вычисления факторов
    """
    @cached_property
    def statbox(self):
        return StatboxLogger(mode='test_factors_mixin')

    def __init__(self, userinfo_response, form_values=None, track_id=None):
        super(BundleViewWithFactors, self).__init__()
        self.account = Account().parse(userinfo_response)
        self.form_values = form_values or {}
        if 'track_id' in self.form_values:
            self.track_id = self.form_values['track_id']
            self.read_track()


class BaseCalculateFactorsMixinTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.statbox.bind_entry(
            'test_factors_entry',
            mode='test_factors_mixin',
        )

        self.headers = self.get_headers()
        self.base_params = {
            'headers': self.headers,
            'environ_overrides': {'REMOTE_ADDR': '127.0.0.1'},
        }

    def tearDown(self):
        self.env.stop()
        del self.env

    def get_headers(self, ip=TEST_IP, user_agent=None):
        return Headers(mock_headers(
            cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE,
            host=TEST_HOST,
            user_ip=ip,
            user_agent=user_agent,
        ).items())

    @contextmanager
    def create_base_bundle_view(self, userinfo_response, form_values=None, **params):
        """
        @param userinfo_response: ответ метода userinfo ЧЯ
        @param params: параметры для werkzeug.EnvironBuilder
        """
        params = merge_dicts(self.base_params, params)

        with self.env.client.application.test_request_context(**params):
            self.env.client.application.preprocess_request()
            yield BundleViewWithFactors(userinfo_response, form_values=form_values)

    def get_default_account_kwargs(self, login=TEST_DEFAULT_LOGIN, firstname=TEST_DEFAULT_FIRSTNAME,
                                   lastname=TEST_DEFAULT_LASTNAME, birthday=TEST_DEFAULT_BIRTHDAY,
                                   password=TEST_DEFAULT_PASSWORD,
                                   registration_datetime=TEST_DEFAULT_REGISTRATION_DATETIME,
                                   password_creating_required=False, language='ru',
                                   emails=TEST_EMAILS, **kwargs):
        dbfields = {
            'userinfo.reg_date.uid': registration_datetime,
            'userinfo_safe.hintq.uid': TEST_DEFAULT_HINT_QUESTION,
            'userinfo_safe.hinta.uid': TEST_DEFAULT_HINT_ANSWER,
        }
        attributes = {
            'password.encrypted': '1:%s' % password,
        }

        params = dict(
            kwargs,
            login=login,
            firstname=firstname,
            lastname=lastname,
            birthdate=birthday,
            language=language,
            dbfields=dbfields,
            attributes=attributes,
        )
        return params

    def default_userinfo_response(self, *args, **kwargs):
        account_kwargs = self.get_default_account_kwargs(*args, **kwargs)
        return get_parsed_blackbox_response('userinfo', blackbox_userinfo_response(**account_kwargs))

    def assert_entry_in_statbox(self, entry_kwargs, statbox):
        statbox.log()
        entry = self.env.statbox.entry(
            'test_factors_entry',
            **entry_kwargs
        )
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [entry],
        )

    def time_now_mock(self, timestamp):
        return mock.patch('passport.backend.api.views.bundle.restore.factors.time.time', lambda: timestamp)

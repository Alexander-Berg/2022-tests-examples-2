# -*- coding: utf-8 -*-
from flask.testing import FlaskClient
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.crypto.faker import FakeKeyStorage
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.library.configurator.test import FakeConfig
from passport.infra.daemons.yasmsapi.api.app import create_app
from passport.infra.daemons.yasmsapi.api.logging_utils import get_external_request_id
from passport.infra.daemons.yasmsapi.common.statbox_loggers import YasmsStatboxPrivateLogEntry


def test_statbox_params():
    entry = YasmsStatboxPrivateLogEntry(foo='bar')

    eq_(
        entry.params,
        {
            'unixtimef': TimeNow(),
            'unixtime': TimeNow(),
            'tskv_format': 'yasms-log',
            'foo': 'bar',
            'sms': '1',
        },
    )


def test_with_crypto():
    with FakeConfig('passport.infra.daemons.yasmsapi.configs.config', {'historydb_log_encryption_enabled': False}):
        entry = YasmsStatboxPrivateLogEntry(text='abc')

        entry_string = str(entry)
        ok_('encryptedtext=' not in entry_string)
        ok_('text=abc' in entry_string)

    with FakeConfig('passport.infra.daemons.yasmsapi.configs.config', {'historydb_log_encryption_enabled': True}):
        with FakeKeyStorage(602, b'1' * 24):
            entry = YasmsStatboxPrivateLogEntry(text='abc')

            entry_string = str(entry)
            ok_('encryptedtext=' in entry_string)
            ok_('text=abc' not in entry_string)


def test_external_request_id():
    app = create_app()
    app.test_client_class = FlaskClient
    app.testing = True
    client = app.test_client()
    with client.application.test_request_context() as context:
        eq_(get_external_request_id(), '-')
        context.request.request_id = '123'
        eq_(get_external_request_id(), '123')

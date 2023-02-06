# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from io import BytesIO
from textwrap import dedent

from django.test import TestCase
from passport_grants_configurator.apps.core.exceptions import NetworkResolveError

import passport_grants_configurator.apps.core.export_utils as export_utils
from passport_grants_configurator.apps.core.models import Environment
from passport_grants_configurator.apps.core.test.utils import (
    MockRedis,
    MockNetworkApi,
)
from .test_data import *


class TestExportBlackbox(TestCase):
    fixtures = ['default.json']

    def setUp(self):
        self.buffer = BytesIO()
        self.environment = Environment.objects.get(id=1)

        self.redis = MockRedis()
        self.redis.start()
        self.network = MockNetworkApi()
        self.network.start()

        # Подготовим ожидаемые ответы от dns & hbf
        self.network.setup_response(
            'expand_firewall_macro',
            {
                '_C_PASSPORT_GRANTUSHKA_STABLE_': [
                    TEST_GRANTS_HOST1,
                    TEST_GRANTS_HOST2,
                ],
            },
        )
        self.network.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST1: [TEST_GRANTS_IP1],
            TEST_GRANTS_HOST2: [TEST_GRANTS_IP2],
        })

    def tearDown(self):
        self.network.stop()
        self.redis.stop()

    def expected_export(self, ip1=TEST_GRANTS_IP1, ip2=TEST_GRANTS_IP2):
        return dedent('''\
            <?xml version='1.0' encoding='utf-8'?>
            <peers>
              <entry id="%s; %s">
                <name>bb_consumer</name>
                <allow_check_sign>oauth_otp,passport_otp</allow_check_sign>
                <allow_sign>oauth_otp,passport_otp</allow_sign>
                <allowed_attributes>16,17</allowed_attributes>
                <allowed_phone_attributes>1,2</allowed_phone_attributes>
                <bb_grant>bb_action</bb_grant>
                <can_captcha/>
                <can_delay>1000</can_delay>
                <dbfield id="tablename.field_name.1337"/>
              </entry>
            </peers>
            ''') % (ip1 or TEST_GRANTS_IP1, ip2 or TEST_GRANTS_IP2)

    def test_export(self):
        export_utils.export_blackbox_grants_to_file(self.environment, self.buffer)

        self.assertEqual(self.buffer.getvalue(), self.expected_export())

    def test_macros_resolve_error__warning(self):
        self.network.setup_response(
            'expand_firewall_macro',
            {
                '_C_PASSPORT_GRANTUSHKA_STABLE_': NetworkResolveError('test'),
            },
        )
        exported = export_utils.export_blackbox_grants_to_file(
            environment=self.environment,
            file_=self.buffer,
        )

        self.assertEqual(
            exported,
            {
                'errors': [],
                'manual_resolve': [
                    'ОШИБКА - сеть "_C_PASSPORT_GRANTUSHKA_STABLE_", потребитель "bb_consumer": test'
                ],
                'warnings': [],
            },
        )

    def test_one_host_resolve_error__warning(self):
        self.network.setup_response('getipsfromaddr', {
            TEST_GRANTS_HOST2: [TEST_GRANTS_IP2],
            TEST_GRANTS_HOST1: NetworkResolveError('test'),
        })

        exported = export_utils.export_blackbox_grants_to_file(
            environment=self.environment,
            file_=self.buffer,
        )

        # Пропущен тот хост, что неудалось разрешить в ip-адрес
        expected = self.expected_export().replace('%s; ' % TEST_GRANTS_IP1, '', 1)
        self.assertEqual(self.buffer.getvalue(), expected)

        self.assertEqual(
            exported,
            {
                'errors': [],
                'manual_resolve': [],
                'warnings': [
                    'Предупреждение - сеть "_C_PASSPORT_GRANTUSHKA_STABLE_", потребитель "bb_consumer": '
                    'не найдены ip-адреса для имен %s' % TEST_GRANTS_HOST1,
                ],
            },
        )

    def test_with_trypo(self):
        self.network.setup_response(
            'expand_firewall_macro',
            {
                '_C_PASSPORT_GRANTUSHKA_STABLE_': [
                    TEST_TRYPO_NET_1,
                    TEST_TRYPO_NET_2,
                ],
            },
        )
        export_utils.export_blackbox_grants_to_file(self.environment, self.buffer)
        self.assertEqual(
            self.buffer.getvalue(),
            self.expected_export(TEST_TRYPO_NET_1, TEST_TRYPO_NET_2),
        )

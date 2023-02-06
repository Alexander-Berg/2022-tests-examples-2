# coding: utf-8

import json

import mock
from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.core.builders.yasm_agent.faker.fake_yasm_agent import (
    FakeYasmAgent,
    TEST_YASM_AGENT_OK_RESPONSE,
)
from passport.backend.library.test.time_mock import TimeMock
from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestGolovanCommands(BaseTestClass):
    fill_database = False

    def setUp(self):
        super(TestGolovanCommands, self).setUp()
        self.runner = self.app.test_cli_runner()
        self.fqdn_mock = mock.patch('socket.getfqdn', return_value='vault-v3.passport.yandex.net')
        self.fqdn_mock.start()

    def tearDown(self):
        self.fqdn_mock.stop()

    def assert_xunistater_request_equal(self, request, request_data):
        request.assert_properties_equal(
            url='http://localhost:10281/xpush',
            method='POST',
            post_args=json.dumps(request_data, sort_keys=True),
        )

    def assert_yasm_agent_request_equal(self, request, request_data):
        request.assert_properties_equal(
            url='http://localhost:11005',
            method='POST',
            post_args=json.dumps(request_data, sort_keys=True),
        )

    def test_global_print_ok(self):
        with self.app.app_context():
            with TimeMock(incrementing=True):
                self.fixture.insert_data()
                result = self.runner.invoke(self.cli, ['golovan', 'global', '--ttl', '120', '--print'], catch_exceptions=False)
                self.assertEqual(result.exit_code, 0)
                self.assertDictEqual(
                    json.loads(result.output),
                    {
                        u'today_count_versions': 14,
                        u'count_active_secrets': 4,
                        u'count_active_versions': 14,
                        u'count_secrets': 4,
                        u'count_versions': 14,
                        u'today_versions_creators': 2,
                        u'count_revoked_tokens': 0,
                        u'count_hidden_secrets': 0,
                        u'today_count_tokens': 0,
                        u'today_secrets_creators': 2,
                        u'today_tokens_creators': 0,
                        u'count_tokens': 0,
                        u'today_count_secrets': 4,
                        u'count_hidden_versions': 0
                    }
                )

    def test_global_push_ok(self):
        with FakeXunistater() as fake_xunistater:
            with FakeYasmAgent() as fake_yasm_agent:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                fake_yasm_agent.set_response_value('', json.dumps(TEST_YASM_AGENT_OK_RESPONSE))

                with self.app.app_context():
                    with TimeMock(incrementing=True):
                        self.fixture.insert_data()
                        result = self.runner.invoke(self.cli, ['golovan', 'global'], catch_exceptions=False)
                        self.assertEqual(result.exit_code, 0)
                        self.assertEqual(
                            result.output,
                            u"Push to the YASM Agent: {u'status': u'ok'}\n"
                            u"Push to the Xunistater: {u'status': u'OK'}\n"
                        )

                    self.assertEqual(len(fake_xunistater.requests), 1)
                    self.assert_xunistater_request_equal(
                        fake_xunistater.requests[0],
                        {
                            u'today_count_versions_axxx': {'value': 14},
                            u'count_active_secrets_axxx': {'value': 4},
                            u'count_active_versions_axxx': {'value': 14},
                            u'count_secrets_axxx': {'value': 4},
                            u'count_versions_axxx': {'value': 14},
                            u'today_versions_creators_axxx': {'value': 2},
                            u'count_revoked_tokens_axxx': {'value': 0},
                            u'count_hidden_secrets_axxx': {'value': 0},
                            u'today_count_tokens_axxx': {'value': 0},
                            u'today_secrets_creators_axxx': {'value': 2},
                            u'today_tokens_creators_axxx': {'value': 0},
                            u'count_tokens_axxx': {'value': 0},
                            u'today_count_secrets_axxx': {'value': 4},
                            u'count_hidden_versions_axxx': {'value': 0},
                        }
                    )

                    self.assertEqual(len(fake_yasm_agent.requests), 1)
                    self.assert_yasm_agent_request_equal(
                        fake_yasm_agent.requests[0],
                        [
                            {
                                "tags": {
                                    "ctype": self.config['environment'],
                                    "geo": self.config['application']['current_dc'] or 'none',
                                    "itype": "yav",
                                    "prj": "vault-api"
                                },
                                "ttl": 60,
                                "values": [
                                    {"name": "today_secrets_creators_max", "val": 2},
                                    {"name": "count_active_secrets_max", "val": 4},
                                    {"name": "count_active_versions_max", "val": 14},
                                    {"name": "count_secrets_max", "val": 4},
                                    {"name": "count_versions_max", "val": 14},
                                    {"name": "today_versions_creators_max", "val": 2},
                                    {"name": "count_revoked_tokens_max", "val": 0},
                                    {"name": "count_hidden_secrets_max", "val": 0},
                                    {"name": "today_count_tokens_max", "val": 0},
                                    {"name": "today_count_versions_max", "val": 14},
                                    {"name": "today_tokens_creators_max", "val": 0},
                                    {"name": "count_tokens_max", "val": 0},
                                    {"name": "today_count_secrets_max", "val": 4},
                                    {"name": "count_hidden_versions_max", "val": 0}
                                ],
                            },
                        ],
                    )

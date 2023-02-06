# -*- coding: utf-8 -*-

import json
from unittest import TestCase

from passport.backend.core.builders.yasm_agent import (
    get_yasm_agent,
    YasmAgentPermanentError,
)
from passport.backend.core.builders.yasm_agent.faker.fake_yasm_agent import (
    FakeYasmAgent,
    TEST_YASM_AGENT_OK_RESPONSE,
)
from passport.backend.core.test.test_utils import with_settings


@with_settings(
    YASM_AGENT_URL=u'http://local_yasm_agent/push',
    YASM_AGENT_TIMEOUT=1,
    YASM_AGENT_RETRIES=2,
)
class TestYasmAgent(TestCase):
    def _build_yasm_agent_request_data(self):
        return [{
            'metric_one_dmmm': {'value': 124},
            'tier=tag1;metric_two_dxxx': {'value': 0.24},
        }]

    def assert_yasm_agent_request_equal(self, request, request_data):
        request.assert_properties_equal(
            url='http://local_yasm_agent/push',
            method='POST',
            post_args=json.dumps(request_data, sort_keys=True),
        )

    def test_yasm_agent_ok(self):
        with FakeYasmAgent() as fake_yasm_agent:
            fake_yasm_agent.set_response_value('', json.dumps(TEST_YASM_AGENT_OK_RESPONSE))
            request_data = self._build_yasm_agent_request_data()

            response = get_yasm_agent().push_metrics(request_data)
            self.assertDictEqual(
                response,
                TEST_YASM_AGENT_OK_RESPONSE,
            )
            self.assertEqual(len(fake_yasm_agent.requests), 1)
            self.assert_yasm_agent_request_equal(fake_yasm_agent.requests[0], request_data)

    def test_yasm_agent_error(self):
        with FakeYasmAgent() as fake_yasm_agent:
            fake_yasm_agent.set_response_value('', 'Server is down', status=500)
            request_data = self._build_yasm_agent_request_data()

            with self.assertRaises(YasmAgentPermanentError) as e:
                get_yasm_agent().push_metrics(request_data)

            self.assertEqual(
                str(e.exception),
                'YasmAgent is down. response=Server is down code=500',
            )

            self.assertEqual(len(fake_yasm_agent.requests), 1)
            self.assert_yasm_agent_request_equal(fake_yasm_agent.requests[0], request_data)

# -*- coding: utf-8 -*-
import json
import unittest

from passport.backend.core.builders.xunistater.faker.fake_xunistater import (
    FakeXunistater,
    TEST_XUNISTATER_OK_RESPONSE,
)
from passport.backend.library.configurator import Configurator
from passport.backend.logbroker_client.{{cookiecutter.project_slug_snake}}.handler import (
    {{cookiecutter.project_slug_upper_camel}}Handler,
)
from passport.backend.utils.logging_mock import LoggingMock


class Test{{cookiecutter.project_slug_upper_camel}}Handler(unittest.TestCase):
    def setUp(self):
        self.config = Configurator(
            name='logbroker-client',
            configs=[
                'base.yaml',
                '{{cookiecutter.project_slug_snake}}/base.yaml',
                '{{cookiecutter.project_slug_snake}}/testing.yaml',
                'logging.yaml',
                '{{cookiecutter.project_slug_snake}}/export.yaml',
            ],
        )
        self.config.set_as_passport_settings()
        self.handler = {{cookiecutter.project_slug_upper_camel}}Handler(self.config)

    def test_log_and_push_metrics(self):
        handler = {{cookiecutter.project_slug_upper_camel}}Handler(
            self.config,
            log_metrics=True,
            push_metrics_to_xunistater=True,
        )

        with LoggingMock() as log:
            with FakeXunistater() as fake_xunistater:
                fake_xunistater.set_response_value('', json.dumps(TEST_XUNISTATER_OK_RESPONSE))
                # TODO: process() args here
                handler.process()

        assert len(fake_xunistater.requests) == 1
        fake_xunistater.requests[0].assert_properties_equal(
            url='http://localhost:{{cookiecutter.xunistater_port}}/xpush',
            method='POST',
            #TODO: metric path
            post_args=json.dumps(
                {
                    '{{cookiecutter.project_slug_snake}}.entries._.!!!.log_dmmm': {
                        'value': 1,
                    },
                    '{{cookiecutter.project_slug_snake}}.entries.total.!!!.log_dmmm': {
                        'value': 1,
                    },
                },
                sort_keys=True,
            ),
        )

        #TODO: metric path
        assert log.getLogger('logbroker_client.metrics').entries == [
            (
                {
                    'file': '!!!',
                    'handler_name': '{{cookiecutter.project_slug_snake}}',
                    'metric:{{cookiecutter.project_slug_snake}}.entries._.!!!': 1,
                    'metric:{{cookiecutter.project_slug_snake}}.entries.total.!!!': 1,
                    'server': '_',
                },
                'INFO',
                None,
                None,
            ),
        ]

    def test_no_events(self):
        #TODO: process() args, assertion
        self.handler.process()

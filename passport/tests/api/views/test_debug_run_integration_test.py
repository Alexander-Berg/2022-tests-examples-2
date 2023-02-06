# -*- coding: utf-8 -*-
import mock
from passport.backend.core.logbroker.faker.fake_logbroker import FakeLogbrokerWriterProto
from passport.backend.takeout.api.grants import GRANT_DEBUG_INTEGRATION_TEST
from passport.backend.takeout.api.views.forms import (
    DebugIntegrationForm,
    MAX_UID,
)
from passport.backend.takeout.common.conf.services import ServiceConfig
from passport.backend.takeout.common.logbroker import TakeoutLogbrokerWriterProto
from passport.backend.takeout.test_utils.base import BaseTestCase
from passport.backend.takeout.test_utils.forms import assert_form_errors
from passport.backend.takeout.test_utils.time import freeze_time
import pytest
from werkzeug.datastructures import MultiDict
import yenv


TEST_UNIXTIME = 123456789
TEST_SERVICE_NAME = 'test-service'
TEST_OTHER_SERVICE_NAME = 'other'

TEST_SERVICES_CONFIG = {
    TEST_SERVICE_NAME: ServiceConfig.from_dict({
        'enabled': True,
        'type': 'sync',
        'tvm_dst_alias': 'fake_sync',
        'urls': {'base': ''},
        'run_integration_test_consumers': ['dev'],
    }),
    TEST_OTHER_SERVICE_NAME: ServiceConfig.from_dict({
        'enabled': True,
        'type': 'sync',
        'tvm_dst_alias': 'fake_async',
        'urls': {'base': ''},
        'run_integration_test_consumers': [],
    }),
}


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict({'uid': '123', 'consumer': 'dev', 'service_name': 'test-service'}),
        MultiDict({'uid': '0', 'consumer': 'dev', 'service_name': 'test-service'}),
        MultiDict({'uid': str(MAX_UID), 'consumer': 'dev', 'service_name': 'test-service'}),
        MultiDict({'uid': '123', 'consumer': 'dev', 'service_name': 'test-service', 'unixtime': '123456'}),
    ],
)
def test_form_valid(input_form):
    form = DebugIntegrationForm(formdata=input_form)
    assert form.validate()


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict({}),
        MultiDict({'uid': '123'}),
        MultiDict({'consumer': 'dev'}),
        MultiDict({'uid': '-1', 'consumer': 'dev'}),
        MultiDict({'uid': str(MAX_UID + 1), 'consumer': 'dev'}),
        MultiDict({'uid': '123', 'consumer': 'dev', 'service_name': ''}),
        MultiDict({'uid': '123', 'consumer': 'dev', 'service_name': 'test-service', 'unixtime': '-1'}),
    ],
)
def test_form_invalid(input_form):
    form = DebugIntegrationForm(formdata=input_form)
    assert not form.validate()


class DebugRunIntegrationTestTestCase(BaseTestCase):
    def setUp(self):
        super(DebugRunIntegrationTestTestCase, self).setUp()

        self.logbroker_writer_faker = FakeLogbrokerWriterProto(TakeoutLogbrokerWriterProto, 'takeout_tasks')

        self.logbroker_writer_faker.start()

    def tearDown(self):
        self.logbroker_writer_faker.stop()

        super(DebugRunIntegrationTestTestCase, self).tearDown()

    def test_run_integration_test_missing_uid_and_service_name(self):
        rv = self.client.post(
            '/1/debug/run_integration_test/?consumer=dev',
        )
        assert_form_errors(rv, ['uid', 'service_name'])

    def test_run_integration_test_invalid_uid(self):
        rv = self.client.post(
            '/1/debug/run_integration_test/?consumer=dev',
            data={
                'uid': 'not_a_uid',
                'service_name': TEST_SERVICE_NAME,
            },
        )
        assert_form_errors(rv, ['uid'])

    def test_run_integration_test_no_grants(self):
        self.grants_faker.set_grant_list([])

        rv = self.client.post(
            '/1/debug/run_integration_test/?consumer=dev',
            data={
                'uid': 123,
                'service_name': TEST_SERVICE_NAME,
            },
        )
        assert rv.status_code == 403

    def test_run_integration_test_ok(self):
        self.grants_faker.set_grant_list([GRANT_DEBUG_INTEGRATION_TEST])

        with mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG)
        ), mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_extract_id',
        ) as get_extract_id_mock:
            get_extract_id_mock.return_value = 'extract-id'

            with freeze_time(TEST_UNIXTIME):
                rv = self.client.post(
                    '/1/debug/run_integration_test/?consumer=dev',
                    data={
                        'uid': 123,
                        'service_name': TEST_SERVICE_NAME,
                    },
                )
        assert rv.status_code == 200, rv.data
        assert rv.json == {
            'status': 'ok',
            'uid': 123,
            'extract_id': 'extract-id',
            'service_name': TEST_SERVICE_NAME,
            'env': yenv.type,
        }

        assert len(self.logbroker_writer_faker.requests) == 1

    def test_run_integration_test_with_unixtime_ok(self):
        self.grants_faker.set_grant_list([GRANT_DEBUG_INTEGRATION_TEST])

        with mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG)
        ), mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_extract_id',
        ) as get_extract_id_mock:
            get_extract_id_mock.return_value = 'extract-id'

            with freeze_time(TEST_UNIXTIME):
                rv = self.client.post(
                    '/1/debug/run_integration_test/?consumer=dev',
                    data={
                        'uid': 123,
                        'service_name': TEST_SERVICE_NAME,
                        'unixtime': 123456,
                    },
                )
        assert rv.status_code == 200, rv.data
        assert rv.json == {
            'status': 'ok',
            'uid': 123,
            'extract_id': 'extract-id',
            'service_name': TEST_SERVICE_NAME,
            'env': yenv.type,
        }

        assert len(self.logbroker_writer_faker.requests) == 1

    def test_run_integration_test_no_grants_to_run_selected_service(self):
        self.grants_faker.set_grant_list([GRANT_DEBUG_INTEGRATION_TEST])

        with mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG)
        ), mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_extract_id',
        ) as get_extract_id_mock:
            get_extract_id_mock.return_value.id = 'extract-id'

            rv = self.client.post(
                '/1/debug/run_integration_test/?consumer=dev',
                data={
                    'uid': 123,
                    'service_name': TEST_OTHER_SERVICE_NAME,
                },
            )
        assert rv.status_code == 403

        assert len(self.logbroker_writer_faker.requests) == 0

    def test_run_integration_test_unknown_service(self):
        self.grants_faker.set_grant_list([GRANT_DEBUG_INTEGRATION_TEST])

        with mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_service_configs',
            mock.Mock(return_value=TEST_SERVICES_CONFIG)
        ), mock.patch(
            'passport.backend.takeout.api.views.debug_integration.get_extract_id',
        ) as get_extract_id_mock:
            get_extract_id_mock.return_value.id = 'extract-id'

            rv = self.client.post(
                '/1/debug/run_integration_test/?consumer=dev',
                data={
                    'uid': 123,
                    'service_name': 'unknown',
                },
            )
        assert rv.status_code == 400

        assert len(self.logbroker_writer_faker.requests) == 0

# -*- coding: utf-8 -*-

from hamcrest import (
    assert_that,
    has_entries,
)
import mock
import passport.backend.core.logbroker.exceptions as logbroker_exceptions
from passport.backend.core.logbroker.faker.fake_logbroker import FakeLogbrokerWriterProto
from passport.backend.takeout.api.grants import GRANT_PREPARE_ARCHIVE
from passport.backend.takeout.api.views.forms import (
    MAX_UID,
    PrepareArchiveForm,
)
from passport.backend.takeout.common.logbroker import TakeoutLogbrokerWriterProto
from passport.backend.takeout.test_utils.base import BaseTestCase
from passport.backend.takeout.test_utils.forms import assert_form_errors
from passport.backend.takeout.test_utils.time import freeze_time
import pytest
from werkzeug.datastructures import MultiDict


TEST_UNIXTIME = 123456789


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict({'uid': '123', 'unixtime': '123', 'consumer': 'dev'}),
        MultiDict({'uid': '0', 'unixtime': '123', 'consumer': 'dev'}),
        MultiDict({'uid': str(MAX_UID), 'unixtime': '123', 'consumer': 'dev'}),
    ],
)
def test_form_valid(input_form):
    form = PrepareArchiveForm(formdata=input_form)
    assert form.validate()


@pytest.mark.parametrize(
    'input_form',
    [
        MultiDict({}),
        MultiDict({'uid': '123'}),
        MultiDict({'unixtime': '123'}),
        MultiDict({'consumer': 'dev'}),
        MultiDict({'uid': '-1', 'unixtime': '123'}),
        MultiDict({'uid': '123', 'unixtime': '-1'}),
        MultiDict({'uid': str(MAX_UID + 1), 'unixtime': '123'}),
    ],
)
def test_form_invalid(input_form):
    form = PrepareArchiveForm(formdata=input_form)
    assert not form.validate()


class PrepareArchiveTestCase(BaseTestCase):
    def setUp(self):
        super(PrepareArchiveTestCase, self).setUp()

        self.logbroker_writer_faker = FakeLogbrokerWriterProto(TakeoutLogbrokerWriterProto, 'takeout_tasks')

        self.logbroker_writer_faker.start()

    def tearDown(self):
        self.logbroker_writer_faker.stop()

        super(PrepareArchiveTestCase, self).tearDown()

    def setup_environment(self):
        self.grants_faker.set_grant_list([GRANT_PREPARE_ARCHIVE])

    def test_prepare_archive_missing_uid_and_unixtime(self):
        rv = self.client.post(
            '/1/prepare_archive/?consumer=dev',
        )
        assert_form_errors(rv, ['uid', 'unixtime'])

    def test_prepare_archive_invalid_uid_and_unixtime(self):
        rv = self.client.post(
            '/1/prepare_archive/?consumer=dev',
            data={
                'uid': 'not_a_uid',
                'unixtime': 'not_a_unixtime',
            },
        )
        assert_form_errors(rv, ['uid', 'unixtime'])

    def test_prepare_archive_no_grants(self):
        self.grants_faker.set_grant_list([])

        rv = self.client.post(
            '/1/prepare_archive/?consumer=dev',
            data={
                'uid': 123,
                'unixtime': TEST_UNIXTIME,
            },
        )
        assert rv.status_code == 403

    def test_prepare_archive_invalid_ticket(self):
        self.setup_environment()

        rv = self.client.post(
            '/1/prepare_archive/?consumer=dev',
            data={
                'uid': 123,
                'unixtime': TEST_UNIXTIME,
            },
            headers={
                'X-Ya-Service-Ticket': 'invalid ticket',
            },
        )
        assert rv.status_code == 403
        assert 'error' in rv.json
        assert 'Malformed ticket' in rv.json['error']
        assert 'status=malformed' in rv.json['error']

    def test_prepare_archive_ok(self):
        self.setup_environment()

        with mock.patch(
            'passport.backend.takeout.api.views.prepare_archive.get_extract_id',
            autospec=True,
        ) as get_extract_id_mock:
            get_extract_id_mock.return_value = 'extract-id'

            with freeze_time(TEST_UNIXTIME):
                rv = self.client.post(
                    '/1/prepare_archive/?consumer=dev',
                    data={
                        'uid': 123,
                        'unixtime': TEST_UNIXTIME,
                    },
                )

        assert rv.status_code == 200
        assert rv.json == {
            'status': 'ok',
            'extract_id': 'extract-id',
        }
        assert len(self.logbroker_writer_faker.requests) == 1

    def test_logbroker_connection_lost(self):
        self.setup_environment()
        self.logbroker_writer_faker.set_send_side_effect([logbroker_exceptions.ConnectionLost()])

        rv = self.client.post(
            '/1/prepare_archive/?consumer=dev',
            data={
                'uid': 123,
                'unixtime': TEST_UNIXTIME,
            },
        )

        assert rv.status_code == 503
        assert_that(
            rv.json,
            has_entries(
                description='Logbroker unavailable',
                error='internal.temporary_error',
                status='error',
            )
        )

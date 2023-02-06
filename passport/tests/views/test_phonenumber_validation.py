# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.utils import assert_errors
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import (
    mask_for_statbox,
    PhoneNumber,
)


@with_settings_hosts()
class TestPhoneNumberValidation(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_number': ['validate']}))
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()
        self.setup_statbox_templates()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'sanitize_phone_number',
            action='sanitize_phone_number',
            track_id=self.track_id,
        )

    def phone_number_validation_request(self, **kwargs):
        return self.env.client.post('/1/validation/phone_number/?consumer=dev', **kwargs)

    def test_bad_request(self):
        eq_(self.phone_number_validation_request().status_code, 400)

    def test_ok(self):
        phone_number = '+74951234567'
        rv = self.phone_number_validation_request(
            data={
                'phone_number': phone_number,
                'ignore_phone_compare': '1',
                'track_id': self.track_id,
            },
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'phone_number': phone_number})

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                sanitize_phone_result=mask_for_statbox(phone_number),
            ),
        ])

    def test_track_counter(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={'phone_number': ['validate'], 'track': ['update']}))
        for count in range(1, 4):
            rv = self.phone_number_validation_request(
                data={
                    'phone_number': '+74951234567',
                    'ignore_phone_compare': '1',
                    'track_id': self.track_id,
                },
            )
            eq_(rv.status_code, 200)
            eq_(json.loads(rv.data), {'status': 'ok', 'phone_number': '+74951234567'})

            track = self.env.track_manager.get_manager().read(self.track_id)
            eq_(track.phone_number_validation_count.get(), count)

    def test_ok_with_country(self):
        rv = self.phone_number_validation_request(
            data={
                'phone_number': '4951234567',
                'country': 'ru',
                'ignore_phone_compare': '1',
                'track_id': self.track_id,
            },
        )
        eq_(rv.status_code, 200)
        eq_(json.loads(rv.data), {'status': 'ok', 'phone_number': '+74951234567'})

    def test_different_user_and_parsed_number(self):
        rv = self.phone_number_validation_request(
            data={
                'phone_number': '4951234567',
                'country': 'ru',
                'track_id': self.track_id,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        eq_(response['validation_errors'], [{'code': 'differentphonenumber',
                                             'field': 'phone_number',
                                             'message': 'Normalized number is different to user input',
                                             'value': PhoneNumber.parse('+74951234567').international}])
        track = self.env.track_manager.get_manager().read(self.track_id)
        ok_(track.sanitize_phone_changed_phone)

    def test_fail_no_country(self):
        rv = self.phone_number_validation_request(
            data={
                'phone_number': '4951234567',
                'track_id': self.track_id,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], {'phone_number': 'badphonenumber'})
        track = self.env.track_manager.get_manager().read(self.track_id)
        ok_(track.sanitize_phone_error)

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'sanitize_phone_number',
                sanitize_phone_error='badPhoneNumber',
                sanitize_phone_result=mask_for_statbox('4951234567'),
            ),
        ])

    def test_fail_with_country(self):
        rv = self.phone_number_validation_request(
            data={
                'phone_number': '11224951234567',
                'country': 'ru',
                'track_id': self.track_id,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')
        assert_errors(response['validation_errors'], {'phone_number': 'badphonenumber'})

    def test_fail_short_phone_no_statbox(self):
        rv = self.phone_number_validation_request(
            data={
                'phone_number': '34567',
                'track_id': self.track_id,
            },
        )
        eq_(rv.status_code, 200)
        response = json.loads(rv.data)
        eq_(response['status'], 'ok')

        self.env.statbox.assert_has_written([])

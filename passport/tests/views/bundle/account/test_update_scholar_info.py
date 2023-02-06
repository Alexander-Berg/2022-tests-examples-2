# -*- coding: utf-8 -*-

from nose_parameterized import parameterized
from passport.backend.api.test.mixins import make_clean_web_test_mixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.eav_type_mapping import get_attr_name
from passport.backend.core.test.consts import (
    TEST_CONSUMER1,
    TEST_FIRSTNAME1,
    TEST_FIRSTNAME2,
    TEST_LASTNAME1,
    TEST_LASTNAME2,
    TEST_LOGIN1,
    TEST_SCHOLAR_LOGIN1,
    TEST_UID1,
    TEST_USER_AGENT1,
    TEST_USER_IP1,
)
from passport.backend.core.test.events import EventCompositor
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.string import smart_bytes


all_params = [
    'firstname',
    'lastname',
]


@with_settings_hosts(
    CLEAN_WEB_API_ENABLED=False,
)
class TestUpdateScholarPersonalInfo(
    make_clean_web_test_mixin(
        'test_all',
        list(all_params),
        has_force_parameter=False,
        statbox_action='submitted',
    ),
    BaseBundleTestViews,
):
    consumer = TEST_CONSUMER1
    default_url = '/1/bundle/scholar/update/'
    http_headers = dict(
        user_ip=TEST_USER_IP1,
        user_agent=TEST_USER_AGENT1,
    )
    http_method = 'POST'

    def __init__(self, *args, **kwargs):
        super(TestUpdateScholarPersonalInfo, self).__init__(*args, **kwargs)
        self.aliases = dict(scholar=TEST_SCHOLAR_LOGIN1)
        self.new_values = dict(
            firstname=TEST_FIRSTNAME1,
            lastname=TEST_LASTNAME1,
        )
        self.old_values = dict(
            firstname=TEST_FIRSTNAME2,
            lastname=TEST_LASTNAME2,
        )
        self.scholar_uid = TEST_UID1

    @property
    def http_query_args(self):
        return dict(
            firstname=self.new_values['firstname'],
            lastname=self.new_values['lastname'],
            uid=str(self.scholar_uid),
        )

    def setUp(self):
        super(TestUpdateScholarPersonalInfo, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestUpdateScholarPersonalInfo, self).tearDown()

    def setup_environment(self):
        self.setup_blackbox()
        self.setup_grants()
        self.setup_statbox_templates()

    def setup_grants(self):
        self.env.grants.set_grants_return_value(
            mock_grants(
                consumer=self.consumer,
                grants={'account_person': ['scholar_by_uid']},
            ),
        )

    def setup_blackbox(self):
        userinfo_response = blackbox_userinfo_response(
            aliases=self.aliases,
            birthdate=None,
            city=None,
            firstname=self.old_values['firstname'],
            gender=None,
            lastname=self.old_values['lastname'],
            uid=self.scholar_uid,
        )
        self.env.blackbox.set_response_side_effect('userinfo', [userinfo_response])
        self.env.db.serialize(userinfo_response)

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'base_update_scholar_personal_info',
            consumer=TEST_CONSUMER1,
            ip=TEST_USER_IP1,
            user_agent=TEST_USER_AGENT1,
        )
        self.env.statbox.bind_entry(
            'submitted',
            _inherit_from=['base_update_scholar_personal_info'],
            action='submitted',
            mode='scholar_personal_info',
        )
        self.env.statbox.bind_entry(
            'update_attribute',
            event='account_modification',
            operation='updated',
            uid=str(self.scholar_uid),
        )
        self.env.statbox.bind_entry(
            'person.fullname',
            _inherit_from=[
                'update_attribute',
                'base_update_scholar_personal_info',
            ],
            entity='person.fullname',
            new=self.new_values['firstname'] + u' ' + self.new_values['lastname'],
            old=self.old_values['firstname'] + u' ' + self.old_values['lastname'],
        )

        for param in all_params:
            self.env.statbox.bind_entry(
                'person.%s' % param,
                _inherit_from=[
                    'update_attribute',
                    'base_update_scholar_personal_info',
                ],
                entity='person.%s' % param,
                new=self.new_values[param],
                old=self.old_values[param],
            )

    def assert_ok_update_scholar_personal_info_db(self):
        expected_attrs = dict()
        for key in self.scholar_required_attributes:
            if key not in expected_attrs:
                expected_attrs[key] = self.scholar_required_attributes[key]

        attrs = self.env.db.select('attributes', uid=self.scholar_uid, db='passportdbshard1')
        attrs = {get_attr_name(a['type']): a['value'] for a in attrs}
        self.assertEqual(attrs, expected_attrs)

    @property
    def scholar_required_attributes(self):
        return {
            'person.firstname': self.new_values['firstname'].encode('utf8'),
            'person.lastname': self.new_values['lastname'].encode('utf8'),
        }

    def assert_ok_update_scholar_personal_info_event_log(self, extra_events=None):
        extra_events = extra_events or dict()
        e = EventCompositor(uid=str(self.scholar_uid))

        def opt(name):
            if name in extra_events:
                e(name, smart_bytes(extra_events[name]))

        opt('info.firstname')
        opt('info.lastname')
        e('action', 'person')
        e('consumer', TEST_CONSUMER1)
        e('user_agent', TEST_USER_AGENT1)

        self.env.event_logger.assert_events_are_logged_with_order(e.to_lines())

    def assert_ok_update_scholar_personal_info_statbox_log(self, extra_lines=None):
        extra_lines = extra_lines or set()
        lines = list()

        def req(name):
            lines.append(self.env.statbox.entry(name))

        def opt(name):
            if name in extra_lines:
                lines.append(self.env.statbox.entry(name))

        req('submitted')
        opt('person.firstname')
        opt('person.lastname')
        opt('person.fullname')

        self.env.statbox.assert_equals(lines)

    @parameterized.expand([(p,) for p in all_params])
    def test_change_one(self, param):
        value = self.new_values[param]
        self.new_values.update(self.old_values)
        self.new_values[param] = value
        self.setup_environment()

        rv = self.make_request(exclude_args=set(all_params) - {param})

        self.assert_ok_response(rv)
        self.assert_ok_update_scholar_personal_info_db()
        self.assert_ok_update_scholar_personal_info_event_log(
            extra_events={
                'info.' + param: value,
            },
        )

        statbox_lines = {'person.' + param}
        if param in {'firstname', 'lastname'}:
            statbox_lines.add('person.fullname')
        self.assert_ok_update_scholar_personal_info_statbox_log(extra_lines=statbox_lines)

    @parameterized.expand([(p,) for p in all_params])
    def test_delete_one(self, param):
        self.setup_environment()

        rv = self.make_request(
            query_args={param: ''},
            exclude_args=set(all_params) - {param},
        )

        self.assert_error_response(rv, [param + '.empty'])

    def test_all(self):
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv)
        self.assert_ok_update_scholar_personal_info_db()
        self.assert_ok_update_scholar_personal_info_event_log(
            extra_events={'info.' + n: self.new_values[n] for n in self.new_values},
        )
        self.assert_ok_update_scholar_personal_info_statbox_log(
            {'person.fullname'} |
            {'person.' + p for p in all_params}
        )

    def test_completed_scholar(self):
        self.aliases.update(portal=TEST_LOGIN1)
        self.setup_environment()

        rv = self.make_request()

        self.assert_ok_response(rv)

    def test_never_was_scholar(self):
        self.aliases = dict(portal=TEST_LOGIN1)
        self.setup_environment()

        rv = self.make_request()

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_no_params(self):
        self.setup_environment()

        rv = self.make_request(exclude_args=all_params)

        self.assert_error_response(rv, ['form.invalid'])

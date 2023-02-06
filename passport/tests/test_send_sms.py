# -*- coding: utf-8 -*-
from collections import (
    defaultdict,
    namedtuple,
)
from copy import copy
from datetime import (
    datetime,
    timedelta,
)
from json import dump
from os import remove
from unittest import TestCase
from urllib import quote_plus

from flask.testing import FlaskClient
import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox.exceptions import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
)
from passport.backend.core.builders.kolmogor.exceptions import KolmogorPermanentError
from passport.backend.core.builders.kolmogor.faker import FakeKolmogor
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.models.phones.faker import build_phone_bound
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)
from passport.backend.core.xml.test_utils import assert_xml_response_equals
from passport.backend.library.configurator.test import FakeConfig
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.string import (
    smart_str,
    smart_text,
)
from passport.backend.utils.time import datetime_to_integer_unixtime
from passport.infra.daemons.yasmsapi.api.app import create_app
from passport.infra.daemons.yasmsapi.api.exceptions import (
    BadPhone,
    BaseError,
    BlackboxError,
    DBConnectionError,
    DontKnowYou,
    LimitExceeded,
    NoCurrent,
    NoRights,
    NoRoute,
    PhoneBlocked,
    TicketInvalid,
    TicketMissing,
    BadUserIp,
    UnknownUid,
    UserDataNotInBody,
    InvalidTemplateOrParams,
)
from passport.infra.daemons.yasmsapi.api.grants import (
    get_grant_name_for_action,
    get_name_for_checking_grants,
    SEND_ANONYMOUS_SMS_GRANT,
    SMS_FROM_UID_GRANT,
    SPECIFY_GATE_GRANT,
    SPECIFY_PREVIOUS_GATES_GRANT,
)
from passport.infra.daemons.yasmsapi.api.views.base import (
    INTERNAL_ERROR_CODE,
    INTERNAL_ERROR_MESSAGE,
)
from passport.infra.daemons.yasmsapi.common.helpers import mask_for_statbox
from passport.infra.daemons.yasmsapi.db import queries
from passport.infra.daemons.yasmsapi.db.connection import DBError

from .fake_db import FakeYasmsDB
from .fake_statbox import (
    YasmsStatboxPrivateLoggerFaker,
    YasmsStatboxPublicLoggerFaker,
)
from .test_data import (
    TEST_AUTORU_GATE_ID,
    TEST_BLACKBOX_CLIENT_ID,
    TEST_BLOCKED_PHONE,
    TEST_CACHED_ROUTES,
    TEST_CONSUMER_IP,
    TEST_DEFAULT_ROUTE,
    TEST_FROM_UID,
    TEST_GATE_ID,
    TEST_GATE_ID_DEVNULL,
    TEST_GSM_TEXT,
    TEST_IDENTITY,
    TEST_INVALID_PHONE,
    TEST_KOLMOGOR_CLIENT_ID,
    TEST_LONG_TEXT,
    TEST_MASKED_PHONE,
    TEST_NOT_EXISTING_GATE_ID,
    TEST_OTHER_PHONE,
    TEST_OTHER_PHONE_ID,
    TEST_PHONE,
    TEST_PHONE_ID,
    TEST_SENDER,
    TEST_TAXI_ROUTE,
    TEST_TAXI_SENDER,
    TEST_UID,
    TEST_UNICODE16_TEXT,
    TEST_TEMPLATE_TEXT,
    TEST_TEMPLATE_PARAMS,
    TEST_TEMPLATE_RENDERED,
    TEST_TEMPLATE_RENDERED_MASKED,
    TEST_METADATA,
)


_host = namedtuple('host', 'name id dc')

KEYS_FILE = './keys.json'


@with_settings(
    CURRENT_FQDN='yasms-dev.passport.yandex.net',
    HOSTS=[_host(name='yasms-dev.passport.yandex.net', id=0x7F, dc='i')],
    KOLMOGOR_URL='http://badauthdb-test.passport.yandex.net:9080/',
    KOLMOGOR_TIMEOUT=1,
    KOLMOGOR_RETRIES=2,
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_TIMEOUT=1,
    BLACKBOX_RETRIES=2,
    BLACKBOX_PHONE_EXTENDED_ATTRIBUTES=['number', 'bound'],
)
class SendSmsViewTestCase(TestCase):
    url = '/sendsms'
    packed_sms_id = '2127000000000001'

    def setUp(self):
        with open(KEYS_FILE, 'wt') as f:
            dump(
                [
                    {
                        'id': 1,
                        'body': 'abcdef',
                        'create_ts': 500,
                    },
                ],
                f,
            )

        self.patches = []

        self.fake_config = FakeConfig(
            'passport.infra.daemons.yasmsapi.api.configs.config',
            {
                'anonymous_sms_limit_by_sender': {
                    TEST_TAXI_SENDER: 3,
                },
                'anonymous_sms_limit': 1,
                'blackbox': {
                    'phone_extended_attributes': ['number', 'bound'],
                },
                'routes_cache_lifetime': 300,
                'test_sms_centers': ['devnull'],
                'sms_encryptor': {
                    'keys_path': KEYS_FILE,
                    'reload_period': 600,
                    'key_depth': 1,
                    'encrypt_sms': False,
                },
            },
        )
        self.patches.append(self.fake_config)

        self.grants = FakeGrants()
        self.patches.append(self.grants)

        self.db = FakeYasmsDB()
        self.patches.append(self.db)

        self.blackbox = FakeBlackbox()
        self.patches.append(self.blackbox)

        self.kolmogor = FakeKolmogor()
        self.patches.append(self.kolmogor)

        self.statbox_private = YasmsStatboxPrivateLoggerFaker()
        self.patches.append(self.statbox_private)

        self.statbox_public = YasmsStatboxPublicLoggerFaker()
        self.patches.append(self.statbox_public)

        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.patches.append(self.tvm_credentials_manager)
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_BLACKBOX_CLIENT_ID): {'alias': 'blackbox', 'ticket': TEST_TICKET},
                    str(TEST_KOLMOGOR_CLIENT_ID): {'alias': 'kolmogor', 'ticket': TEST_TICKET},
                },
            ),
        )
        self.mock_weighted_random = mock.Mock(return_value=0)
        self.patch_weighted_random = mock.patch(
            'passport.infra.daemons.yasmsapi.api.views.send_sms.make_weighted_random_choice',
            self.mock_weighted_random,
        )
        self.patches.append(self.patch_weighted_random)

        for patch in self.patches:
            patch.start()

        # создаем тестовый клиент
        app = create_app()
        app.test_client_class = FlaskClient
        app.testing = True
        self.client = app.test_client()

        self.setup_statbox_templates()

        self.db.load_initial_data()
        self.setup_grants()
        self.setup_kolmogor_response()
        self.setup_bb_response()
        self.setup_random_response()

        self.clear_cache()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.clear_cache()
        remove(KEYS_FILE)

    def clear_cache(self):
        queries.ROUTES_CACHE = []
        queries.ROUTES_CACHE_UPDATED = 0

    def fill_cache(self, cache=None):
        queries.ROUTES_CACHE = cache or TEST_CACHED_ROUTES

    def set_cache_upd(self, dt):
        queries.ROUTES_CACHE_UPDATED = datetime_to_integer_unixtime(dt)

    def set_weighted_random(self, i):
        self.mock_weighted_random.return_value = i

    @property
    def all_grants(self):
        return [
            SPECIFY_GATE_GRANT,
            SPECIFY_PREVIOUS_GATES_GRANT,
            SEND_ANONYMOUS_SMS_GRANT,
            SMS_FROM_UID_GRANT,
            get_grant_name_for_action('Route', TEST_DEFAULT_ROUTE),
        ]

    @property
    def default_params(self):
        return {
            'sender': TEST_SENDER,
            'phone': TEST_PHONE,
            'text': TEST_GSM_TEXT,
        }

    def setup_grants(self, grants_list=None, client_id=None):
        grants_list = self.all_grants if grants_list is None else grants_list
        taxi_grants_list = copy(grants_list)
        taxi_grants_list.append(get_grant_name_for_action('Route', TEST_TAXI_ROUTE))
        taxi_grants = defaultdict(list)
        for grant in taxi_grants_list:
            name, action = grant.split('.')
            taxi_grants[name].append(action)
        grants = {
            get_name_for_checking_grants(TEST_SENDER): {
                u'grants': dict((grant.split('.') for grant in grants_list)),
                u'networks': ['127.0.0.1'],
            },
            get_name_for_checking_grants(TEST_TAXI_SENDER): {
                u'grants': taxi_grants,
                u'networks': ['127.0.0.1'],
            },
        }
        if client_id:
            for k, v in grants.iteritems():
                v.update(client={'client_id': client_id})
        self.grants.set_grants_return_value(grants)

    def setup_bb_response(self, phones=None, default=False):
        if phones is None:
            phones = build_phone_bound(
                phone_id=TEST_PHONE_ID,
                phone_number=TEST_PHONE,
                is_default=default,
            )
        else:
            phones = {}
        self.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=TEST_UID, **phones),
        )

    def setup_kolmogor_response(self, counter=0):
        self.kolmogor.set_response_value('get', str(counter))
        self.kolmogor.set_response_value('inc', 'OK')

    def setup_random_response(self, ind=0):
        self.patch_weighted_random.return_value = ind

    def setup_statbox_templates(self):
        base_entry = dict(
            global_smsid=self.packed_sms_id,
            local_smsid='1',
            sender=TEST_SENDER,
            rule=TEST_DEFAULT_ROUTE,
            gate='1',
            chars=str(len(TEST_GSM_TEXT)),
            segments='1',
            encoding='gsm0338',
            masked_number=TEST_MASKED_PHONE,
        )
        self.statbox_public.bind_entry('queue_sms', **base_entry)
        self.statbox_private.bind_entry(
            'queue_sms', number=TEST_PHONE, text=smart_text(TEST_GSM_TEXT), consumer_ip='127.0.0.1', **base_entry
        )
        self.statbox_private.bind_entry(
            'limit_exceeded',
            error='limit_exceeded',
            number=TEST_PHONE,
            previous_gates='',
            sender=TEST_SENDER,
        )

    def make_request(
        self,
        url=None,
        method='get',
        query_string=None,
        data=None,
        exclude_from_query=None,
        remote_addr=TEST_CONSUMER_IP,
        headers=None,
    ):
        url = url or self.url
        query_string = merge_dicts(
            self.default_params,
            query_string or {},
        )
        exclude = exclude_from_query or []
        for key in exclude:
            query_string.pop(key, None)
        kwargs = {
            'query_string': query_string,
            'data': data,
            'headers': headers,
            'environ_base': {'REMOTE_ADDR': remote_addr},
        }
        return getattr(self.client, method)(url, **kwargs)

    def assert_headers(self, resp):
        eq_(resp.headers.get('Content-Type'), 'text/xml; charset=utf-8')
        eq_(resp.headers.get('Pragma'), 'no-cache')
        eq_(resp.headers.get('Cache-control'), 'private, max-age=0, no-cache, no-store, must-revalidate')
        eq_(resp.headers.get('Expires'), 'Thu, 01 Jan 1970 00:00:00 GMT')

    def assert_kolmogor_by_tvm(self):
        self.kolmogor.requests[-1].assert_headers_contain(
            {'X-Ya-Service-Ticket': TEST_TICKET},
        )

    def assert_kolmogor_counter_keys(self, key):
        self.kolmogor.requests[0].assert_properties_equal(
            method='GET',
            url='http://badauthdb-test.passport.yandex.net:9080/get?keys=%s&space=yasms_counters' % quote_plus(key),
            headers={'X-Ya-Service-Ticket': TEST_TICKET},
        )
        self.kolmogor.requests[-1].assert_properties_equal(
            method='POST',
            url='http://badauthdb-test.passport.yandex.net:9080/inc',
            post_args={
                'keys': key,
                'space': 'yasms_counters',
            },
            headers={'X-Ya-Service-Ticket': TEST_TICKET},
        )

    def assert_blackbox_by_tvm(self):
        self.blackbox.requests[-1].assert_headers_contain(
            {'X-Ya-Service-Ticket': TEST_TICKET},
        )

    def assert_statbox(self, common_kwargs=None, private_kwargs=None):
        common_kwargs = common_kwargs or {}
        private_kwargs = private_kwargs or {}
        self.statbox_private.assert_equals(
            [
                self.statbox_private.entry('queue_sms', **merge_dicts(common_kwargs, private_kwargs)),
            ]
        )
        self.statbox_public.assert_equals(
            [
                self.statbox_public.entry('queue_sms', **common_kwargs),
            ]
        )

    def assert_statbox_empty(self):
        self.statbox_private.assert_has_written([])
        self.statbox_public.assert_has_written([])

    def assert_db_enqueued(self, upd_values=None, upd_metadata=None):
        metadata = TEST_METADATA.copy()
        metadata.update(upd_metadata or {})

        values = {
            'phone': TEST_PHONE,
            'gateid': TEST_GATE_ID,
            'text': smart_str(TEST_GSM_TEXT),
            'sender': TEST_SENDER,
            'create_time': DatetimeNow(),
            'touch_time': DatetimeNow(),
            'metadata': metadata,
        }
        if upd_values:
            values = merge_dicts(values, upd_values)
        self.db.assert_enqueued(values=values)

    def assert_ok_response(self, resp, packed_sms_id=None, bb_tvm=False, klm_tvm=False, gates=None):
        eq_(resp.status_code, 200)
        gates = ','.join(list(map(str, gates or [TEST_GATE_ID])))
        assert_xml_response_equals(
            resp,
            u"""<?xml version="1.0" encoding="utf-8"?>
               <doc>
               <message-sent id="{sms_id}" />
               <gates ids="{gates}" />
               </doc>
            """.format(
                sms_id=packed_sms_id or self.packed_sms_id, gates=gates
            ),
        )
        self.assert_headers(resp)
        if bb_tvm:
            self.assert_blackbox_by_tvm()
        if klm_tvm:
            self.assert_kolmogor_by_tvm()

    def assert_error_response(
        self, resp, error_cls, check_db=True, status_code=200, bb_tvm=False, klm_tvm=False, check_statbox=True
    ):
        eq_(resp.status_code, status_code)
        if issubclass(error_cls, BaseError):
            error_code = error_cls.code
            error_message = error_cls.message
        else:
            error_code = INTERNAL_ERROR_CODE
            error_message = INTERNAL_ERROR_MESSAGE
        assert_xml_response_equals(
            resp,
            u"""<?xml version="1.0" encoding="utf-8"?>
               <doc>
               <error>{message}</error>
               <errorcode>{code}</errorcode>
               </doc>
            """.format(
                message=error_message, code=error_code
            ),
        )
        self.assert_headers(resp)
        if check_statbox:
            self.assert_statbox_empty()
        if check_db:
            self.db.assert_empty()
        if bb_tvm:
            self.assert_blackbox_by_tvm()
        if klm_tvm:
            self.assert_kolmogor_by_tvm()

    def test_no_previous_gates_grant(self):
        self.setup_grants(
            grants_list=[
                SPECIFY_GATE_GRANT,
                SEND_ANONYMOUS_SMS_GRANT,
                get_grant_name_for_action('Route', TEST_DEFAULT_ROUTE),
            ]
        )
        resp = self.make_request(query_string={'previous_gates': '1,2'})
        self.assert_error_response(resp, NoRights)

    def test_form_invalid__error(self):
        query = {
            'phone': 2,
            'text': TEST_LONG_TEXT,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, BadPhone)

    def test_uid_invalid__error(self):
        query = {
            'uid': -1,
            'text': TEST_GSM_TEXT,
            'phone': TEST_PHONE,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, BlackboxError)

    def test_invalid_consumer_ip__error(self):
        self.setup_grants()
        resp = self.make_request(remote_addr=None)
        self.assert_error_response(resp, DontKnowYou)

    def test_no_grants__error(self):
        self.setup_grants(grants_list=[])
        resp = self.make_request()
        self.assert_error_response(resp, NoRights)

    def test_invalid_ip_for_sender__error(self):
        resp = self.make_request(remote_addr='178.90.90.78')
        self.assert_error_response(resp, DontKnowYou)

    def test_not_enough_grants__error(self):
        self.setup_grants(
            grants_list=[
                get_grant_name_for_action('Route', TEST_DEFAULT_ROUTE),
            ]
        )
        resp = self.make_request()
        self.assert_error_response(resp, NoRights)

    def test_with_user_stuff(self):
        resp = self.make_request(
            headers={
                'Ya-Consumer-Client-Ip': '127.1.1.1',
                'ya-client-user-agent': "some agent",
            },
            query_string={
                'scenario': 'test_with_user_stuff',
                'device_id': 'ca2c4cfc56ed4465861356647d76865b',
                'request_path': 'please-send-my-sms.com/send?stuff=1#tag',
            },
        )
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(
            private_kwargs={
                'user_ip': '127.1.1.1',
                'user_agent': "some agent",
            },
        )
        self.assert_db_enqueued(
            upd_metadata={
                "ip": "127.1.1.1",
                "user_agent": "some agent",
                "scenario": "test_with_user_stuff",
                "device_id": "ca2c4cfc56ed4465861356647d76865b",
                "request_path": "please-send-my-sms.com/send?stuff=1#tag",
            }
        )

    def test_invalid_user_ip(self):
        resp = self.make_request(headers={'Ya-Consumer-Client-Ip': '127_1_1_1'})
        self.assert_error_response(resp, BadUserIp)

    def test_with_service_ticket(self):
        self.setup_grants(client_id=TEST_CLIENT_ID_2)
        resp = self.make_request(headers={'X-Ya-Service-Ticket': TEST_TICKET})
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox()
        self.assert_db_enqueued()

    def test_missing_ticket(self):
        self.setup_grants(client_id=TEST_CLIENT_ID_2)
        resp = self.make_request()
        self.assert_error_response(resp, TicketMissing)

    def test_invalid_source(self):
        self.setup_grants(client_id=TEST_CLIENT_ID)
        resp = self.make_request(headers={'X-Ya-Service-Ticket': TEST_TICKET})
        self.assert_error_response(resp, TicketInvalid)

    def test_by_phone__ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox()
        self.assert_db_enqueued()
        self.assert_kolmogor_counter_keys('by_phone:%s' % TEST_PHONE)

    def test_with_template__ok(self):
        resp = self.make_request(
            method='post',
            query_string={
                'text': TEST_TEMPLATE_TEXT,
                'allow_unused_text_params': True,
            },
            data={
                'text_template_params': TEST_TEMPLATE_PARAMS,
            },
        )

        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(
            common_kwargs={'chars': str(len(TEST_TEMPLATE_RENDERED_MASKED)), 'encoding': 'utf16'},
            private_kwargs={
                'text': smart_text(TEST_TEMPLATE_RENDERED_MASKED),
            },
        )
        self.assert_db_enqueued(
            upd_values={
                'text': smart_str(TEST_TEMPLATE_RENDERED),
            },
            upd_metadata={'masked_text': TEST_TEMPLATE_RENDERED_MASKED},
        )

    def test_with_template__params_url(self):
        resp = self.make_request(
            method='post',
            query_string={
                'text': TEST_TEMPLATE_TEXT,
                'text_template_params': TEST_TEMPLATE_PARAMS,
            },
        )

        self.assert_error_response(resp, UserDataNotInBody)

    def test_with_template__invalid_template(self):
        resp = self.make_request(
            method='post',
            query_string={
                'text': u'{{a}',
            },
            data={
                'text_template_params': '{"a":"1"}',
            },
        )

        self.assert_error_response(resp, InvalidTemplateOrParams)

    def test_with_template__invalid_params(self):
        resp = self.make_request(
            method='post',
            query_string={
                'text': u'{{a}}',
            },
            data={
                'text_template_params': '{"b":"1"}',
            },
        )

        self.assert_error_response(resp, InvalidTemplateOrParams)

    def test_with_template__unused_params(self):
        resp = self.make_request(
            method='post',
            query_string={
                'text': TEST_TEMPLATE_TEXT,
            },
            data={
                'text_template_params': TEST_TEMPLATE_PARAMS,
            },
        )

        self.assert_error_response(resp, InvalidTemplateOrParams)

    def test_with_template__template_keys(self):
        resp = self.make_request(
            method='post',
            query_string={
                'text': u'{{a-}}',
            },
            data={
                'text_template_params': '{"a":"1"}',
            },
        )

        self.assert_error_response(resp, InvalidTemplateOrParams)

    def test_with_template__params_keys(self):
        resp = self.make_request(
            method='post',
            query_string={
                'text': u'{{a}}',
            },
            data={
                'text_template_params': '{"a-":"1"}',
            },
        )

        self.assert_error_response(resp, InvalidTemplateOrParams)

    def test_by_phone_with_trailing_slash__ok(self):
        resp = self.make_request(url='{}/'.format(self.url))
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox()
        self.assert_db_enqueued()

    def test_by_uid_take_default__ok(self):
        query = {
            'uid': TEST_UID,
        }
        resp = self.make_request(query_string=query, exclude_from_query=['phone'])
        self.assert_ok_response(resp, bb_tvm=True, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                uid=str(TEST_UID),
                phoneid=str(TEST_PHONE_ID),
            ),
        )
        self.assert_db_enqueued(upd_metadata={'uid': TEST_UID})

    def test_by_uid_no_default__error(self):
        self.setup_bb_response(phones=[])
        query = {
            'uid': TEST_UID,
        }
        resp = self.make_request(query_string=query, exclude_from_query=['phone'])
        self.assert_error_response(resp, NoCurrent, bb_tvm=True)

    def test_by_uid_with_number__ok(self):
        query = {
            'uid': TEST_UID,
            'number': TEST_PHONE,
        }
        resp = self.make_request(query_string=query, exclude_from_query=['phone'])
        self.assert_ok_response(resp, bb_tvm=True, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                uid=str(TEST_UID),
                phoneid=str(TEST_PHONE_ID),
            ),
        )
        self.assert_db_enqueued(upd_metadata={'uid': TEST_UID})

    def test_by_uid_with_number__error(self):
        query = {
            'uid': TEST_UID,
            'number': TEST_OTHER_PHONE,
        }
        resp = self.make_request(query_string=query, exclude_from_query=['phone'])
        self.assert_error_response(resp, NoCurrent, bb_tvm=True)

    def test_by_uid_with_phone_id__ok(self):
        query = {
            'uid': TEST_UID,
            'phone_id': TEST_PHONE_ID,
        }
        resp = self.make_request(query_string=query, exclude_from_query=['phone'])
        self.assert_ok_response(resp, bb_tvm=True, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                uid=str(TEST_UID),
                phoneid=str(TEST_PHONE_ID),
            ),
        )
        self.assert_db_enqueued(upd_metadata={'uid': TEST_UID})

    def test_by_uid_with_phone_id__error(self):
        query = {
            'uid': TEST_UID,
            'phone_id': TEST_OTHER_PHONE_ID,
        }
        resp = self.make_request(query_string=query, exclude_from_query=['phone'])
        self.assert_error_response(resp, NoCurrent, bb_tvm=True)

    def test_query_over_data__ok(self):
        query = {
            'uid': TEST_UID,
            'number': 2,
        }
        data = {
            'phone': TEST_PHONE,
            'sender': TEST_TAXI_SENDER,
            'text': TEST_UNICODE16_TEXT,
        }
        resp = self.make_request(
            method='post',
            query_string=query,
            data=data,
            exclude_from_query=['phone', 'text'],
        )
        self.assert_ok_response(resp, bb_tvm=True, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                phoneid=str(TEST_PHONE_ID),
                uid=str(TEST_UID),
                chars=str(len(TEST_UNICODE16_TEXT)),
                encoding='utf16',
            ),
            private_kwargs=dict(
                text=smart_text(TEST_UNICODE16_TEXT),
            ),
        )
        values = {
            'text': smart_str(TEST_UNICODE16_TEXT),
        }
        self.assert_db_enqueued(values, upd_metadata={'uid': TEST_UID})

    def test_taxi__ok(self):
        query = {
            'sender': TEST_TAXI_SENDER,
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                sender='taxi',
                rule=TEST_DEFAULT_ROUTE,
                gate='1',
            ),
        )
        values = {
            'gateid': 1,
            'sender': TEST_TAXI_SENDER,
        }
        self.assert_db_enqueued(values, upd_metadata={'service': 'Yandex.Taxi'})
        self.assert_kolmogor_counter_keys('by_sender:%s:by_phone:%s' % (TEST_TAXI_SENDER, TEST_PHONE))

    def test_sender_and_caller(self):
        query = {
            'caller': TEST_TAXI_SENDER,
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(common_kwargs={'caller': TEST_TAXI_SENDER})
        self.assert_db_enqueued(upd_metadata={'service': 'dev/{}'.format(TEST_TAXI_SENDER)})

    def test_scenario_and_identity(self):
        query = {
            'scenario': 'test_scenario',
            'identity': 'test_identity',
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(
            common_kwargs={
                'identity': 'test_identity',
            }
        )
        self.assert_db_enqueued(upd_metadata={'scenario': 'test_scenario'})

    def test_not_scenario_and_identity(self):
        query = {
            'identity': 'test_identity',
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(common_kwargs={'identity': 'test_identity'})
        self.assert_db_enqueued(upd_metadata={'scenario': 'test_identity'})

    def test_phone_blocked__error(self):
        query = {
            'phone': TEST_BLOCKED_PHONE,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, PhoneBlocked)

    def test_no_gate__error(self):
        query = {
            'gate_id': TEST_NOT_EXISTING_GATE_ID,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, NoRoute)

    def test_gate_by_gate_id__ok(self):
        query = {
            'gate_id': TEST_AUTORU_GATE_ID,
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, klm_tvm=True, gates=[2])
        self.assert_statbox(
            common_kwargs=dict(
                gate=str(TEST_AUTORU_GATE_ID),
            ),
        )
        values = {
            'gateid': TEST_AUTORU_GATE_ID,
        }
        self.assert_db_enqueued(values)

    def test_void_aliase_after_block__ok(self):
        query = {
            'phone': TEST_OTHER_PHONE,
            'gate_id': TEST_GATE_ID_DEVNULL,
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, gates=[TEST_GATE_ID_DEVNULL])
        self.assert_statbox_empty()
        self.db.assert_empty()

    def test_limits_exceeded_by_sender__error(self):
        self.setup_kolmogor_response(counter=3)
        query = {
            'uid': TEST_UID,
            'sender': TEST_TAXI_SENDER,
            'route': 'taxi',
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, LimitExceeded, bb_tvm=True, klm_tvm=True, check_statbox=False)
        self.statbox_public.assert_has_written([])
        self.statbox_private.assert_has_written(
            [
                self.statbox_private.entry('limit_exceeded', sender=TEST_TAXI_SENDER, count='3'),
            ]
        )

    def test_limits_exceeded_by_default__error(self):
        self.setup_kolmogor_response(counter=2)
        resp = self.make_request()
        self.assert_error_response(resp, LimitExceeded, klm_tvm=True, check_statbox=False)
        self.statbox_public.assert_has_written([])
        self.statbox_private.assert_has_written(
            [
                self.statbox_private.entry('limit_exceeded', count='2'),
            ]
        )

    def test_blackbox_error(self):
        self.blackbox.set_response_side_effect(
            'userinfo',
            BlackboxTemporaryError(),
        )
        query = {
            'uid': TEST_UID,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, BlackboxError, bb_tvm=True)

    def test_get_counters_kolmogor_failed__ok(self):
        self.kolmogor.set_response_side_effect('get', KolmogorPermanentError)
        resp = self.make_request()
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox()
        self.assert_db_enqueued()

    def test_update_counters_kolmogor_failed__ok(self):
        self.kolmogor.set_response_side_effect('inc', KolmogorPermanentError)
        resp = self.make_request()
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox()
        self.assert_db_enqueued()

    def test_with_from_uid_and_identity__ok(self):
        query = {
            'from_uid': TEST_FROM_UID,
            'identity': TEST_IDENTITY,
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                uid=str(TEST_FROM_UID),
                identity=TEST_IDENTITY,
            ),
        )
        self.assert_db_enqueued(upd_metadata={"uid": TEST_FROM_UID, "scenario": TEST_IDENTITY})

    def test_blocked_phone_db_failed__ok(self):
        """
        Телефон заблокирован, но бд недоступна.
        Ожидаемые вызовы к бд:
            1. Проверка телефона на блокировку
            2. Получение роутов
            3. Запись смс в очередь
        """
        self.db.set_side_effect(
            [
                DBError(),
                self.db.set_cursor_fetchall_result(TEST_CACHED_ROUTES),
                self.db.set_cursor_inserted_key_result([1]),
            ]
        )
        query = {
            'phone': TEST_BLOCKED_PHONE,
        }
        resp = self.make_request(query_string=query)
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                masked_number=TEST_BLOCKED_PHONE[:-4] + '*' * 4,
            ),
            private_kwargs=dict(
                number=TEST_BLOCKED_PHONE,
            ),
        )

    def test_all_gates_db_failed__error(self):
        """
        Передаем гейт, бд недоступна.
        Ожидаемые вызовы к бд:
            1. Проверка телефона на блокировку
            2. Получение гейтов
        """
        self.db.set_side_effect(
            [
                self.db.set_cursor_fetchall_result([]),
                DBError(),
            ]
        )
        query = {
            'gate_id': TEST_AUTORU_GATE_ID,
        }
        resp = self.make_request(query_string=query)
        self.assert_error_response(resp, NoRoute, check_db=False)

    def test_possible_routes_db_failed__error(self):
        """
        Поучаем гейт по номеру и роуту, бд недоступна.
        Ожидаемые вызовы к бд:
            1. Проверка телефона на блокировку
            2. Получение возможных роутов по номеру
        """
        self.db.set_side_effect(
            [
                self.db.set_cursor_fetchall_result([]),
                DBError(),
            ]
        )
        resp = self.make_request()
        self.assert_error_response(resp, NoRoute, check_db=False)

    def test_enqueue_sms_db_failed__error(self):
        """
        Записываем смс в очередь, бд недоступна.
        Ожидаемые вызовы к бд:
            1. Проверка телефона на блокировку
            2. Получение возможных роутов по номеру
            3. Запись в очередь
        """
        self.db.set_side_effect(
            [
                self.db.set_cursor_fetchall_result([]),
                self.db.set_cursor_fetchall_result(TEST_CACHED_ROUTES),
                DBError(),
            ]
        )
        resp = self.make_request()
        self.assert_error_response(resp, DBConnectionError, check_db=False, klm_tvm=True)

    def test_weighted_random__ok(self):
        cache = [
            {'gateid': 1, 'prefix': '+', 'mode': 'default', 'weight': 1, 'aliase': 'infobip'},
            {'gateid': 2, 'prefix': '+', 'mode': 'default', 'weight': 2, 'aliase': 'infobipyt'},
        ]
        self.fill_cache(cache)
        self.set_cache_upd(datetime.now() + timedelta(days=2))
        self.set_weighted_random(1)

        resp = self.make_request(url='/2{}'.format(self.url))
        self.assert_ok_response(resp, klm_tvm=True, gates=[2])
        self.assert_statbox(
            common_kwargs=dict(gate='2'),
        )
        self.assert_db_enqueued(upd_values={'gateid': 2})

    def test_phone_invalid_ok(self):
        resp = self.make_request(query_string={'phone': TEST_INVALID_PHONE})
        self.assert_ok_response(resp, klm_tvm=True)
        self.assert_statbox(
            common_kwargs=dict(
                masked_number=TEST_INVALID_PHONE[:-4] + '*' * 4,
            ),
            private_kwargs=dict(
                number=TEST_INVALID_PHONE,
            ),
        )
        self.assert_db_enqueued({'phone': TEST_INVALID_PHONE})

    def test_enqueue_sms_db_unhandled__error(self):
        """
        Записываем смс в очередь, бд недоступна.
        Ожидаемые вызовы к бд:
            1. Проверка телефона на блокировку
            2. Получение возможных роутов по номеру
            3. Запись в очередь - внезапно ошибка
        """
        self.db.set_side_effect(
            [
                self.db.set_cursor_fetchall_result([]),
                self.db.set_cursor_fetchall_result(TEST_CACHED_ROUTES),
                ValueError('Test'),
            ]
        )
        resp = self.make_request()
        self.assert_error_response(resp, ValueError, status_code=500, check_db=False, klm_tvm=True)

    def test_unknown_uid(self):
        self.blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(uid=None),
        )
        query = {
            'uid': TEST_UID,
        }
        resp = self.make_request(query_string=query, exclude_from_query=['phone'])
        self.assert_error_response(resp, UnknownUid, check_db=False, bb_tvm=True)

    def test_previous_gates_use_second(self):
        self.set_weighted_random(0)
        resp = self.make_request(query_string={'previous_gates': '1'})
        self.assert_ok_response(resp, klm_tvm=True, gates=[1, 7])
        self.assert_statbox(common_kwargs={'gate': '7', 'previous_gates': '1'})
        values = {
            'gateid': 7,
        }
        self.assert_db_enqueued(values)
        self.assert_kolmogor_counter_keys('by_phone:%s' % TEST_PHONE)

    def test_previous_gates_use_third(self):
        # Тут порядок такой 1 -> 7 -> 8
        self.set_weighted_random(0)
        resp = self.make_request(query_string={'previous_gates': '1,7'})
        self.assert_ok_response(resp, klm_tvm=True, gates=[1, 7, 8])
        self.assert_statbox(common_kwargs={'gate': '8', 'previous_gates': '1,7'})
        values = {
            'gateid': 8,
        }
        self.assert_db_enqueued(values)
        self.assert_kolmogor_counter_keys('by_phone:%s' % TEST_PHONE)

    def test_previous_gates_mixed_use_third_unused(self):
        # Тут порядок такой 7 -> 1 -> 8
        self.set_weighted_random(1)
        resp = self.make_request(query_string={'previous_gates': '1,7'})
        self.assert_ok_response(resp, klm_tvm=True, gates=[1, 7, 8])
        self.assert_statbox(common_kwargs={'gate': '8', 'previous_gates': '1,7'})
        values = {
            'gateid': 8,
        }
        self.assert_db_enqueued(values)
        self.assert_kolmogor_counter_keys('by_phone:%s' % TEST_PHONE)

    def test_previous_gates_all_used_use_first_again(self):
        # Тут порядок такой 1 -> 7 -> 8
        self.set_weighted_random(0)
        resp = self.make_request(query_string={'previous_gates': '1,7,8'})
        self.assert_ok_response(resp, klm_tvm=True, gates=[7, 8, 1])
        self.assert_statbox(common_kwargs={'gate': '1', 'previous_gates': '1,7,8'})
        values = {
            'gateid': 1,
        }
        self.assert_db_enqueued(values)
        self.assert_kolmogor_counter_keys('by_phone:%s' % TEST_PHONE)

    def test_previous_gates_all_used_use_second_again(self):
        # Тут порядок такой 1 -> 7 -> 8
        self.set_weighted_random(0)
        resp = self.make_request(query_string={'previous_gates': '7,8,1'})
        self.assert_ok_response(resp, klm_tvm=True, gates=[8, 1, 7])
        self.assert_statbox(common_kwargs={'gate': '7', 'previous_gates': '7,8,1'})
        values = {
            'gateid': 7,
        }
        self.assert_db_enqueued(values)
        self.assert_kolmogor_counter_keys('by_phone:%s' % TEST_PHONE)

    def test_previous_gates_no_used(self):
        # Тут порядок такой 1 -> 7 -> 8
        self.set_weighted_random(0)
        resp = self.make_request(query_string={'previous_gates': '5'})
        self.assert_ok_response(resp, klm_tvm=True, gates=[5, 1])
        self.assert_statbox(common_kwargs={'gate': '1', 'previous_gates': '5'})
        values = {
            'gateid': 1,
        }
        self.assert_db_enqueued(values)
        self.assert_kolmogor_counter_keys('by_phone:%s' % TEST_PHONE)

    def test_previous_gates_one_possible_route(self):
        test_number = '+79001002030'
        resp = self.make_request(query_string={'phone': test_number, 'previous_gates': '8'})
        eq_(self.mock_weighted_random.call_count, 0)
        self.assert_ok_response(resp, klm_tvm=True, gates=[8, 1])
        self.assert_statbox(
            common_kwargs={'gate': '1', 'masked_number': mask_for_statbox(test_number), 'previous_gates': '8'},
            private_kwargs={'number': test_number},
        )
        self.assert_db_enqueued({'gateid': 1, 'phone': test_number})
        self.assert_kolmogor_counter_keys('by_phone:%s' % test_number)

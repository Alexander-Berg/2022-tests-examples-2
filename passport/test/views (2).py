# -*- coding: utf-8 -*-
from collections import defaultdict
from functools import partial
import json
import logging
import re
import time
from xml.etree.ElementTree import fromstring

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.app import create_app
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.core.builders.afisha.faker.fake_afisha_api import FakeAfishaApi
from passport.backend.core.builders.antifraud.faker.fake_antifraud import FakeAntifraudAPI
from passport.backend.core.builders.avatars_mds_api.faker import FakeAvatarsMdsApi
from passport.backend.core.builders.bbro_api.faker import FakeBBroApi
from passport.backend.core.builders.bilet_api.faker.fake_bilet_api import FakeBiletApi
from passport.backend.core.builders.blackbox.faker.blackbox import FakeBlackbox
from passport.backend.core.builders.bot_api.faker.fake_bot_api import FakeBotApi
from passport.backend.core.builders.captcha.faker import FakeCaptcha
from passport.backend.core.builders.clean_web_api.faker.fake_clean_web_api import FakeCleanWebAPI
from passport.backend.core.builders.collections.faker.fake_collections_api import FakeCollectionsApi
from passport.backend.core.builders.datasync_api.faker.fake_disk_api import FakeDiskApi
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import FakePersonalityApi
from passport.backend.core.builders.federal_configs_api.faker import FakeFederalConfigsApi
from passport.backend.core.builders.frodo.faker import FakeFrodo
from passport.backend.core.builders.geosearch.faker import FakeGeoSearchApi
from passport.backend.core.builders.historydb_api.faker.historydb_api import FakeHistoryDBApi
from passport.backend.core.builders.kolmogor.faker import FakeKolmogor
from passport.backend.core.builders.mail_apis.faker import (
    FakeCollie,
    FakeFurita,
    FakeHuskyApi,
    FakeRPOP,
    FakeWMI,
)
from passport.backend.core.builders.market.faker.fake_market import FakeMarketContentApi
from passport.backend.core.builders.messenger_api.faker.fake_messenger_api import FakeMessengerAPI
from passport.backend.core.builders.music_api.faker import FakeMusicApi
from passport.backend.core.builders.oauth.faker import FakeOAuth
from passport.backend.core.builders.octopus.faker import FakeOctopus
from passport.backend.core.builders.perimeter_api.faker import FakePerimeterApi
from passport.backend.core.builders.phone_squatter.faker import FakePhoneSquatter
from passport.backend.core.builders.push_api.faker import FakePushApi
from passport.backend.core.builders.shakur.faker import FakeShakur
from passport.backend.core.builders.social_api.faker.social_api import FakeSocialApi
from passport.backend.core.builders.social_broker.faker.social_broker import FakeSocialBroker
from passport.backend.core.builders.staff.faker import FakeStaff
from passport.backend.core.builders.suggest.faker import FakeFioSuggest
from passport.backend.core.builders.tensornet.faker.tensornet import FakeTensorNet
from passport.backend.core.builders.trust_api.faker import FakeTrustPayments
from passport.backend.core.builders.ufo_api.faker import (
    FakeUfoApi,
    ufo_api_profile_response,
)
from passport.backend.core.builders.video.faker import FakeVideoSearchApi
from passport.backend.core.builders.yasms.faker import FakeYaSms
from passport.backend.core.builders.ysa_mirror.faker.ysa_mirror import FakeYsaMirrorAPI
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.grants.faker.grants import FakeGrants
from passport.backend.core.historydb.converter import (
    AuthChallengeEntryConverter,
    AuthEntryConverter,
    EventEntryConverter,
    RestoreEntryConverter,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.core.logbroker.faker.fake_logbroker import FakeLogbrokerWriterProto
from passport.backend.core.logging_utils.faker.fake_tskv_logger import (
    AccessLoggerFaker,
    AntifraudLoggerFaker,
    AvatarsLoggerFaker,
    CredentialsLoggerFaker,
    FamilyLoggerFaker,
    GraphiteLoggerFaker,
    PharmaLoggerFaker,
    PhoneLoggerFaker,
    SocialBindingLoggerFaker,
    StatboxLoggerFaker,
    YasmsPrivateLoggerFaker,
)
from passport.backend.core.mailer.faker import FakeMailer
from passport.backend.core.services import SERVICES
from passport.backend.core.suggest.faker import FakeLoginSuggester
from passport.backend.core.test.events import EventLoggerFaker
from passport.backend.core.test.fake_code_generator import CodeGeneratorFaker
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    check_statbox_log_entries,
    check_statbox_log_entry,
    iterdiff,
    PassportTestCase,
    pseudo_diff,
)
from passport.backend.core.test.xunistater.xunistater import XunistaterChecker
from passport.backend.core.tracks.faker import (
    FakeTrackIdGenerator,
    FakeTrackManager,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    FakeTvmTicketChecker,
    TEST_TICKET,
)
from passport.backend.core.types.login.faker.login import FakeLoginGenerator
from passport.backend.core.ydb.faker.ydb import FakeYdb
from passport.backend.utils.common import merge_dicts
from six.moves.urllib.parse import urlencode
import yatest.common as yc

from ..common.logbroker import ApiLogbrokerWriterProto
from .client import FlaskTestClient
from .mixins import EmailTestToolkit


log = logging.getLogger('tests.utils')


class BaseTestViews(PassportTestCase):

    def _get_log_field(self, field_name, log_type='event', log_msg=''):
        if log_type == 'event':
            converter_cls = EventEntryConverter
        elif log_type == 'restore':
            converter_cls = RestoreEntryConverter
        elif log_type == 'auth_challenge':
            converter_cls = AuthChallengeEntryConverter
        else:
            converter_cls = AuthEntryConverter

        for value, name in zip(re.findall(r'(`.*?`|[^ ]+)', log_msg), converter_cls.fields):
            if name == field_name:
                return value.strip('`')

    def get_events_from_handler(self, logger_handler_mock):
        log_entries = dict()
        for call_arg in logger_handler_mock.call_args_list:
            name1 = self._get_log_field('name', 'event', call_arg[0][0])
            value1 = self._get_log_field('value', 'event', call_arg[0][0])
            log_entries.update({name1: value1})
        return log_entries

    def assert_events_are_empty(self, logger_handler_mock):
        """Проверит что event-лог не использовался"""
        self.env.event_logger.assert_events_are_logged([])

    def assert_events_are_logged(self, logger_handler_mock, names_values):
        """Проверит что только эти event-записи передавались в логгер."""
        self.env.event_logger.assert_events_are_logged(names_values)

    def assert_events_are_logged_with_order(self, logger_handler_mock, names_values):
        """
        Проверит, что логгер вызывался со всеми переданными записями
        в указанном порядке.
        """
        self.env.event_logger.assert_events_are_logged_with_order(names_values)

    def assert_event_is_logged(self, logger, name, value):
        """
        Проверит что в логгер передавалась запись с указанным именем и значением.
        Без внимания к порядку передачи этой записи логгеру
        """
        self.env.event_logger.assert_event_is_logged(name, value)

    def check_auth_log_entry(self, logger, field, value, record_index=-1):
        """Проверит значение одного поля в одной(последней) записи в auth-логгере"""
        log_entry = logger.call_args_list[record_index][0][0]
        actual = self._get_log_field(field, log_type='auth', log_msg=log_entry)
        eq_(
            actual,
            value,
            'Auth log: for field "%s" expected "%s", but found "%s" in entry "%s"' % (
                field, value, actual, log_entry,
            ),
        )

    def check_auth_log_entries(self, logger, entries, record_index=-1):
        """Проверит значения нескольких полей в одной(последней) записи auth-логгера"""
        for name, value in entries:
            self.check_auth_log_entry(logger, name, value, record_index)

    def check_all_auth_log_records(self, logger, records):
        """
        Проверит всю последовательность записей auth-логгера на соответствие переданному списку
        :param logger - mock-auth-logger
        :param records - список списков, состоящих из кортежей (имя_поля, ожидаемое_значение)
        Например, для проверки двух последовальных записей в auth-логгере, можно передать:
        [
            [
                ('uid', '1'),
                ('track_id', 'asd'),
                ('type', 'web'),
                ('status', 'ses_update'),
            ],
            [
                ('uid', '1'),
                ('track_id', 'asd'),
                ('type', 'web'),
                ('status': 'safeses_sync'),
            ],
        ]
        """
        for record_index, record in enumerate(records):
            self.check_auth_log_entries(logger, record, record_index)

    def check_xml_output(self, actual_content, expected, root_attrs,
                         skip_elements=None, check_elements=None):
        root = fromstring(actual_content)
        eq_(len(expected.keys()), 1)

        eq_(root.tag, list(expected.keys())[0])
        eq_(root.attrib, root_attrs)

        skip_elements = skip_elements or []
        actual_result = dict((e.tag, e.text) for e in root if e.tag not in skip_elements)

        check_elements = check_elements or []
        for element in check_elements:
            actual_result.update({element: [(e.tag, e.text) for e in root.find(element)]})

        eq_(actual_result, expected[root.tag])

    def check_xml_list(self, actual_content, expected):
        """
        Функция проверки xml-документа
        Проверяет атрибуты элементов
        """
        root = fromstring(actual_content)
        eq_(len(expected.keys()), 1)
        eq_(root.tag, list(expected.keys())[0])

        actual_result = list((e.tag, e.text, e.attrib) for e in root)
        eq_(actual_result, expected[root.tag])

    def check_statbox_log_entries(self, logger_handler_mock, statbox_lines):
        check_statbox_log_entries(logger_handler_mock, statbox_lines)

    def check_statbox_log_entry(self, logger_handler_mock, statbox_line, entry_index=-1):
        check_statbox_log_entry(logger_handler_mock, statbox_line, entry_index)

    def track_transaction(self, track_id=None):
        if track_id is None:
            track_id = self.track_id
        track_manager = self.get_track_manager()
        return track_manager.transaction(track_id).rollback_on_error()

    def get_track_manager(self):
        return self.track_manager


class BaseBundleTestViews(BaseTestViews):
    """Функции для удобной проверки bundle-views"""

    consumer = None
    default_url = '/1/'
    http_method = 'get'
    http_query_args = {}
    http_headers = {}

    def make_request(self, url=None, method=None, query_args=None, exclude_args=None, headers=None,
                     exclude_headers=None, consumer=None, **kwargs):
        url = url or self.default_url
        method = method or self.http_method
        method = method.lower()

        headers = merge_dicts(self.http_headers or {}, headers or {})

        if exclude_headers:
            for key in exclude_headers:
                headers.pop(key)

        headers = mock_headers(**headers)

        query_args = merge_dicts(self.http_query_args or {}, query_args or {})

        if exclude_args and query_args:
            for key in exclude_args:
                query_args.pop(key)

        query_string = {}
        data = {}

        if method in ('get', 'delete'):
            query_string = query_args
        elif method in ('post', 'put'):
            data = query_args

        consumer = consumer or self.consumer
        if consumer:
            query_string['consumer'] = consumer

        return getattr(self.env.client, method)(
            url,
            query_string=query_string or None,
            data=data or None,
            headers=headers,
            **kwargs
        )

    def match_cookie_name(self, name, cookie):
        return re.match(r'^%s=([^;]*);.+$' % name, cookie)

    def assert_ok_response(self, response, check_all=True, ignore_order_for=None,
                           skip=None, **expected_response):
        expected_response['status'] = 'ok'
        eq_(response.status_code, 200)

        skip = skip or []
        expected_response = {k: v for k, v in expected_response.items() if k not in skip}

        actual_response = json.loads(response.data)
        actual_response = {k: v for k, v in actual_response.items() if k not in skip}

        for field in (ignore_order_for or []):
            if field in expected_response and field in actual_response:
                expected_response[field] = sorted(expected_response[field])
                actual_response[field] = sorted(actual_response[field])
        if not check_all:
            actual_response = {k: v for k, v in actual_response.items() if k in expected_response}
        eq_(
            actual_response,
            expected_response,
            pseudo_diff(expected_response, actual_response),
        )

    def assert_error_response(self, response, error_codes=None, status_code=200,
                              ignore_error_message=True, check_content=True, ignore_order_for=None, **kwargs):
        """Проверим код ответа и коды ошибок (без учета порядка)"""
        eq_(response.status_code, status_code)

        original_response = json.loads(response.data)
        if 'errors' in original_response:
            original_response['errors'] = sorted(original_response['errors'])
        if ignore_error_message:
            original_response.pop('error_message', None)

        base_response = {
            'status': 'error',
            'errors': sorted(error_codes or ['exception.unhandled']),
        }
        expected_response = merge_dicts(base_response, kwargs)

        if check_content:
            for field in (ignore_order_for or []):
                original_response[field] = sorted(original_response[field])
                expected_response[field] = sorted(expected_response[field])

            eq_(
                original_response,
                expected_response,
                pseudo_diff(expected_response, original_response),
            )
        else:
            eq_(original_response.get('status'), expected_response['status'])
            eq_(original_response.get('errors'), expected_response['errors'])

    def assert_error_response_with_track_id(self, response, error_codes=None, **kwargs):
        """Проверим код ответа и код ошибки, ожидаем track_id в теле"""
        self.assert_error_response(response, error_codes=error_codes, track_id=self.track_id, **kwargs)

    def assert_cookie_ok(self, cookie, name, value=None,
                         domain='.yandex.ru', expires='Tue, 19 Jan 2038 03:14:07 GMT', path='/',
                         http_only=None, secure=None):
        """Простой помощник для проверки атрибутов куки"""
        name_re_match = self.match_cookie_name(name, cookie)
        ok_(name_re_match, 'Cookie has unexpected name %s: %s' % (name, cookie))

        ok_('Domain=%s' % domain in cookie, 'Domain "%s" not in cookie "%s"' % (domain, cookie))
        ok_('Path=%s' % path in cookie, 'Path "%s" not in cookie "%s"' % (path, cookie))

        if expires is not None:
            ok_('Expires=%s' % expires in cookie, 'Expires "%s" not in cookie "%s"' % (expires, cookie))
        if http_only:
            ok_('HttpOnly' in cookie, 'HttpOnly attribute not in cookie "%s"' % cookie)
        if secure:
            ok_('Secure' in cookie, 'Secure attribute not in cookie "%s"' % cookie)

        if value:
            value_re_match = name_re_match.groups()[0]
            ok_(value_re_match, 'Cookie %s has an empty value: %s' % (name, cookie))
            ok_(value in cookie, [value, cookie])


class ViewsTestEnvironment(object):

    TEST_UID = 1
    TEST_PDD_UID = 1130000000000001

    def __init__(self, mock_redis=False):
        # создаем тестовый клиент
        app = create_app()
        app.test_client_class = FlaskTestClient
        app.testing = True
        self.client = app.test_client()

        self.afisha_api = FakeAfishaApi()
        self.antifraud_api = FakeAntifraudAPI()
        self.avatars_mds_api = FakeAvatarsMdsApi()
        self.bbro_api = FakeBBroApi()
        self.bilet_api = FakeBiletApi()
        self.blackbox = FakeBlackbox()
        self.bot_api = FakeBotApi()
        self.captcha_mock = FakeCaptcha()
        self.clean_web_api = FakeCleanWebAPI()
        self.code_generator = CodeGeneratorFaker()
        self.collections_api = FakeCollectionsApi()
        self.collie = FakeCollie()
        self.db = FakeDB()
        self.disk_api = FakeDiskApi()
        self.event_logger = EventLoggerFaker()
        self.federal_configs_api = FakeFederalConfigsApi()
        self.fio_suggest = FakeFioSuggest()
        self.frodo = FakeFrodo()
        self.furita = FakeFurita()
        self.grants = FakeGrants()
        self.geosearch_api = FakeGeoSearchApi()
        self.husky_api = FakeHuskyApi()
        self.historydb_api = FakeHistoryDBApi()
        self.fake_ydb = FakeYdb()
        self.fake_ydb.set_execute_return_value([])
        self.kolmogor = FakeKolmogor()
        self.login_generator = FakeLoginGenerator()
        self.login_suggester = FakeLoginSuggester()
        self.mailer = FakeMailer()
        self.market_content_api = FakeMarketContentApi()
        self.messenger_api = FakeMessengerAPI()
        self.music_api = FakeMusicApi()
        self.oauth = FakeOAuth()
        self.octopus = FakeOctopus()
        self.perimeter_api = FakePerimeterApi()
        self.personality_api = FakePersonalityApi()
        self.phone_squatter = FakePhoneSquatter()
        self.push_api = FakePushApi()
        self.rpop = FakeRPOP()
        self.shakur = FakeShakur()
        self.social_api = FakeSocialApi()
        self.social_broker = FakeSocialBroker()
        self.staff = FakeStaff()
        self.tensornet = FakeTensorNet()
        self.trust_payments = FakeTrustPayments()
        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.tvm_ticket_checker = FakeTvmTicketChecker()
        self.ufo_api = FakeUfoApi()
        self.video_search_api = FakeVideoSearchApi()
        self.wmi = FakeWMI()
        self.yasms = FakeYaSms()
        self.ysa_mirror = FakeYsaMirrorAPI()

        self.yasms_fake_global_sms_id_mock = mock.Mock()
        self.yasms_fake_global_sms_id_mock.return_value = 'fake-01234567890123456789012345678901'
        self.yasms_fake_global_sms_id_patch = mock.patch(
            'passport.backend.api.common.yasms._generate_fake_global_sms_id',
            self.yasms_fake_global_sms_id_mock,
        )

        self.email_toolkit = EmailTestToolkit(self.mailer)

        fake_lbw = partial(FakeLogbrokerWriterProto, ApiLogbrokerWriterProto)
        self.lbw_challenge_pushes = fake_lbw('challenge_pushes')
        self.lbw_takeout_tasks = fake_lbw('takeout_tasks')

        # mock-аем логгеры
        self.statbox_logger = StatboxLoggerFaker()
        self.statbox = self.statbox_logger
        self.phone_logger = PhoneLoggerFaker()
        self.graphite_logger = GraphiteLoggerFaker()
        self.access_logger = AccessLoggerFaker()
        self.family_logger = FamilyLoggerFaker()
        self.avatars_logger = AvatarsLoggerFaker()
        self.pharma_logger = PharmaLoggerFaker()
        self.antifraud_logger = AntifraudLoggerFaker()
        self.social_binding_logger = SocialBindingLoggerFaker()
        self.yasms_private_logger = YasmsPrivateLoggerFaker()
        self.credentials_logger = CredentialsLoggerFaker()

        self.xunistater_checker = XunistaterChecker(
            cs_id2parser_id_map={
                'challenges_shown': 'statbox.log',
                'challenges_skipped': 'statbox.log',
                'challenges_passed_or_failed': 'statbox.log',
                'drive_auth.start.rps': 'statbox.log',
                'drive_auth.build_nonce.rps': 'statbox.log',
                'drive_auth.stop.rps': 'statbox.log',
                'drive_auth.issue_authorization_code.rps': 'statbox.log',
                'drive_auth.check_nonce.rps': 'statbox.log',
                'auth_social.rps': 'statbox.log',
                'auth_password.rps': 'statbox.log',
                'auth_2fa.rps': 'statbox.log',
                'auth_magic.rps': 'statbox.log',
                'ufo_status.rps': 'statbox.log',
                'ufo_failed.rps': 'statbox.log',
                'is_challenge_required.web.rps': 'statbox.log',
                'is_challenge_required.mobile.rps': 'statbox.log',
                'af_fallback.decision.rps': 'statbox.log',
                'af_fallback.disabled.rps': 'statbox.log',

                'builder.rps': 'graphite.log',
                'builder.http_code.rps': 'graphite.log',
                'builder.success.rps': 'graphite.log',
                'builder.failed.rps': 'graphite.log',
                'builder.timeout.rps': 'graphite.log',
            },
            config_path=yc.source_path() + '/passport/backend/api/deb/xunistater/etc/yandex/passport-xunistater/passport-python-api.conf',
        )

        # Чтобы не переписывать сотни тестов, уже завязанных на это имя.
        self.statbox_handle_mock = self.statbox_logger.write_handler_mock

        # mock-аем и патчим логи historydb
        self.handle_mock = self.event_logger._handler

        self.auth_handle_mock = mock.Mock()
        self._auth_logger = mock.Mock()
        self._auth_logger.debug = self.auth_handle_mock

        self.auth_challenge_handle_mock = mock.Mock()
        self._auth_challenge_logger = mock.Mock()
        self._auth_challenge_logger.debug = self.auth_challenge_handle_mock

        # остановка времени для счётчиков, для избежания ситуаций, когда в тестах
        # счётчик прогрет в одном временном бакете, а проверка счётчиков происходит в другом
        self._counters_time_freeze_mock = mock.Mock(
            time=mock.Mock(return_value=time.time()),
        )
        self._counters_time_freeze_patch = mock.patch(
            'passport.backend.core.counters.buckets.time',
            self._counters_time_freeze_mock,
        )

        self.request_id = mock.Mock(name='get_request_id', return_value='request_id')

        self.patches = [
            mock.patch('passport.backend.api.common.authorization.auth_log', self._auth_logger),
            mock.patch('passport.backend.api.common.auth_challenge.auth_challenge_log', self._auth_challenge_logger),
            mock.patch('passport.backend.core.logging_utils.request_id.RequestIdManager.get_request_id', self.request_id),
            self._counters_time_freeze_patch,
            self.access_logger,
            self.afisha_api,
            self.antifraud_api,
            self.antifraud_logger,
            self.avatars_mds_api,
            self.bbro_api,
            self.bilet_api,
            self.blackbox,
            self.bot_api,
            self.captcha_mock,
            self.clean_web_api,
            self.code_generator,
            self.collections_api,
            self.collie,
            self.credentials_logger,
            self.db,
            self.disk_api,
            self.event_logger,
            self.federal_configs_api,
            self.fio_suggest,
            self.frodo,
            self.furita,
            self.geosearch_api,
            self.grants,
            self.graphite_logger,
            self.husky_api,
            self.historydb_api,
            self.fake_ydb,
            self.kolmogor,
            self.login_generator,
            self.login_suggester,
            self.lbw_challenge_pushes,
            self.lbw_takeout_tasks,
            self.mailer,
            self.market_content_api,
            self.messenger_api,
            self.family_logger,
            self.music_api,
            self.oauth,
            self.octopus,
            self.perimeter_api,
            self.personality_api,
            self.pharma_logger,
            self.phone_logger,
            self.phone_squatter,
            self.push_api,
            self.rpop,
            self.shakur,
            self.social_api,
            self.social_binding_logger,
            self.social_broker,
            self.staff,
            self.statbox_logger,
            self.tensornet,
            self.trust_payments,
            self.tvm_credentials_manager,
            self.tvm_ticket_checker,
            self.ufo_api,
            self.avatars_logger,
            self.video_search_api,
            self.wmi,
            self.yasms,
            self.ysa_mirror,
            self.yasms_fake_global_sms_id_patch,
            self.yasms_private_logger,
        ]

        if mock_redis:
            self.patches.append(
                mock.patch(
                    'passport.backend.core.redis_manager.redis_manager._redises',
                    defaultdict(mock.Mock),
                ),
            )
        else:
            self.track_manager = FakeTrackManager()
            self.patches.append(self.track_manager)

        LazyLoader.flush()

    def start(self):
        for patch in self.patches:
            patch.start()
        SERVICES['dev'].sid = 100400
        self.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(),
            ),
        )
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(i): {
                        'alias': alias,
                        'ticket': TEST_TICKET,
                    }
                    for i, alias in enumerate([
                        'antifraud_api',
                        'blackbox',
                        'collie',
                        'drive_api',
                        'federal_configs_api',
                        'historydb_api',
                        'husky',
                        'logbroker_api',
                        'messenger_api',
                        'oauth',
                        'phone_squatter',
                        'push_api',
                        'social_api',
                        'social_broker',
                        'trust_binding_api',
                        'trust_payment_api',
                        'wmi_api',
                        'yasms',
                    ], start=1)
                },
            ),
        )

    def stop(self):
        for patch in reversed(self.patches):
            patch.stop()
        SERVICES['dev'].sid = ''
        for attr in list(self.__dict__.keys()):
            self.__delattr__(attr)


class BaseMdapiTestCase(BaseTestViews):
    TEST_IP = '3.3.3.3'
    TEST_USER_AGENT = 'curl'
    TEST_ACCEPT_LANGUAGE = 'ru'
    TEST_HOST = 'passport-test.yandex.ru'

    TEST_COOKIE_TIMESTAMP = 1383144488
    TEST_COOKIE_L = ('VFUrAHh8fkhQfHhXW117aH4GB2F6UlZxWmUHQmEBdxwEHhZBDyYxVUYCIxEcJEYfFTpdBF9dGRMuJHU4HwdSNQ=='
                     '.%s.1002323.298169.6af3100a8920a270bd9a933bbcd48181') % TEST_COOKIE_TIMESTAMP
    TEST_YANDEXUID_COOKIE = 'yandexuid'
    TEST_YANDEX_GID_COOKIE = 'yandex_gid'
    TEST_FUID01_COOKIE = 'fuid'
    TEST_COOKIE_MY = 'YycCAAYA'
    TEST_SESSIONID = '0:old-session'
    TEST_SSL_SESSIONID = '0:old-sslsession'

    TEST_USER_COOKIES = 'Session_id=%s; Session_id2=%s; yandexuid=%s; yandex_gid=%s; fuid01=%s; my=%s; L=%s;' % (
        TEST_SESSIONID, TEST_SSL_SESSIONID, TEST_YANDEXUID_COOKIE, TEST_YANDEX_GID_COOKIE, TEST_FUID01_COOKIE,
        TEST_COOKIE_MY, TEST_COOKIE_L,
    )

    test_data = {
        'host': TEST_HOST,
        'user_ip': TEST_IP,
        'cookie': TEST_USER_COOKIES,
        'user_agent': TEST_USER_AGENT,
        'accept_language': TEST_ACCEPT_LANGUAGE,
    }
    url = None
    mocked_grants = None
    method = None

    def build_headers(self):
        return mock_headers(
            host=self.test_data['host'],
            user_ip=self.test_data['user_ip'],
            cookie=self.test_data['cookie'],
            user_agent=self.test_data['user_agent'],
            accept_language=self.test_data['accept_language'],
        )

    def make_request(self, headers=None, data=None, method=None):
        req_kwargs = {}
        method = method or self.method
        method_map = {
            'POST': self.env.client.post,
            'GET': self.env.client.get,
            'DELETE': self.env.client.delete,
            'PUT': self.env.client.put,
        }

        if not method:
            method = 'POST'

        if method not in method_map:
            raise ValueError('Unknown HTTP method')  # pragma: no cover
        request_method = method_map[method]

        if headers is None:
            headers = self.build_headers()
        if headers:
            req_kwargs['headers'] = headers
        if data:
            if method == 'GET':
                self.url = '%s?%s' % (self.url, urlencode(data))
            else:
                req_kwargs['data'] = data

        return request_method(
            self.url,
            **req_kwargs
        )

    def setUp(self):
        super(BaseMdapiTestCase, self).setUp()
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager = self.env.track_manager.get_manager()

        if isinstance(self.mocked_grants, dict):
            self.env.grants.set_grants_return_value(
                mock_grants(grants=self.mocked_grants),
            )
        elif isinstance(self.mocked_grants, list):
            self.env.grants.set_grant_list(self.mocked_grants)

        self.patches = []

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.patches
        del self.track_manager
        super(BaseMdapiTestCase, self).tearDown()

    def setup_trackid_generator(self, track_type='authorize'):
        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(track_type)
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)
        self.patches.append(self.track_id_generator)

    def check_response_ok(self, response):
        response_data = json.loads(response.data)
        eq_(response_data['status'], 'ok')
        return response_data

    def check_error_response(self, response, errors):
        response_data = json.loads(response.data)
        eq_(response_data['status'], 'error')
        iterdiff(eq_)(sorted(response_data['errors']), sorted(errors))
        return response_data

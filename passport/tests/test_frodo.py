# -*- coding: utf-8 -*-

import datetime
import time
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_userinfo_response,
    FakeBlackbox,
    get_parsed_blackbox_response,
)
from passport.backend.core.builders.frodo import (
    Frodo,
    FrodoInfo,
)
from passport.backend.core.builders.frodo.exceptions import FrodoError
from passport.backend.core.builders.frodo.faker import FakeFrodo
from passport.backend.core.builders.frodo.service import User
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.differ import diff
from passport.backend.core.frodo.frodo import (
    check_spammer,
    FrodoStatus,
    generate_karma,
    get_account,
    KARMA_TIME,
    process_user_karma,
    update_karma,
)
from passport.backend.core.logging_utils.faker.fake_tskv_logger import StatboxLoggerFaker
from passport.backend.core.models.account import (
    Account,
    UnknownUid,
)
from passport.backend.core.processor import run_eav
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.test.test_utils.mock_objects import mock_env
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.utils.time import datetime_to_unixtime


RESPONSE_SPAM_USER = '''
    <spamlist>
        <spam_user login="alpha" weight="85" />
        <spam_user login="beta" weight="85" />
        <spam_user login="gamma" weight="85" />
        <spam_user login="delta" weight="75" />
    </spamlist>
'''


@with_settings_hosts(
    FRODO_URL='http://localhost/',
    FRODO_RETRIES=3,
    BLACKBOX_URL='http://localhost/',
    BLACKBOX_ATTRIBUTES=[],
)
class BaseFrodoTestCase(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()
        self.blackbox = blackbox.Blackbox()

    def tearDown(self):
        self.fake_blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_blackbox
        del self.fake_tvm_credentials_manager


class ProcessUserKarmaTestCase(BaseFrodoTestCase):
    def setUp(self):
        super(ProcessUserKarmaTestCase, self).setUp()
        self.db = FakeDB()
        self.db.start()
        self.env = mock.Mock()
        self.env.user_agent = 'firefox'
        self.env.cookies = {'yandexuid': 'yandexuid'}
        self.statbox_logger = StatboxLoggerFaker()
        self.statbox_logger.start()

    def tearDown(self):
        self.db.stop()
        self.statbox_logger.stop()
        del self.db
        del self.statbox_logger
        del self.env
        super(ProcessUserKarmaTestCase, self).tearDown()

    def set_blackbox_user_response(self, karma, login='u1', uid=1):
        response = blackbox_userinfo_response(uid=uid, karma=karma, login=login)
        self.fake_blackbox.set_blackbox_response_value('userinfo', response)
        self.db.serialize(response)

    def test_with_account_get_from_blackbox_for_changepass(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=2, karma=60, login='u2'),
        )
        account = Account().parse(response)

        self.set_blackbox_user_response(60)

        user = User(login='u1', karma=85, is_pdd=False, spam=False, change_pass=True)

        uid, fs = process_user_karma(user, self.env, 'dev', account)

        eq_(self.fake_blackbox._mock.request.call_count, 1)

        eq_(self.db.query_count('passportdbcentral'), 0)
        eq_(self.db.query_count('passportdbshard1'), 1)
        self.db.check('attributes', 'karma.value', '7060', uid=1, db='passportdbshard1')
        self.db.check_missing('attributes', 'karma.activation_datetime', uid=1, db='passportdbshard1')

        eq_(uid, 1)
        ok_(fs.is_karma_prefix_returned)
        ok_(not fs.is_karma_suffix_returned)

    def test_with_registrated_account_for_spam_user(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=1, karma=60, login='u1'),
        )
        account = Account().parse(response)

        run_eav(None, account, diff(None, account))

        self.db.check('attributes', 'karma.value', '60', uid=1, db='passportdbshard1')
        self.db.check_missing('attributes', 'karma.activation_datetime', uid=1, db='passportdbshard1')
        self.db.reset_mocks()

        karma_time_min = int(time.time() + KARMA_TIME)
        user = User(login='u1', karma=75, is_pdd=False, spam=True, change_pass=False)

        uid, fs = process_user_karma(user, self.env, 'dev', account)

        eq_(self.fake_blackbox._mock.request.call_count, 0)

        eq_(self.db.query_count('passportdbcentral'), 0)
        eq_(self.db.query_count('passportdbshard1'), 1)
        self.db.check('attributes', 'karma.value', '75', uid=1, db='passportdbshard1')

        actual_time = int(self.db.get('attributes', 'karma.activation_datetime', uid=1, db='passportdbshard1'))
        ok_(actual_time > karma_time_min)
        ok_(actual_time < karma_time_min + 601)

        self.db.check('attributes', 'karma.activation_datetime', str(actual_time), uid=1, db='passportdbshard1')

        eq_(uid, 1)
        ok_(fs.is_karma_prefix_returned)
        ok_(fs.is_karma_suffix_returned)

    def test_process_user_karma_zero_karma(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=2, karma=60, login='u1'),
        )
        account = Account().parse(response)

        self.set_blackbox_user_response(0)

        user = User(login='u2', karma=0, is_pdd=False, spam=True, change_pass=True)

        uid, fs = process_user_karma(user, self.env, 'dev', account)

        eq_(self.fake_blackbox._mock.request.call_count, 1)

        eq_(self.db.query_count('passportdbshard1'), 0)

        eq_(uid, 1)
        ok_(fs.is_karma_prefix_returned)
        ok_(fs.is_karma_suffix_returned)

    def test_process_user__new_user__log_to_statbox_and_historydb(self):
        """
        При выставлении кармы пользователям после регистрации, записываем правильное событие в statbox & historydb
        """
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=1, karma=50, login='u1'),
        )
        account = Account().parse(response)
        user = User(login='u1', karma=0, is_pdd=False, spam=True, change_pass=True)

        run_eav(None, account, diff(None, account))
        self.db.reset_mocks('passportdbshard1')

        self.db.check('attributes', 'karma.value', '50', uid=1, db='passportdbshard1')

        historydb_logger, historydb_handler = mock.Mock(), mock.Mock()
        historydb_logger.debug = historydb_handler

        with mock.patch('passport.backend.core.serializers.logs.historydb.runner.event_log', historydb_logger):
            uid, fs = process_user_karma(user, self.env, 'dev', account)

            eq_(self.statbox_logger.write_handler_mock.call_count, 1)
            log_entry = self.statbox_logger.write_handler_mock.call_args[0][0]
            ok_('action=karma' in log_entry)
            eq_(historydb_handler.call_count, 5)
            log_entry = historydb_handler.call_args_list[2][0][0]
            ok_('action karma' in log_entry)

            eq_(uid, 1)
            ok_(fs.is_karma_prefix_returned)
            ok_(fs.is_karma_suffix_returned)

        # Не происходило вызова ЧЯ для получения информации об аккаунте
        eq_(self.fake_blackbox._mock.request.call_count, 0)

    def test_process_user__postpone_karma_update__log_event_to_statbox_and_historydb(self):
        """При обновлении кармы пользователям "задним числом", записываем в statbox & historydb правильное событие"""
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=1, karma=60, login='u1'),
        )
        account = Account().parse(response)
        other_user = User(login='u2', karma=0, is_pdd=False, spam=True, change_pass=True)
        self.set_blackbox_user_response(50, login='u2', uid=2)

        run_eav(None, account, diff(None, account))
        self.db.reset_mocks('passportdbshard1')

        self.db.check('attributes', 'karma.value', '60', uid=1, db='passportdbshard1')

        historydb_logger, historydb_handler = mock.Mock(), mock.Mock()
        historydb_logger.debug = historydb_handler

        with mock.patch('passport.backend.core.serializers.logs.historydb.runner.event_log', historydb_logger):
            uid, fs = process_user_karma(other_user, self.env, 'dev', account)

            eq_(self.statbox_logger.write_handler_mock.call_count, 1)
            log_entry = self.statbox_logger.write_handler_mock.call_args[0][0]
            ok_('action=pending_karma_update' in log_entry)
            eq_(historydb_handler.call_count, 5)
            log_entry = historydb_handler.call_args_list[2][0][0]
            ok_('action pending_karma_update' in log_entry)

            eq_(uid, 2)
            ok_(fs.is_karma_prefix_returned)
            ok_(fs.is_karma_suffix_returned)

        eq_(self.fake_blackbox._mock.request.call_count, 1)


class GetAccountByUserTestCase(BaseFrodoTestCase):
    def setUp(self):
        super(GetAccountByUserTestCase, self).setUp()
        self.env = mock.Mock()
        self.env.user_agent = 'firefox'
        self.env.cookies = {'yandexuid': 'yandexuid'}

    def tearDown(self):
        del self.env
        super(GetAccountByUserTestCase, self).tearDown()

    def test_pdd_account(self):
        blackbox_response = blackbox_userinfo_response(uid=1130000000000001, karma=60, login='u1@ya.ru')
        self.fake_blackbox.set_blackbox_response_value('userinfo', blackbox_response)

        account = get_account(
            User(login='u1@ya.ru', karma=31, is_pdd=True, spam=False, change_pass=True),
        )
        eq_(self.fake_blackbox._mock.request.call_count, 1)
        eq_(account.uid, 1130000000000001)
        eq_(account.login, 'u1@ya.ru')
        eq_(account.karma.value, 60)


class GenerateKarmaTestCase(BaseFrodoTestCase):
    def test_user_karma_for_spam_user(self):
        karma_prefix, karma_suffix, activation_datetime = generate_karma(
            User(login='u1', karma=75, is_pdd=False, spam=True, change_pass=False),
        )

        eq_(karma_prefix, 0)
        eq_(karma_suffix, 75)

    def test_activation_datetime_for_spam_user(self):
        karma_time_min = int(time.time() + KARMA_TIME)

        karma_prefix, karma_suffix, activation_datetime = generate_karma(
            User(login='u1', karma=85, is_pdd=False, spam=True, change_pass=False),
        )
        eq_(karma_prefix, 0)
        eq_(karma_suffix, 85)
        activation_datetime = datetime_to_unixtime(activation_datetime)
        ok_(activation_datetime >= karma_time_min)
        ok_(activation_datetime < karma_time_min + 601)

    def test_zero_karma_for_spam_user(self):
        karma_prefix, karma_suffix, activation_datetime = generate_karma(
            User(login='u1', karma=0, is_pdd=False, spam=True, change_pass=False),
        )
        eq_(karma_prefix, 0)
        eq_(karma_suffix, 0)
        eq_(activation_datetime, None)

    def test_karma_for_changepass_1(self):
        karma_prefix, karma_suffix, activation_datetime = generate_karma(
            User(login='u1', karma=85, is_pdd=False, spam=False, change_pass=True),
        )
        eq_(karma_prefix, 7)
        eq_(karma_suffix, None)
        eq_(activation_datetime, None)

    def test_karma_for_changepass_2(self):
        karma_prefix, karma_suffix, activation_datetime = generate_karma(
            User(login='u1@ya.ru', karma=31, is_pdd=True, spam=False, change_pass=True),
        )
        eq_(karma_prefix, 8)
        eq_(karma_suffix, None)
        eq_(activation_datetime, None)


class UpdateKarmaTestCase(BaseFrodoTestCase):
    def setUp(self):
        super(UpdateKarmaTestCase, self).setUp()
        self.db = FakeDB()
        self.db.start()
        self.env = mock.Mock()
        self.statbox_logger = StatboxLoggerFaker()
        self.statbox_logger.start()
        self.env.user_agent = 'firefox'
        self.env.cookies = {'yandexuid': 'yandexuid'}

    def tearDown(self):
        self.statbox_logger.stop()
        self.db.stop()
        del self.statbox_logger
        del self.db
        del self.env
        super(UpdateKarmaTestCase, self).tearDown()

    def test_karma_prefix_suffix_activation_datetime_and_historydb_log(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=1, login='u1'),
        )
        account = Account().parse(response)
        run_eav(None, account, diff(None, account))

        self.db.check_missing('attributes', 'karma.value', uid=1, db='passportdbshard1')
        self.db.check_missing('attributes', 'karma.activation_datetime', uid=1, db='passportdbshard1')
        self.db.reset_mocks()

        karma_prefix = 1
        karma_suffix = 75
        activation_datetime = datetime.datetime.now()

        historydb_handler, historydb_logger = mock.Mock(), mock.Mock()
        historydb_logger.debug = historydb_handler

        with mock.patch(
            'passport.backend.core.serializers.logs.historydb.runner.event_log',
            historydb_logger,
        ):
            account = update_karma(
                account,
                karma_prefix,
                karma_suffix,
                activation_datetime,
                self.env,
                'dev',
                action='test_action',
            )

            timenow = TimeNow()
            eq_(self.db.query_count('passportdbcentral'), 0)
            eq_(self.db.query_count('passportdbshard1'), 1)
            self.db.check('attributes', 'karma.value', '1075', uid=1, db='passportdbshard1')
            self.db.check('attributes', 'karma.activation_datetime', timenow, uid=1, db='passportdbshard1')

            # проверяем хистори дб лог
            eq_(historydb_handler.call_count, 7)

            def extract_arg(i):
                return historydb_handler.call_args_list[i][0][0]
            ok_('info.karma_prefix 1' in extract_arg(0))
            ok_('info.karma_full 1075' in extract_arg(1))
            ok_('info.karma 75' in extract_arg(2))
            ok_('info.karma_full 1075' in extract_arg(3))
            ok_('action test_action' in extract_arg(4))
            ok_('consumer dev' in extract_arg(5))

            eq_(self.statbox_logger.write_handler_mock.call_count, 1)
            log_entry = self.statbox_logger.write_handler_mock.call_args[0][0]
            ok_('destination=frodo' in log_entry)
            ok_('consumer=dev' in log_entry)
            ok_('uid=1' in log_entry)
            ok_('action=test_action' in log_entry)


class CheckSpamerTestCase(BaseFrodoTestCase):
    def setUp(self):
        super(CheckSpamerTestCase, self).setUp()
        self.statbox_logger = StatboxLoggerFaker()
        self.statbox_logger.start()

        self.fake_frodo = FakeFrodo()
        self.fake_frodo.start()
        self.frodo = Frodo()

        self._process_user_karma = mock.Mock(name='process_user_karma')
        self._process_user_karma_patch = mock.patch(
            'passport.backend.core.frodo.frodo.process_user_karma',
            self._process_user_karma,
        )
        self._process_user_karma_patch.start()

        self.env = mock_env(
            cookies={'fuid01': 'fuid111', 'yandexuid': 'test_uid'},
            user_agent='ua',
            host='h',
        )
        self.args = {
            'login': 'u1',
            'action': 'test',
        }
        self.consumer = 'dev'

        self.frodo_info = FrodoInfo.create(self.env, self.args)
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=1, karma=60, login='u1'),
        )
        self.account = Account().parse(response)

    def tearDown(self):
        self._process_user_karma_patch.stop()
        self.fake_frodo.stop()
        self.statbox_logger.stop()
        del self.fake_frodo
        del self.statbox_logger
        del self._process_user_karma
        del self._process_user_karma_patch
        del self.env
        del self.frodo_info
        super(CheckSpamerTestCase, self).tearDown()

    def test_check_spammer_for_spam_user(self):
        user = User(login='u1', karma=75, is_pdd=False, spam=True, change_pass=False)
        with mock.patch.object(
            Frodo,
            'check',
        ) as check_mock, mock.patch.object(
            Frodo,
            'confirm',
        ) as confirm_mock:
            check_mock.return_value = [user]
            self._process_user_karma.return_value = (
                self.account.uid,
                FrodoStatus(
                    is_karma_prefix_returned=True,
                    is_karma_suffix_returned=True,
                ),
            )
            account, fs = check_spammer(self.frodo_info, self.env, self.consumer, self.account)
            self._process_user_karma.assert_called_once_with(
                user,
                self.env,
                'dev',
                self.account,
                action_to_log='test',
            )
            eq_(check_mock.call_count, 1)
            confirm_mock.assert_called_once_with({'u1': '75'})

            eq_(account.uid, self.account.uid)
            ok_(fs.is_karma_prefix_returned)
            ok_(fs.is_karma_suffix_returned)

    def test_check_spammer_for_change_pass_user(self):
        response = get_parsed_blackbox_response(
            'userinfo',
            blackbox_userinfo_response(uid=1, karma=60, login='zxfzxf2'),
        )
        account = Account().parse(response)
        user = User(login='zxfzxf2', karma=85, is_pdd=False, spam=False, change_pass=True)
        with mock.patch.object(
            Frodo,
            'check',
        ) as check_mock, mock.patch.object(
            Frodo,
            'confirm',
        ) as confirm_mock:
            check_mock.return_value = [user]
            self._process_user_karma.return_value = (
                self.account.uid,
                FrodoStatus(
                    is_karma_prefix_returned=True,
                    is_karma_suffix_returned=False,
                ),
            )
            account, fs = check_spammer(self.frodo_info, self.env, self.consumer, account)
            self._process_user_karma.assert_called_once_with(
                user,
                self.env,
                'dev',
                account,
                action_to_log='test',
            )
            eq_(check_mock.call_count, 1)
            confirm_mock.assert_called_once_with({'zxfzxf2': '85-'})

            eq_(account.uid, self.account.uid)
            ok_(fs.is_karma_prefix_returned)
            ok_(not fs.is_karma_suffix_returned)

    def test_check_spammer_zero_karma(self):
        user = User(login='u1', karma=0, is_pdd=False, spam=True, change_pass=False)
        with mock.patch.object(
            Frodo,
            'check',
        ) as check_mock, mock.patch.object(
            Frodo,
            'confirm',
        ) as confirm_mock:
            check_mock.return_value = [user]
            self._process_user_karma.return_value = (
                self.account.uid,
                FrodoStatus(
                    is_karma_prefix_returned=True,
                    is_karma_suffix_returned=True,
                ),
            )
            account, fs = check_spammer(self.frodo_info, self.env, self.consumer, self.account)
            self._process_user_karma.assert_called_once_with(
                user, self.env,
                'dev',
                self.account,
                action_to_log='test',
            )
            eq_(check_mock.call_count, 1)
            confirm_mock.assert_called_once_with({'u1': '0'})

            eq_(account.uid, self.account.uid)
            ok_(fs.is_karma_prefix_returned)
            ok_(fs.is_karma_suffix_returned)

    def test_check_spammer_frodo_returns_no_users(self):
        with mock.patch.object(
            Frodo,
            'check',
        ) as check_mock, mock.patch.object(
            Frodo,
            'confirm',
        ) as confirm_mock:
            check_mock.return_value = []
            account, fs = check_spammer(self.frodo_info, self.env, self.consumer, self.account)
            eq_(self._process_user_karma.call_count, 0)
            eq_(check_mock.call_count, 1)
            eq_(confirm_mock.call_count, 0)

            eq_(account.uid, self.account.uid)
            ok_(not fs.is_karma_prefix_returned)
            ok_(not fs.is_karma_suffix_returned)

    def test_check_spammer_error_in_frodo(self):
        self.fake_frodo.set_response_side_effect('check', FrodoError())

        account, fs = check_spammer(self.frodo_info, self.env, self.consumer, self.account, frodo=self.frodo)
        eq_(self._process_user_karma.call_count, 0)

        eq_(account.uid, self.account.uid)
        ok_(not fs.is_karma_prefix_returned)
        ok_(not fs.is_karma_suffix_returned)

        self.fake_frodo.set_response_side_effect('check', Exception())
        with assert_raises(Exception):
            check_spammer(self.frodo_info, self.env, self.consumer, self.account, frodo=self.frodo)

            eq_(account.uid, self.account.uid)
            ok_(not fs.is_karma_prefix_returned)
            ok_(not fs.is_karma_suffix_returned)

    def test_check_spammer_dberror_in_process_user_karma(self):
        self.fake_frodo.set_response_value('check', RESPONSE_SPAM_USER)
        self._process_user_karma.side_effect = DBError

        account, fs = check_spammer(self.frodo_info, self.env, self.consumer, self.account, frodo=self.frodo)

        eq_(self._process_user_karma.call_count, 4)
        eq_(account.uid, self.account.uid)
        ok_(not fs.is_karma_prefix_returned)
        ok_(not fs.is_karma_suffix_returned)
        requests = self.fake_frodo.requests
        eq_(len(requests), 1)
        requests[0].assert_url_starts_with('http://localhost/check?')

        eq_(self.statbox_logger.write_handler_mock.call_count, 0)

    def test_check_spammer_blackbox_error_in_process_user_karma(self):
        self.fake_frodo.set_response_value('check', RESPONSE_SPAM_USER)
        self._process_user_karma.side_effect = blackbox.BaseBlackboxError

        account, fs = check_spammer(self.frodo_info, self.env, self.consumer, self.account, frodo=self.frodo)

        requests = self.fake_frodo.requests
        eq_(len(requests), 1)
        requests[0].assert_url_starts_with('http://localhost/check?')
        eq_(self._process_user_karma.call_count, 4)
        eq_(account.uid, self.account.uid)
        ok_(not fs.is_karma_prefix_returned)
        ok_(not fs.is_karma_suffix_returned)

        eq_(self.statbox_logger.write_handler_mock.call_count, 0)

    def test_check_spammer_unknownid_error_in_process_user_karma(self):
        self.fake_frodo.set_response_value('check', RESPONSE_SPAM_USER)
        self.fake_frodo.set_response_value('confirm', '')
        self._process_user_karma.side_effect = UnknownUid

        account, fs = check_spammer(self.frodo_info, self.env, self.consumer, self.account, frodo=self.frodo)

        requests = self.fake_frodo.requests
        eq_(len(requests), 2)

        requests[0].assert_url_starts_with('http://localhost/check?')
        eq_(self._process_user_karma.call_count, 4)
        eq_(account.uid, self.account.uid)
        ok_(not fs.is_karma_prefix_returned)
        ok_(not fs.is_karma_suffix_returned)

        requests[1].assert_url_starts_with('http://localhost/loginrcpt?')
        requests[1].assert_query_equals({'alpha': '85', 'beta': '85', 'gamma': '85', 'delta': '75'})

        eq_(self.statbox_logger.write_handler_mock.call_count, 0)

    def test_check_spammer_error_in_process_user_karma(self):
        self.fake_frodo.set_response_value('check', RESPONSE_SPAM_USER)
        self._process_user_karma.side_effect = Exception
        with assert_raises(Exception):
            check_spammer(self.frodo_info, self.env, self.consumer, self.account, frodo=self.frodo)
        eq_(self._process_user_karma.call_count, 4)

        requests = self.fake_frodo.requests
        eq_(len(requests), 2)
        requests[0].assert_url_starts_with('http://localhost/check?')
        requests[1].assert_url_starts_with('http://localhost/loginrcpt?')
        requests[1].assert_query_equals({'alpha': '85', 'beta': '85', 'gamma': '85', 'delta': '75'})

        eq_(self.statbox_logger.write_handler_mock.call_count, 4)
        for i in range(4):
            log_entry = self.statbox_logger.write_handler_mock.call_args_list[i][0][0]
            ok_('destination=frodo' in log_entry)
            ok_('action=unhandled_error' in log_entry)

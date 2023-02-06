# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.yasms import exceptions
from passport.backend.core.builders.yasms.faker import yasms_send_sms_response
from passport.backend.core.counters import sms_per_ip
from passport.backend.core.env.env import Environment
from passport.backend.core.models.phones.faker import build_account
from passport.backend.core.models.phones.phones import SECURITY_IDENTITY
from passport.backend.core.test.test_utils.mock_objects import mock_counters
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags

from .base import BaseYasmsTestCase


PHONE_NUMBER_ALPHA = u'+79010000001'
PHONE_NUMBER_BETA = u'+79020000002'
UID_ALPHA = 1250
UID_BETA = 4120
USER_IP = u'1.2.3.4'
USER_AGENT = u'curl'
CONSUMER = u'TEST_CONSUMER'
CONSUMER_IP = u'5.6.7.8'
TEST_DATE = datetime(2015, 2, 17, 1, 2, 3)


class DeletePhoneTestCase(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
    )

    def _build_args(self, **kwargs):
        kwargs.setdefault(u'phone_number', PHONE_NUMBER_ALPHA)
        kwargs.setdefault(u'user_ip', USER_IP)
        kwargs.setdefault(u'user_agent', USER_AGENT)
        kwargs.setdefault(u'statbox', self._statbox)
        kwargs.setdefault(u'consumer', CONSUMER)
        return kwargs

    @staticmethod
    def _build_env():
        return Environment(user_ip=USER_IP)

    def test_phone_number_not_bound(self):
        """
        Номер не привязан.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=None,
                confirmed=None,
            )],
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'notfound')

    def test_phone_number_unbound(self):
        """
        Номер отвязан.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=None,
                confirmed=TEST_DATE,
            )],
        )

        status = self._yasms.delete_phone(**self._build_args(account=account))

        eq_(status, u'notfound')

    def test_phone_number_not_confirmed(self):
        """
        Номер не подтверждён.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=None,
            )],
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'notfound')

    def test_phone_number_being_bound(self):
        """
        Номер привязывется.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=None,
                confirmed=None,
            )],
            phone_operations=[dict(
                id=2,
                phone_id=4,
                type=u'bind',
                started=TEST_DATE,
                code_value=u'1234',
                phone_number=PHONE_NUMBER_ALPHA,
            )],
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'notfound')

    def test_phone_number_not_on_account(self):
        """
        Номера нет среди данных учётной записи.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
            )],
            phone_operations=[],
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_BETA,
        ))

        eq_(status, u'notfound')

    def test_invalid_phone_number(self):
        """
        Номер неправильной формы.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
            )],
            phone_operations=[],
        )
        for phone_number in [u'+7ABCDABCDAB', u'9010000001', u'02', u'']:
            status = self._yasms.delete_phone(**self._build_args(
                account=account,
                phone_number=phone_number,
            ))
            eq_(status, u'notfound')

    def test_valid_phone_number(self):
        """
        Номер правильной формы.
        """
        for phone_number in [u'+79010000001', u'89010000001']:
            account = build_account(
                uid=UID_ALPHA,
                phones=[dict(
                    id=4,
                    number=u'+79010000001',
                    created=TEST_DATE,
                    bound=TEST_DATE,
                    confirmed=TEST_DATE,
                )],
                phone_operations=[],
            )
            status = self._yasms.delete_phone(**self._build_args(
                account=account,
                phone_number=phone_number,
            ))
            eq_(status, u'ok')

    def test_operation_on_phone_number(self):
        """
        Над номером идёт операция.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
            )],
            phone_operations=[dict(
                phone_id=4,
                type=u'securify',
                started=TEST_DATE,
                phone_number=PHONE_NUMBER_ALPHA,
                code_value=u'1234',
            )],
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'interror')

    def test_remove_operation_on_phone_number(self):
        """
        Над номером идёт операция удаления.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
            )],
            phone_operations=[dict(
                phone_id=4,
                type=u'remove',
                started=TEST_DATE,
                finished=TEST_DATE + timedelta(hours=24 * 30),
                phone_number=PHONE_NUMBER_ALPHA,
                code_value=u'1234',
            )],
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'interror')

    def test_account_has_no_phone_numbers(self):
        """
        На учётной записи нет номеров.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[],
            phone_operations=[],
        )

        status = self._yasms.delete_phone(**self._build_args(account=account))

        eq_(status, u'notfound')

    # ТЕЛЕФОН НЕ ЗАЩИЩЁН
    def test_phone_number__default_insecure_single__ok(self):
        """
        Номер привязан, подтверждён, не защищён и используется по-умолчанию.
        На аккаунте больше нет номеров.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
            )],
            attributes={u'phones.default': 4},
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'ok')
        ok_(not account.phones.has_number(PHONE_NUMBER_ALPHA))
        ok_(not account.phones.default)

    def test_phone_number__default_insecure_many__ok(self):
        """
        Номер привязан, подтверждён, не удалён и используется по-умолчанию.
        На аккаунте есть другие номера.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[
                dict(
                    id=4,
                    number=PHONE_NUMBER_ALPHA,
                    created=TEST_DATE,
                    bound=TEST_DATE,
                    confirmed=TEST_DATE,
                ),
                dict(
                    id=5,
                    number=PHONE_NUMBER_BETA,
                    created=TEST_DATE,
                    bound=TEST_DATE,
                    confirmed=TEST_DATE,
                ),
            ],
            attributes={u'phones.default': 4},
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'ok')
        ok_(not account.phones.has_number(PHONE_NUMBER_ALPHA))
        eq_(account.phones.default.number.e164, PHONE_NUMBER_BETA)

    def test_phone_number__default_insecure_many_unbound__ok(self):
        """
        Номер привязан, подтверждён, не удалён и используется по-умолчанию.
        На аккаунте есть другие номера, но они не привязаны.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[
                dict(
                    id=4,
                    number=PHONE_NUMBER_ALPHA,
                    created=TEST_DATE,
                    bound=TEST_DATE,
                    confirmed=TEST_DATE,
                ),
                dict(
                    id=5,
                    number=PHONE_NUMBER_BETA,
                    created=TEST_DATE,
                    bound=None,
                    confirmed=TEST_DATE,
                ),
            ],
            attributes={u'phones.default': 4},
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'ok')
        ok_(not account.phones.has_number(PHONE_NUMBER_ALPHA))
        ok_(not account.phones.default)

    def test_dont_write_statbox__phone_number__insecure(self):
        """
        Не пишем в статбокс, когда удалили незащищённый номер.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
            )],
            attributes={u'phones.default': 4},
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
            statbox=self._statbox,
        ))
        self._statbox.dump_stashes()

        eq_(status, u'ok')
        self.env.statbox.assert_has_written([])

    # ТЕЛЕФОН ЗАЩИЩЁН
    def test_phone_number__default_secure__ok(self):
        """
        Номер защищён, создаём операцию.
        Статус started.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'started')

    def test_phone_number__default_secure__operation_created(self):
        """
        Номер защищён, создаём операцию.
        Операция заполняется значениями.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        # Телефонные свойства не изменились
        ok_(account.phones.has_id(4))
        phone = account.phones.by_id(4)
        eq_(account.phones.secure, phone)
        eq_(account.phones.default, phone)

        # Создали операцию удаления
        ok_(phone.operation)
        op = phone.operation
        eq_(op.security_identity, SECURITY_IDENTITY)
        eq_(op.type, u'remove')
        eq_(op.started, DatetimeNow())
        eq_(op.finished, DatetimeNow() + timedelta(hours=24 * 14))
        ok_(op.code_value)
        eq_(op.code_last_sent, DatetimeNow())
        eq_(op.code_checks_count, 0)
        eq_(op.code_send_count, 1)
        ok_(not op.code_confirmed)
        ok_(not op.password_verified)
        eq_(op.flags, PhoneOperationFlags())
        ok_(not op.phone_id2)

    def test_phone_number__default_secure__code_sent(self):
        """
        Номер защищён, создаём операцию.
        Выслали код.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        send_sms_requests = self.env.yasms.get_requests_by_method(u'send_sms')
        send_sms_requests[0].assert_query_contains(dict(
            text=u'Ваш код подтверждения: {{code}}. Наберите его в поле ввода.',
            phone=PHONE_NUMBER_ALPHA,
            from_uid=str(UID_ALPHA),
        ))
        send_sms_requests[0].assert_post_data_contains(dict(
            text_template_params=u'{"code": "%s"}' % account.phones.by_id(4).operation.code_value,
        ))

    def test_phone_number__default_secure__sms_note(self):
        """
        Номер защищён, создаём операцию.
        Уведомляем СМСкой.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        send_sms_requests = self.env.yasms.get_requests_by_method(u'send_sms')
        send_sms_requests[1].assert_query_contains(dict(
            text=u'Начато удаление телефона на Яндексе: https://ya.cc/sms-help-ru',
            phone=PHONE_NUMBER_ALPHA,
            from_uid=str(UID_ALPHA),
        ))

    def test_write_to_statbox__default_secure__ok(self):
        """
        Пишем в статбокс, когда номер защищён.
        """
        self.env.yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(sms_id=1),
        )
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=u'+79012244666',
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=u'+79012244666',
            statbox=self._statbox,
        ))
        self._statbox.dump_stashes()

        self.env.statbox.assert_has_written([
            self.env.statbox.entry(
                'yasms',
                uid=str(UID_ALPHA),
                number=u'+79012******',
                action=u'delete_phone.notify_user_by_sms_that_secure_phone_removal_started.notification_sent',
                sms_id=u'1',
            ),
            self.env.statbox.entry(
                'yasms',
                uid=str(UID_ALPHA),
                number=u'+79012******',
                ip=USER_IP,
                action=u'delete_phone.send_confirmation_code.code_sent',
                sms_count=u'1',
                sms_id=u'1',
            ),
        ])

    def test_phone_number__secure__account_2fa_enabled(self):
        """
        Номер защищён и 2fa активна.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
                u'account.2fa_on': True,
            },
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'interror')

    def test_phone_number__secure__account_sms_2fa_enabled(self):
        """
        Номер защищён и sms-2fa активна.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=PHONE_NUMBER_ALPHA,
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
                u'account.sms_2fa_on': True,
            },
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=PHONE_NUMBER_ALPHA,
        ))

        eq_(status, u'interror')

    def test_phone_number__secure__send_confirmation_code_impossible(self):
        """
        Запрещается высылать код для подтверждения.
        """
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=u'+79012233444',
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        with self._default_settings(
            **mock_counters(
                PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 300, 2),
                UNTRUSTED_PHONE_CONFIRMATION_SMS_PER_IP_LIMIT_COUNTER=(1, 300, 2),
            )
        ):
            # Необходимо увеличить счётчик после проставления настроек, т.к.
            # оно сбрасывает счётчик.
            for _ in range(2):
                # Увеличим счётчик до предела.
                sms_per_ip.get_counter(USER_IP).incr(USER_IP)

            status = self._yasms.delete_phone(**self._build_args(
                account=account,
                phone_number=u'+79012233444',
                user_ip=USER_IP,
            ))

        eq_(status, u'interror')

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'yasms',
                uid=str(UID_ALPHA),
                number=u'+79012******',
                action=u'delete_phone.send_confirmation_code',
                error=u'sms_limit.exceeded',
                reason='ip_limit',
            ),
        ])

    def test_phone_number__secure__send_confirmation_code_failed__expected(self):
        """
        Не удалось отправить код (ожидаемый сбой).
        """
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            exceptions.YaSmsError(),
        )
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=u'+79012233444',
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        status = self._yasms.delete_phone(**self._build_args(
            account=account,
            phone_number=u'+79012233444',
        ))

        eq_(status, u'interror')

        self.env.statbox.assert_contains([
            self.env.statbox.entry(
                'yasms',
                uid=str(UID_ALPHA),
                number=u'+79012******',
                action=u'delete_phone.send_confirmation_code',
                error=u'sms.isnt_sent',
            ),
        ])

    def test_phone_number__secure__send_confirmation_code__not_yasms__unexpected(self):
        """
        Не удалось отправить код (неожиданный сбой).
        """
        self.env.yasms.set_response_side_effect(
            u'send_sms',
            _UnexpectedError(),
        )
        account = build_account(
            uid=UID_ALPHA,
            phones=[dict(
                id=4,
                number=u'+79012233444',
                created=TEST_DATE,
                bound=TEST_DATE,
                confirmed=TEST_DATE,
                secured=TEST_DATE,
            )],
            attributes={
                u'phones.default': 4,
                u'phones.secure': 4,
            },
        )

        with self.assertRaises(_UnexpectedError):
            self._yasms.delete_phone(**self._build_args(
                account=account,
                phone_number=u'+79012233444',
            ))

        self.env.statbox.assert_has_written([])


class _UnexpectedError(Exception):
    """Неожиданная ошибка."""

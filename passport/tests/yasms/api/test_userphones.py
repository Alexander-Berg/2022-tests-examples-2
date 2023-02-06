# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.api.yasms.api import userphones_get_validations_left
from passport.backend.core.models.phones.faker import (
    build_account,
    build_phone_being_bound,
    build_phone_secured,
    build_remove_operation,
    build_secure_phone_being_bound,
)
from passport.backend.core.models.phones.phones import SECURITY_IDENTITY
from passport.backend.core.types.bit_vector.bit_vector import PhoneOperationFlags
from passport.backend.utils.common import deep_merge

from .base import BaseYasmsTestCase


_CREATION_DATE = datetime(2000, 1, 2, 10, 11, 12)
_BINDING_DATE = datetime(2000, 1, 2, 10, 11, 15)
_ADMISSION_DATE = datetime(2000, 1, 2, 10, 11, 20)
_SECURIFATION_DATE = datetime(2000, 1, 2, 10, 11, 25)
_CONFIRMATION_DATE = datetime(2000, 1, 2, 10, 11, 30)

_UID = 7878
_PHONE_NUMBER = u'+79054433222'
_PHONE_ID = 933
_OPERATION_ID = 934
_PHONE_NUMBER_EXTRA = u'+79082414400'
_PHONE_ID_EXTRA = 722


def _phone(id=13, number=u'+79010099888', created=_CREATION_DATE,
           bound=_BINDING_DATE, confirmed=_CONFIRMATION_DATE, secured=None,
           admitted=None):
    phone = {
        u'id': id,
        u'number': number,
        u'created': created,
    }
    if bound is not None:
        phone[u'bound'] = bound
    if confirmed is not None:
        phone[u'confirmed'] = confirmed
    if admitted is not None:
        phone[u'admitted'] = admitted
    if secured is not None:
        phone[u'secured'] = secured
    return phone


class TestUserphones(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        SMS_VALIDATION_MAX_CHECKS_COUNT=3,
    )

    def test_empty_list_when_blackbox_returns_no_phones(self):
        account = build_account(uid=72, phones=[])
        user_phones = self._yasms.userphones(account)
        eq_(user_phones, [])

    def test_success(self):
        account = build_account(
            uid=72,
            phones=[_phone(
                id=13,
                number=u'+79010099888',
                created=_CREATION_DATE,
                bound=_BINDING_DATE,
                confirmed=_CONFIRMATION_DATE,
            )],
        )

        user_phones = self._yasms.userphones(account)

        eq_(
            user_phones,
            [{
                u'id': 13,
                u'number': u'+79010099888',
                u'active': True,
                u'secure': False,
                u'cyrillic': True,
                u'valid': u'valid',
                u'validation_date': _CONFIRMATION_DATE,
                u'validations_left': 0,
                u'autoblocked': False,
                u'permblocked': False,
                u'blocked': False,
            }],
        )

    def test_number_is_active_when_it_equals_to_phones_default(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13)],
            attributes={u'phones.default': 13},
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'active'], True)

    def test_number_is_not_active_when_it_does_not_equal_to_phones_default(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13)],
            attributes={u'phones.default': 47},
        )
        account.phones.create(existing_phone_id=47, number=_PHONE_NUMBER, bound=_BINDING_DATE)

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'active'], False)

    def test_number_is_secure_when_it_equals_to_phones_secure(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13)],
            attributes={u'phones.secure': 13},
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'secure'], True)

    def test_number_is_not_secure_when_it_does_not_equal_to_phones_secure(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13)],
            attributes={u'phones.secure': 77},
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'secure'], False)

    def test_number_secure__secure_being_bound(self):
        account = build_account(
            uid=_UID,
            **build_secure_phone_being_bound(
                _PHONE_ID,
                _PHONE_NUMBER,
                _OPERATION_ID,
            )
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'secure'], True)

    def test_number_not_secure__simple_being_bound(self):
        account = build_account(
            uid=_UID,
            **build_phone_being_bound(
                _PHONE_ID,
                _PHONE_NUMBER,
                _OPERATION_ID,
            )
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'secure'], False)

    def test_number_is_valid_when_it_is_bound(self):
        account = build_account(
            uid=72,
            phones=[_phone(
                bound=_BINDING_DATE,
                confirmed=None,
                secured=None,
                admitted=None,
            )],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'valid'], u'valid')

    def test_number_is_in_message_sent_state_when_it_is_being_bound_and_message_sent(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13, bound=None)],
            phone_operations=[{
                u'type': u'bind',
                u'id': 33,
                u'phone_id': 13,
                u'phone_number': _PHONE_NUMBER,
                u'started': datetime(2014, 11, 28, 13, 0, 0),
                u'finished': datetime(2014, 12, 28, 12, 59, 59),
                u'code_value': u'1111',
                u'code_checks_count': 0,
                u'code_send_count': 0,
                u'code_last_sent': datetime(2014, 11, 28, 13, 0, 1),
                u'flags': PhoneOperationFlags(),
            }],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'valid'], u'msgsent')

    def test_number_is_message_sent_state_when_it_is_being_bound_and_message_not_sent(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13, bound=None)],
            phone_operations=[{
                u'type': u'bind',
                u'id': 33,
                u'phone_id': 13,
                u'phone_number': _PHONE_NUMBER,
                u'started': datetime(2014, 11, 28, 13, 0, 0),
                u'finished': datetime(2014, 12, 28, 12, 59, 59),
                u'code_value': u'1111',
                u'code_checks_count': 0,
                u'code_send_count': 0,
                u'flags': PhoneOperationFlags(),
            }],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'valid'], u'msgsent')

    def test_number_is_omitted_when_it_is_neither_bound_nor_being_bound(self):
        account = build_account(uid=72, phones=[_phone(bound=None)])

        user_phones = self._yasms.userphones(account)

        eq_(user_phones, [])

    def test_time_of_last_confirmation_code_sending_is_code_last_sent_when_number_is_being_bound_and_message_sent(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13, bound=None)],
            phone_operations=[{
                u'type': u'bind',
                u'id': 33,
                u'phone_id': 13,
                u'phone_number': _PHONE_NUMBER,
                u'started': datetime(2014, 11, 28, 13, 0, 0),
                u'finished': datetime(2014, 12, 28, 12, 59, 59),
                u'code_value': u'1111',
                u'code_checks_count': 0,
                u'code_send_count': 0,
                u'code_last_sent': datetime(2014, 11, 28, 13, 0, 1),
                u'flags': PhoneOperationFlags(),
            }],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validation_date'], datetime(2014, 11, 28, 13, 0, 1))

    def test_time_of_last_confirmation_code_sending_is_creation_time_when_number_is_being_bound_and_message_not_sent(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13, created=_CREATION_DATE, bound=None)],
            phone_operations=[{
                u'type': u'bind',
                u'id': 33,
                u'phone_id': 13,
                u'phone_number': _PHONE_NUMBER,
                u'code_last_sent': None,
                u'code_value': None,
                u'code_checks_count': 0,
                u'code_send_count': 0,
            }],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validation_date'], _CREATION_DATE)

    def test_validation_date__number_bound__number_admitted__operation___code_sent(self):
        account = build_account(
            uid=_UID,
            **deep_merge(
                build_phone_secured(
                    _PHONE_ID,
                    _PHONE_NUMBER,
                    phone_created=_CREATION_DATE,
                    phone_bound=_BINDING_DATE,
                    phone_confirmed=_CONFIRMATION_DATE,
                    phone_secured=_SECURIFATION_DATE,
                    phone_admitted=_ADMISSION_DATE,
                ),
                build_remove_operation(
                    _OPERATION_ID,
                    _PHONE_ID,
                    code_send_count=1,
                    code_last_sent=datetime(2014, 11, 28, 13, 0, 1),
                ),
            )
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validation_date'], _ADMISSION_DATE)

    def test_time_of_last_confirmation_code_sending_is_admission_time_when_number_is_bound_and_no_ops_and_number_is_admitted(self):
        account = build_account(
            uid=72,
            phones=[_phone(admitted=_ADMISSION_DATE, bound=_BINDING_DATE)],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validation_date'], _ADMISSION_DATE)

    def test_time_of_last_confirmation_code_sending_is_confirmation_time_when_number_is_bound_and_no_ops_and_number_is_not_admitted_and_number_is_confirmed(self):
        account = build_account(
            uid=72,
            phones=[_phone(
                admitted=None,
                bound=_BINDING_DATE,
                confirmed=_CONFIRMATION_DATE,
            )],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validation_date'], _CONFIRMATION_DATE)

    def test_time_of_last_confirmation_code_sending_is_binding_time_when_number_is_bound_and_no_ops_and_number_is_not_admitted_and_number_is_not_confirmed(self):
        account = build_account(
            uid=72,
            phones=[_phone(
                admitted=None,
                bound=_BINDING_DATE,
                confirmed=None,
            )],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validation_date'], _BINDING_DATE)

    def test_validations_left_is_zero_when_number_is_bound_and_no_ops(self):
        account = build_account(uid=72, phones=[_phone(bound=_BINDING_DATE)])

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validations_left'], 0)

    def test_validations_left_is_zero_when_number_is_bound_and_op_in_progress(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13, bound=_BINDING_DATE, secured=_SECURIFATION_DATE)],
            phone_operations=[{
                u'type': u'remove',
                u'id': 33,
                u'phone_id': 13,
                u'security_identity': SECURITY_IDENTITY,
                u'started': datetime(2014, 11, 28, 13, 0, 0),
                u'finished': datetime(2014, 12, 28, 12, 59, 59),
                u'code_value': u'1111',
                u'code_checks_count': 0,
                u'code_send_count': 0,
                u'code_last_sent': datetime(2014, 11, 28, 13, 0, 1),
                u'flags': PhoneOperationFlags(),
            }],
            attributes={u'phones.secure': 13}
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validations_left'], 0)

    def test_validations_left_is_effected_by_code_attempted_when_number_is_being_bound(self):
        account = build_account(
            uid=72,
            phones=[_phone(id=13, bound=None)],
            phone_operations=[{
                u'type': u'bind',
                u'id': 33,
                u'phone_id': 13,
                u'phone_number': _PHONE_NUMBER,
                u'started': datetime(2014, 11, 28, 13, 0, 0),
                u'finished': datetime(2014, 12, 28, 12, 59, 59),
                u'code_value': u'1111',
                u'code_checks_count': 1,
                u'code_send_count': 0,
                u'code_last_sent': datetime(2014, 11, 28, 13, 0, 1),
                u'flags': PhoneOperationFlags(),
            }],
        )

        user_phones = self._yasms.userphones(account)

        eq_(user_phones[0][u'validations_left'], 2)


class TestCompoundUserphones(BaseYasmsTestCase):
    def test_not_empty(self):
        """
        В ЧЯ есть сведения о телефонах данного пользователя.
        """
        account = build_account(
            uid=_UID,
            phones=[_phone(
                id=_PHONE_ID,
                number=_PHONE_NUMBER,
                created=_CREATION_DATE,
                bound=_BINDING_DATE,
                confirmed=_CONFIRMATION_DATE,
            )],
        )

        with self._default_settings():
            user_phones = self._yasms.userphones(account)

        eq_(
            user_phones,
            [{
                u'id': _PHONE_ID,
                u'number': _PHONE_NUMBER,
                u'active': True,
                u'secure': False,
                u'cyrillic': True,
                u'valid': u'valid',
                u'validation_date': _CONFIRMATION_DATE,
                u'validations_left': 0,
                u'autoblocked': False,
                u'permblocked': False,
                u'blocked': False,
            }],
        )


@raises(ValueError)
def test_userphones_get_validations_left_inappropriate_phone():
    account = build_account(uid=72, phones=[_phone(id=2, bound=None)])
    phone = account.phones.by_id(2)
    userphones_get_validations_left(phone)

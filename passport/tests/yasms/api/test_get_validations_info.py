# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_phone_bindings_response

from .base import BaseYasmsTestCase


__all__ = (
    u'TestGetValidationsInfo',
)


PHONE_ALPHA = u'+79010000001'
PHONE_BETA = u'+79020000002'
BINDING_DATE = datetime(2014, 12, 21, 20, 0, 0)
MINUTE = timedelta(minutes=1)


class TestGetValidationsInfo(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
    )

    def test_calling_with_no_phones(self):
        """Передаём методу пустой список."""
        self._set_blackbox_history([])

        info = self._yasms.get_validations_info([])

        eq_(info, {})

    def test_no_bindings(self):
        """В ЧЯ нет сведений о данных телефонах."""
        self._set_blackbox_history([])

        info = self._yasms.get_validations_info([PHONE_ALPHA, PHONE_BETA])

        eq_(info, {
            PHONE_ALPHA: {u'uids': set(), u'bindings_count': 0},
            PHONE_BETA: {u'uids': set(), u'bindings_count': 0},
        })

    def test_has_bindings(self):
        """История телефонных связей данного номера находится в ЧЯ."""
        self._set_blackbox_history([
            {
                u'type': u'history',
                u'number': PHONE_ALPHA,
                u'uid': 1,
                u'bound': BINDING_DATE,
            },
            {
                u'type': u'history',
                u'number': PHONE_ALPHA,
                u'uid': 1,
                u'bound': BINDING_DATE + MINUTE,
            },
            {
                u'type': u'history',
                u'number': PHONE_ALPHA,
                u'uid': 2,
                u'bound': BINDING_DATE,
            },
        ])

        info = self._yasms.get_validations_info([PHONE_ALPHA])

        eq_(info, {PHONE_ALPHA: {u'uids': {1, 2}, u'bindings_count': 3}})

    def test_has_bindings_of_not_normalized_phone_number(self):
        """
        Передаём методу ненормализованную форму номера.
        Сведения о связях с этим номером находятся в ЧЯ.
        """
        self._set_blackbox_history([{
            u'type': u'history',
            u'number': u'+79998877666',
            u'uid': 1,
            u'bound': BINDING_DATE,
        }])

        info = self._yasms.get_validations_info([u'89998877666'])

        eq_(
            info,
            {
                u'89998877666': {u'uids': {1}, u'bindings_count': 1},
            },
        )

    def _set_blackbox_history(self, history):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response(history),
        )

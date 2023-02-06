# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.dbscripts.test.base import TestCase as _TestCase


class TestCase(_TestCase):
    def _setup_statbox_templates(self):
        self._statbox_faker.bind_entry(
            'phone_operation_cancelled',
            _exclude={'consumer', 'ip', 'user_agent'},
            is_harvester='1',
        )
        self._statbox_faker.bind_entry(
            'phonenumber_alias_subscription_removed',
            _exclude={'ip'},
            consumer='-',
            user_agent='-',
        )
        self._statbox_faker.bind_entry(
            'secure_phone_removed',
            _exclude={'consumer', 'ip', 'user_agent'},
            is_harvester='1',
        )
        self._statbox_faker.bind_entry(
            'simple_phone_bound',
            _exclude={'consumer', 'ip', 'user_agent'},
            is_harvester='1',
        )
        self._statbox_faker.bind_entry(
            'secure_phone_replaced',
            _exclude={'consumer', 'ip', 'user_agent'},
            is_harvester='1',
        )
        self._statbox_faker.bind_entry(
            'phone_unbound',
            _exclude={'consumer', 'ip', 'user_agent'},
            is_harvester='1',
        )
        self._statbox_faker.bind_entry(
            'secure_phone_modified',
            _inherit_from=['account_modification'],
            _exclude={'ip'},
            entity='phones.secure',
            old='-',
            old_entity_id='-',
            new='-',
            new_entity_id='-',
            consumer='-',
            user_agent='-',
        )
        self._statbox_faker.bind_entry(
            'phone_acquired_before_unbinding',
            _inherit_from=['mark_operation_created'],
            _exclude={'consumer', 'ip'},
            user_agent='-',
        )
        self._statbox_faker.bind_entry(
            'phonenumber_alias_removed',
            _exclude={'ip'},
            consumer='-',
        )

# -*- coding: utf-8 -*-
from pprint import pformat

from nose.tools import assert_true
from passport.backend.core.logging_utils.faker.fake_tskv_logger import TskvLoggerFaker
from passport.backend.core.test.time_utils.time_utils import TimeNow


YASMS_STATBOX_TEMPLATES = {
    'base': {
        'tskv_format': 'yasms-log',
        'unixtime': TimeNow,
        'unixtimef': TimeNow,
        'sms': '1',
    },
    'queue_sms': {
        'action': 'enqueued',
    },
}


class YasmsStatboxPrivateLoggerFaker(TskvLoggerFaker):
    logger_class_module = 'passport.infra.daemons.yasmsapi.common.statbox_loggers.YasmsStatboxPrivateLogger'
    templates = YASMS_STATBOX_TEMPLATES


class YasmsStatboxPublicLoggerFaker(TskvLoggerFaker):
    logger_class_module = 'passport.infra.daemons.yasmsapi.common.statbox_loggers.YasmsStatboxPublicLogger'
    templates = YASMS_STATBOX_TEMPLATES

    def fuzzy_order_comparator(self, contents, expected_records):
        assert_true(
            len(contents) == len(expected_records),
            'Expected %s statbox entries, found %s.'
            % (
                len(expected_records),
                len(contents),
            ),
        )

        expected_stack = expected_records[:]
        for actual in contents:
            found_i = None
            for i, expected in enumerate(expected_stack):
                try:
                    self.equality_checker(actual, expected)
                    found_i = i
                    break
                except AssertionError:
                    pass
            if found_i is not None:
                expected_stack.pop(found_i)

        assert_true(
            not expected_stack,
            'Non-matched entries found: {}\n\nActual: {}'.format(
                ',\n'.join([pformat(e) for e in reversed(expected_stack)]),
                ',\n'.join([pformat(e) for e in contents]),
            ),
        )

    def assert_has_written_in_some_order(self, entries):
        self._check_contents(entries, comparator=self.fuzzy_order_comparator)

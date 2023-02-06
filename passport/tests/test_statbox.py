# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.logging_utils.faker.fake_tskv_logger import StatboxLoggerFaker
from passport.backend.core.logging_utils.loggers.statbox import (
    StatboxLogEntry,
    StatboxLogger,
)
from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)


def test_statbox_params():
    entry = StatboxLogEntry(foo='bar')

    eq_(
        entry.params,
        {
            'py': True,
            'unixtime': TimeNow(),
            'timestamp': DatetimeNow(convert_to_datetime=True),
            'timezone': '+0300',
            'tskv_format': 'passport-log',
            'foo': 'bar',
        },
    )


class TestStatboxLogger(unittest.TestCase):
    def setUp(self):
        self._statbox_faker = StatboxLoggerFaker()
        self._statbox_faker.start()

    def tearDown(self):
        self._statbox_faker.stop()
        del self._statbox_faker

    def test_bind(self):
        statbox = StatboxLogger()
        eq_(statbox.all_values, {})
        ok_(not statbox.has_data)
        statbox.bind_context(py=1, format='log')
        eq_(statbox.all_values, {'py': 1, 'format': 'log'})
        statbox.bind(hello='world')
        eq_(statbox.all_values, {'py': 1, 'format': 'log', 'hello': 'world'})
        self._statbox_faker.assert_has_written([])
        statbox.log()
        self._statbox_faker.assert_has_written(
            [
                self._statbox_faker.entry('base', hello='world', format='log'),
            ],
        )
        eq_(statbox.all_values, {'py': 1, 'format': 'log'})

    def test_bind_dict(self):
        statbox = StatboxLogger()
        eq_(statbox.all_values, {})
        ok_(not statbox.has_data)
        statbox.bind_context(dict(py=1), dict(pl=0), format='log')
        eq_(statbox.all_values, {'py': 1, 'pl': 0, 'format': 'log'})
        statbox.bind(dict(hello='world'), goodbye='columbus')
        eq_(statbox.all_values, {'py': 1, 'pl': 0, 'format': 'log', 'hello': 'world', 'goodbye': 'columbus'})
        self._statbox_faker.assert_has_written([])
        statbox.log()
        self._statbox_faker.assert_has_written(
            [
                self._statbox_faker.entry(
                    'base',
                    hello='world',
                    format='log',
                    pl='0',
                    goodbye='columbus',
                ),
            ],
        )
        eq_(statbox.all_values, {'py': 1, 'pl': 0, 'format': 'log'})

        with assert_raises(TypeError):
            statbox.bind('text')

        with assert_raises(TypeError):
            statbox.bind_context('text')

    def test_child(self):
        statbox = StatboxLogger(py=1)
        statbox.bind(hello='world')
        child = statbox.get_child(format='log')
        eq_(statbox.all_values, {'py': 1, 'hello': 'world'})
        eq_(child.all_values, {'py': 1, 'format': 'log'})

    def test_stash(self):
        statbox = StatboxLogger(py=1)
        statbox.bind(hello='world')
        statbox.stash()
        statbox.stash()
        statbox.stash(bye='world')
        statbox.log(foo='bar')

        eq_(
            statbox.all_stashes,
            [
                {'py': 1, 'hello': 'world'},
                {'py': 1},
                {'py': 1, 'bye': 'world'},
            ],
        )

    def test_stash_extra_values(self):
        statbox = StatboxLogger()
        statbox.bind(hello='world')
        statbox.stash(foo='bar')

        eq_(
            statbox.all_stashes,
            [{'hello': 'world', 'foo': 'bar'}],
        )

    def test_dump_stashes_cleans_stashes(self):
        statbox = StatboxLogger(foo='bar')
        statbox.stash()
        statbox.dump_stashes()
        eq_(statbox.all_stashes, [])

    def test_dump_stashes_writes_to_log(self):
        statbox = StatboxLogger(foo='bar')
        statbox.bind(alice='bob')
        statbox.stash()
        statbox.stash(mike='don')
        statbox.dump_stashes()
        self._statbox_faker.assert_has_written(
            [
                self._statbox_faker.entry('base', foo='bar', alice='bob'),
                self._statbox_faker.entry('base', foo='bar', mike='don'),
            ],
        )

    def test_dump_stashes_extra_values(self):
        statbox = StatboxLogger()
        statbox.stash(hello='world')
        statbox.dump_stashes(foo='bar')
        self._statbox_faker.assert_has_written(
            [
                self._statbox_faker.entry('base', foo='bar', hello='world'),
            ],
        )

    def test_dump_stashes_does_not_log_empty_stashes(self):
        statbox = StatboxLogger()
        statbox.dump_stashes(foo='bar')
        self._statbox_faker.assert_has_written([])
        statbox.stash()
        statbox.dump_stashes(foo='bar')
        self._statbox_faker.assert_has_written([])

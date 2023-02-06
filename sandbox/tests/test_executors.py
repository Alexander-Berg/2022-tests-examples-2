# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function

from datetime import date
from unittest import TestCase, main

from sandbox.projects.direct_internal_analytics.laborer.executor import get_executor
from sandbox.projects.direct_internal_analytics.laborer.executor.base import ClickHouseSelectExecutor, YqlSelectExecutor
from sandbox.projects.direct_internal_analytics.laborer.executor.ch_write import ClickHouseInsertExecutor
from sandbox.projects.direct_internal_analytics.laborer.target_types.base import ClickHouseInsertTarget, \
    ClickHouseSelectTarget, YqlSelectTarget


class TestYqlTarget(YqlSelectTarget):
    title = 'yql'


class TestChSelectTarget(ClickHouseSelectTarget):
    title = 'select'


class TestChInsertTarget(ClickHouseInsertTarget):
    title = 'insert'
    columns = ()


class ExecutorTestCase(TestCase):
    def test_get_executor(self):
        config = {'home': 'tmp'}
        context = {'token': 'test', 'date': date.today()}
        self.assertIsInstance(get_executor(TestYqlTarget, config, context, False), YqlSelectExecutor)
        self.assertIsInstance(get_executor(TestChSelectTarget, config, context, False), ClickHouseSelectExecutor)
        self.assertIsInstance(get_executor(TestChInsertTarget, config, context, False), ClickHouseInsertExecutor)


if __name__ == '__main__':
    main()

# coding=utf-8
"""
Тестовые цели для быстрой проверки обработки зависимостей задач для сендбокса в боевых условиях.
"""
from __future__ import absolute_import, unicode_literals, print_function

import datetime
import time

from sandbox.projects.direct_internal_analytics.laborer.target_types.base import YqlSelectTarget


class TestTask1(YqlSelectTarget):
    title = 'test_1'
    yql_syntax_version = 1
    query = """
INSERT INTO `{{ insert_target }}` WITH truncate
SELECT m.PageID AS page_id
     , ListSort(ListMap(ListMap(ListMap(ListMap(
             String::SplitToList(m.DomainList, ','),
             String::Strip), Url::ForcePunycodeToHostName), Url::GetHostPort), Url::CutWWW)
       ) AS mirrors
 FROM `home/yabs/dict/PartnerPage` AS m
 LIMIT 1000
"""


class TestTask2(YqlSelectTarget):
    title = 'test_2'
    yql_syntax_version = 1
    query = """
INSERT INTO `{insert_target}` WITH truncate
SELECT page_id, mirrors
 FROM `{dependencies[0]}` AS m
 LIMIT 1000
"""
    dependencies = [TestTask1]


class TestTask3(YqlSelectTarget):
    title = 'test_3'
    yql_syntax_version = 1
    query = """
INSERT INTO `{insert_target}` WITH truncate
SELECT page_id, mirrors
 FROM `{dependencies.test_2}` AS m
 LIMIT 1000
"""
    dependencies = [TestTask1, TestTask2]


class TestTask4(YqlSelectTarget):
    title = 'test_4'
    yql_syntax_version = 1
    query = """
INSERT INTO `{{ insert_target }}` WITH truncate
SELECT page_id, mirrors
 FROM `{{ dependencies.test_1 }}` AS m
 LIMIT 1000
"""
    dependencies = [TestTask1, TestTask3]
    final = True

    @classmethod
    def user_attributes(cls, context):
        date_str = "{date:%Y%m%d%H}".format(**context)
        max_unix_time = int(time.mktime(datetime.datetime.strptime(date_str, "%Y%m%d%H").timetuple()))
        max_unix_time = max_unix_time + 12 * 60 * 60 - 1
        return {"max_unix_time": max_unix_time}

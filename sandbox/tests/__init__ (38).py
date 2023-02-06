# coding=utf-8

from __future__ import unicode_literals

import math
import mock
import datetime

from sandbox.projects.cornholio.TicketWeightAutoincrement.process_modifier import process_modifier, process_deadline


class Priority(object):
    def __init__(self, val):
        self.id = val


class Type(object):
    def __init__(self, val):
        self.key = val


class TestIssue(object):
    tags = []
    type = Type("task")
    components = []
    votes = 2
    priority = Priority(2)
    createdAt = "2017-10-03T05:49:23.452+0000"


class TestProcessModifierFloatValue(object):
    def test_float_parsing(self):
        assert process_modifier(TestIssue(), 1.0, "priority/id:f+50") == 101.0,\
            "should parse field value as float and add value*modifier"

    def test_float_parsing_1(self):
        assert process_modifier(TestIssue(), 1.0, "votes:f+8") == 17.0,\
            "should parse field value as float and add value*modifier"

    def test_float_parsing_multiplication(self):
        assert process_modifier(TestIssue(), 1.0, "priority/id:f*50") == 100.0,\
            "should parse field value as float and multiply to value*modifier"

    def test_float_parsing_subtraction(self):
        assert process_modifier(TestIssue(), 10.0, "type/key==task:-3") == 7.0,\
            "should parse field value as int and subtract from current score"

    def test_float_parsing_negative(self):
        issue = TestIssue()
        issue.priority = None

        assert process_modifier(issue, 1.0, "priority/id:f+50") == 1.0,\
            "should return initial value if field is absent"


class TestProcessModifierMultiplication(object):
    def test_mult(self):
        issue = TestIssue()
        issue.tags = ["я_нужен_из-за_факапа"]
        assert process_modifier(issue, 1.0, "tags/я_нужен_из-за_факапа:*1.3") == 1.3,\
            "should apply mutliplication if tag is in place"

    def test_mult_1(self):
        issue = TestIssue()
        issue.tags = ["я_нужен_из-за_факапа"]
        assert process_modifier(issue, 1.0, "priority/id:*1.3") == 1.3,\
            "should apply mutliplication for attribute"

    def test_mult_2(self):
        issue = TestIssue()
        issue.components = [{"id": "# SEO"}]
        assert process_modifier(issue, 1.0, "components/[id==# SEO]:*1.3") == 1.3,\
            "should apply mutliplication for attribute"

    def test_mult_negative(self):
        assert process_modifier(TestIssue(), 1.0, "tags/я_нужен_из-за_факапа:*1.3") == 1.0,\
            "should not apply mutliplication if tag is not in place"

    def test_mult_negative_1(self):
        assert process_modifier(TestIssue(), 1.0, "components/# SEO:*1.3") == 1.0,\
            "should not apply mutliplication if tag is not in place"


class ProcessModifierAdditionTest(object):
    def test_plus(self):
        issue = TestIssue()
        issue.tags = ["я_нужен_из-за_факапа"]

        assert process_modifier(issue, 1.0, "tags/я_нужен_из-за_факапа:+1.3") == 2.3,\
            "should apply addition if tag is in place"

    def test_plus_negative(self):
        assert process_modifier(TestIssue(), 1.0, "tags/я_нужен_из-за_факапа:+1.3") == 1.0,\
            "should not apply addition if tag is not in place"


class ProcessAgeTest(object):
    def test_plus(self):
        with mock.patch("process_modifier.datetime") as mock_date:
            mock_date.now.return_value = datetime.datetime(2017, 12, 15, 13, 57, 59, 624723)
            issue = TestIssue()
            issue.tags = ["я_нужен_из-за_факапа"]

            assert process_modifier(issue, 1.0, "__age:f+0.15") == 11.95,\
                "should apply addition if tag is in place"

    def test_mult(self):
        with mock.patch("process_modifier.datetime") as mock_date:
            mock_date.now.return_value = datetime.datetime(2017, 12, 15, 13, 57, 59, 624723)
            issue = TestIssue()
            issue.tags = ["я_нужен_из-за_факапа"]
            assert process_modifier(issue, 1.0, "__age:f*0.15") == 10.95,\
                "should apply mutliplication if tag is in place"


class ProcessDeadlineTest(object):
    def test_between1(self):
        with mock.patch("process_modifier.datetime") as mock_date:
            mock_date.now.return_value = datetime.datetime(2016, 10, 10, 13, 57, 59, 624723)
            issue = TestIssue()
            issue.deadline = "2017-12-17"

            assert math.floor(process_deadline(issue, 10.0, 300, 30)) == 10.0,\
                "should apply nothing if deadline is far far away"

    def test_between2(self):
        with mock.patch("process_modifier.datetime") as mock_date:
            mock_date.now.return_value = datetime.datetime(2017, 10, 20, 13, 57, 59, 624723)
            issue = TestIssue()
            issue.deadline = "2017-12-17"

            assert math.floor(process_deadline(issue, 10.0, 300, 30)) == 88.0,\
                "should apply partial deadline addon if deadline is coming"

    def test_between3(self):
        with mock.patch("process_modifier.datetime") as mock_date:
            mock_date.now.return_value = datetime.datetime(2017, 11, 20, 13, 57, 59, 624723)
            issue = TestIssue()
            issue.deadline = "2017-12-17"

            assert math.floor(process_deadline(issue, 10.0, 300, 30)) == 180.0,\
                "should apply partial deadline addon if deadline is coming"

    def test_between4(self):
        with mock.patch("process_modifier.datetime") as mock_date:
            mock_date.now.return_value = datetime.datetime(2017, 12, 13, 13, 57, 59, 624723)
            issue = TestIssue()
            issue.deadline = "2017-12-17"

            assert math.floor(process_deadline(issue, 10.0, 300, 30)) == 283.0,\
                "should apply partial deadline addon if deadline is near"

    def test_passed(self):
        with mock.patch("process_modifier.datetime") as mock_date:
            mock_date.now.return_value = datetime.datetime(2018, 01, 18, 13, 57, 59, 624723)
            issue = TestIssue()
            issue.deadline = "2017-12-17"

            assert process_deadline(issue, 10.0, 300, 30) == 310,\
                "should apply full deadline addon if deadline has passed"


class ProcessEqTest(object):
    def test_eq(self):
        issue = TestIssue()
        issue.type = Type("bug")

        assert process_modifier(issue, 1.0, "type/key==bug:*1.8") == 1.8,\
            "should apply modification if last item equals passed value"

    def test_eq_negative(self):
        assert process_modifier(TestIssue(), 1.0, "type/key==bug:*1.8") == 1.0,\
            "should not apply modification if last item not equals passed value"

import os
import pytest

from collections import namedtuple
from textwrap import dedent

from sandbox.projects.yabs.SysConstLifetime.sys_const import SysConstLifetime
from sandbox.projects.yabs.SysConstLifetime.sys_const.sysconst_helper import SysConstHelper
from sandbox.projects.yabs.SysConstLifetime.lib.utils import tokenize_blame, get_blame


class DummyParameters:
    def __getattr__(self, key):
        return key


@pytest.fixture
def empty_sysconst_helper():
    return SysConstHelper(*(7 * (None, )), parameters=DummyParameters())


@pytest.mark.parametrize('name, expected', [
    ('abc-def', 'AbcDef'),
    ('a-b', 'AB'),
    ('abc', 'Abc'),
    ('a', 'A'),
    ('AlreadyFineConstantName', 'AlreadyFineConstantName')
])
def test_camel_case(name, expected, empty_sysconst_helper):
    result = empty_sysconst_helper._camel_case(name)
    assert result == expected


Blame = namedtuple('Blame', ('data', 'tuples', 'dict'))
Blame.__new__.func_defaults = (None,) * len(Blame._fields)


@pytest.fixture
def sysconst_blame():
    blame_data = dedent("""
        3792874   user1 2018-07-03 20:08:33 +0300 (Tue, 03 Jul 2018) package NFP;
        3792874   user1 2018-07-03 20:08:33 +0300 (Tue, 03 Jul 2018)
        3792874   user1 2018-07-03 20:08:33 +0300 (Tue, 03 Jul 2018) message TSysConst {
        6215529   user2 2020-01-15 10:20:47 +0300 (Wed, 15 Jan 2020)     optional int64 AdaptiveBannerCount = 2 [default = 25, (type) = CONSTANT_VALUE];
        4492734   user3 2019-02-23 12:05:26 +0300 (Sat, 23 Feb 2019)     // deleted optional int64 AddMadeRequestBigbResponseBit = 9 [default = 0];
        6481324   user4 2020-03-12 16:28:19 +0300 (Thu, 12 Mar 2020)     optional int64 YacofastBindningsCountLimit = 1670 [default = -1, (no_delete) = true];
        6468743   user5 2020-03-10 09:31:26 +0300 (Tue, 10 Mar 2020)     optional int64 FixMultiplyRPOnBC = 1662 [];
        6467500   user6 2020-03-09 11:19:11 +0300 (Mon, 09 Mar 2020)     optional int64 EnableNewCategoriesAmnestyInSlider = 1661 [(no_delete)=false, default = 0];
        6467501   user6 2020-03-09 11:19:12 +0300 (Mon, 09 Mar 2020)     optional int64 AdaptiveMinSizeCoef = 6 [(type)=FEATURE_FLAG, default = 0];
        4379072   user7 2019-01-29 00:26:59 +0300 (Tue, 29 Jan 2019)     // deleted optional int64 AdditionalNewsHitFlags = 782 [default = 0];
        6524868   user8 2020-03-24 16:54:31 +0300 (Tue, 24 Mar 2020) } // LAST: 1696
    """)
    blame_tuples = [
        ('6215529', 'user2', 'AdaptiveBannerCount', 'default = 25, (type) = CONSTANT_VALUE'),
        ('6481324', 'user4', 'YacofastBindningsCountLimit', 'default = -1, (no_delete) = true'),
        ('6468743', 'user5', 'FixMultiplyRPOnBC', ''),
        ('6467500', 'user6', 'EnableNewCategoriesAmnestyInSlider', '(no_delete)=false, default = 0'),
        ('6467501', 'user6', 'AdaptiveMinSizeCoef', '(type)=FEATURE_FLAG, default = 0')
    ]
    blame_dict = {
        'AdaptiveBannerCount': {
            'revision': '6215529',
            'author': 'user2',
            'options': {'default': '25', '(type)': 'CONSTANT_VALUE'},
            'commit_message': None,
        },
        'YacofastBindningsCountLimit': {
            'revision': '6481324',
            'author': 'user4',
            'options': {'default': '-1', '(no_delete)': 'true'},
            'commit_message': None,
        },
        'FixMultiplyRPOnBC': {
            'revision': '6468743',
            'author': 'user5',
            'options': {},
            'commit_message': None,
        },
        'EnableNewCategoriesAmnestyInSlider': {
            'revision': '6467500',
            'author': 'user6',
            'options': {'default': '0', '(no_delete)': 'false'},
            'commit_message': None,
        },
        'AdaptiveMinSizeCoef': {
            'revision': '6467501',
            'author': 'user6',
            'options': {'default': '0', '(type)': 'FEATURE_FLAG'},
            'commit_message': None,
        }
    }
    return Blame(blame_data, blame_tuples, blame_dict)


Parameters = namedtuple('Parameters', filter(lambda x: not x.startswith('__'), SysConstLifetime.Parameters.__dict__.keys()))
Parameters.__new__.func_defaults = (None,) * len(Parameters._fields)


def test_get_blame(sysconst_blame):
    class MockArcadiaClient:
        @classmethod
        def trunk_url(cls, *args, **kwargs):
            'some url'

        @classmethod
        def blame(cls, *args, **kwargs):
            return sysconst_blame.data

        @classmethod
        def log(cls, url, revisiona, revisionb):
            return [{'msg': 'Amazing commit message for rev %s' % revision} for revision in range(int(revisiona), int(revisionb) + 1)]

    const_arc_path = 'yabs/server/proto/quality/sys_const.proto'

    expected = sysconst_blame.dict.copy()
    for const in expected:
        expected[const]['commit_message'] = 'Amazing commit message for rev %s' % expected[const]['revision']
        expected[const]['source'] = 'ARC_' + os.path.basename(const_arc_path)

    result = get_blame(const_arc_path, MockArcadiaClient)
    assert expected == result


def test_tokenize_blame(sysconst_blame):
    expected = sysconst_blame.tuples
    result = tokenize_blame(sysconst_blame.data)
    assert result == expected

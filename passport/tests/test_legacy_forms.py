# -*- coding: utf-8 -*-

from hamcrest import assert_that
from passport.backend.api.legacy import forms
from passport.backend.core.services import get_service
from passport.backend.core.test.form.common_matchers import raises_invalid
from passport.backend.core.test.form.deep_eq_matcher import deep_eq
from passport.backend.core.test.form.submitted_form_matcher import submitted_with
from passport.backend.core.test.test_utils.utils import with_settings
from passport.backend.utils.common import merge_dicts
import pytest


def with_service(expected):
    if expected.get('sid') is None and expected.get('slug') is None:
        expected['service'] = None
    else:
        expected['service'] = get_service(
            sid=expected.get('sid'), slug=expected.get('slug')
        )
    return expected


@pytest.mark.parametrize(
    'args',
    [
        {},
        {'uid': 1},
        {'login_rule': 1},
        {'from': 'mail'},
        {'sid': 2},
        {'uid': 1, 'login_rule': 1},
        {'uid': 1, 'from': 'mail'},
        {'uid': 1, 'sid': 2},
        {'from': 'mail', 'sid': 2},
        {'login_rule': 1, 'from': 'mail'},
        {'login_rule': 1, 'sid': 2},
        {'uid': 1, 'from': 'mail', 'sid': 2},
        {'uid': 'aaaa', 'login_rule': 1, 'from': 'mail'},
        {'uid': '', 'login_rule': 1, 'from': 'mail', 'sid': 2},
        {'uid': 1, 'login_rule': 'a', 'from': 'mail'},
        {'uid': 1, 'login_rule': 1, 'from': 'fake_test_service'},
        {'uid': 1, 'login_rule': 1, 'sid': 'fake_test_sid'},
        {'uid': 1, 'login_rule': 1, 'from': 10 ** 100},
        {'uid': 1, 'login_rule': 1, 'from': 'mail', 'need_change_pass': 'blah'},
        {'uid': '1', 'login_rule': 1, 'from': 'mail', 'need_change_pass': '1'},
        {'uid': '1', 'login_rule': '', 'from': 'mail'},
        {'uid': 1, 'login_rule': 1, 'from': ''},
    ],
)
def test_should_be_err_on_invalid_admloginrule_form(args):
    assert_that(forms.AdmLoginRule(), submitted_with(args, raises_invalid()))


@pytest.mark.parametrize(
    ('act', 'expected'),
    [
        ({'uid': '1', 'from': 'passport', 'login_rule': '1', 'need_change_pass': 'yes'},
         {'uid': 1, 'from': 'passport', 'login_rule': 1, 'need_change_pass': True, 'sid': 8}),
        ({'uid': 1, 'sid': '8', 'login_rule': 1, 'need_change_pass': 'no'},
         {'uid': 1, 'sid': 8, 'login_rule': 1, 'need_change_pass': False, 'from': 'passport'}),
        ({'uid': 1, 'login_rule': 1, 'from': 'mail', 'sid': 2},
         {'uid': 1, 'login_rule': 1, 'need_change_pass': None, 'sid': 2, 'from': 'mail'}),
        ({'uid': 1, 'login_rule': 1, 'from': 'mail', 'mode': 'admloginrule'},
         {'uid': 1, 'login_rule': 1, 'from': 'mail', 'sid': 2, 'need_change_pass': None}),
    ],
)
def test_admloginrule_form(act, expected):
    assert_that(forms.AdmLoginRule(), submitted_with(act, deep_eq(with_service(expected))))


@pytest.mark.parametrize(
    'invalid_params',
    [
        {},
        {'uid': '1'},
        {'login': 'aaa'},
        {'uid': '1', 'login': 'aaa'},
        {'sid': 2},
        {'from': 'mail'},
        {'sid': 2, 'from': 'mail'},
        {'login_rule': 1},
        {'yastaff_login': 'a'},
        {'unsubscribe': 'no'},
        {'wmode': 1},
        {'uid': '', 'from': 'mail'},
        {'uid': 'a1', 'sid': 2},
        {'uid': '1', 'sid': 'fake_test_sid'},
        {'uid': 'a1', 'from': 'mail'},
        {'uid': '1', 'from': 'fake_test_from'},
        {'uid': '1', 'from': 10 ** 100},
        {'login': 'aaa', 'sid': 'fake_test_sid'},
        {'login': 'aaa', 'from': 'fake_test_from'},
        {'login': 'aaa', 'from': 10 ** 100},
        {'uid': '1', 'sid': 2, 'unsubscribe': 'blah'},
        {'uid': '1', 'sid': 2, 'wmode': 'a'},
        {'uid': '1', 'sid': 2, 'wmode': '2'},
        {'uid': '1', 'sid': 2, 'yastaff_login': 'aaa'},
        {'uid': '1', 'sid': 669},
        {'login': '', 'from': 'metrika'},
        {'uid': '1', 'sid': 669, 'yastaff_login': ''},
        {'uid': '1', 'sid': 669, 'yastaff_login': '    '},
    ],
)
def test_admsubscribe_form_invalid(invalid_params):
    assert_that(forms.AdmLoginRule(), submitted_with(invalid_params, raises_invalid()))


@pytest.mark.parametrize(
    ('valid_params', 'exp'),
    [
        ({'uid': '1', 'from': 'mail'},
         {'uid': 1, 'from': 'mail', 'sid': 2, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': False,
          'login': None}),
        ({'uid': '1', 'sid': '2'},
         {'uid': 1, 'from': 'mail', 'sid': 2, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': False,
          'login': None}),
        ({'uid': '1', 'from': 'mail', 'sid': 2},
         {'uid': 1, 'from': 'mail', 'sid': 2, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': False,
          'login': None}),
        ({'login': 'a1', 'from': 'mail', 'sid': 2},
         {'uid': None, 'from': 'mail', 'sid': 2, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': False,
          'login': 'a1'}),
        ({'uid': '1', 'login': 'a', 'sid': 2},
         {'uid': 1, 'from': 'mail', 'sid': 2, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': False,
          'login': 'a'}),
        ({'uid': '1', 'login': 'a', 'from': 'mail'},
         {'uid': 1, 'from': 'mail', 'sid': 2, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': False,
          'login': 'a'}),
        ({'uid': '1', 'from': 'wwwdgt', 'wmode': '2'},
         {'uid': 1, 'from': 'wwwdgt', 'sid': 42, 'wmode': 2,
          'yastaff_login': None, 'unsubscribe': False,
          'login': None}),
        ({'uid': '1', 'from': 'wwwdgt', 'unsubscribe': 'yes'},
         {'uid': 1, 'from': 'wwwdgt', 'sid': 42, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': True,
          'login': None}),
        ({'uid': '1', 'from': 'yastaff', 'yastaff_login': 'foo'},
         {'uid': 1, 'from': 'yastaff', 'sid': 669, 'yastaff_login': 'foo',
          'wmode': None, 'unsubscribe': False,
          'login': None}),
        ({'uid': '1', 'from': 'yastaff', 'unsubscribe': 'yes'},
         {'uid': 1, 'from': 'yastaff', 'sid': 669, 'yastaff_login': None,
          'wmode': None, 'unsubscribe': True,
          'login': None}),
        ({'uid': '1', 'from': 'mail', 'mode': 'admsubscribe'},
         {'uid': 1, 'from': 'mail', 'sid': 2, 'wmode': None,
          'yastaff_login': None, 'unsubscribe': False,
          'login': None}),
    ],
)
def test_admsubscribe_form(valid_params, exp):
    assert_that(forms.AdmSubscribe(), submitted_with(valid_params, deep_eq(with_service(exp))))


@pytest.mark.parametrize(
    'inv',
    [
        {},
        {'uid': 1},
        {'uid': 1, 'karma': 10, 'prefix': 1},
        {'uid': '', 'karma': '100'},
        {'karma': 10},
        {'prefix': 1},
        {'uid': 'a', 'karma': 10},
        {'uid': 1, 'karma': 'a'},
        {'uid': 'a', 'prefix': 1},
        {'uid': 1, 'prefix': 100},
        {'uid': 1, 'prefix': 'a'},
        {'uid': 1, 'karma': -100},
        {'uid': 1, 'karma': '10'},
        {'uid': 1, 'karma': ''},
        {'uid': 1, 'prefix': ''},
    ],
)
def test_admkarma_form_invalid(inv):
    assert_that(forms.AdmKarma(), submitted_with(inv, raises_invalid()))


@pytest.mark.parametrize(
    ('act', 'exp'),
    [
        ({'uid': '1', 'karma': '100'},
         {'uid': 1, 'karma': 100, 'prefix': None}),
        ({'uid': '1', 'prefix': '1'},
         {'uid': 1, 'prefix': 1, 'karma': None}),
        ({'uid': 1, 'prefix': 1, 'mode': 'admkarma'},
         {'uid': 1, 'prefix': 1, 'karma': None})
    ],
)
def test_admkarma_form(act, exp):
    assert_that(forms.AdmKarma(), submitted_with(act, deep_eq(exp)))


@pytest.mark.parametrize(
    'inv',
    [
        {},
        {'uid': 'a'},
        {'uid': ''},
        {'sid': 2, 'from': 'mail'},
        {'sid': 2},
        {'from': 'mail'},
        {'uid': 1, 'sid': 'fake_test_sid'},
        {'uid': 1, 'from': 'fake_test_from'},
        {'uid': 1, 'from': 10 ** 100},
    ],
)
def test_admblock_form_inv(inv):
    assert_that(forms.AdmBlock(), submitted_with(inv, raises_invalid()))


@pytest.mark.parametrize(
    ('act', 'exp'),
    [
        ({'uid': '1'}, {'uid': 1, 'sid': None, 'from': None}),
        ({'uid': '1', 'sid': '2'}, {'uid': 1, 'sid': 2, 'from': 'mail'}),
        ({'uid': '1', 'from': 'mail'}, {'uid': 1, 'sid': 2, 'from': 'mail'}),
        ({'uid': 1, 'sid': 2, 'from': 'mail'}, {'uid': 1, 'sid': 2, 'from': 'mail'}),
        ({'uid': 1, 'sid': 2, 'mode': 'admblock'},
         {'uid': 1, 'sid': 2, 'from': 'mail'}),
    ],
)
def test_admblock_form(act, exp):
    assert_that(forms.AdmBlock(), submitted_with(act, deep_eq(with_service(exp))))


@pytest.mark.parametrize(
    'params',
    [
        {'login': '', 'maillist': '1'},
        {'maillist': 'abrakadabra'},
        {'login': '(*&!^@(*^@(*&^!'},
    ],
)
def test_admsimplereg_form_inv(params):
    assert_that(forms.AdmSimpleReg(), submitted_with(params, raises_invalid()))


@pytest.mark.parametrize(
    ('act', 'exp'),
    [
        ({'login': 'test-login', 'maillist': '1'},
         {'login': 'test-login', 'maillist': True, 'sid': None, 'from': None}),
        ({'login': 'test-123'},
         {'login': 'test-123', 'maillist': False, 'sid': None, 'from': None}),
    ],
)
def test_admsimplereg_form(act, exp):
    assert_that(forms.AdmSimpleReg(), submitted_with(act, deep_eq(with_service(exp))))


@pytest.mark.parametrize(
    'inv',
    [
        {'login': 'test.login', 'iname': 'Iname', 'fname': 'Fname', 'passwd': '1', 'passwd2': '2'},
        {'passwd': '123456', 'passwd2': '123456'},
        {'login': 'test.login', 'passwd': '', 'passwd2': '', 'iname': 'Iname', 'fname': 'Fname'},
        {'login': 'test.login', 'passwd': '1', 'passwd2': '1', 'iname': 'Iname', 'fname': 'Fname'},
        {'login': 'test.login', 'iname': '', 'fname': '', 'passwd': '123456', 'passwd2': '123456'},
        {'login': 'test.login', 'iname': '  ', 'fname': '  ', 'passwd': '123456', 'passwd2': '123456'},
        {'login': 'test.login', 'iname': 'Iname', 'fname': 'Fname', 'passwd': '123456', 'passwd2': ''},
        {'login': 'test.login', 'iname': 'Iname', 'fname': 'Fname', 'passwd': '123456', 'passwd2': '    '},
        {'login': 'test.login',
          'iname': 'Iname',
          'fname': 'Fname',
          'passwd': '123456',
          'passwd2': '123456',
          'yastaff_login': '   ',
          'from': 'yastaff',
          },
        {'login': 'test.login',
          'iname': 'Iname',
          'fname': 'Fname',
          'passwd': '123456',
          'passwd2': '123456',
          'yastaff_login': '',
          'from': 'yastaff',
          },
        {'login': 'test.login',
          'iname': 'Iname',
          'fname': 'Fname',
          'passwd': '123456',
          'passwd2': '123456',
          'yastaff_login': 'bla',
          },
    ],
)
@with_settings(SHAKUR_WHITELIST_LOGIN_MASKS=[])
def test_admreg_form_inv(inv):
    assert_that(forms.AdmReg(), submitted_with(inv, raises_invalid()))


@pytest.mark.parametrize(
    ('act', 'exp'),
    [
        ({'login': 'test.login',
          'passwd': '123456',
          'passwd2': '123456',
          'iname': 'Iname',
          'fname': 'Fname',
          },
         {'login': 'test.login',
          'passwd': '123456',
          'passwd2': '123456',
          'iname': 'Iname',
          'fname': 'Fname',
          'ignore_stoplist': False,
          'ena': True,
          'yastaff_login': None,
          'sid': None,
          'from': None,
          'lt_middle_quality': True,
          'quality': 0,
          },),
        ({'login': 'test.login',
          'passwd': '123456',
          'passwd2': '123456',
          'iname': 'Iname',
          'fname': 'Fname',
          'from': 'upravlyator',
          },
         {'login': 'test.login',
          'passwd': '123456',
          'passwd2': '123456',
          'iname': 'Iname',
          'fname': 'Fname',
          'ignore_stoplist': False,
          'ena': True,
          'yastaff_login': None,
          'sid': None,
          'from': None,
          'lt_middle_quality': True,
          'quality': 0,
          },),
        ({'login': 'test.login',
          'passwd': '123456',
          'passwd2': '123456',
          'iname': 'Iname',
          'fname': 'Fname',
          'sid': '1234666',
          },
         {'login': 'test.login',
          'passwd': '123456',
          'passwd2': '123456',
          'iname': 'Iname',
          'fname': 'Fname',
          'ignore_stoplist': False,
          'ena': True,
          'yastaff_login': None,
          'sid': None,
          'from': None,
          'lt_middle_quality': True,
          'quality': 0,
          },),
    ],
)
@with_settings(BASIC_PASSWORD_POLICY_MIN_QUALITY=0)
def test_admreg_form(act, exp):
    assert_that(forms.AdmReg(), submitted_with(act, deep_eq(with_service(exp))))


@pytest.mark.parametrize(
    'params',
    [
        dict(),  # Нет операции
        dict(op='unknown-operation'),

        dict(op='create', mx='', prio='-20', db_id='ok'),  # Пустое значение mx
        dict(op='create', mx='some-string', prio='-20'),  # Треубется еще db_id

        dict(op='setprio', prio='bad-number', db_id='ok'),
        dict(op='setprio', db_id='ok'),  # Требуется еще prio
        dict(op='setprio', prio='-20', db_id=''),  # Пустое значение в db_id

        dict(op='delete', db_id=''),  # Пустое значение в db_id
        dict(op='delete', prio='-10'),  # Требуется db_id

        dict(op='assign', suid='bad-number', db_id='ok'),
        dict(op='assign', suid='123', db_id=''),  # Пустое значение в db_id
        dict(op='assign', db_id='ok'),  # Требуется еще suid

        dict(op='find', prio=''),  # Пустое значение в prio
        dict(op='find', db_id='ok'),  # Требуется prio
    ],
)
def test_mailhost_form__invalid_params__error(params):
    assert_that(forms.MailHost(), submitted_with(params, raises_invalid()))


def get_mailhost_valid_params():
    empty_params = dict.fromkeys(['prio', 'mx', 'db_id', 'suid', 'old_db_id', 'sid', 'from'], None)
    return [
        (
            {
                'op': 'create', 'prio': '-1', 'mx': 'mx.yandex.ru',
                'db_id': 'mdb666', 'suid': '555', 'old_db_id': 'old',
            },
            merge_dicts(
                empty_params,
                {
                    'op': 'create', 'prio': -1, 'mx': 'mx.yandex.ru',
                    'db_id': 'mdb666', 'suid': 555, 'old_db_id': 'old',
                },
            ),
        ),
        (
            {'op': 'setprio', 'prio': '-20', 'db_id': 'id'},
            merge_dicts(empty_params, {'op': 'setprio', 'prio': -20, 'db_id': 'id'}),
        ),
        (
            {'op': 'delete', 'db_id': 'old_id'},
            merge_dicts(empty_params, {'op': 'delete', 'db_id': 'old_id'}),
        ),
        (
            {'op': 'assign', 'db_id': '_id', 'suid': '123'},
            merge_dicts(empty_params, {'op': 'assign', 'db_id': '_id', 'suid': 123}),
        ),
        (
            {'op': 'find', 'prio': '10'},  # Положительные числа ОК для op=find
            merge_dicts(empty_params, {'op': 'find', 'prio': 10}),
        ),
    ]


@pytest.mark.parametrize(('act', 'exp'), get_mailhost_valid_params())
def test_mailhost_form__valid_params__ok(act, exp):
    assert_that(forms.MailHost(), submitted_with(act, deep_eq(exp)))

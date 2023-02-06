# -*- coding: utf-8 -*-
import pytest

from nose.tools import assert_tuple_equal, assert_raises, eq_

from passport.infra.daemons.yasmsapi.common.renderer import render


@pytest.mark.parametrize(
    ('template', 'data', 'allow_unused', 'res', 'res_masked'),
    [
        (u'a {{ b }} c', {'b': 'defghijk'}, False, 'a defghijk c', 'a d******k c'),
        (u'a {{ b }} c', {'b': 'd'}, False, 'a d c', 'a d c'),
        (u'a {{ b }} c', {'b': 'de'}, False, 'a de c', 'a de c'),
        (u'a {{ b }} c', {'b': 'de', 'd': 'e', 'f': 'g'}, True, 'a de c', 'a de c'),
        (
            u'Hi, {{title   }}.{{ last_name }}, something {{123text}}_{{123text}} {{1}}{{1}}{{2_2}} ext.',
            {
                'title': 'Ms',
                'last_name': u'АбВг№2',
                '123text': u'<>_&+=-!@#$%^&*()?',
                '1': '123',
                '2_2': '12:11:100-123.123',
            },
            False,
            u'Hi, Ms.АбВг№2, something <>_&+=-!@#$%^&*()?_<>_&+=-!@#$%^&*()? 12312312:11:100-123.123 ext.',
            u'Hi, Ms.А****2, something <****************?_<****************? 1*31*31***************3 ext.',
        ),
    ],
)
def test_render(template, data, allow_unused, res, res_masked):
    assert_tuple_equal(render(template, data, allow_unused), (res, res_masked))


def test_failed_render():
    tests = [
        (u'a {{ b c', {'b': 'defghijk'}, 'invalid template'),
        (u'a {{ b} }} c', {'b': 'defghijk'}, 'invalid key in template'),
        (u'a {{ some key }} c', {'some key': 'defghijk'}, 'invalid key in template'),
        (u'a {{ b}} }} c', {'b': 'defghijk'}, 'special characters outside of template definition'),
        (u'a {{ b}}}}c', {'b': 'defghijk'}, 'special characters outside of template definition'),
        (u'a {{ b }} c', {}, 'missing key'),
        (u'a {{ b }} c', {'b': 'c', 'd': 'e', 'f': 'g'}, 'unused parameters'),
    ]

    for template, data, exc in tests:
        with assert_raises(ValueError) as e:
            render(template, data)
        eq_(str(e.exception), exc)

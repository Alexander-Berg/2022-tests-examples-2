# -*- coding: utf-8 -*-

from passport.backend.api.legacy.common import (
    dict_to_xml,
    list_to_xml,
)
from passport.backend.core.xml.test_utils import assert_xml_documents_equal


def test_dict_to_xml():
    assert_xml_documents_equal(
        dict_to_xml(
            u'foo',
            {u'bar': u'spam'},
            {
                u'alpha': u'a',
                u'beta': [(u'gamma', 'g'), (u'zeta', u'z')],
            },
        ),
        u'''
        <?xml version="1.0" encoding="utf-8" ?>
        <foo bar="spam">
            <alpha>a</alpha>
            <beta>
                <gamma>g</gamma>
                <zeta>z</zeta>
            </beta>
        </foo>
        ''',
    )


def test_list_to_xml():
    assert_xml_documents_equal(
        list_to_xml(
            u'foo',
            {u'bar': u'spam'},
            [
                ('item', {'id': '1', 'text': 'item-text'}),
                ('extra', {'id': '2', 'size': 'big'}),
            ]
        ),
        u'''
        <?xml version="1.0" encoding="utf-8" ?>
        <foo bar="spam">
            <item id="1">item-text</item>
            <extra id="2" size="big" />
        </foo>
        ''',
    )

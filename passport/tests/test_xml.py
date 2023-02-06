# -*- coding: utf-8 -*-

from unittest import TestCase

from lxml.etree import tostring
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.xml.test_utils import (
    assert_html_documents_equal,
    assert_xml_documents_equal,
    assert_xml_elements_equal,
    assert_xml_response_equals,
    get_xml_encoding,
)
from passport.backend.core.xml.xml import (
    XML,
    XMLParser,
    XPath,
    xpath_to_bool,
    xpath_to_float,
    xpath_to_int,
)
import six


class TestXmlParser(TestCase):
    def test_resolve_entities_true(self):
        with assert_raises(ValueError):
            XMLParser(resolve_entities=True)

    def test_resolve_entities_default(self):
        parser = XMLParser()
        xml = b"""<?xml version="1.0" encoding="ISO-8859-1"?>
                 <!DOCTYPE foo [
                     <!ELEMENT foo ANY >
                     <!ENTITY xxe SYSTEM "file:///dev/random" >
                 ]>
                <foo>&xxe;</foo>"""
        eq_(tostring(XML(xml, parser)), b"""<foo>&xxe;</foo>""")

    def test_resolve_entities_false(self):
        parser = XMLParser(resolve_entities=False)
        xml = b"""<?xml version="1.0" encoding="ISO-8859-1"?>
                 <!DOCTYPE foo [
                    <!ELEMENT foo ANY >
                    <!ENTITY xxe SYSTEM "file:///dev/random" >
                 ]>
                 <foo>&xxe;</foo>"""
        eq_(tostring(XML(xml, parser)), b"""<foo>&xxe;</foo>""")


class TestGetXmlEncoding(TestCase):
    def test(self):
        text = u'''<?xml version="1.0" encoding="utf-8"?>
          <doc>
            <uid>23454234</uid>
            <phone id="46" number="79026411724" cyrillic="0" valid="msgsent" validation_date="2006–11–07 15:14:10" validations_left="5" autoblocked="0" permblocked="0" blocked="0"/>
            <phone id="58" number="79256445255" cyrillic="0" valid="msgsent" validation_date="2006–12–11 14:09:05" validations_left="0" autoblocked="0" permblocked="0" blocked="0"/>
            <phone id="64" number="79137135841" cyrillic="0" valid="msgsent" validation_date="2006–12–11 14:27:33" validations_left="5" autoblocked="0" permblocked="0" blocked="0"/>
          </doc>
        '''
        eq_(get_xml_encoding(text), u'utf-8')

        text = u'''<?xml version="1.0" encoding="windows-1251"?>
          <doc foo="bar"></doc>
        '''
        eq_(get_xml_encoding(text), u'windows-1251')

    def test_fallback(self):
        text = u'<doc foo="bar"></doc>'
        eq_(get_xml_encoding(text), u'utf-8')


class ResponseMock(object):
    def __init__(self, text, mimetype, charset):
        self.text = text
        if six.PY2:
            self.data = text.encode(charset)
        else:
            self.data = text
        self.mimetype = mimetype
        self.charset = charset


class TestAssertXmlResponseEquals(TestCase):
    def test_equal(self):
        assert_xml_response_equals(
            ResponseMock(
                u'''<?xml version="1.0" encoding="utf-8"?>
                    <doc></doc>'''.encode('utf-8'),
                mimetype=u'text/xml',
                charset=u'utf-8',
            ),
            u'<?xml version="1.0" encoding="utf-8"?><doc></doc>',
        )

    def test_nonequal(self):
        with assert_raises(AssertionError):
            assert_xml_response_equals(
                ResponseMock(
                    u'''<?xml version="1.0" encoding="utf-8"?>
                        <doc></doc>'''.encode('utf-8'),
                    mimetype=u'text/xml',
                    charset=u'utf-8',
                ),
                u'''<?xml version="1.0" encoding="utf-8"?><cod></cod>''',
            )

    def test_wrong_charset(self):
        with assert_raises(AssertionError):
            assert_xml_response_equals(
                ResponseMock(
                    u'''<?xml version="1.0" encoding="windows-1251"?>
                        <doc></doc>'''.encode('windows-1251'),
                    mimetype=u'text/xml',
                    charset=u'windows-1251',
                ),
                u'''<?xml version="1.0" encoding="utf-8"?><cod></cod>''',
            )


class TestAssertXmlDocumentsEqual(TestCase):
    def test_equal(self):
        assert_xml_documents_equal(
            u'''<?xml version="1.0" encoding="utf-8"?>
                <doc foo="bar" bar="foo"></doc>''',
            u'''<?xml version="1.0" encoding="utf-8"?>
                <doc bar="foo" foo="bar">
                </doc>''',
        )

    def test_nonequal(self):
        with assert_raises(AssertionError):
            assert_xml_documents_equal(
                u'''<?xml version="1.0" encoding="utf-8"?>
                    <doc foo="bar" bar="foo"></doc>''',
                u'''<?xml version="1.0" encoding="utf-8"?>
                    <doc bar="bar" foo="foo">
                    </doc>''',
            )

    def test_expected_is_shorter(self):
        with assert_raises(AssertionError):
            assert_xml_documents_equal(
                u'''<?xml version="1.0" encoding="utf-8"?>
                    <doc foo="bar" bar="foo"><spam></spam></doc>''',

                u'''<?xml version="1.0" encoding="utf-8"?>
                    <doc bar="foo" foo="bar">
                    </doc>''',
            )

    def test_actual_is_shorter(self):
        with assert_raises(AssertionError):
            assert_xml_documents_equal(
                u'''<?xml version="1.0" encoding="utf-8"?>
                    <doc bar="foo" foo="bar">
                    </doc>''',

                u'''<?xml version="1.0" encoding="utf-8"?>
                    <doc foo="bar" bar="foo"><spam></spam></doc>''',
            )


class TestAssertXmlElementsEqual(TestCase):
    def test_equal(self):
        assert_xml_elements_equal(
            XML(u'''<spam foo="bar" bar='foo'> badooga </spam>'''),
            XML(u'''<spam bar="foo" foo='bar' >badooga
                </spam>'''),
        )
        assert_xml_elements_equal(
            XML(u'<spam>badooga ytyt</spam>'),
            XML(u'<spam>badooga   ytyt</spam>'),
        )
        assert_xml_elements_equal(
            XML(u'<spam>badooga   ytyt</spam>'),
            XML(u'<spam>badooga ytyt</spam>'),
        )
        assert_xml_elements_equal(
            XML(u'<spam>badooga ytyt</spam>'),
            XML(u'''<spam>badooga
                ytyt</spam>'''),
        )
        assert_xml_elements_equal(
            XML(u'''<phone autoblocked="0" blocked="" cyrillic="0" id="46" number="*******4587" permblocked="1" valid="msgsent" validation_date="2006-11-07 15:14:10" validations_left="5" />'''),
            XML(u'''<phone autoblocked="0" blocked="" cyrillic="0" id="46" number="*******4587" permblocked="1" valid="msgsent" validation_date="2006-11-07 15:14:10" validations_left="5" />'''),
        )

    def test_no_text_in_expected(self):
        assert_xml_elements_equal(
            XML(u'''<spam>   </spam>'''),
            XML(u'''<spam></spam>'''),
        )

    def test_no_text_in_actual(self):
        assert_xml_elements_equal(
            XML(u'''<spam></spam>'''),
            XML(u'''<spam>   </spam>'''),
        )

    def test_no_text_in_both(self):
        assert_xml_elements_equal(
            XML(u'''<spam></spam>'''),
            XML(u'''<spam></spam>'''),
        )

    def test_tags_non_equal(self):
        with assert_raises(AssertionError):
            assert_xml_elements_equal(
                XML(u'''<spam></spam>'''),
                XML(u'''<foo></foo>'''),
            )

    def test_different_attributes(self):
        with assert_raises(AssertionError):
            assert_xml_elements_equal(
                XML(u'''<spam foo="bar" bar="bar"></spam>'''),
                XML(u'''<spam foo="bar" spam="bar"></spam>'''),
            )

    def test_nonequal_attributes(self):
        with assert_raises(AssertionError):
            assert_xml_elements_equal(
                XML(u'''<spam foo="bar"></spam>'''),
                XML(u'''<spam foo="foo"></spam>'''),
            )


class TestAssertHtmlDocumentsEqual(TestCase):
    def test_equal(self):
        assert_html_documents_equal(
            u'''
            <html>
              <head><title>Hello Alice</title></head>
              <body><h1 class="foo bar" id="foo">foo</h1></body>
            </html>
            ''',
            u'''
            <html>
              <head><title> Hello   Alice  </title></head>
              <body><h1 id="foo" class="foo bar">foo</h1></body>
            </html>
            ''',
        )

    def test_equal__different_class_order(self):
        """
        Не учитывется порядок классов.
        """
        assert_html_documents_equal(
            u'''
            <html>
              <head><title>Foo</title></head>
              <body><h1 class="foo bar">foo</h1></body>
            </html>
            ''',
            u'''
            <html>
              <head><title>Foo</title></head>
              <body><h1 class="bar foo">foo</h1></body>
            </html>
            ''',
        )

    def test_equal__different_style_attr(self):
        """
        Не учитывается атрибут style.
        """
        assert_html_documents_equal(
            u'''
            <html>
              <head><title>Foo</title></head>
            <body><h1 style="margin: 0;">foo</h1></body>
            </html>
            ''',
            u'''
            <html>
              <head><title>Foo</title></head>
              <body><h1 style="margin: 20px;">foo</h1></body>
            </html>
            ''',
        )
        assert_html_documents_equal(
            u'''
            <html>
              <head><title>Foo</title></head>
            <body><h1 style="margin: 0;">foo</h1></body>
            </html>
            ''',
            u'''
            <html>
              <head><title>Foo</title></head>
              <body><h1>foo</h1></body>
            </html>
            ''',
        )

    def test_different_encoding_equal(self):
        doc = u'''
        <html>
        <head><title>Hello</title></head>
        <body><h1>foo</h1></body>
        </html>
        '''
        assert_html_documents_equal(
            doc,
            doc.encode(u'utf-8'),
            encoding=u'utf-8',
        )
        assert_html_documents_equal(
            doc.encode(u'utf-8'),
            doc,
            encoding=u'utf-8',
        )

    def test_nonequal(self):
        with assert_raises(AssertionError):
            assert_html_documents_equal(
                u'''
                <html>
                    <head><title>Hello</title></head>
                    <body><h1>foo</h1></body>
                </html>
                ''',
                u'''
                <html>
                    <head><title>Hello</title></head>
                    <body><h1>bar</h1></body>
                </html>
                ''',
            )

    def test_expected_is_shorter(self):
        with assert_raises(AssertionError):
            assert_html_documents_equal(
                u'''
                <html>
                    <head><title>Hello</title></head>
                    <body><h1>foo</h1><p>bar</p></body>
                </html>
                ''',
                u'''
                <html>
                    <head><title>Hello</title></head>
                    <body><h1>bar</h1></body>
                </html>
                ''',
            )

    def test_non_equal_tail(self):
        with assert_raises(AssertionError):
            assert_html_documents_equal(u'<p>foo<br>foo</p>', u'<p>foo<br>bar</p>')


def test_xpath_to_bool():
    pattern = XPath(".//flag/text()")
    true_values = [
        XML(u"""<doc><flag>1</flag></doc>"""),
        XML(u"""<doc><flag>-1</flag></doc>"""),
    ]

    for tree in true_values:
        ok_(xpath_to_bool(tree, pattern))

    false_values = [
        XML(u"""<doc><flag>abc</flag></doc>"""),
        XML(u"""<doc><flag>0</flag></doc>"""),
        XML(u"""<doc><flag></flag></doc>"""),
        XML(u"""<doc><not_flag></not_flag></doc>"""),
    ]
    for tree in false_values:
        ok_(not xpath_to_bool(tree, pattern))


def test_xpath_to_int():
    pattern = XPath("//doc/size/text()")
    true_values = [
        (XML(u"""<doc><size>480</size></doc>"""), 480),
        (XML(u"""<doc><size>-1</size></doc>"""), -1),
    ]

    for tree, res in true_values:
        eq_(xpath_to_int(tree, pattern), res)

    false_values = [
        XML(u"""<doc><size>abc</size></doc>"""),
        XML(u"""<doc><size>тест</size></doc>"""),
        XML(u"""<doc><size></size></doc>"""),
        XML(u"""<doc><not_size></not_size></doc>"""),
        XML(u"""<doc><size>4.5</size></doc>"""),
    ]
    for tree in false_values:
        ok_(not xpath_to_int(tree, pattern))


def test_xpath_to_float():
    pattern = XPath("//doc/size/text()")
    true_values = [
        (XML(u"""<doc><size>480.0</size></doc>"""), 480.0),
        (XML(u"""<doc><size>-1</size></doc>"""), -1.0),
        (XML(u"""<doc><size>3.14159265358</size></doc>"""), 3.14159265358),
    ]

    for tree, res in true_values:
        eq_(xpath_to_float(tree, pattern), res)

    false_values = [
        XML(u"""<doc><size>abc</size></doc>"""),
        XML(u"""<doc><size>тест</size></doc>"""),
        XML(u"""<doc><size></size></doc>"""),
        XML(u"""<doc><not_size></not_size></doc>"""),
        XML(u"""<doc><size>4.5.1</size></doc>"""),
    ]
    for tree in false_values:
        ok_(not xpath_to_float(tree, pattern))

    default_values = [
        (0.0, 0.0),
        (None, None),
        (123, 123),
    ]
    empty_tree = XML(u"<doc><other_tag>1.0</other_tag></doc>")
    for default_value, res in default_values:
        eq_(xpath_to_float(empty_tree, pattern, default_value), res)

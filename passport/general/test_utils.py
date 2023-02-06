# -*- coding: utf-8 -*-

import operator
import re

from lxml import html
from passport.backend.core.xml.xml import XML
from passport.backend.utils.string import smart_text
import six
from six.moves import zip_longest


def _assert_encoding(expected_enc, actual_enc):
    assert_message = 'Expect HTTP response encoded with %s, but got %s' % (
        expected_enc,
        actual_enc,
    )
    assert actual_enc == expected_enc, assert_message


def assert_xml_response_equals(response, expected_document):
    assert response.mimetype == 'text/xml', 'Response is not text/xml'
    actual = XML(response.data)
    expected = XML(smart_text(expected_document).strip().encode(response.charset))

    expected_enc = expected.getroottree().docinfo.encoding
    _assert_encoding(expected_enc, response.charset)
    assert_xml_objects_equal(actual, expected)


def assert_xml_documents_equal(actual, expected):
    if isinstance(actual, six.text_type):
        actual = actual.encode(get_xml_encoding(actual))
    actual = XML(actual.strip())

    if isinstance(expected, six.text_type):
        expected = expected.encode(get_xml_encoding(expected))
    expected = XML(expected.strip())

    assert_xml_objects_equal(actual, expected)


def assert_xml_objects_equal(actual, expected, attr_to_compare_mapping={}):
    expected_enc = expected.getroottree().docinfo.encoding.lower()
    actual_enc = actual.getroottree().docinfo.encoding.lower()
    _assert_encoding(expected_enc, actual_enc)

    for actual_element, expected_element in zip_longest(
        actual.iter(),
        expected.iter(),
    ):
        if actual_element is None:
            raise AssertionError('Actual document is shorter than expected')
        if expected_element is None:
            raise AssertionError('Expected document is shorter than actual')
        assert_xml_elements_equal(
            actual_element,
            expected_element,
            attr_to_compare_mapping,
        )


def assert_xml_elements_equal(actual, expected, attr_to_compare_mapping={}):
    if actual.text is None:
        actual_text = u''
    else:
        actual_text = space_sequence.sub(u' ', actual.text.strip())

    if expected.text is None:
        expected_text = u''
    else:
        expected_text = space_sequence.sub(u' ', expected.text.strip())

    if actual.tail is None:
        actual_tail = u''
    else:
        actual_tail = space_sequence.sub(u' ', actual.tail.strip())

    if expected.tail is None:
        expected_tail = u''
    else:
        expected_tail = space_sequence.sub(u' ', expected.tail.strip())

    for attr in set(actual.attrib.keys()) | set(expected.attrib.keys()):
        is_equal = attr_to_compare_mapping.get(attr, operator.eq)
        if not is_equal(actual.attrib.get(attr), expected.attrib.get(attr)):
            attrs_equal = False
            break
    else:
        attrs_equal = True

    if not (actual.tag == expected.tag and
            actual_text == expected_text and
            actual_tail == expected_tail and
            attrs_equal):
        raise AssertionError(
            'Expected tag is %s, got %s' % (
                format_tag(expected),
                format_tag(actual),
            ),
        )


space_sequence = re.compile(r'\s{2,}')


def format_tag(tag):
    attrs = [u'%s="%s"' % (attr, tag.attrib[attr]) for attr in sorted(tag.attrib)]
    if attrs:
        attrs = u' ' + ' '.join(attrs)
    else:
        attrs = u''
    if tag.text is not None:
        form = u'<%(tag)s%(attrs)s>%(text)s</%(tag)s>%(tail)s'
        text = tag.text.strip()
    else:
        form = u'<%(tag)s%(attrs)s />%(tail)s'
        text = u''
    if tag.tail is not None:
        tail = tag.tail.strip()
    else:
        tail = u''
    return form % dict(
        tag=tag.tag,
        attrs=attrs,
        text=text,
        tail=tail,
    )


def get_xml_encoding(text):
    xml_enc_match = xml_enc_re.match(text)
    if xml_enc_match is None:
        return u'utf-8'
    return xml_enc_match.group(1)


xml_enc_re = re.compile(r'^<\?xml version="1.0" encoding="([^"]*?)"\?>')


def assert_html_documents_equal(actual, expected, encoding=u'utf-8'):
    """
    Сравнивает гипертекстовые документы.

    Игнорирует атрибут style.
    """
    if not isinstance(actual, six.text_type):
        actual = actual.decode(encoding)
    actual = html.fromstring(actual.strip())

    if not isinstance(expected, six.text_type):
        expected = expected.decode(encoding)
    expected = html.fromstring(expected.strip())

    assert_xml_objects_equal(
        actual,
        expected,
        attr_to_compare_mapping={
            u'style': _ignore_attr,
            u'class': _compare_class_attr,
        },
    )


def _ignore_attr(val1, val2):
    return True


def _compare_class_attr(val1, val2):
    return set(val1.split()) == set(val2.split())

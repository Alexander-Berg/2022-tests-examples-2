import unittest

from formencode.validators import Invalid
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.qa.test_user_service.tus_api.validators import TagsValidator


class TestTagsValidator(unittest.TestCase):

    def test_should_parse_tags(self):
        valid_tags = {
            'aaa': ['aaa'],
            ' aaa ': ['aaa'],
            'aaa,aaa': ['aaa'],
            'aaa,bbb': ['aaa', 'bbb'],
            'aaa,bbb,ccc': ['aaa', 'bbb', 'ccc'],
            'aaa,bbb,ccc,ddd,eee,fff,ggg,hhh,iii,jjj': ['aaa', 'bbb', 'ccc', 'ddd', 'eee',
                                                        'fff', 'ggg', 'hhh', 'iii', 'jjj'],
            'long-tag-name_1234567890-1234567890-1234': ['long-tag-name_1234567890-1234567890-1234'],
        }
        v = TagsValidator()
        for tags_param_value, expected in valid_tags.items():
            eq_(sorted(v.to_python(tags_param_value)), expected)

    def test_should_raise_error(self):
        invalid_tags = [
            '',
            ' ',
            'aaa bbb',
            'aaa, bbb',
            'aa',
            'aaa,a',
            'a,aaa',
            'too-long-tag-name_1234567890-1234567890-1',
            '1aaa',
            'tus_consumer_value=aaa',  # should not contain =
        ]
        v = TagsValidator()
        for tags_param_value in invalid_tags:
            assert_raises(Invalid, v.to_python, tags_param_value)

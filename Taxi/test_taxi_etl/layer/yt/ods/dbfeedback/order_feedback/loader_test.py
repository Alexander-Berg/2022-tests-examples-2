import pytest
from dmp_suite.exceptions import DWHError

from taxi_etl.layer.yt.ods.dbfeedback.order_feedback.impl import get_reasons, \
    normalize_feedback_reason, ReasonsExtractor


def create_doc(choices=None):
    return dict(data=dict(choices=choices))


def filter_(choice):
    return choice['type'] == 'a'


def test_get_reasons():
    assert not get_reasons([], filter_)
    assert not get_reasons([dict(type='b', value='b')], filter_)

    assert {'b'} == get_reasons([dict(type='a', value='b')], filter_)

    choices = [dict(type='b', value='b'), dict(type='a', value='a')]
    assert {'a'} == get_reasons(choices, filter_)

    choices = [dict(type='a', value='b'), dict(type='a', value='a')]
    assert {'a', 'b'} == get_reasons(choices, filter_)

    choices = [dict(type='a', value='b'),
               dict(type='a', value='a'),
               dict(type='a', value='a')]
    assert {'a', 'b'} == get_reasons(choices, filter_)


def test_reasons_extractor():
    mapping = dict(a='b')
    extract = ReasonsExtractor(filter_, mapping)

    assert not extract(dict())
    assert not extract(create_doc(choices=[dict(type='b', value='b')]))

    with pytest.raises(DWHError):
        extract(create_doc(choices=[dict(type='a', value='b')]))

    assert {'b'} == extract(create_doc(choices=[dict(type='a', value='a')]))


def test_normalize_feedback_reason():
    mapping = dict(a='b')

    with pytest.raises(DWHError):
        normalize_feedback_reason(mapping, 'b')

    assert 'b' == normalize_feedback_reason(mapping, 'a')

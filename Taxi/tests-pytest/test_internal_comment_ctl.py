import pytest

from taxi.internal import comment_ctl
from taxi.internal import dbh
from taxi.internal.order_kit import payment_handler


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('comment,expected', [
    ('forcepromotions-tesla', ['tesla']),
    ('forcepromotions-x-y-z', ['x', 'y', 'z']),
    ('key-value', None),
    ('key-value,forcepromotions-1', ['1'])
])
def test_parsing_forced_switched_promotions(comment, expected, monkeypatch):
    monkeypatch.setattr(comment_ctl, 'is_crutches_enabled', lambda: True)
    result = comment_ctl.forced_switch_promotions(
        dbh.order_proc.Doc(**{'order': {'request': {'comment': comment}}})
    )
    assert expected == result


@pytest.mark.parametrize(['comment', 'key', 'value', 'expected'], [
    ('billing-fft-ffr', 'billing', 'ffr', 'billing-fft'),
    (
        'billing-fft-ffr,antifraud-1', 'billing', 'ffr',
        'billing-fft,antifraud-1'
    ),
    ('billing-fft-ffr,antifraud-1', 'antifraud', '1', 'billing-fft-ffr'),
    ('billing-fft-ffr', 'billing', 'ffs', 'billing-fft-ffr'),
    ('antifraud-0', 'antifraud', '1', 'antifraud-0'),
    ('antifraud-0', 'antifraud', '0', ''),
])
def test_remove_from_comment(comment, key, value, expected):
    assert comment_ctl.remove_from_comment(comment, key, value) == expected


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('comment,expected', [
    ('speed-100,wait-0', False),
    ('speed-100,wait-0,forcedrop_complements-1', True),
    ('speed-100,wait-0,forcedrop_complements,key', True),
    ('speed-100,wait-0,forcedrop_complements-0,key', True),
    ('key-value', False),
])
def test_should_forcedrop_comlements(comment, expected, monkeypatch):
    monkeypatch.setattr(comment_ctl, 'is_crutches_enabled', lambda: True)
    doc = dbh.orders.Doc(**{'request': {'comment': comment}})
    payable = payment_handler.PayableOrder(doc)

    result = comment_ctl.should_force_drop_complements(payable)
    assert expected == result

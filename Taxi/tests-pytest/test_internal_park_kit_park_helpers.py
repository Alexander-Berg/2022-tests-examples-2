import datetime

import pytest
import pytz

from taxi.core import db
from taxi.internal.park_kit import park_helpers
from taxi.util import dates


@pytest.inline_callbacks
@pytest.mark.now('2015-09-15 00:00:00 +03')
@pytest.mark.filldb()
def test_get_billing_client_id():
    now = datetime.datetime(2015, 9, 14, 21)
    dt1 = now - datetime.timedelta(days=10)  # -864000 seconds
    dt2 = now - datetime.timedelta(days=1)  # -86400 seconds
    dt3 = now + datetime.timedelta(days=7)  # 604800 seconds
    before_dt1 = dt1 - datetime.timedelta(seconds=1)
    after_dt1 = dt1 + datetime.timedelta(seconds=1)
    after_dt2 = dt2 + datetime.timedelta(seconds=1)
    after_dt3 = dt3 + datetime.timedelta(seconds=1)
    ANY = set([
        before_dt1,
        dt1,
        after_dt1,
        dt2,
        after_dt2,
        dt3,
        after_dt3,
    ])

    expected_results = [
        # (park_id, timestamps, expected result)
        ('park_0', ANY, None),
        ('park_1', ANY, None),
        ('park_2', ANY, '123'),
        ('park_3', ANY, '123'),
        ('park_4', ANY, '124'),
        ('park_5', [before_dt1], '124'),
        ('park_5', ANY - set([before_dt1]), None),
        ('park_6', [before_dt1], None),
        ('park_6', ANY - set([before_dt1]), '125'),
        ('park_7', [before_dt1], '124'),
        ('park_7', ANY - set([before_dt1]), '125'),
        ('park_8', [before_dt1], None),
        ('park_8', [dt1, after_dt1], '124'),
        ('park_8', [dt2, after_dt2, now], '125'),
        ('park_8', [dt3, after_dt3], None),
    ]

    expected_results_now = [
        # (park_id, expected result)
        ('park_0', None),
        ('park_1', None),
        ('park_2', '123'),
        ('park_3', '123'),
        ('park_4', '124'),
        ('park_5', None),
        ('park_6', '125'),
        ('park_7', '125'),
        ('park_8', '125'),
    ]

    for (park_id, timestamps, expected) in expected_results:
        park_doc = yield db.parks.find_one({'_id': park_id})
        for timestamp in timestamps:
            result = park_helpers.get_billing_client_id(park_doc, timestamp)
            assert expected == result

    for (park_id, expected_now) in expected_results_now:
        park_doc = yield db.parks.find_one({'_id': park_id})
        result_now = park_helpers.get_billing_client_id(park_doc)
        assert expected_now == result_now


def test_set_versioned_field():
    now = dates.localize()
    dt1 = dates.localize(now - datetime.timedelta(days=10))
    before_dt1 = dates.localize(dt1 - datetime.timedelta(seconds=1))
    after_dt1 = dates.localize(dt1 + datetime.timedelta(seconds=1))
    dt2 = dates.localize(now - datetime.timedelta(days=1))
    after_dt2 = dates.localize(dt2 + datetime.timedelta(seconds=1))
    dt3 = dates.localize(now + datetime.timedelta(days=7))
    after_dt3 = dates.localize(dt3 + datetime.timedelta(seconds=1))

    new_values = [
        (before_dt1, 'value1'),
        (dt1, 'value2'),
        (after_dt1, 'value3'),
        (dt2, 'value4'),
        (after_dt2, 'value5'),
        (now, 'value_now'),
        (dt3, 'value6'),
        (after_dt3, 'value7'),
    ]

    field = 'versioned_values'
    old_field = 'old_field'

    # one doc has nothing in it and we just fill it with values
    # another has some initial old field
    doc1 = {}
    doc2 = {old_field: 'value0'}

    for i, (start, value) in enumerate(new_values):
        park_helpers.set_versioned_field(doc1, field, value, start, old_field)
        last_value = doc1[field][-1]
        assert last_value[0] == start and last_value[2] == value
        assert len(doc1[field]) == i + 1
        if i > 1:
            value_before_last = doc1[field][-2]
            assert value_before_last[1] == start

        park_helpers.set_versioned_field(doc2, field, value, start, old_field)
        last_value = doc2[field][-1]
        assert last_value[0] == start and last_value[2] == value
        assert len(doc2[field]) == i + 2
        if i > 1:
            value_before_last = doc2[field][-2]
            assert value_before_last[1] == start

    # check first values starts
    assert doc1[field][0][0] == before_dt1
    assert doc2[field][0][0] is None
    # lately added values have no explicit end
    assert doc1[field][-1][1] is None
    assert doc2[field][-1][1] is None


# short alias to write test cases
_d_time = datetime.datetime


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('corp_vats,timestamp,expected_vat', [
    # None corp_vats, we return None
    (None,
     _d_time(2016, 3, 28),
     None),
    # Empty corp_vats, we return None
    ([
     ],
     _d_time(2016, 3, 28),
     None),
    # simple case, return vat
    ([
         [_d_time(2016, 3, 28), None, 11800]
     ],
     _d_time(2016, 3, 28),
     11800),
    # no active vat (too early), return None
    ([
         [_d_time(2016, 3, 28), None, 11800]
     ],
     _d_time(2016, 3, 27),
     None),
    # no active vat (too late), return None
    ([
         [_d_time(2016, 3, 28), _d_time(2016, 3, 29), 11800]
     ],
     _d_time(2016, 3, 30),
     None),
])
def test_get_corp_vat(corp_vats, timestamp, expected_vat):
    park_doc = _make_park_doc_with_corp_vats(corp_vats)
    assert park_helpers.get_corp_vat(park_doc, timestamp) == expected_vat


def _aw_d_time(year, month, day, hour, minute=0, second=0, tz='Europe/Moscow'):
    """Return tz-aware (in Europe/Moscow) datetime."""
    naive = datetime.datetime(year, month, day, hour, minute, second)
    return pytz.timezone(tz).localize(naive)


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('corp_vats,timestamp,vat,expected_corp_vats', [
    # no corp_vats, add new
    (None,
     _d_time(2016, 3, 28, 11),
     11800,
     [
         [_aw_d_time(2016, 3, 28, 14), None, 11800]
     ],
    ),
    # no corp_vats, no new corp vat - do nothing
    (None,
     _d_time(2016, 3, 28, 11),
     None,
     None,
     ),
    # empty corp_vats, add new
    ([],
     _d_time(2016, 3, 28, 11),
     11800,
     [
         [_aw_d_time(2016, 3, 28, 14), None, 11800]
     ],
     ),
    # don't add the same value
    ([
        [_d_time(2016, 3, 28, 11), None, 11800]
     ],
     _d_time(2016, 3, 28, 13),
     11800,
     [
         [_d_time(2016, 3, 28, 11), None, 11800]
     ],
     ),
    # the new value
    ([
         [_d_time(2016, 3, 28, 11), None, 11800]
     ],
     _d_time(2016, 3, 28, 13),
     10000,
     [
         [_aw_d_time(2016, 3, 28, 14), _aw_d_time(2016, 3, 28, 16), 11800],
         [_aw_d_time(2016, 3, 28, 16), None, 10000],
     ],
    ),
    # same date, same value - nothing changes
    ([
         [_d_time(2016, 3, 28, 11), None, 11800]
     ],
     _d_time(2016, 3, 28, 11),
     11800,
     [
         [_d_time(2016, 3, 28, 11), None, 11800]
     ],
    ),
    # same date, different value - value changes
    ([
         [_d_time(2016, 3, 28, 11), None, 11800]
     ],
     _d_time(2016, 3, 28, 11),
     12000,
     [
         [_aw_d_time(2016, 3, 28, 14), None, 12000]
     ],
    ),
])
def test_set_corp_vat(corp_vats, timestamp, vat, expected_corp_vats):
    park_doc = _make_park_doc_with_corp_vats(corp_vats)
    park_helpers.set_corp_vat(park_doc, vat, timestamp)
    assert park_doc.get('corp_vats') == expected_corp_vats


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('corp_vats,timestamp,vat,expected_error', [
    ([
        [_d_time(2016, 3, 28, 11), None, 11800]
     ],
     _d_time(2016, 1, 1, 3),
     10000,
     park_helpers.SetVatBackDateError
    ),
    ([
         [_d_time(2015, 3, 28, 11), _d_time(2016, 3, 28, 14), 11800]
     ],
     _d_time(2016, 1, 1, 3),
     10000,
     park_helpers.SetVatBackDateError
    ),
])
def test_set_corp_vat_in_the_past(corp_vats, timestamp, vat, expected_error):
    park_doc = _make_park_doc_with_corp_vats(corp_vats)
    with pytest.raises(expected_error):
        park_helpers.set_corp_vat(park_doc, vat, timestamp)
    assert park_doc.get('corp_vats') == corp_vats


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('billing,expected_field', [
    ('card', 'billing_product_ids'),
    ('corp', 'billing_corp_product_ids'),
    ('donate', 'billing_donate_product_ids'),
])
def test_set_billing_product_ids(billing, expected_field):
    park_doc = {}
    now = datetime.datetime.utcnow()
    actual_field = park_helpers.set_billing_product_ids(
        billing, park_doc, 1, now
    )
    assert expected_field in park_doc
    assert actual_field == expected_field


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('billing,field,expected_value', [
    ('card', 'billing_product_ids', 'some_card_product'),
    ('corp', 'billing_corp_product_ids', 'some_corp_product'),
    ('donate', 'billing_donate_product_ids', 'some_donate_product'),
])
def test_get_billing_product_ids(billing, field, expected_value):
    park_doc = {
        field: [[None, None, expected_value]]
    }
    timestamp = datetime.datetime(2018, 8, 23, 22, 43)
    actual_value = park_helpers.get_billing_product_ids(
        billing, park_doc, timestamp
    )
    assert actual_value == expected_value


def _make_park_doc_with_corp_vats(corp_vats):
    if corp_vats is None:
        return {}
    else:
        return {
            'corp_vats': corp_vats
        }

import dataclasses
import datetime
import json

import pytest

from partner_offers import models

VALID_COUPON_PAIRS = [
    ('coupon', {'price': '98', 'currency': 'RUB'}),
    (
        'fix_price',
        {
            'old_price': '8.7',
            'new_price': '5',
            'old_curr': 'RUB',
            'new_curr': 'RUB',
        },
    ),
    ('discount', {'percent': '5.07'}),
    ('coupon', {'text': 'some', 'price': '98', 'currency': 'RUB'}),
    ('discount', {'text': 'some', 'percent': '5.07'}),
]

INVALID_COUPON_PAIRS = [
    ('coupon', None),
    ('fix_price', None),
    ('discount', None),
    ('coupon', {'old_price': '8.7', 'new_price': '5'}),
    ('coupon', {'percent': '5.07'}),
    ('fix_price', {'text': 'some', 'price': '98'}),
    ('fix_price', {'percent': '5.07'}),
    ('discount', {'text': 'some', 'price': '98'}),
    ('discount', {'old_price': '8.7', 'new_price': '5'}),
]

BASIC_RECORD_VALUES = {
    'id': [1, 1000],
    'partner_id': [75],
    'title': ['Food', 'Two chickens for one price'],
    'subtitle': ['Good', None],
    'icon_uri': ['http://somewhere.com/image.png', None],
    'consumer': ['driver', 'courier'],
    'description_title': ['Good'],
    'description': ['Some big offer to our loyal drivers', None],
    'comment': ['Some text', None],
    'enabled': [True, False],
    'begin_at': [datetime.datetime.now() + datetime.timedelta(days=7)],
    'finish_at': [datetime.datetime.now() + datetime.timedelta(days=20), None],
    'created_at': [datetime.datetime.now()],
    'updated_at': [datetime.datetime.now()],
    'created_by': ['king'],
    'updated_by': ['somebody'],
    'map_pin_text': ['map text', None],
    'contractor_merch_offer_id': ['100500', None],
}


def _generate_valid_dicts():
    basic_good = {k: BASIC_RECORD_VALUES[k][0] for k in BASIC_RECORD_VALUES}
    basic_good['kind'] = VALID_COUPON_PAIRS[0][0]
    basic_good['kind_json'] = json.dumps(VALID_COUPON_PAIRS[0][1])
    results: list = [{**basic_good}]
    for key in BASIC_RECORD_VALUES:
        for value in BASIC_RECORD_VALUES[key][1:]:
            results.append({**basic_good, key: value})
    results += [
        {**basic_good, 'kind': kind[0], 'kind_json': json.dumps(kind[1])}
        for kind in VALID_COUPON_PAIRS
    ]
    return results


def _generate_invalid_records():
    good = BASIC_RECORD_VALUES
    basic_good = {k: good[k][0] for k in good}
    results = []
    replacements = {
        bool: False,
        str: 'something',
        int: 5,
        datetime.datetime: datetime.datetime.now(),
    }
    for key in good:
        missed_key = {**basic_good}
        del missed_key[key]
        results.append(missed_key)
        original_type = type([x for x in good[key] if x is not None][0])
        new_type = [x for x in replacements if x != original_type][0]
        invalid_type = {**basic_good, key: replacements[new_type]}
        results.append(invalid_type)
        if None not in good[key]:
            none_val = {**basic_good, key: None}
            results.append(none_val)
    for elem in results:
        elem['kind'] = VALID_COUPON_PAIRS[0][0]
        elem['kind_json'] = VALID_COUPON_PAIRS[0][1]

    results += [
        {**basic_good, 'kind': kind[0], 'kind_json': json.dumps(kind[1])}
        for kind in INVALID_COUPON_PAIRS
    ]
    results += [{**basic_good, 'consumer': 'unknown_consumer'}]
    return results


@pytest.mark.parametrize('record', _generate_valid_dicts())
async def test_valid_asyncpg_parse(record, pgsql):
    with pgsql['partner_offers'].cursor() as cursor:
        query = """select column_name from information_schema.columns
             where table_name = 'deal';"""
        cursor.execute(query)
        columns = {x[0] for x in cursor.fetchall()}
    for key in record:
        assert key in columns, columns
    _ = models.DealWithChangelog.from_asyncpg(record)


@pytest.mark.parametrize('record', _generate_invalid_records())
def test_invalid_asyncpg_parse(record):
    try:
        _ = models.DealWithChangelog.from_asyncpg(record)
        assert False, record
    except models.InvalidDataclassSqlError:
        return


def test_changelog():
    basic_good = {x: BASIC_RECORD_VALUES[x][0] for x in BASIC_RECORD_VALUES}
    basic_good.update(
        {
            'kind': VALID_COUPON_PAIRS[0][0],
            'kind_json': json.dumps(VALID_COUPON_PAIRS[0][1]),
        },
    )
    changelog = models.ChangeLog.from_asyncpg(basic_good)
    deal = models.Deal.from_asyncpg(basic_good)
    # Must not have duplicates
    assert not {
        x
        for x in dataclasses.asdict(changelog)
        if x in dataclasses.asdict(deal)
    }

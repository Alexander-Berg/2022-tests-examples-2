import datetime

import pytest

from partner_offers import models

BASIC_RECORD_VALUES = {
    'business_oid': [1000],
    'partner_id': [75],
    'longitude': [79.4],
    'latitude': [-7.123123],
    'name': ['Some name'],
    'country': ['Россия', None],
    'city': ['Ярославль', None],
    'address': ['Россия, Краснодарский край, Сочи, Курортный проспект, 73'],
    'work_time_intervals': [
        '[]',
        '[{"from": 1572347352, "to":1572357352}, {"from":1572358352, "to":1572359352}]',  # noqa: E501
    ],
    'tz_offset': [1500, 0, -405, 10800],
}


def _generate_valid_dicts():
    basic_good = {k: BASIC_RECORD_VALUES[k][0] for k in BASIC_RECORD_VALUES}
    results: list = [{**basic_good}]
    for key in BASIC_RECORD_VALUES:
        for value in BASIC_RECORD_VALUES[key][1:]:
            results.append({**basic_good, key: value})
    return results


@pytest.mark.parametrize('record', _generate_valid_dicts())
async def test_valid_asyncpg_parse(record, pgsql):
    with pgsql['partner_offers'].cursor() as cursor:
        query = """select column_name from information_schema.columns
             where table_name = 'location';"""
        cursor.execute(query)
        columns = {x[0] for x in cursor.fetchall()}
    for key in record:
        assert key in columns, columns
    _ = models.Location.from_asyncpg(record)


def _generate_invalid_records(key_variants: dict):
    keys = list(key_variants)
    basic_good = {k: key_variants[k][0] for k in key_variants}
    results = []
    replacements = {
        str: 'something',
        int: 5,
        datetime.datetime: datetime.datetime.now(),
    }
    for key in keys:
        missed_key = {**basic_good}
        del missed_key[key]
        results.append(missed_key)
        original_type = type(
            [x for x in key_variants[key] if x is not None][0],
        )
        new_type = [x for x in replacements if x != original_type][0]
        invalid_type = {**basic_good, key: replacements[new_type]}
        results.append(invalid_type)
        if None not in key_variants[key]:
            none_val = {**basic_good, key: None}
            results.append(none_val)
    return results


@pytest.mark.parametrize(
    'record', _generate_invalid_records(BASIC_RECORD_VALUES),
)
def test_invalid_asyncpg_parse(record):
    try:
        _ = models.Location.from_asyncpg(record)
        assert False, record
    except models.InvalidDataclassSqlError:
        return

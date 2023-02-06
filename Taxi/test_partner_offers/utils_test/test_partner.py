import dataclasses
import datetime

import pytest

from partner_offers import models

BASIC_RECORD_VALUES = {
    'id': [1, 1000],
    'geo_chain_id': [75, None],
    'category': ['Food', 'cleaning'],
    'name': ['Autovaz'],
    'logo': ['https://example.org/image.png', None],
    'comment': ['Something', None],
    'created_at': [datetime.datetime.now()],
    'updated_at': [datetime.datetime.now()],
    'created_by': ['king'],
    'updated_by': ['somebody'],
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
        query = (
            'select column_name from information_schema.columns'
            # pylint: disable=invalid-string-quote
            ' where table_name = \'partner\';'
        )
        cursor.execute(query)
        columns = {x[0] for x in cursor.fetchall()}
    for key in record:
        assert key in columns, columns
    _ = models.PartnerWithChangelog.from_asyncpg(record)


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
        _ = models.PartnerWithChangelog.from_asyncpg(record)
        assert False, record
    except models.InvalidDataclassSqlError:
        return


def test_changelog():
    basic_good = {x: BASIC_RECORD_VALUES[x][0] for x in BASIC_RECORD_VALUES}
    changelog = models.ChangeLog.from_asyncpg(basic_good)
    partner = models.Partner.from_asyncpg(basic_good)
    # Must not have duplicates
    assert not {
        x
        for x in dataclasses.asdict(changelog)
        if x in dataclasses.asdict(partner)
    }

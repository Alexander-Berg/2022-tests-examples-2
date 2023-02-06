import collections
import datetime
import itertools

import pytest

from taxi_billing_replication import types
from taxi_billing_replication.stuff import common


@pytest.mark.parametrize(
    'old_rows_by_ids,new_rows_by_ids,fields,expected',
    [
        # Test with extra data on both sides
        (
            {1: {'a': 1, 'b': 'z'}, 3: {'a': 2, 'b': 'x'}},
            {1: {'a': 1, 'b': 'z'}, 2: {'a': 3, 'b': 'y'}},
            ['a', 'b'],
            [],
        ),
        # Test on array in different order
        (
            {1: {'a': 1, 'b': [1, 2, 3], 'x': ['a', 'b', 'c']}},
            {1: {'a': 1, 'b': [2, 1, 3], 'x': ['c', 'b', 'a']}},
            ['a', 'b', 'x'],
            [],
        ),
        # Test on arrays of different length + absent array
        (
            {1: {'b': [1, 2, 3], 'd': [1, 4]}},
            {1: {'b': [1, 2], 'c': ['c', 'b', 'a']}},
            ['b', 'c', 'd'],
            [
                types.FieldDiff(
                    id=1, field='b', before=str([1, 2, 3]), after=str([1, 2]),
                ),
                types.FieldDiff(
                    id=1, field='d', before=str([1, 4]), after='None',
                ),
                types.FieldDiff(
                    id=1, field='c', before='None', after=str(['c', 'b', 'a']),
                ),
            ],
        ),
        # Test no diff with extra keys
        (
            {1: {'a': 1, 'b': [1, 2, 3], 'x': 1}},
            {1: {'a': 1, 'b': [1, 2, 3], 'x': 2}},
            ['a', 'b'],
            [],
        ),
        (
            {
                787291: {
                    'NDS': 0,
                    'PAY_TO': 1,
                    'CURRENCY': 'RUR',
                    'COUNTRY': 225,
                    'IS_SUSPENDED': 0,
                    'IS_ACTIVE': 0,
                    'IS_SIGNED': 1,
                    'CONTRACT_TYPE': 81,
                    'PERSON_ID': 7638754,
                    'IS_FAXED': 0,
                    'SERVICES': [135],
                    'REGION': '02000001000',
                    'IS_CANCELLED': 0,
                    'DT': datetime.datetime(2019, 5, 24, 0, 0),
                    'EXTERNAL_ID': 'РАС-259355',
                    'ID': 787291,
                    'OFFER_ACCEPTED': 0,
                },
                787292: {
                    'NDS': 0,
                    'PAY_TO': 1,
                    'CURRENCY': 'RUR',
                    'COUNTRY': 225,
                    'IS_SUSPENDED': 1,
                    'LINK_CONTRACT_ID': 787290,
                    'IS_ACTIVE': 0,
                    'IS_SIGNED': 0,
                    'CONTRACT_TYPE': 87,
                    'PERSON_ID': 7638754,
                    'IS_FAXED': 0,
                    'SERVICES': [137],
                    'REGION': '02000001000',
                    'IS_CANCELLED': 0,
                    'DT': datetime.datetime(2019, 5, 24, 0, 0),
                    'EXTERNAL_ID': 'ОФ-252486/19',
                    'ID': 787292,
                },
            },
            {
                787291: {
                    'NDS': 0,
                    'PAY_TO': 1,
                    'CURRENCY': 'RUR',
                    'COUNTRY': 225,
                    'IS_SUSPENDED': 0,
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'CONTRACT_TYPE': 81,
                    'PERSON_ID': 7638754,
                    'IS_FAXED': 0,
                    'SERVICES': [135],
                    'REGION': '02000001000',
                    'IS_CANCELLED': 0,
                    'DT': datetime.datetime(2019, 5, 24, 0, 0),
                    'EXTERNAL_ID': 'РАС-259355',
                    'ID': 787291,
                    'OFFER_ACCEPTED': 1,
                    'NETTING': None,
                    'NETTING_PCT': None,
                    'NDS_FOR_RECEIPT': None,
                    'PAYMENT_TYPE': None,
                    'PARTNER_COMMISSION_PCT': None,
                    'PARTNER_COMMISSION_PCT2': None,
                    'IND_BEL_NDS': None,
                    'IND_BEL_NDS_PERCENT': None,
                    'END_DT': datetime.datetime(2019, 1, 24, 0, 0),
                },
                787292: {
                    'NDS': 0,
                    'PAY_TO': 1,
                    'CURRENCY': 'RUR',
                    'COUNTRY': 225,
                    'IS_SUSPENDED': 0,
                    'LINK_CONTRACT_ID': 787290,
                    'IS_ACTIVE': 1,
                    'IS_SIGNED': 1,
                    'CONTRACT_TYPE': 87,
                    'PERSON_ID': 7638754,
                    'IS_FAXED': 0,
                    'SERVICES': [137],
                    'REGION': '02000001000',
                    'IS_CANCELLED': 0,
                    'DT': datetime.datetime(2019, 5, 24, 0, 0),
                    'EXTERNAL_ID': 'ОФ-252486/19',
                    'ID': 787292,
                    'FINISH_DT': datetime.datetime(2019, 3, 4, 0, 0, 0),
                    'NETTING': None,
                    'NETTING_PCT': None,
                    'NDS_FOR_RECEIPT': None,
                    'PAYMENT_TYPE': None,
                    'PARTNER_COMMISSION_PCT': None,
                    'PARTNER_COMMISSION_PCT2': None,
                    'IND_BEL_NDS': None,
                    'IND_BEL_NDS_PERCENT': None,
                    'END_DT': datetime.datetime(2020, 1, 1, 0, 0),
                },
            },
            [
                'ID',
                'EXTERNAL_ID',
                'PERSON_ID',
                'IS_ACTIVE',
                'IS_SIGNED',
                'IS_SUSPENDED',
                'CURRENCY',
                'NETTING',
                'NETTING_PCT',
                'LINK_CONTRACT_ID',
                'SERVICES',
                'NDS_FOR_RECEIPT',
                'OFFER_ACCEPTED',
                'NDS',
                'PAYMENT_TYPE',
                'PARTNER_COMMISSION_PCT',
                'PARTNER_COMMISSION_PCT2',
                'IND_BEL_NDS_PERCENT',
                'END_DT',
                'FINISH_DT',
                'DT',
                'CONTRACT_TYPE',
                'IND_BEL_NDS',
            ],
            [
                types.FieldDiff(
                    id=787291,
                    field='END_DT',
                    before='None',
                    after='2019-01-24 00:00:00',
                ),
                types.FieldDiff(
                    id=787291, field='IS_ACTIVE', before='0', after='1',
                ),
                types.FieldDiff(
                    id=787291, field='OFFER_ACCEPTED', before='0', after='1',
                ),
                types.FieldDiff(
                    id=787292,
                    field='END_DT',
                    before='None',
                    after='2020-01-01 00:00:00',
                ),
                types.FieldDiff(
                    id=787292,
                    field='FINISH_DT',
                    before='None',
                    after='2019-03-04 00:00:00',
                ),
                types.FieldDiff(
                    id=787292, field='IS_ACTIVE', before='0', after='1',
                ),
                types.FieldDiff(
                    id=787292, field='IS_SIGNED', before='0', after='1',
                ),
                types.FieldDiff(
                    id=787292, field='IS_SUSPENDED', before='1', after='0',
                ),
            ],
        ),
        (
            {
                1: {
                    'ATTRIBUTES_HISTORY': (
                        '{'
                        '"SERVICES": '
                        '[["2020-01-01 00:00:00", [650]], '
                        '["2021-01-01 00:00:00", [650, 651]]]'
                        '}'
                    ),
                },
            },
            {
                1: {
                    'ATTRIBUTES_HISTORY': (
                        '{'
                        '"SERVICES": '
                        '[["2020-01-01 00:00:00", [650]], '
                        '["2021-01-01 00:00:00", [650, 651]]], '
                        '"PARTNER_COMMISSION_PCT2": '
                        '[["2020-01-01 00:00:00", "1"], '
                        '["2021-01-01 00:00:00", "2"]]'
                        '}'
                    ),
                },
            },
            ['ATTRIBUTES_HISTORY'],
            [
                types.FieldDiff(
                    id=1,
                    field='ATTRIBUTES_HISTORY',
                    before=(
                        '{'
                        '"SERVICES": '
                        '[["2020-01-01 00:00:00", [650]], '
                        '["2021-01-01 00:00:00", [650, 651]]]'
                        '}'
                    ),
                    after=(
                        '{'
                        '"SERVICES": '
                        '[["2020-01-01 00:00:00", [650]], '
                        '["2021-01-01 00:00:00", [650, 651]]], '
                        '"PARTNER_COMMISSION_PCT2": '
                        '[["2020-01-01 00:00:00", "1"], '
                        '["2021-01-01 00:00:00", "2"]]'
                        '}'
                    ),
                ),
            ],
        ),
    ],
)
def test_calculate_diffs(old_rows_by_ids, new_rows_by_ids, fields, expected):
    new_row_keys = set()
    for row in itertools.chain(
            new_rows_by_ids.values(), old_rows_by_ids.values(),
    ):
        new_row_keys.update(row.keys())

    new_row_type = collections.namedtuple('new_row_type', list(new_row_keys))
    all_none_tuple_data = {key: None for key in new_row_keys}

    new_row_tuples_by_ids = {
        id_: new_row_type(**{**all_none_tuple_data, **new_row})
        for id_, new_row in new_rows_by_ids.items()
    }

    diffs = common.calculate_diffs(
        old_rows_by_ids, new_row_tuples_by_ids, fields,
    )
    assert sorted(diffs) == sorted(expected)


@pytest.mark.parametrize(
    'value_type, raw_value, expected_value',
    [
        (
            types.Contract,
            {
                'ATTRIBUTES_HISTORY': {
                    'SERVICES': [
                        [datetime.datetime(2020, 12, 25, 0, 0), [650, 135]],
                        [
                            datetime.datetime(2021, 1, 20, 0, 0),
                            [650, 668, 135],
                        ],
                    ],
                    'PARTNER_COMMISSION_PCT2': [
                        [datetime.datetime(2020, 12, 25, 0, 0), '3.4'],
                    ],
                },
                'IS_ACTIVE': 1,
                'SERVICES': [650, 668, 135],
                'CURRENCY': 'RUR',
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 3,
                'CONTRACT_TYPE': 9,
                'DT': datetime.datetime(2020, 12, 25, 0, 0),
                'IS_CANCELLED': 0,
                'ID': 2594296,
                'IS_SUSPENDED': 0,
                'IS_SIGNED': 1,
                'IS_FAXED': 0,
                'PERSON_ID': 13475773,
                'IS_DEACTIVATED': 0,
                'EXTERNAL_ID': '1449534/20',
                'FIRM_ID': 13,
            },
            {
                'ATTRIBUTES_HISTORY': (
                    '{"SERVICES": [["2020-12-25 00:00:00", [650, 135]], '
                    '["2021-01-20 00:00:00", [650, 668, 135]]], '
                    '"PARTNER_COMMISSION_PCT2": ['
                    '["2020-12-25 00:00:00", "3.4"]]'
                    '}'
                ),
                'IS_ACTIVE': 1,
                'SERVICES': [650, 668, 135],
                'CURRENCY': 'RUR',
                'OFFER_ACCEPTED': 1,
                'PAYMENT_TYPE': 3,
                'CONTRACT_TYPE': 9,
                'DT': datetime.datetime(2020, 12, 25, 0, 0),
                'IS_CANCELLED': 0,
                'ID': 2594296,
                'IS_SUSPENDED': 0,
                'IS_SIGNED': 1,
                'IS_FAXED': 0,
                'PERSON_ID': 13475773,
                'IS_DEACTIVATED': 0,
                'EXTERNAL_ID': '1449534/20',
                'END_DT': None,
                'COUNTRY': None,
                'FINISH_DT': None,
                'FIRM_ID': 13,
                'IND_BEL_NDS': None,
                'IND_BEL_NDS_PERCENT': None,
                'LINK_CONTRACT_ID': None,
                'NDS': None,
                'NDS_FOR_RECEIPT': None,
                'NETTING': None,
                'NETTING_PCT': None,
                'PARTNER_COMMISSION_PCT': None,
                'PARTNER_COMMISSION_PCT2': None,
                'client_id': None,
                'status': None,
                'type': None,
            },
        ),
    ],
)
def test_convert_raw_value_to_type(value_type, raw_value, expected_value):
    actual_value = types.raw_value_to_type(raw_value, value_type)
    assert dict(actual_value.as_dict()) == expected_value

# flake8 noqa: E501
import datetime
import typing

import bson
import pytest

from chatterbox.internal.pi.search import common
from chatterbox.internal.pi.search import convert
from chatterbox.internal.pi.search import grammar
from chatterbox.internal.pi.search import parse
from chatterbox.internal.pi.search import query

CB_STATUSES = common.STATUS_PI_TO_CB


@pytest.mark.parametrize(
    'value_string, expected',
    [
        ('1', 1),
        ('12345', 12345),
        ('\'\'', ''),
        ('\'string with spaces\'', 'string with spaces'),
        ('(1)', [1]),
        ('(5,6)', [5, 6]),
        ('(11,22,44)', [11, 22, 44]),
        ('(\'11\',\'22\',\'44\')', ['11', '22', '44']),
    ],
)
def test_parse_value__given_valid_string__works(
        value_string: str, expected: typing.Any,
):
    value = parse.parse_full(value_string, grammar.Value)
    assert expected == value.value()


@pytest.mark.parametrize('value_string', ['0x16', '--0+', 'qwe'])
def test_parse_value__given_invalid_string__raises(value_string: str):
    with pytest.raises(common.ParseQueryException):
        parse.parse_full(value_string, grammar.Value)


EXPRESSIONS = [
    'x = 1',
    'x != 0',
    'x in (-2,-1,0,1,2)',
    'x.y > fAlSe',
    'x = TRUE',
    'status != \'CLOSED\'',
    'comment != \'Возврат\'',
    'title regexp \'Эльдорадо\'',
    'details.theme in (\'A\', \'B\', \'C\')',
    'lang not in (\'ru\', \'en\')',
    'a > 2 and a < 8',
    'updated > \'day ago\'',
    """created > \'2020-10-10\' and details.theme = \'A\'
        or status = \'OPEN\' and new_comments = true""",
    'status = \'NEED_INFO\' or new_comments = true',
]

PI_QUERIES = [
    {'x': {'$eq': 1}},
    {'x': {'$ne': 0}},
    {'x': {'$in': list(range(-2, 3))}},
    {'x.y': {'$gt': False}},
    {'x': {'$eq': True}},
    {'status': {'$ne': 'CLOSED'}},
    {'comment': {'$ne': 'Возврат'}},
    {'title': {'$regex': 'Эльдорадо'}},
    {'details.theme': {'$in': ['A', 'B', 'C']}},
    {'lang': {'$nin': ['ru', 'en']}},
    {'$and': [{'a': {'$gt': 2}}, {'a': {'$lt': 8}}]},
    {'updated': {'$gt': 'day ago'}},
    {
        '$or': [
            {
                '$and': [
                    {'created': {'$gt': '2020-10-10'}},
                    {'details.theme': {'$eq': 'A'}},
                ],
            },
            {
                '$and': [
                    {'status': {'$eq': 'OPEN'}},
                    {'new_comments': {'$eq': True}},
                ],
            },
        ],
    },
    {
        '$or': [
            {'status': {'$eq': 'NEED_INFO'}},
            {'new_comments': {'$eq': True}},
        ],
    },
]


@pytest.mark.parametrize('expr_string', EXPRESSIONS)
def test_parse_expression__given_valid_string__works(expr_string: str):
    parse.parse_full(expr_string, grammar.Expression)


INVALID_EXPRESSIONS = [
    '',
    'q',
    '1',
    '"',
    '""',
    '@',
    '\'',
    '\'\'',
    '(',
    '((1))',
    '()',
    '<',
    '<>',
    '((x) > (y))',
    '1 2',
    '1 > 2',
    'id',
    ' a b c',
    'for (i in xs)',
    'x or',
    'and > or',
    'x > 1 and',
    'status !=! \'CLOSED\'',
    'comment \'Возврат\'',
    'title regexpsps \'Эльдорадо\'',
    'details.theme.park inside (\'A\', \'B\', \'C\')',
    'lang not in (\'ru\',, \'en\')',
    'in (1,2)',
    'a > 2 or and a < 8',
    '<updated> 4',
]


@pytest.mark.parametrize('expr_string', INVALID_EXPRESSIONS)
def test_parse_expression__given_invalid_string__raises(expr_string: str):
    with pytest.raises(common.ParseQueryException):
        parse.parse_full(expr_string, grammar.Expression)


@pytest.mark.parametrize(
    'expr_string, expected_pi_query', zip(EXPRESSIONS, PI_QUERIES),
)
def test_expression_query__produces_expected_pi_queries(
        expr_string: str, expected_pi_query: common.Query,
):
    expr = parse.parse_full(expr_string, grammar.Expression)
    assert expr.query() == expected_pi_query


VALID_PI_EXPRESSIONS = [
    'status = \'CLOSED\'',
    'status != \'CLOSED\'',
    'status in (\'CLOSED\', \'NEED_INFO\')',
    'status not in (\'NEED_INFO\', \'CLOSED\')',
    'ticket_id = \'5c110942031552e65884ba0c\'',
    """ticket_id in ('abcdefabcdef123456123456',
                     'aaaaaaaaaaaaaaaaaaaaaaaa')""",
    'details.theme in (\'A\', \'B\', \'C\')',
    'updated > \'2020-01-01\'',
    'created = \'2021-07-04\'',
    """created > '2021-12-24' and details.theme = 'A'
       or status = 'NEED_INFO' """,
]

VALID_PI_QUERIES = [
    {'status': {'$eq': 'CLOSED'}},
    {'status': {'$ne': 'CLOSED'}},
    {'status': {'$in': ['CLOSED', 'NEED_INFO']}},
    {'status': {'$nin': ['NEED_INFO', 'CLOSED']}},
    {'ticket_id': {'$eq': '5c110942031552e65884ba0c'}},
    {
        'ticket_id': {
            '$in': ['abcdefabcdef123456123456', 'aaaaaaaaaaaaaaaaaaaaaaaa'],
        },
    },
    {'details.theme': {'$in': ['A', 'B', 'C']}},
    {'updated': {'$gt': '2020-01-01'}},
    {'created': {'$eq': '2021-07-04'}},
    {
        '$or': [
            {
                '$and': [
                    {'created': {'$gt': '2021-12-24'}},
                    {'details.theme': {'$eq': 'A'}},
                ],
            },
            {'status': {'$eq': 'NEED_INFO'}},
        ],
    },
]

MONGO_QUERIES = [
    {'status': {'$in': CB_STATUSES['CLOSED']}},
    {'status': {'$nin': CB_STATUSES['CLOSED']}},
    {'status': {'$in': (CB_STATUSES['CLOSED'] + CB_STATUSES['NEED_INFO'])}},
    {'status': {'$nin': (CB_STATUSES['NEED_INFO'] + CB_STATUSES['CLOSED'])}},
    {'_id': {'$eq': bson.ObjectId('5c110942031552e65884ba0c')}},
    {
        '_id': {
            '$in': [
                bson.ObjectId('abcdefabcdef123456123456'),
                bson.ObjectId('aaaaaaaaaaaaaaaaaaaaaaaa'),
            ],
        },
    },
    {'meta_info.partner_details.theme': {'$in': ['A', 'B', 'C']}},
    {'updated': {'$gt': datetime.datetime(2020, 1, 1)}},
    {'created': {'$eq': datetime.datetime(2021, 7, 4)}},
    {
        '$or': [
            {
                '$and': [
                    {'created': {'$gt': datetime.datetime(2021, 12, 24)}},
                    {'meta_info.partner_details.theme': {'$eq': 'A'}},
                ],
            },
            {'status': {'$in': CB_STATUSES['NEED_INFO']}},
        ],
    },
]

INVALID_PI_QUERIES = [
    {'x': {'$eq': 1}},
    {'x.y': {'$gt': False}},
    {'mystatus': {'$ne': 1}},
    {'comment': {'$ne': 'Возврат'}},
    {'title': {'$regex': 'Эльдорадо'}},
    {'info.theme': {'$in': ['A', 'B', 'C']}},
    {'lang': {'$nin': ['ru', 'en']}},
    {'$and': [{'a': {'$gt': 2}}, {'a': {'$lt': 8}}]},
    {
        '$or': [
            {
                '$and': [
                    {'new_comments': {'$eq': True}},
                    {'details.theme': {'$eq': 'A'}},
                ],
            },
            {
                '$and': [
                    {'status': {'$eq': 'OPEN'}},
                    {'created': {'$gt': 'week ago'}},
                ],
            },
        ],
    },
]


@pytest.mark.parametrize(
    'pi_query, expected_mongo_query', zip(VALID_PI_QUERIES, MONGO_QUERIES),
)
def test_make_chatterbox_query__given_valid_pi_query__works_as_expected(
        pi_query: common.Query, expected_mongo_query: common.Query,
):
    assert convert.make_chatterbox_query(pi_query) == expected_mongo_query


@pytest.mark.parametrize('pi_query', INVALID_PI_QUERIES)
def test_make_chatterbox_query__given_invalid_pi_query__raises(
        pi_query: common.Query,
):
    with pytest.raises(common.ConvertQueryException):
        convert.make_chatterbox_query(pi_query)


def test_chatterbox_query__given_different_pids__works_as_expected():
    expr = ''
    with pytest.raises(common.QueryException):
        query.ChatterboxQuery(expr, [])

    partner_ids = ['a']
    cbox_query = query.ChatterboxQuery(expr, partner_ids)
    assert cbox_query.query == {'meta_info.partner_id': {'$eq': 'a'}}

    for pid in 'bcdef':
        partner_ids.append(pid)
        cbox_query = query.ChatterboxQuery(expr, partner_ids)
        assert cbox_query.query == {
            'meta_info.partner_id': {'$in': partner_ids},
        }

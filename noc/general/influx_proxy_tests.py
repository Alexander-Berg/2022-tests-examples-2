# coding: utf-8
import json

import pytest

from influx_proxy_async import apply_sumseries, make_other, try_json
from influxql_parser import parse_query
from tag_grouping import get_by_tag, get_ifname_tags


class TestInfluxqlParser:
    @pytest.fixture
    def phase1_results(self):
        yield {
            'results': [
                {
                    'series': [
                        {
                            'columns': ['time', 'aggr_result'],
                            'name': 'weblog',
                            'tags': {'url': '/url3/'},
                            'values': [[1490093699908, 3]],
                        },
                        {
                            'columns': ['time', 'aggr_result'],
                            'name': 'weblog',
                            'tags': {'url': '/url2/'},
                            'values': [[1490093699908, 2]],
                        },
                        {
                            'columns': ['time', 'aggr_result'],
                            'name': 'weblog',
                            'tags': {'url': '/url1/'},
                            'values': [[1490093699908, 1]],
                        },
                        {
                            'columns': ['time', 'aggr_result'],
                            'name': 'weblog',
                            'tags': {'url': '/url4/'},
                            'values': [[1490093699908, 4]],
                        },
                    ],
                    'statement_id': 0,
                }
            ]
        }

    @pytest.mark.parametrize(
        'query, expected',
        (
            (
                'SELECT a FROM "b" WHERE c =~ /.*/',
                'SELECT a FROM "b" WHERE TRUE',
            ),
            (
                'SELECT a FROM "b" WHERE c =~ /.*/ AND (d =~ /^.*$/)',
                'SELECT a FROM "b" WHERE TRUE AND (TRUE)',
            ),
            (
                'SELECT a FROM "b" WHERE c =~ /^(.*)$/',
                'SELECT a FROM "b" WHERE TRUE',
            ),
            (
                'SELECT a / 30s FROM "b" GROUP BY time(30s) fill(null)',
                'SELECT a / 30 FROM "b" GROUP BY TIME(30s) FILL(null)',
            ),
            (
                'SELECT a / 10m FROM "b" GROUP BY time(10m) FILL(null)',
                'SELECT a / 600 FROM "b" GROUP BY TIME(10m) FILL(null)',
            ),
            (
                (r"""SELECT a FROM "b" WHERE c ~ '~ \/any\.\*thing\\\.\/'""" r"""AND d = 4"""),
                r'SELECT a FROM "b" WHERE c =~ /(?i)any.*thing\./ AND d = 4',
            ),
            (
                r'''SELECT a FROM "b" WHERE c ~ 'any\.\*thing' AND d = 4''',
                r'SELECT a FROM "b" WHERE c =~ /^(any.*thing)$/ AND d = 4',
            ),
            (
                r'''SELECT a FROM "b" WHERE c ~ 'any\.\*thing\/24' AND d = 4''',
                r'SELECT a FROM "b" WHERE c =~ /^(any.*thing\/24)$/ AND d = 4',
            ),
        ),
    )
    def test_fix_expressions(self, query, expected):
        parsed = parse_query(query)
        assert str(parsed[0].fix_expresions()) == expected

    @pytest.mark.parametrize(
        'query, expected',
        (
            (
                'SELECT a FROM "b" WHERE c = 1',
                'SELECT a FROM "b" WHERE c = 1',
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY (url)',
                'SELECT a FROM "b" WHERE c = 1',
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY (url) USING MAX',
                'SELECT a FROM "b" WHERE c = 1',
            ),
            (
                ('SELECT a FROM "b" GROUP BY time(10m) SWAP ((a, d)) ' 'TOP 5 e BY (f)'),
                'SELECT a FROM "b" GROUP BY TIME(10m)',
            ),
            (
                'SELECT * FROM "b" WHERE c = 1',
                'SELECT * FROM "b" WHERE c = 1',
            ),
            (
                'SELECT MEAN(*) FROM "b" WHERE c = 1',
                'SELECT MEAN(*) FROM "b" WHERE c = 1',
            ),
            (
                'SELECT * FROM b WHERE c = 1',
                'SELECT * FROM b WHERE c = 1',
            ),
            (
                'SELECT * FROM b.a WHERE c = 1',
                'SELECT * FROM b.a WHERE c = 1',
            ),
            (
                'SELECT * FROM b.a.c WHERE c = 1',
                'SELECT * FROM b.a.c WHERE c = 1',
            ),
            (
                'SELECT * FROM b..c WHERE c = 1',
                'SELECT * FROM b..c WHERE c = 1',
            ),
            (
                'SELECT * FROM b."a".c WHERE c = 1',
                'SELECT * FROM b."a".c WHERE c = 1',
            ),
            (
                'SELECT a FROM "b" GROUP BY TIME(10m) FILL(0)',
                'SELECT a FROM "b" GROUP BY TIME(10m) FILL(0)',
            ),
            (
                'SELECT DERIVATIVE(water_level, 6m) FROM "b" WHERE c = 1',
                'SELECT DERIVATIVE(water_level, 6m) FROM "b" WHERE c = 1',
            ),
            (
                'SELECT TIME() FROM "b" WHERE c = 1',
                'SELECT TIME() FROM "b" WHERE c = 1',
            ),
            (
                'SELECT SUMSERIES a FROM "b"',
                'SELECT a FROM "b"',
            ),
        ),
    )
    def test_get_orig_query(self, query, expected):
        parsed = parse_query(query)
        assert str(parsed[0].get_orig_query()) == expected

    @pytest.mark.parametrize(
        'query, expected',
        (
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY (url)',
                'SELECT SUM(rps) AS aggr_result FROM "b" WHERE c = 1 GROUP BY url',
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY (url) USING SUM',
                'SELECT SUM(rps) AS aggr_result FROM "b" WHERE c = 1 GROUP BY url',
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY (url) USING MAX',
                'SELECT MAX(rps) AS aggr_result FROM "b" WHERE c = 1 GROUP BY url',
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY (url) USING MEAN',
                ('SELECT MEAN(rps) AS aggr_result FROM "b" WHERE c = 1 ' 'GROUP BY url'),
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY (url|vlan)',
                ('SELECT SUM(rps) AS aggr_result FROM "b" WHERE c = 1 ' 'GROUP BY url, vlan'),
            ),
            (
                ('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s) ' 'SWAP((url, vlan)) TOP 5 rps BY (url|vlan)'),
                ('SELECT SUM(rps) AS aggr_result FROM "b" WHERE c = 1 ' 'GROUP BY vlan, url'),
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY url',
                'SELECT SUM(rps) AS aggr_result FROM "b" WHERE c = 1 GROUP BY url',
            ),
            (
                ('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s) ' 'SWAP((url, vlan)) TOP 5 rps BY url|vlan'),
                ('SELECT SUM(rps) AS aggr_result FROM "b" WHERE c = 1 ' 'GROUP BY vlan, url'),
            ),
            (
                'SELECT a FROM "b" WHERE c = 1 TOP 5 rps BY ()',
                '',
            ),
        ),
    )
    def test_get_top_query_phase1(self, query, expected):
        parsed = parse_query(query)
        assert str(parsed[0].get_top_query_phase1() or '') == expected

    def test_multiselect(self):
        parsed = parse_query('SELECT a FROM "b";SELECT c FROM "d"')
        assert str(parsed[0]) == 'SELECT a FROM "b"'
        assert str(parsed[1]) == 'SELECT c FROM "d"'

    @pytest.mark.parametrize(
        'query, expected',
        (
            (
                'SELECT a FROM "b" GROUP BY TIME(30s) TOP 3 rps BY (url)',
                (
                    'SELECT a FROM "b" WHERE '
                    '''(("url" = '/url2/') OR ("url" = '/url3/') OR ("url" = '/url4/')) '''
                    'GROUP BY url, TIME(30s)'
                ),
            ),
            (
                'SELECT a FROM "b" GROUP BY TIME(30s) TOP 3+ rps BY (url)',
                (
                    'SELECT a FROM "b" WHERE '
                    '''(("url" = '/url2/') OR ("url" = '/url3/') OR ("url" = '/url4/')) '''
                    'GROUP BY url, TIME(30s)'
                ),
            ),
            (
                ('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s) ' 'TOP 3 rps BY (url)'),
                (
                    'SELECT a FROM "b" WHERE c = 1 AND '
                    '''(("url" = '/url2/') OR ("url" = '/url3/') OR ("url" = '/url4/')) '''
                    'GROUP BY url, TIME(30s)'
                ),
            ),
            (
                ('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s) ' 'SWAP((not_url, url)) TOP 3 rps BY (not_url)'),
                (
                    'SELECT a FROM "b" WHERE c = 1 AND '
                    '''(("url" = '/url2/') OR ("url" = '/url3/') OR ("url" = '/url4/')) '''
                    'GROUP BY url, TIME(30s)'
                ),
            ),
            (
                'SELECT a FROM "b" GROUP BY TIME(30s) TOP 3: rps BY (url)',
                (
                    'SELECT a FROM "b" WHERE '
                    '''(("url" != '/url2/') AND ("url" != '/url3/') AND ("url" != '/url4/')) '''
                    'GROUP BY url, TIME(30s)'
                ),
            ),
        ),
    )
    def test_get_top_query_phase2(self, query, expected, phase1_results):
        parsed = parse_query(query)
        assert str(parsed[0].get_top_query_phase2(phase1_results)) == expected

    @pytest.mark.parametrize(
        'query, expected',
        (
            ('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s)', False),
            (('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s) ' 'TOP 3 rps BY (url)'), False),
            (('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s) ' 'TOP 3+ rps BY (url)'), True),
        ),
    )
    def test_needs_top_query_phase3(self, query, expected):
        parsed = parse_query(query)
        assert parsed[0].needs_top_query_phase3() == expected

    @pytest.mark.parametrize(
        'query, expected',
        (
            (
                'SELECT a FROM "b" GROUP BY TIME(30s) TOP 3+ rps BY (url)',
                (
                    'SELECT a FROM "b" WHERE '
                    '''(("url" != '/url2/') AND ("url" != '/url3/') AND ("url" != '/url4/')) '''
                    'GROUP BY TIME(30s)'
                ),
            ),
            (
                ('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s) ' 'TOP 3+ rps BY (url)'),
                (
                    'SELECT a FROM "b" WHERE c = 1 AND '
                    '''(("url" != '/url2/') AND ("url" != '/url3/') AND ("url" != '/url4/')) '''
                    'GROUP BY TIME(30s)'
                ),
            ),
        ),
    )
    def test_get_top_query_phase3(self, query, expected, phase1_results):
        parsed = parse_query(query)
        assert str(parsed[0].get_top_query_phase3(phase1_results)) == expected

    @pytest.mark.parametrize(
        'query', (('SELECT a FROM "b" WHERE c = 1 GROUP BY TIME(30s), error ' 'TOP 3+ rps BY (error)'),)
    )
    def test_validate(self, query):
        with pytest.raises(ValueError):
            parse_query(query)


@pytest.mark.parametrize(
    'text, expected',
    (
        (
            {
                'results': [
                    {
                        'series': [
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url3/'},
                                'values': [[1490093699908, 3]],
                            },
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url2/'},
                                'values': [[1490093699908, 2]],
                            },
                        ],
                        'statement_id': 0,
                    },
                    {
                        'series': [
                            {'columns': ['time', 'aggr_result'], 'name': 'weblog', 'values': [[1490093699908, 4]]},
                            {'columns': ['time', 'aggr_result'], 'name': 'weblog', 'values': [[1490093699908, 6]]},
                        ],
                        'statement_id': 1,
                    },
                ]
            },
            {
                'results': [
                    {
                        'series': [
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url3/'},
                                'values': [[1490093699908, 3]],
                            },
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url2/'},
                                'values': [[1490093699908, 2]],
                            },
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '[OTHER]'},
                                'values': [[1490093699908, 4]],
                            },
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '[OTHER]'},
                                'values': [[1490093699908, 6]],
                            },
                        ],
                        'statement_id': 0,
                    },
                ]
            },
        ),
        (
            {
                'results': [
                    {
                        'series': [
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url3/'},
                                'values': [[1490093699908, 3]],
                            },
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url2/'},
                                'values': [[1490093699908, 2]],
                            },
                        ],
                        'statement_id': 0,
                    },
                    {
                        'statement_id': 1,
                    },
                ]
            },
            {
                'results': [
                    {
                        'series': [
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url3/'},
                                'values': [[1490093699908, 3]],
                            },
                            {
                                'columns': ['time', 'aggr_result'],
                                'name': 'weblog',
                                'tags': {'url': '/url2/'},
                                'values': [[1490093699908, 2]],
                            },
                        ],
                        'statement_id': 0,
                    },
                ]
            },
        ),
    ),
)
def test_make_other(text, expected):
    results = json.dumps(text)
    assert json.loads(make_other(results, {'url'})) == expected


def test_apply_sumseries():
    orig_response = json.dumps(
        {
            'results': [
                {
                    'statement_id': 0,
                    'series': [
                        {
                            'name': 'network',
                            'tags': {'host': 'iva-b-decap1', 'ifname': 'lagg0'},
                            'columns': ['time', 'rx_pps'],
                            'values': [[1510063200000, 1], [1510063500000, 2], [1510063800000, None]],
                        },
                        {
                            'name': 'network',
                            'tags': {'host': 'iva-b-decap2', 'ifname': 'lagg0'},
                            'columns': ['time', 'rx_pps'],
                            'values': [[1510063200000, 3], [1510063500000, None], [1510063800000, None]],
                        },
                        {
                            'name': 'network',
                            'tags': {'host': 'iva-b-decap4', 'ifname': 'lagg0'},
                            'columns': ['time', 'rx_pps'],
                            'values': [[1510063200000, 4]],
                        },
                    ],
                }
            ]
        }
    )

    response = apply_sumseries(orig_response)

    assert json.loads(response) == {
        'results': [
            {
                'statement_id': 0,
                'series': [
                    {
                        'name': 'network',
                        'tags': {'host': '[SUMSERIES]', 'ifname': '[SUMSERIES]'},
                        'columns': ['time', 'rx_pps'],
                        'values': [[1510063200000, 8], [1510063500000, 2], [1510063800000, None]],
                    },
                ],
            }
        ]
    }


@pytest.mark.parametrize(
    'ifnames, tagname, expected',
    (
        (['100GE1/0/0', '100GE2/0/0', '100GE2/0/0.345'], '100GE1/∗', ['100GE1/0/0']),
        (['100GE1/0/0', '100GE2/0/0', '100GE2/0/0.345'], '100GE2/∗', ['100GE2/0/0']),
        (['100GE1/0/0', '100GE2/0/0', '100GE2/0/0.345'], '∗.345', ['100GE2/0/0.345']),
    ),
)
def test_get_by_tag(ifnames, tagname, expected):
    assert get_by_tag(ifnames, tagname) == expected


def test_get_ifname_tags():
    ifnames = [
        '10GE1/0/1',
        '10GE1/0/2',
        '10GE1/0/2.3013',
        '10GE1/0/3',
        '10GE1/0/3.3013',
        '10GE1/0/4',
        '40GE1/0/1',
        '40GE1/0/2',
        'Console9/0/0',
        'Eth-Trunk10',
        'GE1/0/1',
        'GE1/0/10',
        'GE1/0/11',
        'GE1/0/12',
        'GE1/0/13',
        'GE1/0/14',
        'GE1/0/15',
        'GE1/0/16',
        'GE1/0/17',
        'GE1/0/18',
        'GE1/0/19',
        'GE1/0/2',
        'GE1/0/20',
        'GE1/0/21',
        'GE1/0/22',
        'GE1/0/23',
        'GE1/0/24',
        'GE1/0/25',
        'GE1/0/26',
        'GE1/0/27',
        'GE1/0/28',
        'GE1/0/29',
        'GE1/0/3',
        'GE1/0/30',
        'GE1/0/31',
        'GE1/0/32',
        'GE1/0/33',
        'GE1/0/34',
        'GE1/0/35',
        'GE1/0/36',
        'GE1/0/37',
        'GE1/0/38',
        'GE1/0/39',
        'GE1/0/4',
        'GE1/0/40',
        'GE1/0/41',
        'GE1/0/42',
        'GE1/0/43',
        'GE1/0/44',
        'GE1/0/45',
        'GE1/0/46',
        'GE1/0/47',
        'GE1/0/48',
        'GE1/0/5',
        'GE1/0/6',
        'GE1/0/7',
        'GE1/0/8',
        'GE1/0/9',
        'GigabitEthernet0/0/1',
        'GigabitEthernet0/0/10',
        'GigabitEthernet0/0/11',
        'GigabitEthernet0/0/12',
        'GigabitEthernet0/0/13',
        'GigabitEthernet0/0/14',
        'GigabitEthernet0/0/15',
        'GigabitEthernet0/0/16',
        'GigabitEthernet0/0/17',
        'GigabitEthernet0/0/18',
        'GigabitEthernet0/0/19',
        'GigabitEthernet0/0/2',
        'GigabitEthernet0/0/20',
        'GigabitEthernet0/0/21',
        'GigabitEthernet0/0/22',
        'GigabitEthernet0/0/23',
        'GigabitEthernet0/0/24',
        'GigabitEthernet0/0/25',
        'GigabitEthernet0/0/26',
        'GigabitEthernet0/0/27',
        'GigabitEthernet0/0/28',
        'GigabitEthernet0/0/29',
        'GigabitEthernet0/0/3',
        'GigabitEthernet0/0/30',
        'GigabitEthernet0/0/31',
        'GigabitEthernet0/0/32',
        'GigabitEthernet0/0/33',
        'GigabitEthernet0/0/34',
        'GigabitEthernet0/0/35',
        'GigabitEthernet0/0/36',
        'GigabitEthernet0/0/37',
        'GigabitEthernet0/0/38',
        'GigabitEthernet0/0/39',
        'GigabitEthernet0/0/4',
        'GigabitEthernet0/0/40',
        'GigabitEthernet0/0/41',
        'GigabitEthernet0/0/42',
        'GigabitEthernet0/0/43',
        'GigabitEthernet0/0/44',
        'GigabitEthernet0/0/45',
        'GigabitEthernet0/0/46',
        'GigabitEthernet0/0/47',
        'GigabitEthernet0/0/48',
        'GigabitEthernet0/0/5',
        'GigabitEthernet0/0/6',
        'GigabitEthernet0/0/7',
        'GigabitEthernet0/0/8',
        'GigabitEthernet0/0/9',
        'InLoopBack0',
        'MEth0/0/0',
        'MEth0/0/1',
        'NULL0',
        'Vlanif1',
        'Vlanif333',
        'Vlanif688',
        'Vlanif700',
        'Vlanif788',
        'XGigabitEthernet0/1/1',
        'XGigabitEthernet0/1/2',
    ]
    assert get_ifname_tags(ifnames) == [
        'All',
        '10GE1/0/∗',
        '40GE1/0/∗',
        'GE1/0/∗',
        'GigabitEthernet0/0/∗',
        'MEth0/0/∗',
        'Vlanif∗',
        'XGigabitEthernet0/1/∗',
        '∗.3013',
    ]


def test_try_jsontry_json():
    res = try_json('{"project_id":"noc"}')
    assert res == {'project_id': 'noc'}
    res = try_json('{"project_id":"noc"} ;{"project_id":"noc"}')
    assert res == [{'project_id': 'noc'}, {'project_id': 'noc'}]

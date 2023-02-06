import datetime

import pytest

from testsuite.mockserver import classes
from testsuite.utils import json_util

NOW = datetime.datetime(2019, 9, 19, 13, 4)
MOCKSERVER_INFO = classes.MockserverInfo(
    'localhost', 123, 'http://localhost:123/', None,
)
MOCKSERVER_SSL_INFO = classes.MockserverInfo(
    'localhost',
    456,
    'https://localhost:456/',
    classes.SslCertInfo('/some_dir/cert.cert', '/some_dir/cert.key'),
)


@pytest.mark.parametrize(
    'json_input,expected_result',
    [
        (  # simple list
            [{'some_date': {'$dateDiff': 0}}, 'regular_element'],  # json_input
            [{'some_date': NOW}, 'regular_element'],  # expected_result
        ),
        (  # simple dict
            {  # json_input
                'some_date': {'$dateDiff': 0},
                'regular_key': 'regular_value',
            },
            {'some_date': NOW, 'regular_key': 'regular_value'},  # json_input
        ),
        (  # nested list and dict
            {  # json_input
                'regular_root_key': 'regular_root_value',
                'root_date': {'$dateDiff': 0},
                'parent_key': {
                    'nested_date': {'$dateDiff': 0},
                    'nested_list': [
                        'regular_element1',
                        {'$dateDiff': 0},
                        {'$dateDiff': 0},
                        'regular_element2',
                    ],
                },
            },
            {  # expected_result
                'regular_root_key': 'regular_root_value',
                'root_date': NOW,
                'parent_key': {
                    'nested_date': NOW,
                    'nested_list': [
                        'regular_element1',
                        NOW,
                        NOW,
                        'regular_element2',
                    ],
                },
            },
        ),
    ],
)
def test_substitute_now(json_input, expected_result):
    result = json_util.substitute(json_input, now=NOW)
    assert result == expected_result


@pytest.mark.parametrize(
    'json_input,expected_result',
    [
        (
            ({'client_url': {'$mockserver': '/path'}}),
            ({'client_url': 'http://localhost:123/path'}),
        ),
        (
            ({'client_url': {'$mockserver': '/path', '$schema': False}}),
            ({'client_url': 'localhost:123/path'}),
        ),
    ],
)
def test_substitute_mockserver(json_input, expected_result):
    result = json_util.substitute(json_input, mockserver=MOCKSERVER_INFO)
    assert result == expected_result


@pytest.mark.parametrize(
    'json_input,expected_result',
    [
        (
            ({'client_url': {'$mockserver_https': '/path'}}),
            ({'client_url': 'https://localhost:456/path'}),
        ),
        (
            ({'client_url': {'$mockserver_https': '/path', '$schema': False}}),
            ({'client_url': 'localhost:456/path'}),
        ),
    ],
)
def test_substitute_mockserver_https(json_input, expected_result):
    result = json_util.substitute(
        json_input, mockserver_https=MOCKSERVER_SSL_INFO,
    )
    assert result == expected_result


@pytest.mark.parametrize(
    ('json_input', 'expected_result'),
    [
        ({'$timeDelta': 60}, datetime.timedelta(seconds=60)),
        ({'$timeDelta': '1e-6'}, datetime.timedelta(microseconds=1)),
        ({'$timeDelta': -0.5}, -(datetime.timedelta(milliseconds=500))),
    ],
)
def test_substitute_timedelta(json_input, expected_result):
    result = json_util.substitute(json_input)
    assert result == expected_result

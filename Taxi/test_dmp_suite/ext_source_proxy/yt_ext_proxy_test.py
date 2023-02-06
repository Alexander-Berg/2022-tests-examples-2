import pytest
from datetime import datetime
from dmp_suite.ext_source_proxy.logfeller import YtExtProxy


@pytest.mark.parametrize(
    'attributes, expected', [
        (
                [],
                None,
        ),
        (
                [{'$value': '2021-06-10', '$attributes': {'row_count': 0}}],
                None,
        ),
        (
                [{'$value': '2021-05-12', '$attributes': {'row_count': 36490957}}],
                datetime(2021, 5, 13, 0, 0),
        ),
        (
                [{'$value': '2021-05-11', '$attributes': {'row_count': 36490957}},
                 {'$value': '2021-05-12', '$attributes': {'row_count': 0}}],
                datetime(2021, 5, 12, 0, 0),
        ),
        (
                [{'$value': '2021-04-01', '$attributes': {'row_count': 36490}},
                 {'$value': '2021-04-03', '$attributes': {'row_count': 0}},
                 {'$value': '2021-04-02', '$attributes': {'row_count': 80}}],
                datetime(2021, 4, 3, 0, 0),
        ),
        (
                [{'$value': '2021-03-23', '$attributes': {'row_count': 0}},
                 {'$value': '2021-03-24', '$attributes': {'row_count': 0}},
                 {'$value': '2021-03-22', '$attributes': {'row_count': 134}}],
                datetime(2021, 3, 23, 0, 0),
        ),
        (
                [{'$value': '2021-07-10', '$attributes': {'row_count': 0}},
                 {'$value': '2021-07-11', '$attributes': {'row_count': 0}},
                 {'$value': '2021-07-12', '$attributes': {'row_count': 0}}],
                None,
        ),
        (
                [{'$value': '2021-07-16', '$attributes': {'row_count': 4524}},
                 {'$value': '2021-07-17', '$attributes': {'row_count': 2134}},
                 {'$value': '2021-07-18', '$attributes': {'row_count': 2341}}],
                datetime(2021, 7, 19, 0, 0),
        )
    ]
)
def test_yt_ext_proxy(attributes, expected):
    assert YtExtProxy.last_nonzero_date(attributes) == expected

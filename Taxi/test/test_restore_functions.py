# -*- coding: utf-8 -*-
from suite.gp import compare_partitions_parameter
import pytest


@pytest.mark.fast
@pytest.mark.parametrize(
    'parameter,compare_parameter,result',
    [
        (
                {},
                {},
                True
        ),
        (
                {'list': ['first']},
                {},
                True
        ),
        (
                {},
                {'list': ['first']},
                True
        ),
        (
                {'start_dttm': '2020-02-05 00:00:00', 'end_dttm': '2021-02-05 00:00:00'},
                {},
                True
        ),
        (
                {},
                {'start_dttm': '2020-02-05 00:00:00', 'end_dttm': '2021-02-05 00:00:00'},
                True
        ),
        (
                {'start_dttm': '2020-02-05 00:00:00', 'end_dttm': '2021-02-05 00:00:00'},
                {'list': ['first'], 'default': True},
                False
        ),
        (
                {'list': ['first'], 'default': False},
                {'list': ['first', 'last'], 'default': True},
                True
        ),
        (
                {'list': ['first']},
                {'list': ['last']},
                False
        ),
        (
                {'start_dttm': '2019-01-01 00:00:00', 'end_dttm': '2020-01-01 00:00:00', 'default': False},
                {'start_dttm': '2020-02-05 00:00:00', 'end_dttm': '2021-02-05 00:00:00'},
                False
        ),
        (
                {'start_dttm': '2019-01-01 00:00:00', 'end_dttm': '2020-01-01 00:00:00', 'default': False},
                {'start_dttm': '2019-02-05 00:00:00', 'end_dttm': '2019-03-05 00:00:00'},
                True
        ),
        (
                {'start_dttm': '9999-12-31 23:59:59', 'end_dttm': '10000-01-01 00:00:00', 'default': False},
                {'start_dttm': '2019-02-05 00:00:00', 'end_dttm': '10000-01-01 00:00:00'},
                True
        ),
        (
                {'start_dttm': '9999-12-31 23:59:59', 'end_dttm': '10000-01-01 00:00:00', 'default': False},
                {'start_dttm': '2019-02-05 00:00:00', 'end_dttm': '9999-01-01 00:00:00'},
                False
        ),
        (
                {'start_dttm': '9999-12-31 23:59:59', 'end_dttm': '10000-01-01 00:00:00', 'default': False},
                {'start_dttm': '2019-02-05 00:00:00', 'end_dttm': '9999-12-31 23:59:59'},
                True
        ),
        (
                {'start_dttm': '2019-02-01 00:00:00', 'end_dttm': '2019-04-01 00:00:00', 'default': False},
                {'start_dttm': '2019-02-05 00:00:00', 'end_dttm': '10000-01-01 00:00:00'},
                True
        ),
        (
                {'start_dttm': '2019-02-01 00:00:00', 'end_dttm': '2019-02-02 00:00:00', 'default': False},
                {'start_dttm': '2019-02-01 08:51:00', 'end_dttm': '2019-02-01 08:51:00'},
                True
        ),
        (
                {'start_dttm': '2019-02-01 00:00:00', 'end_dttm': '2019-02-02 00:00:00', 'default': False},
                {'start_dttm': '2019-01-01 00:00:00', 'end_dttm': '2019-02-01 00:00:00'},
                True
        ),
        (
                {'start_dttm': '2019-02-01 01:00:00', 'end_dttm': '2019-02-02 00:00:00', 'default': False},
                {'start_dttm': '2019-01-01 00:00:00', 'end_dttm': '2019-02-01 01:00:00'},
                True
        )
    ]
)
def test_compare_partitions_parameter(parameter, compare_parameter, result):
    assert result == compare_partitions_parameter(parameter, compare_parameter)

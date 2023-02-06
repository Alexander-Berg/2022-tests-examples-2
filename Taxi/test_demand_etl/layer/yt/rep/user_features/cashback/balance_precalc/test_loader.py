from argparse import Namespace

import pytest

from demand_etl.layer.yt.rep.user_features.cashback.balance_precalc.loader import source
from test_dmp_suite.testing_utils.spark_testing_utils import apply_spark_source_function, order_data
# noinspection PyUnresolvedReferences
from test_dmp_suite.testing_utils.spark_testing_utils import local_spark_session

from dmp_suite import datetime_utils as dtu

from . import data

from business_models import deep_compare
from typing import Union
import json

PERIOD = dtu.period('2020-08-17', '2020-08-23 23:59:59')

@pytest.mark.parametrize(
    'transactions_log, period, expected',
    [
        pytest.param(
            i['transactions'],
            PERIOD,
            i['expected']
        )
        for i in data.test_cases()
    ]
)
@pytest.mark.slow
def test_balance_calc(
        transactions_log, period, expected, local_spark_session
):
    inputs = dict(
        transactions_log=transactions_log,
    )
    actual = apply_spark_source_function(local_spark_session, source, inputs, args=Namespace(period=period))
    actual = [dict(i) for i in actual]
    actual.sort(key=lambda x: (x['wallet_id'], x['service_name']))
    expected.sort(key=lambda x: (x['wallet_id'], x['service_name']))
    errors = deep_compare(actual, expected, ordered=True, validate_types=False,
                          with_return=True)
    # Тут получится красивый путь до значения в EXPECTED, фактическое значение и ожидаемое
    errors = '\n'.join(sorted(['{}: {}'.format(k, v) for k, v in errors.items()]))
    assert errors == ''

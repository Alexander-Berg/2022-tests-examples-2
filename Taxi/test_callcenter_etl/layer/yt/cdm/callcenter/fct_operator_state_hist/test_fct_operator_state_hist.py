from argparse import Namespace

import pytest

from callcenter_etl.layer.yt.cdm.callcenter.fct_operator_state_hist.loader import source
from test_dmp_suite.testing_utils.spark_testing_utils import apply_spark_source_function, order_data
# noinspection PyUnresolvedReferences
from test_dmp_suite.testing_utils.spark_testing_utils import local_spark_session

from dmp_suite import datetime_utils as dtu

from .data import *

from business_models import deep_compare
from typing import Union

PERIOD = dtu.period('2020-06-28', '2020-06-29')

@pytest.mark.parametrize(
    'commutation, operator_status_log, period, expected',
    [
        pytest.param(
            COMMUTATIONS,
            STATUS_LOG,
            PERIOD,
            EXPECTED
        ),
    ]
)
@pytest.mark.slow
@pytest.mark.skip(reason='Тест нужно проверить и возможно переписать. В работе')
def test_events_source(
        commutation, operator_status_log, period, expected, local_spark_session
):
    inputs = dict(
        commutation=commutation,
        operator_status_log=operator_status_log
    )
    actual = apply_spark_source_function(local_spark_session, source, inputs, args=Namespace(period=period))

    def reformat_values(k: str, v: str) -> Union[None, int, float, str]:
        if v == 'NONE':
            return None
        if k == 'agent_id':
            return int(v)
        if k == 'state_dur_sec':
            return round(float(v), 3)
        return v

    actual = [{k: reformat_values(k, v) for k, v in values}
              for values in actual]
    actual.sort(key=lambda x: x['utc_valid_from_dttm'])
    errors = deep_compare(actual, expected, ordered=True, validate_types=False,
                          with_return=True)
    # Тут получится красивый путь до значения в EXPECTED, фактическое значение и ожидаемое
    errors = '\n'.join(sorted(['{}: {}'.format(k, v) for k, v in errors.items()]))
    assert errors == ''

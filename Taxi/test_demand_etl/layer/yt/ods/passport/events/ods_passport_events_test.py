from argparse import Namespace

import pytest

from demand_etl.layer.yt.ods.passport.events.loader import source
from test_dmp_suite.testing_utils.spark_testing_utils import apply_spark_source_function, order_data
# noinspection PyUnresolvedReferences
from test_dmp_suite.testing_utils.spark_testing_utils import local_spark_session

from dmp_suite import datetime_utils as dtu

from .data import *


@pytest.mark.parametrize(
    'passport, period, expected',
    [
        pytest.param(
            # passport
            [
                MAIL0T0,
                MAIL0T1,
                TAXI0T0,
                TAXI0T1,
                TAXI0T2,
                MAIL1T0,
                TAXI1T0,
                TAXI1T1,
                TAXI1Y0,
                MAIL1Y0,
            ],
            # period
            dtu.period('2020-06-28', '2020-06-28'),
            # expected
            [
                TAXI0T0R,
                TAXI0T1R,
                TAXI0T2R,
                TAXI1T0R,
                TAXI1T1R,
            ]
        ),
    ]
)
@pytest.mark.skip(reason="Test is flaky. Will fix in TAXIDWH-17106")
@pytest.mark.slow
def test_events_source(
        passport, period, expected, local_spark_session
):
    inputs = dict(
        passport=passport,
    )
    actual = apply_spark_source_function(local_spark_session, source, inputs, args=Namespace(period=period))
    expected = order_data(expected)

    assert actual == expected

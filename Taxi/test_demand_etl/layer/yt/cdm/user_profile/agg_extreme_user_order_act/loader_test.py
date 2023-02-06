import pytest
from argparse import Namespace

from dmp_suite import datetime_utils as dtu
from dmp_suite.spark.client import create_local_spark_session

from test_dmp_suite.testing_utils.spark_testing_utils import apply_spark_source_function

from demand_etl.layer.yt.cdm.user_profile.fct_extreme_user_order_act.loader import source

from .data import ORDER, UBER_ORDER, CURRENT_EXTREME_USER_ORDER, EXPECTED


@pytest.mark.slow
def test_events_source():
    period = dtu.period('2020-10-01', '2020-10-15')
    inputs = dict(
        order=ORDER,
        uber_order=UBER_ORDER,
        current_extreme_user_order=CURRENT_EXTREME_USER_ORDER
    )
    with create_local_spark_session(source.get_config()['spark_conf_args']) as spark:
        actual = apply_spark_source_function(spark, source, inputs, args=Namespace(period=period))
        actual = sorted(map(dict, actual), key=lambda r: (r['phone_pd_id'], r['brand_name']))
        assert actual == EXPECTED

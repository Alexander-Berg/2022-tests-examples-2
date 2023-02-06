# coding: utf-8
from nile.api.v1.clusters import MockCluster

from test_dmp_suite.testing_utils import NileJobTestCase

from taxi_etl.layer.yt.cdm.money.dim_currency_rate.impl import get_refs_rates

# get_refs_rates params for test
LOAD_END_DT = '2019-08-09'
CURRENCY_LINKS = [
    {'source_cur': 'RUB', 'target_cur': 'USD', 'source': 'RUS'},
    {'source_cur': 'USD', 'target_cur': 'RUB', 'source': 'RUS'},
    {'source_cur': 'GHS', 'target_cur': 'USD', 'source': 'BAR'},
    {'source_cur': 'USD', 'target_cur': 'GHS', 'source': 'BAR'},
    {'source_cur': 'RUB', 'target_cur': 'FOO', 'source': 'RUS'},
    {'source_cur': 'FOO', 'target_cur': 'RUB', 'source': 'RUS'},
]


class TestDdsDimCurrencyRateRefsRates(NileJobTestCase):
    """
    Tests check following cases:
        - rate changes over time;
        - from two rates from different sources choose a rate with the highest priority;
        - take rank that is not listed in the handbook, if it came from the Central Bank;
        - calculate rates for currencies that do not have rates with the ruble (GHS, ILS, XOF, etc.);
        - add extra rates RUB-RUB;
        - if today there is no rate from the Central Bank, take it from yesterday,
          and ignore the rates from other sources (FIXER, etc.);
        - write rates until the last load date, even if there is no rate data.
    """
    def setUp(self):
        self.job = MockCluster().job()
        self.job \
            .table("dummy") \
            .call(
                get_refs_rates,
                currency_links=CURRENCY_LINKS,
                load_end_dttm=LOAD_END_DT,
            )

    def test_refs_rates_ranking_done(self):
        """
        Test checks following cases:
            - rate changes over time;
            - from two rates from different sources choose a rate with the highest priority;
            - take rank that is not listed in the handbook, if it came from the Central Bank.
        """
        self.assertCorrectLocalRun(
            self.job,
            sources={"raw_refs": "refs_rates/input.json"},
            expected_sinks={"ranking_done": "refs_rates/ranking_done.json"},
        )

    def test_refs_rates_missing_dates_filled(self):
        """
        Test checks following cases:
            - if today there is no rate from the Central Bank, take it from yesterday,
              and ignore the rates from other sources (FIXER, etc.);
            - write rates until the last load date, even if there is no rate data.
        """
        self.assertCorrectLocalRun(
            self.job,
            sources={"ranking_done": "refs_rates/ranking_done.json"},
            expected_sinks={"missing_dates_filled": "refs_rates/missing_dates_filled.json"},
        )

    def test_refs_rates_calculations_added(self):
        """
        Test checks following cases:
            - calculate rates for currencies that do not have rates with the ruble (GHS, ILS, XOF, etc.);
            - add extra rates RUB-RUB.
        """
        self.assertCorrectLocalRun(
            self.job,
            sources={"missing_dates_filled": "refs_rates/missing_dates_filled.json"},
            expected_sinks={"calculations_added": "refs_rates/calculations_added.json"},
        )

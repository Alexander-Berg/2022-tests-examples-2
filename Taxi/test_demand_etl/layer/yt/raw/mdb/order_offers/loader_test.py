from datetime import datetime
from unittest import TestCase
from pytest import raises

from dmp_suite import datetime_utils as dtu
from demand_etl.layer.yt.raw.order_offer.legacy_order_offers.impl import make_worker_periods


class TestOrderOffersPeriodSplit(TestCase):
    def test_single_date(self):
        self.assertEqual(
            make_worker_periods(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 11, 0)),
            [[
                dtu.period(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 10, 20)),
                dtu.period(datetime(2021, 2, 1, 10, 20), datetime(2021, 2, 1, 10, 40)),
                dtu.period(datetime(2021, 2, 1, 10, 40), datetime(2021, 2, 1, 11, 0)),
            ]]
        )

        self.assertEqual(
            make_worker_periods(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 11, 0), max_worker_cnt=6),
            [[
                dtu.period(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 10, 10)),
                dtu.period(datetime(2021, 2, 1, 10, 10), datetime(2021, 2, 1, 10, 20)),
                dtu.period(datetime(2021, 2, 1, 10, 20), datetime(2021, 2, 1, 10, 30)),
                dtu.period(datetime(2021, 2, 1, 10, 30), datetime(2021, 2, 1, 10, 40)),
                dtu.period(datetime(2021, 2, 1, 10, 40), datetime(2021, 2, 1, 10, 50)),
                dtu.period(datetime(2021, 2, 1, 10, 50), datetime(2021, 2, 1, 11, 0)),
            ]]
        )

    def test_multiple_dates(self):
        self.assertEqual(
            make_worker_periods(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 2, 11, 0)),
            [
                [
                    dtu.period(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 2, 0, 0), datetime(2021, 2, 2, 11, 0)),
                ]
            ]
        )

        self.assertEqual(
            make_worker_periods(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 5, 10, 0)),
            [
                [
                    dtu.period(datetime(2021, 2, 5, 0, 0), datetime(2021, 2, 5, 10, 0)),
                    dtu.period(datetime(2021, 2, 4, 0, 0), datetime(2021, 2, 4, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 3, 0, 0), datetime(2021, 2, 3, 23, 59, 59, 999999)),
                ],
                [
                    dtu.period(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 2, 0, 0), datetime(2021, 2, 2, 23, 59, 59, 999999)),
                ],
            ]
        )

        self.assertEqual(
            make_worker_periods(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 5, 10, 0), max_worker_cnt=2),
            [
                [
                    dtu.period(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 2, 0, 0), datetime(2021, 2, 2, 23, 59, 59, 999999)),
                ],
                [
                    dtu.period(datetime(2021, 2, 3, 0, 0), datetime(2021, 2, 3, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 4, 0, 0), datetime(2021, 2, 4, 23, 59, 59, 999999)),
                ],
                [
                    dtu.period(datetime(2021, 2, 5, 0, 0), datetime(2021, 2, 5, 10, 0)),
                ],

            ]
        )

        self.assertEqual(
            make_worker_periods(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 6, 10, 0)),
            [
                [
                    dtu.period(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 1, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 2, 0, 0), datetime(2021, 2, 2, 23, 59, 59, 999999)),
                ],
                [
                    dtu.period(datetime(2021, 2, 3, 0, 0), datetime(2021, 2, 3, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 4, 0, 0), datetime(2021, 2, 4, 23, 59, 59, 999999)),
                ],
                [
                    dtu.period(datetime(2021, 2, 5, 0, 0), datetime(2021, 2, 5, 23, 59, 59, 999999)),
                    dtu.period(datetime(2021, 2, 6, 0, 0), datetime(2021, 2, 6, 10, 0)),
                ],
            ]
        )

    def test_max_workers_assertion(self):
        with raises(AssertionError):
            make_worker_periods(datetime(2021, 2, 1, 10, 0), datetime(2021, 2, 6, 10, 0), max_worker_cnt=1)

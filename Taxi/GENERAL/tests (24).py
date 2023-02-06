import unittest
from . import CouriersCubeContext
from nile.api.v1 import clusters
from projects.common.nile.environment import configure_environment
from taxi_pyml.common.time_utils import timestamp

import datetime as dt


class CouriersCubeTests(unittest.TestCase):
    def test_get_orders(self):
        cluster = configure_environment(
            clusters.yt.YT(proxy="hahn"), requirements=[],
        )

        job = cluster.job()

        orders = CouriersCubeContext(
            job,
            dt.datetime(2020, 1, 1),
            dt.datetime(2020, 2, 1)
        ).get_orders(
            order_fields=[
                "courier_id",
                "cancel_reason_id"
            ]
        )

        orders = orders.put('//tmp/tst_ord')

        job.run()

        for record in orders.read():
            record = record.to_dict()
            self.assertTrue(
                isinstance(record['courier_id'], str)
            )
            self.assertTrue(
                isinstance(record['cancel_id'], (str, type(None)))
            )

    def test_get_shifts(self):
        cluster = configure_environment(
            clusters.yt.YT(proxy="hahn"), requirements=[],
        )

        job = cluster.job()

        shifts = CouriersCubeContext(
            job,
            dt.datetime(2020, 1, 1),
            dt.datetime(2020, 2, 1)
        ).get_shifts(
            courier_fields=[
                'region_name',
                'per_hour_guarantee',
                'per_dropoff',
                'per_surge_order',
                'per_km_to_client',
                'per_long_to_rest',
                'per_pickup',
                'guarantee'
            ]
        )

        shifts = shifts.put('//tmp/tst_sft')

        job.run()

        for record in shifts.read():
            record = record.to_dict()
            self.assertTrue(
                isinstance(record['per_km_to_client'], (int, float, type(None)))
            )
            self.assertTrue(
                isinstance(record['per_pickup'], (int, float, type(None)))
            )

            self.assertLessEqual(
                timestamp(dt.datetime(2020, 1, 1), timezone='UTC'),
                record['created_at_timestamp']
            )
            self.assertLessEqual(
                record['created_at_timestamp'],
                timestamp(dt.datetime(2020, 2, 1), timezone='UTC')
            )


if __name__ == '__main__':
    unittest.main()

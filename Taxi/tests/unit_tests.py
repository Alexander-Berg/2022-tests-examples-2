#coding=utf-8

import unittest

from zoo.optimal_offer.delta_sh_model.predict_extractor import NileModel
from zoo.optimal_offer.run_driver_offers.analytics import random_partitioning
from catboost import CatBoostRegressor
from nile.api.v1 import clusters
from nile.api.v1 import Record
from nile.api.v1.local import ListSink, StreamSource


import numpy as np
from zoo.optimal_offer.run_driver_offers.analytics import calculate_bonus_sum


class TestPredictExtractor(unittest.TestCase):
    def test_nile_model(self):
        example_model = CatBoostRegressor(loss_function='MultiRMSE',
                                          iterations=1)

        nile_model = NileModel(
            example_model,
            X_fields = ['x2', 'x1'],
            y_fields = ['y1', 'y2'],
            kws_fields = {'sample_weight': 'sw'}
        )

        data = [
            {
                'x1': 'Moscow',
                'x2': 2,
                'x3': 2,
                'y1': 1,
                'y2': 2,
                'y3': 5,
                'sw': 1
            },
            {
                'x1': 'Spb',
                'x2': 0,
                'x3': 0,
                'y1': 0,
                'y2': 0,
                'y3': 0,
                'sw': 1
            },
            {
                'x1': 'Moscow',
                'x2': 10,
                'x3': 2,
                'y1': 1,
                'y2': 1,
                'y3': 5,
                'sw': 1,
            }
        ]

        nile_model.fit(data, cat_features=[1])

        predictions = nile_model.predict(data)
        prediction = predictions[0]

        self.assertIn('y1', prediction.keys())
        self.assertIn('y2', prediction.keys())
        self.assertNotIn('x1', prediction.keys())
        self.assertNotIn('x2', prediction.keys())
        self.assertNotIn('x3', prediction.keys())
        self.assertNotIn('sw', prediction.keys())

        cluster = clusters.Hahn()
        job = cluster.job()
        predictions_mapper = []

        job.table(
            'start'
        ).label('start').map(
            nile_model.nile_predict('model_name')
        ).label('result')

        job.local_run(
            sources={
                'start': StreamSource(data),
            },
            sinks={
                'result': ListSink(predictions_mapper)
            })

        prediction_mapper = predictions_mapper[0]

        self.assertEqual(prediction_mapper['model_name_y1'], prediction['y1'])
        self.assertIn('model_name_y1', prediction_mapper.to_dict().keys())
        self.assertIn('model_name_y2', prediction_mapper.to_dict().keys())
        self.assertNotIn('model_name_x1', prediction_mapper.to_dict().keys())
        self.assertNotIn('model_name_x2', prediction_mapper.to_dict().keys())
        self.assertNotIn('model_name_x3', prediction_mapper.to_dict().keys())
        self.assertNotIn('model_name_sw', prediction_mapper.to_dict().keys())


class TestAnalytics(unittest.TestCase):
    def test_analytics_mapper(self):
        pass

    def test_bonus_sum_currency(self):
        """
        This tests that quantile_international targets unlike quantile targets
        do not depend on currency_rate (if the rounding does not happen)
        """
        for kpi in range(10, 180):
            bonus_sum_cr1_inter = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=1.1,
                mean_cost_city=150, targets_scheme='quantile_international'
            )
            bonus_sum_cr2_inter = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=2,
                mean_cost_city=150, targets_scheme='quantile_international'
            )
            bonus_sum_cr3_inter = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=0.5,
                mean_cost_city=150, targets_scheme='quantile_international'
            )
            bonus_sum_cr4_inter = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=0.9,
                mean_cost_city=150, targets_scheme='quantile_international'
            )
            self.assertEqual(bonus_sum_cr1_inter, bonus_sum_cr2_inter)
            self.assertEqual(bonus_sum_cr4_inter, bonus_sum_cr3_inter)

            bonus_sum_cr1 = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=2,
                mean_cost_city=150, targets_scheme='quantile'
            )
            bonus_sum_cr2 = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=2,
                mean_cost_city=200, targets_scheme='quantile'
            )

            self.assertEqual(bonus_sum_cr1, bonus_sum_cr2)

            bonus_sum_cr1_more = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=4,
                mean_cost_city=150, targets_scheme='quantile'
            )
            bonus_sum_cr2_more = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=2,
                mean_cost_city=150, targets_scheme='quantile'
            )

            self.assertTrue(bonus_sum_cr2_more > bonus_sum_cr1_more)

    def test_bonus_sum_flat(self):
        """
        This tests flat targets and checks that quantile targets do not depend on
        'flat_bonus_sum' parameter
        """
        for kpi in range(180):
            bonus_sum_cr1_inter = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=500, currency_rate=1,
                mean_cost_city=150, targets_scheme='quantile_international'
            )
            bonus_sum_cr2_inter = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=10000, currency_rate=1,
                mean_cost_city=150, targets_scheme='quantile_international'
            )

            self.assertEqual(bonus_sum_cr1_inter, bonus_sum_cr2_inter)

        bonus_sum_cr1_flat = calculate_bonus_sum(
            orders_kpi=kpi, days_long=7, money_multiplier=0.3,
            flat_bonus_sum=500, currency_rate=1,
            mean_cost_city=150, targets_scheme='flat'
        )
        bonus_sum_cr2_flat = calculate_bonus_sum(
            orders_kpi=kpi, days_long=7, money_multiplier=0.3,
            flat_bonus_sum=20000, currency_rate=1,
            mean_cost_city=150, targets_scheme='flat'
        )

        self.assertEqual(bonus_sum_cr1_flat, 500)
        self.assertEqual(bonus_sum_cr2_flat, 20000)

    def test_bonus_sum_mm(self):
        """
        This checks monotonicity wrt money_multiplier
        """
        for kpi in range(180):

            bonus_sum_cr1 = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=1,
                mean_cost_city=150, targets_scheme='quantile'
            )

            bonus_sum_cr2 = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=0.8,
                flat_bonus_sum=1, currency_rate=1,
                mean_cost_city=150, targets_scheme='quantile'
            )


            bonus_sum_cr3 = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=0.6,
                flat_bonus_sum=1, currency_rate=1,
                mean_cost_city=150, targets_scheme='quantile'
            )

            self.assertTrue(bonus_sum_cr3 <= bonus_sum_cr2)
            self.assertTrue(bonus_sum_cr2 <= bonus_sum_cr1)

    def test_bonus_sum_indifference_point(self):
        """
        this tests the points of mean_cost_city=130, targets_scheme='quantile' and
        mean_cost_city=170, targets_scheme='quantile_international'.
        The city_multiplier is intented to be equal to 1 for these points. Therefore
        for zny kpi the outputs should be the same
        """
        for kpi in range(180):

            bonus_sum_cr1 = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=1,
                mean_cost_city=130, targets_scheme='quantile'
            )

            bonus_sum_cr2 = calculate_bonus_sum(
                orders_kpi=kpi, days_long=7, money_multiplier=1,
                flat_bonus_sum=1, currency_rate=1,
                mean_cost_city=170, targets_scheme='quantile_international'
            )
            self.assertEqual(bonus_sum_cr1, bonus_sum_cr2)

    def test_bonus_sum_gap(self):
        """
        Here i test that in the end difference between quantile and quantile_international
        is not that big for different mean_cost_city
        """

        for mm in np.arange(0.6, 1, 0.1):
            for kpi in range(50, 150):
                for mean_cost_city in range(120, 450, 10):
                    bonus_sum_cr1 = calculate_bonus_sum(
                        orders_kpi=kpi, days_long=7, money_multiplier=mm,
                        flat_bonus_sum=1, currency_rate=1,
                        mean_cost_city=mean_cost_city, targets_scheme='quantile'
                    )

                    bonus_sum_cr2 = calculate_bonus_sum(
                        orders_kpi=kpi, days_long=7, money_multiplier=mm,
                        flat_bonus_sum=1, currency_rate=1,
                        mean_cost_city=mean_cost_city, targets_scheme='quantile_international'
                    )
                    if mean_cost_city < 170:
                        self.assertTrue(abs(bonus_sum_cr2*1.0/bonus_sum_cr1 - 1) < 0.32)
                    elif mean_cost_city < 220:
                        self.assertTrue(abs(bonus_sum_cr2*1.0/bonus_sum_cr1 - 1) < 0.21)
                    elif mean_cost_city < 320:
                        self.assertTrue(abs(bonus_sum_cr2*1.0/bonus_sum_cr1 - 1) < 0.11)
                    else:
                        self.assertTrue(abs(bonus_sum_cr2*1.0/bonus_sum_cr1 - 1) < 0.21)

    def test_rounding(self):
        """
        Here I do explicitly test a certain output value and
        also test that the rounding works correctly
        """
        bonus_sum_1 = calculate_bonus_sum(
            orders_kpi=90, days_long=7, money_multiplier=1,
            flat_bonus_sum=1, currency_rate=1,
            mean_cost_city=130, targets_scheme='quantile_international'
        )
        self.assertEqual(bonus_sum_1, 2900)

        bonus_sum_01 = calculate_bonus_sum(
            orders_kpi=90, days_long=7, money_multiplier=1,
            flat_bonus_sum=1, currency_rate=12,
            mean_cost_city=130, targets_scheme='quantile_international'
        )
        self.assertEqual(bonus_sum_01, 2868)

        bonus_sum_02 = calculate_bonus_sum(
            orders_kpi=90, days_long=7, money_multiplier=1,
            flat_bonus_sum=1, currency_rate=0.2,
            mean_cost_city=130, targets_scheme='quantile_international'
        )
        self.assertEqual(bonus_sum_02, 2868)


        bonus_sum_1 = calculate_bonus_sum(
            orders_kpi=90, days_long=7, money_multiplier=1,
            flat_bonus_sum=1, currency_rate=0.1,
            mean_cost_city=130, targets_scheme='quantile_international'
        )
        self.assertEqual(bonus_sum_1, 2868)


class TestRandomization(unittest.TestCase):
    def test_hashing(self):
        cluster = clusters.Hahn()
        job = cluster.job()

        config = [
            {
                'probability': 0.2, 'segment': u'some_segment', 'bonus_type': u'shift'
            }
        ]
        mapper = random_partitioning(config)

        data = [
            {
                'hash_value_16_1': 23214,
                'hash_value_16_2': 23244,
                'some_field': 'b',
            },
            {
                'hash_value_16_1': 234,
                'hash_value_16_2': 23244,
                'some_field': 'b',
            },
            {
                'hash_value_16_1': 23214,
                'hash_value_16_2': 324,
                'some_field': 'b',
            }
        ]

        results = []

        job.table(
            'start'
        ).label('start').map(
            mapper
        ).label('result')

        job.local_run(
            sources={
                'start': StreamSource(data),
            },
            sinks={
                'result': ListSink(results)
            }
        )

        expected_result = [
            Record(
                bonus_type=u'shift',
                group=False,
                hash_value_16_1=23214,
                hash_value_16_2=23244,
                probability=0.2,
                segment=u"{'bonus_type': u'shift', 'segment': u'some_segment', 'probability': 0.2}",
                some_field='b'
            ),
            Record(
                bonus_type=u'shift',
                group=True,
                hash_value_16_1=234,
                hash_value_16_2=23244,
                probability=0.2,
                segment=u"{'bonus_type': u'shift', 'segment': u'some_segment', 'probability': 0.2}",
                some_field='b'
            ),
            Record(
                bonus_type=u'shift',
                group=False,
                hash_value_16_1=23214,
                hash_value_16_2=324,
                probability=0.2,
                segment=u"{'bonus_type': u'shift', 'segment': u'some_segment', 'probability': 0.2}",
                some_field='b'
            ),
        ]

        self.assertEqual(results, expected_result)


if __name__ == '__main__':
    unittest.main()

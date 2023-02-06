from unittest import TestCase
from datetime import datetime
from .utils import create_data_for_cost_before_antisurge, create_by_paths

from taxi_etl.layer.yt.ods.dbprocessing.order.impl import (
    get_cost_before_antisurge, corp_client_id_extractor,
    mobile_app_version_extractor, order_source_extractor,
    parse_main_card_payment_id, get_plan_destination_point_count
)


class TestExtractors(TestCase):
    def test_cost_before_antisurge(self):
        created = datetime(2016, 1, 1, 22, 0, 12)
        doc = create_data_for_cost_before_antisurge(created=created)
        self.assertIsNone(get_cost_before_antisurge(doc))

        calc = dict()
        doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
        self.assertIsNone(get_cost_before_antisurge(doc))

        calc = dict(alternative_type='not_explicit_antisurge')
        doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
        self.assertIsNone(get_cost_before_antisurge(doc))

        created = datetime(2019, 1, 1, 22, 0, 12)
        calc = dict(alternative_type='explicit_antisurge')
        doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
        self.assertIsNone(get_cost_before_antisurge(doc))

        allowed_tariffs = {
            "__park__": {
                "business": 3,
                "child_tariff": 2,
                "econom": 1,
            }
        }

        calc['allowed_tariffs'] = allowed_tariffs

        doc = create_data_for_cost_before_antisurge(created=created, calc=calc)
        self.assertIsNone(get_cost_before_antisurge(doc))

        driver_tariff = 'econom'
        doc = create_data_for_cost_before_antisurge(created=created, calc=calc, driver_tariff=driver_tariff)
        self.assertEqual(get_cost_before_antisurge(doc), 1)

        driver_tariff = 'undefined'
        doc = create_data_for_cost_before_antisurge(created=created, calc=calc, driver_tariff=driver_tariff)
        self.assertIsNone(get_cost_before_antisurge(doc))

        request_class = ['undefined']
        doc = create_data_for_cost_before_antisurge(created=created, calc=calc, request_class=request_class)
        self.assertIsNone(get_cost_before_antisurge(doc))

        request_class = ['business']
        doc = create_data_for_cost_before_antisurge(created=created, calc=calc, request_class=request_class)
        self.assertIsNone(get_cost_before_antisurge(doc))

        request_class = ['business']
        driver_tariff = 'econom'
        doc = create_data_for_cost_before_antisurge(
            created=created, calc=calc, request_class=request_class, driver_tariff=driver_tariff
        )
        self.assertEqual(get_cost_before_antisurge(doc), 1)

    def test_corp_client_id(self):
        self.assertIsNone(corp_client_id_extractor(dict()))

        doc = create_by_paths(
            {
                'order.request.corp.client_id': '00000111110011',
                'payment_tech.type': 'corp',
                'payment_tech.main_card_billing_id': '1112223334445556'
            }
        )
        self.assertEqual(corp_client_id_extractor(doc), '00000111110011')

        doc = create_by_paths(
            {
                'payment_tech.type': 'corp',
                'payment_tech.main_card_billing_id': '1112223334445556'
            }
        )
        self.assertEqual(corp_client_id_extractor(doc), '1112223334445556')

        doc = create_by_paths(
            {
                'payment_tech.type': 'nocorp',
                'payment_tech.main_card_billing_id': '1112223334445556'
            }
        )
        self.assertIsNone(corp_client_id_extractor(doc))


    def test_destination_count(self):
        self.assertIsNone(get_plan_destination_point_count(dict()))

        doc = create_by_paths(
            {
                'order.request.destinations':[[11.11111111,22.22222222],[33.33333333,44.555555]]
            })
        self.assertEqual(get_plan_destination_point_count(doc), 3)


    def test_mobile_app_version_extractor(self):
        self.assertIsNone(mobile_app_version_extractor(dict()))

        doc = create_by_paths(
            {
                'order.statistics.application': 'corpweb',
                'order.user_agent': 'Python/3.7 aiohttp/3.5.4'
            }
        )
        self.assertIsNone(mobile_app_version_extractor(doc))

        doc = create_by_paths(
            {
                'order.statistics.application': 'iphone',
                'order.user_agent': 'ru.yandex.ytaxi/5.41.55761 (iPhone; iPhone12,3; iOS 13.3.1; Darwin)'
            }
        )
        self.assertEqual(mobile_app_version_extractor(doc), '5.41.55761')

        doc = create_by_paths(
            {
                'order.statistics.application': 'uber_iphone',
                'order.user_agent': 'ru.yandex.uber/5.37.53957 (iPhone; iPhone9,3; iOS 13.1.2; Darwin)'
            }
        )
        self.assertEqual(mobile_app_version_extractor(doc), '5.37.53957')

    def test_order_source_extractor(self):
        created = datetime(2019, 1, 1, 22, 0, 12)
        doc = create_data_for_cost_before_antisurge(created=created)
        self.assertEqual(order_source_extractor(doc), 'yandex')

        created = datetime(2018, 3, 1, 22, 0, 12)
        driver_tariff = 'uber_econom'
        source = 'econom'
        doc = create_data_for_cost_before_antisurge(created=created, driver_tariff=driver_tariff, source=source)
        self.assertEqual(order_source_extractor(doc), 'uber')

        created = datetime(2018, 3, 1, 22, 0, 12)
        source = 'raw_source'
        doc = create_data_for_cost_before_antisurge(created=created, source=source)
        self.assertEqual(order_source_extractor(doc), 'raw_source')

        created = datetime(2019, 1, 1, 22, 0, 12)
        source = 'raw_source'
        doc = create_data_for_cost_before_antisurge(created=created, source=source)
        self.assertEqual(order_source_extractor(doc), 'raw_source')

        created = datetime(2019, 1, 1, 22, 0, 12)
        driver_tariff = 'no_uber_econom'
        doc = create_data_for_cost_before_antisurge(created=created, driver_tariff=driver_tariff)
        self.assertEqual(order_source_extractor(doc), 'yandex')

    def test_main_card_payment_id(self):
        main_card_payment_id_extractor = parse_main_card_payment_id('main_card_payment_id')

        self.assertIsNone(main_card_payment_id_extractor(dict()))

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'zzzz'
            }
        )
        self.assertIsNone(main_card_payment_id_extractor(doc))

        doc = create_by_paths(
            {
                'payment_tech.type': 'other',
            }
        )
        self.assertIsNone(main_card_payment_id_extractor(doc))

        doc = create_by_paths(
            {
                'payment_tech.type': 'other',
                'payment_tech.main_card_payment_id': 'zzzz'
            }
        )
        self.assertEqual(main_card_payment_id_extractor(doc), 'zzzz')

    def test_coop_account_type(self):
        coop_account_type_extractor = parse_main_card_payment_id('coop_account_type')
        self.assertIsNone(coop_account_type_extractor(dict()))

        doc = create_by_paths(
            {
                'payment_tech.type': 'other',
                'payment_tech.main_card_payment_id': 'zzzz'
            }
        )
        self.assertIsNone(coop_account_type_extractor(doc))

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
            }
        )
        self.assertIsNone(coop_account_type_extractor(doc))

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'zzzz'
            }
        )
        self.assertEqual(coop_account_type_extractor(doc), 'family')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'family-zzzz'
            }
        )
        self.assertEqual(coop_account_type_extractor(doc), 'family')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'qqq-zzzz'
            }
        )
        self.assertEqual(coop_account_type_extractor(doc), 'qqq')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'business-zzzz'
            }
        )
        self.assertEqual(coop_account_type_extractor(doc), 'business')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'businesszzzz'
            }
        )
        self.assertEqual(coop_account_type_extractor(doc), 'family')

    def test_coop_account_id(self):
        coop_account_id_extractor = parse_main_card_payment_id('coop_account_id')
        self.assertIsNone(coop_account_id_extractor(dict()))

        doc = create_by_paths(
            {
                'payment_tech.type': 'other',
                'payment_tech.main_card_payment_id': 'zzzz'
            }
        )
        self.assertIsNone(coop_account_id_extractor(doc))

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
            }
        )
        self.assertIsNone(coop_account_id_extractor(doc))

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'zzzz'
            }
        )
        self.assertEqual(coop_account_id_extractor(doc), 'zzzz')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'business-zzzz'
            }
        )
        self.assertEqual(coop_account_id_extractor(doc), 'zzzz')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'qqqq-zzzz'
            }
        )
        self.assertEqual(coop_account_id_extractor(doc), 'zzzz')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'family-zzzz'
            }
        )
        self.assertEqual(coop_account_id_extractor(doc), 'zzzz')

        doc = create_by_paths(
            {
                'payment_tech.type': 'coop_account',
                'payment_tech.main_card_payment_id': 'businesszzzz'
            }
        )
        self.assertEqual(coop_account_id_extractor(doc), 'businesszzzz')

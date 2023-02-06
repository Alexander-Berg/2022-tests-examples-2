import os
import json
from unittest import TestCase


from dmp_suite.performance_utils import extract_service, \
    extract_goal, extract_audience, extract_geo, \
    extract_platform, extract_purchase, extract_category_subcategory, \
    extract_restype, extract_opt


def parse_campaign_name(campaign_name):
    purchase = extract_purchase(campaign_name)
    return dict(
        service_code=extract_service(campaign_name),
        purchase_code=purchase,
        goal_code=extract_goal(campaign_name),
        audience_code=extract_audience(campaign_name),
        geo_code=extract_geo(campaign_name),
        platform=extract_platform(campaign_name, purchase),
    )


def parse_campaign_name_food(campaign_name):
    purchase = extract_purchase(campaign_name)
    category = extract_category_subcategory(campaign_name, 'category')
    subcategory = extract_category_subcategory(campaign_name, 'subcategory')
    return dict(
        service_code=extract_service(campaign_name),
        purchase_code=purchase,
        goal_code=extract_goal(campaign_name),
        audience_code=extract_audience(campaign_name),
        geo_code=extract_geo(campaign_name),
        restype=extract_restype(campaign_name),
        opt=extract_opt(campaign_name),
        platform=extract_platform(campaign_name, purchase),
        category=category,
        subcategory=subcategory
    )


class TestDdsPerformanceGroupHandbook(TestCase):
    def _assert_parameter(self, name, groups, campaign_data):
        self.assertEqual(
            groups[name], campaign_data[name],
            msg='Wrong extract of {} for {}:\nresult: {}\nexpected: {}' .format(
                name,
                campaign_data['campaign_name'].encode('utf8') if campaign_data['campaign_name'] else None,
                groups[name],
                campaign_data[name]
            )
        )

    def test_parse_campaign_name(self):
        data_path = os.path.join(os.path.dirname(__file__), 'test_data.json')
        with open(data_path) as f:
            data = json.load(f)
        for campaign_data in data:
            groups = parse_campaign_name(campaign_data['campaign_name'])
            for name in [
                'service_code',
                'purchase_code',
                'goal_code',
                'platform',
                'audience_code',
                'geo_code'
            ]:
                self._assert_parameter(name, groups, campaign_data)

    def test_parse_campaign_name_food(self):
        data_path = os.path.join(os.path.dirname(__file__), 'test_food_data.json')
        with open(data_path) as f:
            data = json.load(f)
        for campaign_data in data:
            groups = parse_campaign_name_food(campaign_data['campaign_name'])
            for name in [
                'service_code',
                'purchase_code',
                'goal_code',
                'platform',
                'audience_code',
                'geo_code',
                'opt',
                'restype',
                'subcategory',
                'category'
            ]:
                self._assert_parameter(name, groups, campaign_data)

    def test_extract_geo(self):
        for campaign_name, utm_content, expected_geo in (
            ('ru-all-all_android_vk-ok_rt_call', None, 'ru-all-all'),
            ('ru-all-all_android_vk-ok_rt_call', 'ru-mow-msk', 'ru-all-all'),
            ('ru-all-all_android_vk-ok_rt_call', 'foo', 'ru-all-all'),
            ('dt_ytcf-coding-fest_ret', None, None),
            ('dt_ytcf-coding-fest_ret', 'ru-mow-msk', 'ru-mow-msk'),
            ('dt_ytcf-coding-fest_ret', 'foo', None),
            (None, None, None),
            (None, 'ru-mow-msk', 'ru-mow-msk'),
            (None, 'foo', None)

        ):
            actual_geo = extract_geo(campaign_name, utm_content)
            self.assertEqual(expected_geo, actual_geo)

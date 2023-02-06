import datetime as dt
import json
import re
from typing import List
import xml.etree.ElementTree as ET

import pytest
import pytz

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_retail_seo_plugins import *  # noqa: F403 F401

from . import models


@pytest.fixture
async def push_lb_message(taxi_eats_retail_seo):
    async def _do(topic_name, consumer_name, cookie, data):
        response = await taxi_eats_retail_seo.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': consumer_name,
                    'data': data,
                    'topic': topic_name,
                    'cookie': cookie,
                },
            ),
        )
        assert response.status_code == 200

    return _do


@pytest.fixture(name='to_utc_datetime')
def _to_utc_datetime():
    def do_to_utc_datetime(stamp):
        if not isinstance(stamp, dt.datetime):
            stamp = dt.datetime.fromisoformat(stamp)
        if stamp.tzinfo is not None:
            stamp = stamp.astimezone(pytz.UTC)
        return stamp

    return do_to_utc_datetime


@pytest.fixture(name='assert_objects_lists')
def assert_objects_lists():
    def do_assert(lhs: List[any], rhs: List[any]):
        lhs_sorted = [models.recursive_dict(i) for i in sorted(lhs)]
        rhs_sorted = [models.recursive_dict(i) for i in sorted(rhs)]
        assert lhs_sorted == rhs_sorted

    return do_assert


@pytest.fixture(name='bool_to_sql')
def _bool_to_sql():
    def do_bool_to_sql(value):
        return 'true' if value else 'false'

    return do_bool_to_sql


@pytest.fixture(name='sql_escape')
def _sql_escape():
    def do_sql_escape(value):
        return value.replace('\'', '\'\'')

    return do_sql_escape


@pytest.fixture(name='opt_to_sql')
def _opt_to_sql(bool_to_sql, sql_escape):
    def do_opt_to_sql(value):
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return bool_to_sql(value)
        if isinstance(value, str):
            return f'\'{sql_escape(value)}\''
        return value

    return do_opt_to_sql


@pytest.fixture(name='verify_periodic_metrics')
def _verify_periodic_metrics(
        taxi_eats_retail_seo, taxi_eats_retail_seo_monitor, testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_retail_seo.run_distlock_task
            if is_distlock
            else taxi_eats_retail_seo.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_retail_seo-') :]
        )

        should_fail = False

        @testpoint(f'eats-retail-seo_{periodic_short_name}::fail')
        def _fail(param):
            return {'inject_failure': should_fail}

        @testpoint(f'eats-retail-seo_periodic-data::use-current-epoch')
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_retail_seo.tests_control(reset_metrics=True)

        await periodic_runner(periodic_name)
        # assert _fail.has_calls

        metrics = await taxi_eats_retail_seo_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 1
        assert data['oks'] == 1
        assert data['fails'] == 0
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

        should_fail = True
        try:
            await periodic_runner(periodic_name)
        except taxi_eats_retail_seo.PeriodicTaskFailed:
            pass
        # assert _fail.has_calls

        metrics = await taxi_eats_retail_seo_monitor.get_metrics()
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 2
        assert data['oks'] == 1
        assert data['fails'] == 1
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

    return _verify


@pytest.fixture(name='enable_periodic_in_config')
def _enable_periodic_in_config(update_taxi_config):
    def _enable(periodic_name):
        update_taxi_config(
            'EATS_RETAIL_SEO_PERIODICS',
            {periodic_name: {'is_enabled': True, 'period_in_sec': 86400}},
        )

    return _enable


@pytest.fixture
def generate_feed_s3_path(mds_s3_storage):
    def do_generate(s3_dir: str, brand: models.Brand):
        return f"""{s3_dir}/retail_{brand.slug}.xml"""

    return do_generate


@pytest.fixture
def load_expected_market_feed(mds_s3_storage):
    def do_load(xml_feed, mock_date: dt.datetime):
        expected_xml = xml_feed.replace('{mock_date}', mock_date.isoformat())
        return expected_xml

    return do_load


@pytest.fixture
def normalize_market_feed_xml():
    def do_normalize(xml):
        # XML parser preserves original spacing between tags
        # (newlines and indentation) when the document is
        # serialized back to XML. When elements are re-ordered,
        # new indentation looks broken.
        # Since this is not important and only a test detail, the spaces
        # between tags are removed from the XML.
        no_indent_xml = re.sub(r'>\s+<', '>\n<', xml)
        root = ET.fromstring(no_indent_xml)
        categories = root.find('shop/categories')
        categories[:] = sorted(categories, key=lambda x: x.get('id'))
        offers = root.find('shop/offers')
        offers[:] = sorted(offers, key=lambda x: x.get('id'))
        return ET.tostring(root, encoding='unicode', method='xml')

    return do_normalize


@pytest.fixture
def set_feeds_settings_dsa_title(update_taxi_config):
    def do_set_feeds_settings_dsa_title(feeds_settings_key):
        update_taxi_config(
            'EATS_RETAIL_SEO_FEEDS_SETTINGS',
            {
                feeds_settings_key: {
                    'allowed_countries': ['РОССИЯ'],
                    'dsa_title': 'DSA_TITLE',
                },
            },
        )

    return do_set_feeds_settings_dsa_title


@pytest.fixture
def get_first_offer_exact_field():
    def do_get_first_offer_exact_field(xml, field_name):
        root = ET.fromstring(xml)
        dsa_title = root.find('shop/offers')[0].find(field_name)
        return dsa_title.text

    return do_get_first_offer_exact_field

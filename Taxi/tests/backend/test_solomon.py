import json
import logging
from random import randrange
from unittest.mock import patch

from odoo import tools

from common.client.wms import WMSConnector
from freezegun import freeze_time
from odoo.tests.common import HttpSavepointCase, tagged
from odoo.addons.lavka.tests.utils import get_products_from_csv, read_json_data

_logger = logging.getLogger(__name__)

FIXTURES_PATH = 'approvals'


_sensors = [
    'wms_processing_error',
    'wms_unprocessed_docs',
    'wms_unsent_po',
    'wms_today_processed',
    'wms_procesing_lag',
    'heart_beat',
    'wms_procesing_time',
    'queue_job_max_retry_count',
    'queue_job_count',
    'queue_job_max_time',
    'queue_job_import_job_lag'
]

@tagged('lavka', 'sol')
class TestSolomonNoData(HttpSavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wms_connector = WMSConnector()
        parnter = cls.env['res.partner'].create([{
            'name': 'Test'
        }])
        usr_vals = {
            'login': 'test',
            'password': 'test',
            'partner_id': parnter.id
        }
        cls.test_user = cls.env['res.users'].create([usr_vals])

    def test_solomon_metrics_no_data(self):
        self.authenticate('test', 'test')
        response = self.url_open(
            '/metrics',
            headers={'Content-Type': 'text/html'},
        )

        self.assertEqual(response.status_code, 200)
        _metrics = json.loads(response.content)

        metrics = {
            i['labels']['sensor']: i['value']
            for i
            in _metrics['metrics']
        }

        for sensor, value in metrics.items():
            # в сенсорах не должно быть значений null
            self.assertIsNotNone(value)
            self.assertTrue(sensor in _sensors)

    def test_solomon_query_from_param(self):
        query_text = """
            SELECT 'heart_beat' as sensor,
            1 as value
            """
        # заменим своим ззапросом
        self.env['ir.config_parameter'].set_param(
            'metric_query_text',
            query_text
        )

        self.authenticate('test', 'test')
        response = self.url_open(
            '/metrics',
            headers={'Content-Type': 'text/html'},
        )

        self.assertEqual(response.status_code, 200)
        _metrics = json.loads(response.content)

        metrics = {
            i['labels']['sensor']: i['value']
            for i
            in _metrics['metrics']
        }
        _sensors = ['heart_beat']

        self.assertEqual(len(metrics), len(_sensors))
        for sensor, value in metrics.items():
            # в сенсорах не должно быть значений null
            self.assertIsNotNone(value)
            self.assertTrue(sensor in _sensors)

        query_text_param = self.env['ir.config_parameter'].search([
            ('key', '=', 'metric_query_text')
        ])
        query_text_param.unlink()

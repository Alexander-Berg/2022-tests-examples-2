import datetime
import logging
from unittest.mock import patch
from odoo.tests.common import SingleTransactionCase
from odoo.tests.common import tagged
from odoo.addons.lavka.backend.models.wms.wms_stock_log import unlink_old_records

_logger = logging.getLogger(__name__)


@tagged('lavka', 'stock', 'log')
class TestStockLog(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = cls.env['factory_common_wms']
        cls.logs_response = cls.factory.generate_stock_log()

    def test_99_logs_happy(self):
        self.env['ir.config_parameter'].set_param('sleep', 'false')
        self.env.cr.execute(
            """
                TRUNCATE TABLE wms_stock_log
            """
        )
        self.env.cr.commit()
        with patch('common.client.wms.WMSConnector.get_wms_data') as log_data:
            log_data.return_value = self.logs_response, None
            self.env['wms_stock_log'].import_from_wms()
            self.env.cr.commit()

        logs = self.env['wms_stock_log'].search([])
        # нулевой дельта каунт пропускаем
        self.assertEqual(len(logs), 99)
        self.env.cr.execute(
            """
                TRUNCATE TABLE wms_stock_log
            """
        )
        self.env.cr.execute(
            """
                TRUNCATE TABLE current_wms_cursor
            """
        )
        logs2 = self.env['wms_stock_log'].search([])
        self.assertEqual(len(logs2), 0)
        self.env.cr.commit()

    def test_99_logs_sad(self):
        self.env.cr.execute(
            """
                TRUNCATE TABLE wms_stock_log
            """
        )
        self.env.cr.commit()
        new = self.logs_response.copy()
        for k, line in enumerate(new):
            if k > 15:
                line['product_id'] = None
        self.env['ir.config_parameter'].set_param('sleep', 'false')
        with patch('common.client.wms.WMSConnector.get_wms_data') as log_data:
            log_data.return_value = new, 'test_cursor.tail'
            with self.assertRaises(Exception):
                self.env['wms_stock_log'].import_from_wms()
                self.env.cr.commit()

        logs = self.env['wms_stock_log'].search([])
        # никаких строк не должно быть...
        self.assertEqual(len(logs), 0)
        self.env.cr.execute(
            """
                TRUNCATE TABLE wms_stock_log
            """
        )
        self.env.cr.commit()
        self.env.cr.execute(
            """
                TRUNCATE TABLE current_wms_cursor
            """
        )
        self.env.cr.commit()
        logs2 = self.env['wms_stock_log'].search([])
        self.assertEqual(len(logs2), 0)

    def test_99_logs_unlink(self):
        self.env['ir.config_parameter'].set_param('sleep', 'false')
        self.env.cr.execute(
            """
                TRUNCATE TABLE current_wms_cursor
            """
        )
        self.env.cr.commit()
        self.env.cr.execute(
            """
                TRUNCATE TABLE wms_stock_log
            """
        )
        self.env.cr.commit()
        logs_response = self.factory.generate_stock_log()
        with patch('common.client.wms.WMSConnector.get_wms_data') as log_data:
            log_data.return_value = logs_response, None
            self.env['wms_stock_log'].import_from_wms()
            self.env.cr.commit()

        logs = self.env['wms_stock_log'].search([])
        self.assertEqual(len(logs), 99)
        #  меняем дату у логов
        for log in logs:
            log.created = datetime.datetime.now() - datetime.timedelta(days=100)
        self.env.cr.commit()
        un_cr = self.env.registry.cursor()
        unlink_old_records(un_cr, 90)
        _logs = self.env['wms_stock_log'].search([])
        self.assertEqual(len(_logs), 0)
        self.env.cr.execute(
            """
                TRUNCATE TABLE wms_stock_log
            """
        )
        self.env.cr.commit()
        self.env.cr.execute(
            """
                TRUNCATE TABLE current_wms_cursor
            """
        )
        logs2 = self.env['wms_stock_log'].search([])
        self.assertEqual(len(logs2), 0)
        self.env.cr.commit()

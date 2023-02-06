import datetime as dt
import json
import logging
import os
from csv import DictReader
from random import randrange
from unittest.mock import patch

from common.client.wms import WMSConnector
from freezegun import freeze_time
from odoo.addons.queue_job.job import Job, FAILED, DONE
from odoo.addons.queue_job.exception import RetryableJobError
from odoo.tests.common import SavepointCase, tagged, Form
from odoo.addons.lavka.tests.utils import read_json_data

_logger = logging.getLogger(__name__)

FIXTURES_PATH = 'queue_postprocessing'


@tagged('lavka', 'q')
class TestQueuePostprocessing(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestQueuePostprocessing, cls).setUpClass()

        cls.wms_connector = WMSConnector()
        cls.orders = read_json_data(
            folder=FIXTURES_PATH,
            filename='orders',
        )

        cls.external_id = 'external_id_test'
        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 't',
            },
        ]
        )
        # создаем склады вмс
        cls.store_ids = []
        for i in range(5):
            store_id = cls.orders[0].get('store_id')
            wh = cls.env['stock.warehouse'].create({
                'name': f'England Lavka Test_{i+1}',
                'code': f'9321123123{i+1}',
                'warehouse_tag_ids': cls.tag,
                'wms_id': f'{store_id}.{i+1}'
            })
            cls.store_ids.append(wh.wms_id)
            new_channel = cls.env['queue.job.channel'].create(
                {
                    'name': wh.name,
                    'parent_id': cls.env.ref('queue_job.channel_root').id

                }
            )

        cls.partner = cls.env['res.partner'].create({'name': 'Vendor'})

        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')

        # создаем товары
        cls.products = cls.env['product.product']
        for c, line in enumerate(cls.orders[0].get('required')):
            p = cls.env['product.product'].create(
                {
                    'name': f'test_product_{c}',
                    'default_code': f'{c}',
                    'type': 'product',
                    'wms_id': line.get('product_id'),
                    'taxes_id': 1,
                }
            )
            cls.products += p
        # создаем пройсы
        cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
            'product_id': i.id,
            'start_date': dt.datetime.now(),
            'price_unit': 12,
            'product_uom_id': i.uom_id.id,
            'tax_id': i.supplier_taxes_id.id,
            'requisition_id': cls.purchase_requsition.id,
            'approve_tax': True,
            'approve_price': True,
            'product_qty': 9999,
            'product_code': '300',
            'product_name': 'vendor product name',
            'qty_multiple': 1,
        }) for i in cls.products]

        for r in cls.requsition_lines:
            r._compute_approve()
        cls.purchase_requsition.action_in_progress()
        _logger.debug(f'Purchase requsition  {cls.purchase_requsition.id} confirmed')
        sleep = cls.env['ir.config_parameter'].search([
            ('key', '=', 'sleep')
        ])
        if sleep:
            sleep.unlink()

    def test_order_post_processing_happy(self):

        order_data = self.orders[0]
        order_ids = []
        id_doc = order_data['order_id']
        with freeze_time('2021-03-15 12:00:00'):
            for i, wh in enumerate(self.env['stock.warehouse'].search([])):
                _logger.debug(f'creating docs for {wh.name}')
                for j in range(i+1):
                    order_data.update(
                        {
                            'store_id': wh.wms_id,
                            'order_id': id_doc + f'.{i}.{j+1}',
                            'doc_number': id_doc + f'.{i}.{j + 1}',
                            'attr': {
                                'doc_date': dt.date.today().strftime('%Y-%m-%d'),
                                'doc_number': id_doc + f'.{i}.{j + 1}',
                                'request_type': 'ordinary',
                            }
                        }
                    )
                    order_ids.append(order_data['order_id'])
                    with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                        get_wms_data_mock.return_value = {}, None
                        self.env['wms_integration.order'].create_wms_order([order_data], self.wms_connector)
                _logger.debug(f'---->OK')

        docs = self.env['wms_integration.order'].search(
            [
                ('order_id', 'in', order_ids)
            ]
        )
        #  создаем первые таски по каждому складу

        self.env['wms_integration.order'].postprocess_in_queue()

        tasks = self.env['queue.job'].search([
            ('identity_key', '!=', 'reborn_jobs')
        ])
        self.assertEqual(len(tasks), len(self.store_ids))
        child_tasks = []
        doc = self.env['wms_integration.order']
        for task in tasks:

            wh = self.env['stock.warehouse'].search([('name', '=', task.channel)])
            channel = self.env['queue.job.channel'].search([('name', '=', wh.name)])

            _logger.debug(f'task for channel {task.channel}')
            res = doc.with_context(job_uuid=task.uuid).__getattribute__(task.method_name)(wh, channel.name)
            self.assertTrue(isinstance(res, (Job, str)))
            if isinstance(res, Job):
                _logger.debug(f'Child task for === {channel.name} ==> priority> {res.priority} ')
                child_tasks.append(res)
        child_tasks2 = []

        _logger.debug('=================================================')
        _logger.debug('==================SECOND=========================')
        _logger.debug('=================================================')

        for task in child_tasks:

            wh = self.env['stock.warehouse'].search([('name', '=', task.channel)])
            channel = self.env['queue.job.channel'].search([('name', '=', wh.name)])

            _logger.debug(f'task for channel {task.channel}')
            res = doc.with_context(job_uuid=task.uuid).__getattribute__(task.method_name)(wh, channel.name)
            self.assertTrue(isinstance(res, (Job, str)))
            if isinstance(res, Job):
                _logger.debug(f'Child task for === {channel.name} ==> priority> {res.priority} ')
                child_tasks2.append(res)

        child_tasks3 = []

        _logger.debug('=================================================')
        _logger.debug('==================THIRD=========================')
        _logger.debug('=================================================')

        for task in child_tasks2:

            wh = self.env['stock.warehouse'].search([('name', '=', task.channel)])
            channel = self.env['queue.job.channel'].search([('name', '=', wh.name)])

            _logger.debug(f'task for channel {task.channel}')
            res = doc.with_context(job_uuid=task.uuid).__getattribute__(task.method_name)(wh, channel.name)
            self.assertTrue(isinstance(res, (Job, str)))
            if isinstance(res, Job):
                _logger.debug(f'Child task for === {channel.name} ==> priority> {res.priority} ')
                child_tasks3.append(res)
            if channel.name == 'England Lavka Test_1':
                # должны на первом складе закончится доки
                self.assertTrue(isinstance(res, str))

        c = 1

    def test_order_post_processing_sad(self):

        order_data = self.orders[0]
        order_ids = []
        id_doc = order_data['order_id']
        with freeze_time('2021-03-15 12:00:00'):
            for i, wh in enumerate(self.env['stock.warehouse'].search([])):
                _logger.debug(f'creating docs for {wh.name}')
                for j in range(i+1):
                    order_data.update(
                        {
                            'store_id': wh.wms_id,
                            'order_id': id_doc + f'.{i}.{j+1}'
                        }
                    )
                    order_ids.append(order_data['order_id'])
                    with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                        get_wms_data_mock.return_value = {}, None
                        self.env['wms_integration.order'].create_wms_order([order_data], self.wms_connector)
                _logger.debug(f'---->OK')

        # испортим товары
        for p in self.products:
            p.taxes_id = None

        #  саоздаем первые таски по каждому складу

        self.env['wms_integration.order'].postprocess_in_queue()

        tasks = self.env['queue.job'].search([
            ('identity_key', '!=', 'reborn_jobs')
        ])
        self.assertEqual(len(tasks), len(self.store_ids))

        doc = self.env['wms_integration.order']
        for task in tasks:
            wh = self.env['stock.warehouse'].search([('name', '=', task.channel)])
            channel = self.env['queue.job.channel'].search([('name', '=', wh.name)])
            _logger.debug(f'task for channel {task.channel}')
            with self.assertRaises(RetryableJobError):
                res = doc.with_context(job_uuid=task.uuid).__getattribute__(task.method_name)(
                    wh,
                    channel.name,
                )

        # пробуем еще раз инициализировать обработку
        self.env['wms_integration.order'].postprocess_in_queue()
        # так как уже созданы таски с таким identity_key, новых тасок появиться не должно
        tasks = self.env['queue.job'].search([
            ('identity_key', '!=', 'reborn_jobs')
        ])
        self.assertEqual(len(tasks), len(self.store_ids))

        # вдруг что-то случилось и таски свалились в failed
        for task in tasks:
            task.state = FAILED

        # пробуем еще раз инициализировать обработку
        self.env['wms_integration.order'].postprocess_in_queue()
        # и в этом случае не должно быть новых тасок
        tasks = self.env['queue.job'].search([
            ('identity_key', '!=', 'reborn_jobs')
        ])
        self.assertEqual(len(tasks), len(self.store_ids))


# pylint: disable=protected-access,attribute-defined-outside-init,import-error
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated
import json
import logging
from datetime import datetime

from freezegun import freeze_time
from odoo import fields

from odoo.addons.lavka.tests.utils import get_products_from_csv
from odoo.tests.common import SavepointCase, Form
from odoo.osv.expression import normalize_domain
_logger = logging.getLogger(__name__)


FIXTURES_PATH = 'common'


class TestVeluationCommon(SavepointCase):
    """
    Тест создания энвайремента
    """

    @classmethod
    def setUpClass(cls):
        super(TestVeluationCommon, cls).setUpClass()
        cls.differenses = []
        cls.inventory = cls.env['stock.inventory']
        cls.picking = cls.env['stock.picking']
        cls.stock_move = cls.env['stock.move']
        cls.quant = cls.env['stock.quant']
        cls.sale_order = cls.env['sale.order']
        cls.sale_order_line = cls.env['sale.order.line']
        cls.valuation_layer = cls.env['stock.valuation.layer']
        cls.inventory_line = cls.env['stock.inventory.line']
        cls.tag = cls.env['stock.warehouse.tag'].create([
            {
                'type': 'geo',
                'name': 'test_tag',
            },
        ]
        )
        cls.warehouse_1 = cls.env['stock.warehouse'].create({
            'name': 'Test `warehouse 1',
            'code': 'TT1',
            'warehouse_tag_ids': cls.tag,
            'wms_id': 'wms_id 1'
        })
        cls.warehouse_2 = cls.env['stock.warehouse'].create({
            'name': 'Test `warehouse 2',
            'code': 'TT2',
            'warehouse_tag_ids': cls.tag,
            'wms_id': 'wms_id 2',
        })
        cls.warehouse_3 = cls.env['stock.warehouse'].create({
            'name': 'Test `warehouse 3',
            'code': 'TT3',
            'warehouse_tag_ids': cls.tag,
            'wms_id': 'wms_id 3',
        })
        cls.warehouse_4 = cls.env['stock.warehouse'].create({
            'name': 'Test `warehouse 4',
            'code': 'TT4',
            'warehouse_tag_ids': cls.tag,
            'wms_id': 'wms_id 4',
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Test Purchaser'})
        cls.purchase_requsition = cls.env['purchase.requisition'].create({
            'vendor_id': cls.partner.id,
            'warehouse_tag_ids': cls.tag,
            'state': 'ongoing',
        })
        _logger.debug(f'Partner {cls.partner.name} created')
        cls.common_products_dict = get_products_from_csv(
            folder=FIXTURES_PATH,
            filename='products_import',
        )
        cls.products = cls.env['product.product'].create(cls.common_products_dict)

        with freeze_time('2021-03-15 12:00:00'):
            cls.requsition_lines = [cls.env['purchase.requisition.line'].create({
                'product_id': i.id,
                'price_unit': 5.25,
                'start_date': fields.Datetime.today(),
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


def _lavka_process_fvg(self, model, fvg, level=5):
    """ Post-processes to augment the fields_view_get with:

     * an id field (may not be present if not in the view but needed)
     * pre-processed modifiers (map of modifier name to json-loaded domain)
     * pre-processed onchanges list
     """
    fvg['fields'].setdefault('id', {'type': 'id'})
    # pre-resolve modifiers & bind to arch toplevel
    modifiers = fvg['modifiers'] = {'id': {'required': False, 'readonly': True}}
    contexts = fvg['contexts'] = {}
    order = fvg['fields_ordered'] = []
    for f in fvg['tree'].xpath('//field[not(ancestor::field)]'):
        fname = f.get('name')
        order.append(fname)

        modifiers[fname] = {
            modifier: bool(domain) if isinstance(domain, int) else normalize_domain(domain)
            for modifier, domain in json.loads(f.get('modifiers', '{}')).items()
        }
        ctx = f.get('context')
        if ctx:
            contexts[fname] = ctx

        descr = fvg['fields'].get(fname) or {'type': None}
        # FIXME: better widgets support
        # NOTE: selection breaks because of m2o widget=selection
        if f.get('widget') in ['many2many']:
            descr['type'] = f.get('widget')
        if level and descr['type'] == 'one2many':
            self._o2m_set_edition_view(descr, f, level)

    fvg['onchange'] = model._onchange_spec(fvg)


Form._process_fvg = _lavka_process_fvg

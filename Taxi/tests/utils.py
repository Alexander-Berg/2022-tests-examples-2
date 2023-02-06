import logging
import json
import os
from csv import DictReader


_logger = logging.getLogger(__name__)


FIXTURE_PATH = '/fixtures'


def save_xlsx_report(self, locations, report_name=None, ):
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    res = []
    valuation_lines = self.env['stock.valuation.layer'].search([
        ('location_id', 'in', locations),
    ])
    for val in valuation_lines:
        try:
            cost_price = val.remaining_value / val.remaining_qty
        except ZeroDivisionError:
            cost_price = 0
        res.append({
            'PRICE_RULE': val.price_rule,
            'TRANSACTION_SYSTEM_NAME': val.transaction_system_name,
            'TRANS_SYSTEM_GROUP': val.trans_system_group,
            'TRANS_ID': val.trans_id,
            'PRODUCT_EXTERNAL_ID': val.product_id.default_code,
            'VIRT_WHS': val.location_id.name,
            'UNIT_COST': val.unit_cost,
            'QTY': val.quantity,
            'VALUE': val.value,
            'TAX_ID': val.tax_id.name,
            'TAX_SUM': val.tax_sum,
            'REMAINING-QTY': val.remaining_qty,
            'REMAINING-VALUE': val.remaining_value,
            'COST_PRICE': cost_price,
            'DESCRIPTION': val.description,
            'DOCUMENT_DATETIME': val.document_datetime,
            'DOCUMENT_DATE': val.document_date,
            'CREATE': val.create_date,
            'COMPANY_ID': val.company_id.id,
        })
    df = pd.DataFrame(res)
    writer = pd.ExcelWriter(f'{report_name}.xlsx') # pylint: disable=abstract-class-instantiated
    df.to_excel(writer, 'Sheet1')
    writer.save()


# суммы товаров на location
# pylint: disable=protected-access
def get_stock_loc(self, loc):
    quant_obj = self.env['stock.quant']
    value_obj = self.env['stock.valuation.layer']
    qty = sum([
        i.quantity for i in quant_obj.search([
            ('location_id', '=', loc.id)
        ])
    ])
    valuation_qty = sum([
        i.quantity for i in value_obj.search([
            ('location_id', '=', loc.id)
        ])
    ])
    value = sum([
        i.value for i in value_obj.search([
            ('location_id', '=', loc.id)
        ])
    ])
    rem_qty = 0.0
    rem_value = 0.0
    for prod in self.products[:5]:
        svl = value_obj._sequential_formula(prod, loc)
        if svl:
            rem_qty += svl.remaining_qty
            rem_value += svl.remaining_value

    return qty, valuation_qty, value, rem_qty, rem_value


def get_products_from_csv(folder, filename):
    products = []
    _logger.debug('open test products')
    # path = 'fixtures / stowages_test / stw_products.csv'
    with open(
            f'{os.path.dirname(__file__)}/{FIXTURE_PATH}/{folder}/{filename}.csv',
            encoding='UTF-8') as file_products:
        reader = DictReader(file_products, delimiter=';')
        for i in reader:
            name = i.get('\ufeffname')
            if name:
                i.update({'name': name})
                i.pop('\ufeffname')
            if i.get('is_kitchen'):
                i.update({'is_kitchen': True if i.get(
                    'is_kitchen') == '1' else False})
            products.append(i)
    return products


def read_json_data(folder, filename):
    _logger.debug('reading json')
    with open(
            f'{os.path.dirname(__file__)}/{FIXTURE_PATH}/{folder}/{filename}.json',
            encoding='UTF-8') as wms_json:
        res_json = json.load(wms_json)
    return res_json

def assertEqualFloat(self, a, b):
    self.assertTrue(abs(a-b) <= 1, '%f != %f' % (a, b))

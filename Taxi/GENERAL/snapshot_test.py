from business_models.databases import gdocs
from business_models import hahn

import requests
import json
from os.path import isfile

import pandas as pd
import numpy as np

from concurrent.futures import ThreadPoolExecutor

import traceback
from pprint import pprint

from datetime import datetime, timedelta

from column_types import types
from column_order import order

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

sheet_id = '1eMngJcN25smf7n9gseByacSYhoyRfIQagra0PRKMdu4'

def pctg_to_float(string):
    try:
        return float(string.strip().replace('%', '')) / 100
    except:
        return string

def try_eval_dict(x):
    try:
        x = dict(eval(x))
        for competitor in x:
            x[competitor] = float(x[competitor])
        return x
    except:
        return {}

def comp_from_list_to_dict(x):
    try:
        print(x, type(x))
        x = eval(x)
        if not isinstance(x, list):
            print('NOT LIST')
            return {}

        c = {}
        for comp in x:
            name = comp[0]
            price_no_disc = comp[1]
            price_disc = comp[2]
            c[name + '_original'] = price_no_disc
            c[name + '_promo'] = price_disc

        return c

    except Exception as e:
        print(e)
        return {}

def fetch(data, session, total):
    try:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = json.dumps(data)

        with session.post(URL, data=data, headers=headers) as response:
            r = response.json()
            # pprint(r)
            print(r['comp_prices'])
            total.append(r)
    except Exception as e:
        pprint(e)
        pprint(traceback.print_tb(e.__traceback__))


# Читает данные с листа table_name в pandas.DataFrame
params = gdocs.read(
    table_name='data',  # Название листа в google.sheet
    sheet_id=sheet_id,   # ID google.sheet (берется из ссылки)
    header=1,            # Количество строк-заголовков
#     index=1            # Количество столбцов индексов. Если не передать, индекса не будет
)

params = params.replace(r'^\s*$', np.nan, regex=True)

params_columns = [
    'item_id',
    'price_list',
    'city',
    'samokat_minimarket_original_coef',	
    'samokat_supermarket_original_coef',	
    'perekrestok_okolo_original_coef',	
    'vkusvill_original_coef', 
    '5ka_original_coef',
    'initial_base_strategy',
    'base_strategy',	
    'base_competitor',	
    'base_base_margin',	
    'lower_strategy',	
    'lower_competitor',	
    'lower_base_margin',	
    'upper_strategy',	
    'upper_competitor',	
    'upper_base_margin',
    'basket',
    'fix_price',
    'line',
    'priority_competitors',
    'is_checked',
]

print(params.columns)
params['item_id'] = params['item_id'].astype('int64')
params['is_checked'] = params['is_checked'].astype(str)

coefs = [
    'samokat_minimarket_original_coef',	
    'samokat_supermarket_original_coef',	
    'perekrestok_okolo_original_coef',	
    'vkusvill_original_coef', 
    '5ka_original_coef',
]

for coef in coefs:
    params[coef] = params[coef].apply(pctg_to_float)

HAHN_TYPES = {
    'city': 'String?',
    'price_list': 'String?',
    'outcoming_nds': 'Double?',
    'front_margin': 'Double?',
    'comp_prices': 'String?',
    'samokat_minimarket_original': 'Double?',
    'samokat_minimarket_promo': 'Double?',
    'samokat_supermarket_original': 'Double?',
    'samokat_supermarket_promo': 'Double?',
    'perekrestok_okolo_original': 'Double?',
    'perekrestok_okolo_promo': 'Double?',
    'vkusvill_original': 'Double?',
    'vkusvill_promo': 'Double?',
    '5ka_original': 'Double?',
    '5ka_promo': 'Double?',
    'samokat_minimarket_original_coef': 'Double?',
    'samokat_supermarket_original_coef': 'Double?',
    'perekrestok_okolo_original_coef': 'Double?',
    'vkusvill_original_coef': 'Double?',
    '5ka_original_coef': 'Double?',
    'item_id': 'Integer?',
    'product_name': 'String?',
    'category_name': 'String?',
    'subcategory_name': 'String?',
    'supplier_id': 'String?',
    'purchase_price_without_nds': 'Double?',
    'purchase_price_with_nds': 'Double?',
    'retail_price_with_nds': 'Double?',
    'sales_quantity': 'Integer?',
    'item_stock': 'Integer?',
    'basket': 'String?',
    'initial_base_strategy': 'String?',
    'base_competitor': 'String?',
    'base_base_margin': 'Double?',
    'lower_strategy': 'String?',
    'lower_competitor': 'String?',
    'lower_base_margin': 'Double?',
    'upper_strategy': 'String?',
    'upper_competitor': 'String?',
    'upper_base_margin': 'Double?',
    'line': 'String?',
    'fix_price': 'Integer?',
    'base_strategy_price': 'Double?',
    'lower_strategy_price': 'Double?',
    'upper_strategy_price': 'Double?',
    'prefinal_price': 'Double?',
    'final_price_before_lines': 'Integer?',
    'log': 'String?',
    'base_strategy': 'String?',
    'priority_competitors': 'String?',
    'is_checked': 'String?',
}

print(params.info())
print(HAHN_TYPES)

hahn.write(params, table_name=f'home/lavka-analytics/pricing_rules/snapshots/test', types=HAHN_TYPES, force_drop=True)



import pandas as pd
import numpy as np

from pprint import pprint

from strategy.base import *
from strategy.basic import *
from params import DTYPES

import datetime

from ETL import rounding_pricing, margin_limit_pricing, promo, diff_pricing, bounds_check, fix_price_check

def try_eval_dict(x):
    try:
        x = dict(eval(x))
        for competitor in x:
            x[competitor] = float(x[competitor])
        return x
    except:
        return {}

def percent_to_float(x):
    try:
        x = float(x.strip('%')) / 100
    except:
        pass
    return x

converters = {
                'base_plus/minus': percent_to_float,
                'base_base_margin': percent_to_float,
                'lower_plus/minus': percent_to_float,
                'lower_base_margin': percent_to_float,
                'upper_plus/minus': percent_to_float,
                'upper_base_margin': percent_to_float,
             }

if __name__ == "__main__":

    base_tree = {'Приоритет конкурентов': ['Приоритет конкурентов', 'Базовая маржа', 'Текущая цена'],
                 'По конкуренту': ['По конкуренту', 'Базовая маржа', 'Текущая цена'],
                 'Минимальная цена': ['Минимальная цена', 'Базовая маржа', 'Текущая цена'],
                 'Базовая маржа': ['Базовая маржа', 'Текущая цена'],
                 'Текущая цена': ['Текущая цена']}
    
    lower_tree = {'Приоритет конкурентов': ['Приоритет конкурентов'],
                 'По конкуренту': ['По конкуренту'],
                 'Минимальная цена': ['Минимальная цена'],
                 'Базовая маржа': ['Базовая маржа'],
                 'Текущая цена': ['Текущая цена']}
    
    upper_tree = {'Приоритет конкурентов': ['Приоритет конкурентов'],
                 'По конкуренту': ['По конкуренту'],
                 'Минимальная цена': ['Минимальная цена'],
                 'Базовая маржа': ['Базовая маржа'],
                 'Текущая цена': ['Текущая цена']}

    base_strategy_col = 'base_' # if column name is "strategy", then "base_strategy"
    lower_strategy_col = 'lower_'
    upper_strategy_col = 'upper_'

    base_applier = StrategyApplier(tree=base_tree, strategy_col=base_strategy_col)
    lower_applier = StrategyApplier(tree=lower_tree, strategy_col=lower_strategy_col)
    upper_applier = StrategyApplier(tree=upper_tree, strategy_col=upper_strategy_col)
    

    # For everything else:
    # new_applier = StrategyApplier(tree=new_tree, ...)

    #pprint(base_applier.strategies_list)
    #pprint(base_applier.strategies_dict)
    #pprint(base_applier.tree)

    table = pd.read_excel('text.xlsx', dtype=DTYPES, converters=converters)
    table = table.replace(r'^\s*$', np.nan, regex=True)

    table['log'] = '[]'
    table['log'] = table['log'].apply(eval)

    #dtypes = {key: value for key, value in DTYPES.items() if key in table.columns}

    #table = table.astype(dtype=dtypes)
    #table.rename(columns=RUS_TO_ENG, inplace=True)

    #print(table['priority_competitors'].unique())
    table['comp_prices'] = table['comp_prices'].apply(try_eval_dict)
    table['priority_competitors'] = table['priority_competitors'].apply(lambda x: eval(x))

    table = table.apply(base_applier.run, axis=1)
    table = table.apply(lower_applier.run, axis=1)
    table = table.apply(upper_applier.run, axis=1)
    
    table = table.apply(bounds_check, axis = 1)
    table = table.apply(rounding_pricing, axis=1)
    table = table.apply(diff_pricing, axis=1)
    table = table.apply(fix_price_check, axis = 1)

    #table = table.apply(margin_limit_pricing, axis=1)
    #table = table.apply(rounding_pricing, axis=1)
    #table = table.apply(diff_pricing, axis=1)
    #table = table.apply(promo, axis=1)

    #table['front_margin_forecast'] =\
    #        (table['strategy_price'] / (1 + table['outcoming_nds'])\
    #        - table['purchase_price_without_nds'])\
    #        / (table['strategy_price'] / (1 + table['outcoming_nds']))

    #table['front_margin_abs_forecast'] = table['front_margin_forecast'] * table['sales_quantity'] * table['strategy_price']
    #table['front_margin_delta'] = (table['front_margin_forecast'] - table['front_margin']).round(2)
    #table['front_margin'] = (table['front_margin'].round(2) * 100).astype(str) + '%'

    # table.rename(columns=ENG_TO_RUS, inplace=True)
    # table['priority_competitors'] = table['priority_competitors'].astype(str)
    # table['comp_prices'] = table['comp_prices'].astype(str)

    #pprint(table.head())

    table.to_excel('out_test.xlsx')

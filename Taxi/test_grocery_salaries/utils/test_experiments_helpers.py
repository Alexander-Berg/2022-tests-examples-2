from decimal import Decimal

import pandas as pd
import pytest

from grocery_salaries.utils.experiments_helpers import get_heavy_order


@pytest.mark.client_experiments3(
    consumer='grocery_salaries/is_heavy_order',
    experiment_name='grocery_salaries_heavy_order_experiment',
    args=[{'name': 'region_id', 'type': 'int', 'value': 54}],
    value={'order_weight_threshold_g': 15000},
)
@pytest.mark.client_experiments3(
    consumer='grocery_salaries/is_heavy_order',
    experiment_name='grocery_salaries_heavy_order_experiment',
    args=[{'name': 'region_id', 'type': 'int', 'value': 23}],
    value={'order_weight_threshold_g': 150000},
)
@pytest.mark.client_experiments3(
    consumer='grocery_salaries/is_heavy_order',
    experiment_name='grocery_salaries_heavy_order_experiment',
    value={'order_weight_threshold_g': 150000},
)
async def test_get_heavy_order(cron_context):
    result = pd.DataFrame(
        [
            (54, 14000, Decimal(0)),
            (54, 15000, Decimal(1)),
            (54, 16000, Decimal(1)),
            (23, 14000, Decimal(0)),
            (23, 15000, Decimal(0)),
            (23, 16000, Decimal(0)),
            (None, 16000, Decimal(0)),
        ],
        columns=['region_id', 'order_weight_g', 'heavy_orders'],
    )

    dataframe = result[['region_id', 'order_weight_g']].copy()
    dataframe = await get_heavy_order(cron_context, dataframe)
    pd.testing.assert_frame_equal(dataframe, result)

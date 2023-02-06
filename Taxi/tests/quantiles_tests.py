# coding: utf-8

import pytest
import numpy as np
import pandas as pd

from business_models.models.outliers import MultipleOutliers
from business_models.util import get_list


@pytest.mark.parametrize(
    "outliers_class,x,y,x_filtered_expected,y_filtered_expected,drop_kwargs",
    [
        (
                MultipleOutliers, np.arange(1, 101), np.arange(1, 101), np.arange(3, 99), np.arange(3, 99),
                {"x_axis": True, "y_axis": False, "x_how": "both", "y_how": "both", "x_quantile": 0.98,
                 "y_quantile": 0.98}
         ),
        (
                MultipleOutliers, np.arange(1, 101), np.arange(1, 101), np.arange(3, 99), np.arange(3, 99),
                {"x_axis": True, "y_axis": True, "x_how": "both", "y_how": "both", "x_quantile": 0.98,
                 "y_quantile": 0.98}
        ),
        (
                MultipleOutliers, np.arange(1, 101), np.arange(100, 0, -1), np.arange(3, 99), np.arange(98, 2, -1),
                {"x_axis": True,"y_axis": True, "x_how": "right", "y_how": "right", "x_quantile": 0.98,
                 "y_quantile": 0.98}
        ),
        (
                MultipleOutliers, np.arange(1, 101), np.arange(100, 0, -1), np.arange(3, 99), np.arange(98, 2, -1),
                {"x_axis": True, "y_axis": True, "x_how": "both", "y_how": "both", "x_quantile": 0.98,
                 "y_quantile": 0.98}
        ),
        (
                MultipleOutliers, np.arange(1, 101), np.arange(1, 101), np.arange(1, 101), np.arange(1, 101), {}
        ),
        (
                MultipleOutliers, np.arange(1, 2), np.arange(1, 2), np.arange(1, 2), np.arange(1, 2),
                {"x_axis": True, "y_axis": False, "x_how": "both", "y_how": "both", "x_quantile": 0.98,
                 "y_quantile": 0.98}
        ),
        (
                MultipleOutliers, np.arange(1, 101), np.arange(100, 0, -1), np.arange(3, 99), np.arange(98, 2, -1),
                [
                    {"x_axis": True, "y_axis": True, "x_how": "both", "y_how": "both",
                        "x_quantile": 0.99, "y_quantile": 0.99},
                    {"x_axis": True, "y_axis": True, "x_how": "both", "y_how": "both",
                     "x_quantile": 0.99, "y_quantile": 0.99}
                ]
        ),
    ]

)
def drop_outliers_tests(outliers_class, x, y, x_filtered_expected, y_filtered_expected, drop_kwargs):
    mo = outliers_class()
    drop_kwargs = get_list(drop_kwargs)
    test = mo.drop(pd.Series(x), pd.Series(y), ["QuantileOutliers"] * len(drop_kwargs), drop_kwargs)

    assert pd.Series(y_filtered_expected).equals(test[1])
    assert pd.Series(x_filtered_expected).equals(test[0])


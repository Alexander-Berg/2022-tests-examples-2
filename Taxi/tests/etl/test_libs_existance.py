# -*- coding: utf-8 -*-
import os
from etl.processes.food_orders.backfilling_loader import QUADKEY_LIB_PATH


def test_quadkey_lib_exists():
    assert os.path.exists(QUADKEY_LIB_PATH)

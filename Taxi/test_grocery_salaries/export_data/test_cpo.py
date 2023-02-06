import numpy as np
import pandas as pd
import pytest

from grocery_salaries.salaries.export_data.cpo_exporters import BaseExporter
from grocery_salaries.salaries.export_data.cpo_exporters import compensate_vat
from grocery_salaries.salaries.export_data.cpo_exporters import (
    get_formatted_datetime,
)
from grocery_salaries.salaries.export_data.cpo_exporters import get_record_id
from grocery_salaries.utils import yt_helpers


async def test_export_only_append(monkeypatch, cron_context):
    called = False  # In case we change how we write tables

    class AlmostBaseExporter(BaseExporter):
        def get_full_period(self):
            pass

    async def write_table(*args, **kwargs):
        nonlocal called
        called = True
        assert 'append' in kwargs
        assert kwargs['append']

    monkeypatch.setattr(yt_helpers.YtClient, 'write_table', write_table)
    exporter = object.__new__(AlmostBaseExporter)
    exporter.report = []
    exporter.orders_df = pd.DataFrame(columns=['order_id', 'shift_id'])
    exporter.context = cron_context
    await BaseExporter._export(exporter)  # pylint: disable=protected-access
    assert called


@pytest.mark.parametrize(
    'shift_date, courier_id, shift_id, result',
    [
        ('2022-01-01', 10, 'asdf', '2022-01-01_10_asdf'),
        ('2022-01-01', None, 'asdf', '2022-01-01_None_asdf'),
        (1, 2, 3, '1_2_3'),
        ('1', '2', '3', '1_2_3'),
        (None, None, None, 'None_None_None'),
    ],
)
def test_get_record_id(shift_date, courier_id, shift_id, result):
    assert get_record_id(shift_date, courier_id, shift_id) == result


@pytest.mark.parametrize(
    'datetime, result',
    [
        ('2022-03-23 09:00:00+03:00', '2022-03-23 09:00:00+03:00'),
        ('2022-03-23 09:00:00', '2022-03-23 09:00:00'),
        ('2022-03-23', '2022-03-23 00:00:00'),
        (None, ''),
        (np.nan, ''),
        (np.NAN, ''),
        (np.NaN, ''),
        (pd.NA, ''),
        (pd.NaT, ''),
    ],
)
def test_get_formatted_datetime(datetime, result):
    assert get_formatted_datetime(datetime) == result


@pytest.mark.parametrize(
    'amount, vat, result',
    [
        (100, 0, 100),
        (111.111, 0, 111.111),
        (90, 0.1, 100),
        (-90, 0.1, -100),
        (110, -0.1, 99.99999999999999),
        (90, 0.9, 900.0000000000002),
        (7.5, 0.25, 10),
        (123.456, 0.123, 140.7708095781072),
        (123.456, 1, 123.456),
        (123.456, 7.89, 123.456),
    ],
)
def test_compensate_vat(amount, vat, result):
    assert compensate_vat(amount, vat) == result

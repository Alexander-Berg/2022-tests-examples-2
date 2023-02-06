import decimal

import pytest

from taxi import billing

from billing_functions.repositories import tariffs as tariffs_repo
from test_billing_functions import mocks


def _apply_tariff_mock(stq3_context, load_py_json, monkeypatch):
    tariffs = mocks.Tariffs(load_py_json('db_tariffs.json'))
    monkeypatch.setattr(stq3_context, 'tariffs', tariffs)


@pytest.mark.parametrize(
    'category_id, expected_category_name, expected_category_minimal_cost',
    [
        (
            '05f1a588b7484e68b58a5e86755b0cbf',
            'econom',
            billing.Money(decimal.Decimal('100'), 'RUB'),
        ),
        (
            '05f1a588b7484e68b58a5e86755b0cbd',
            'test1',
            billing.Money(decimal.Decimal('300'), 'RUB'),
        ),
    ],
)
async def test_success_fetch_category_by_id(
        category_id,
        expected_category_name,
        expected_category_minimal_cost,
        stq3_context,
        monkeypatch,
        load_py_json,
):
    _apply_tariff_mock(stq3_context, load_py_json, monkeypatch)

    category = await stq3_context.tariffs.fetch_category_by_id(category_id)

    assert category.name == expected_category_name
    assert category.minimal_cost == expected_category_minimal_cost


async def test_failed_fetch_category_by_id(
        stq3_context, load_py_json, monkeypatch,
):
    _apply_tariff_mock(stq3_context, load_py_json, monkeypatch)

    with pytest.raises(tariffs_repo.CategoryNotFoundError):
        await stq3_context.tariffs.fetch_category_by_id('404')


@pytest.mark.parametrize(
    'zone_name, expected_country, expected_time_zone',
    [('mytishchi', 'rus', 'Europe/Moscow'), ('astana', 'kaz', 'Asia/Omsk')],
)
async def test_success_fetch_tariff_zone(
        zone_name,
        expected_country,
        expected_time_zone,
        stq3_context,
        load_py_json,
        monkeypatch,
):
    _apply_tariff_mock(stq3_context, load_py_json, monkeypatch)

    zone = await stq3_context.tariffs.fetch_tariff_zone_by_name(zone_name)

    assert zone.country == expected_country
    assert zone.name == zone_name
    assert zone.time_zone == expected_time_zone


async def test_failed_fetch_tariff_zone(
        stq3_context, load_py_json, monkeypatch,
):
    _apply_tariff_mock(stq3_context, load_py_json, monkeypatch)

    with pytest.raises(tariffs_repo.TariffZoneNotFoundError):
        await stq3_context.tariffs.fetch_tariff_zone_by_name('404')

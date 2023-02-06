# pylint: disable=too-many-arguments
import pytest

from taxi_billing_tlog.yt import converters

_ENTRIES = (
    (
        'park_b2b_trip_payment.json',
        converters.ExpensesRowConverter,
        'park_b2b_trip_payment',
    ),
    (
        'client_b2b_trip_payment.json',
        converters.RevenuesRowConverter,
        'client_b2b_trip_payment',
    ),
    ('subvention.json', converters.ExpensesRowConverter, 'subsidy'),
    ('subvention.json', converters.RevenuesRowConverter, 'subvention'),
)

_PREFIXES = (
    (None, ''),
    ('econom', ''),
    ('cargo', 'cargo_'),
    ('express', 'delivery_'),
    ('night', 'delivery_'),
)


@pytest.mark.parametrize('tariff_class,prefix', _PREFIXES)
@pytest.mark.parametrize('json,row_converter_cls,product', _ENTRIES)
@pytest.mark.config(
    BILLING_TLOG_SPLIT_PRODUCTS_BY_TARIFF={
        'revenues': {
            'cargo': ['client_b2b_trip_payment', 'subvention'],
            'express': ['client_b2b_trip_payment', 'subvention'],
            'night': ['client_b2b_trip_payment', 'subvention'],
        },
        'expenses': {
            'cargo': ['park_b2b_trip_payment', 'subsidy'],
            'express': ['park_b2b_trip_payment', 'subsidy'],
            'night': ['park_b2b_trip_payment', 'subsidy'],
        },
    },
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'client_b2b_trip_payment': {'payment': 1, 'refund': -1},
        'subvention': {'payment': -1, 'refund': 1},
    },
)
def test_product_splitting_by_tariff_enabled(
        cron_context,
        load_json,
        json,
        row_converter_cls,
        product,
        tariff_class,
        prefix,
):
    _test_product_conversion(
        payload=load_json(json),
        prefix=prefix,
        tariff_class=tariff_class,
        converter=row_converter_cls(context=cron_context),
        expected=prefix + product,
    )


@pytest.mark.parametrize('tariff_class,prefix', _PREFIXES)
@pytest.mark.parametrize('json,row_converter_cls,product', _ENTRIES)
@pytest.mark.config(
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'client_b2b_trip_payment': {'payment': 1, 'refund': -1},
        'subvention': {'payment': -1, 'refund': 1},
    },
)
def test_product_splitting_by_tariff_disabled(
        cron_context,
        load_json,
        json,
        row_converter_cls,
        product,
        tariff_class,
        prefix,
):
    _test_product_conversion(
        payload=load_json(json),
        prefix=prefix,
        tariff_class=tariff_class,
        converter=row_converter_cls(context=cron_context),
        expected=product,
    )


@pytest.mark.parametrize('tariff_class,prefix', _PREFIXES)
@pytest.mark.parametrize('json,row_converter_cls,product', _ENTRIES)
@pytest.mark.config(
    BILLING_TLOG_SPLIT_PRODUCTS_BY_TARIFF={
        'expenses': {'cargo': ['nonexistent']},
        'revenues': {'express': ['nonexistent']},
    },
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'client_b2b_trip_payment': {'payment': 1, 'refund': -1},
        'subvention': {'payment': -1, 'refund': 1},
    },
)
def test_product_splitting_by_tariff_enabled_but_not_allowed(
        cron_context,
        load_json,
        json,
        row_converter_cls,
        product,
        tariff_class,
        prefix,
):
    _test_product_conversion(
        payload=load_json(json),
        prefix=prefix,
        tariff_class=tariff_class,
        converter=row_converter_cls(context=cron_context),
        expected=product,
    )


def _test_product_conversion(
        *, payload, prefix, tariff_class, converter, expected,
):
    if tariff_class:
        payload['details']['tariff_class'] = tariff_class
    entry = converter.ENTRY_CLASS.from_tuple((1, '1', payload))
    result = converter(entry)
    assert result['product'] == expected
    if prefix:
        assert result['detailed_product'].startswith(prefix) is False

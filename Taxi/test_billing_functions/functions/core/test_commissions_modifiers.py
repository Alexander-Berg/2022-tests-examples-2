import decimal

import pytest

from billing_functions.functions.core.commissions import entities
from billing_functions.functions.core.commissions import models
from billing_functions.functions.core.commissions import modifiers
from test_billing_functions import var


Commission = models.Commission
Component = models.Component


@pytest.mark.parametrize(
    'marketing_level, expected',
    [
        pytest.param(
            frozenset(),
            Commission(
                value=var.make_var('20'),
                vat=var.make_var('4'),
                vat_rate=var.make_var('1'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('20'), decimal.Decimal('4')),
            ),
            id='no discount',
        ),
        pytest.param(
            frozenset(['co_branding', 'lightbox', 'sticker']),
            Commission(
                value=var.make_var(
                    '16.0',
                    [
                        (
                            'sub',
                            '4',
                            'sub_discount',
                            '16',
                            {'for': ['co_branding', 'lightbox']},
                        ),
                    ],
                ),
                vat=var.make_var(
                    '3.2',
                    [
                        (
                            'sub',
                            '0.8',
                            'sub_discount',
                            '3.2',
                            {'for': ['co_branding', 'lightbox']},
                        ),
                    ],
                ),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('20'), decimal.Decimal('4')),
                branding_discount=Component(
                    decimal.Decimal('4'), decimal.Decimal('0.8'),
                ),
            ),
            id='happy path',
        ),
    ],
)
def test_apply_branding_discounts(marketing_level, expected):
    modifier = modifiers.BrandingDiscount(
        branding_discounts=entities.BrandingDiscounts(
            [
                (
                    frozenset(['co_branding', 'lightbox']),
                    decimal.Decimal('0.04'),
                ),
                (frozenset(['lightbox']), decimal.Decimal('0.02')),
            ],
        ),
    )
    context = modifiers.BrandingDiscountContext(
        marketing_level=marketing_level,
    )
    actual = modifier.apply(
        context,
        commission=Commission(
            value=var.make_var('20'),
            vat=var.make_var('4'),
            vat_rate=var.make_var('1.2'),
            rate=None,
            cost=var.make_var('100'),
            gross=Component(decimal.Decimal('20'), decimal.Decimal('4')),
        ),
    )
    assert actual == expected


@pytest.mark.parametrize(
    'commission_limit_if_promocode, expected',
    [
        pytest.param(
            decimal.Decimal('24'),
            Commission(
                value=var.make_var('20'),
                vat=var.make_var('4'),
                vat_rate=var.make_var('1'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('20'), decimal.Decimal('4')),
            ),
            id='commission in limit',
        ),
        pytest.param(
            decimal.Decimal('1'),
            Commission(
                value=var.make_var(
                    '0.8333333333333333333333333333',
                    [
                        (
                            'set',
                            '0.8333333333333333333333333333',
                            'set_from_driver_promocode_commission',
                            '0.8333333333333333333333333333',
                        ),
                    ],
                ),
                vat=var.make_var(
                    '0.1666666666666666666666666667',
                    [
                        (
                            'set',
                            '0.1666666666666666666666666667',
                            'set_from_driver_promocode',
                            '0.1666666666666666666666666667',
                        ),
                    ],
                ),
                vat_rate=var.make_var('1.2'),
                rate=None,
                cost=var.make_var('100'),
                gross=Component(decimal.Decimal('20'), decimal.Decimal('4')),
                promocode_discount=Component(
                    decimal.Decimal('19.16666666666666666666666667'),
                    decimal.Decimal('3.833333333333333333333333333'),
                ),
                unrealized=Component(
                    decimal.Decimal('19.16666666666666666666666667'),
                    decimal.Decimal('3.833333333333333333333333333'),
                ),
                unrealized_without_discount_value=decimal.Decimal(
                    '19.16666666666666666666666667',
                ),
            ),
            id='commission out of limit',
        ),
    ],
)
def test_apply_driver_promocode(commission_limit_if_promocode, expected):
    modifier = modifiers.DriverPromocode()
    context = modifiers.DriverPromocodeContext(
        driver_with_promocode=True,
        commission_limit_if_promocode=commission_limit_if_promocode,
    )
    actual = modifier.apply(
        context,
        Commission(
            value=var.make_var('20'),
            vat=var.make_var('4'),
            cost=var.make_var('0'),
            vat_rate=var.make_var('1.2'),
            gross=Component(decimal.Decimal('20'), decimal.Decimal('4')),
            rate=None,
        ),
    )
    assert actual == expected

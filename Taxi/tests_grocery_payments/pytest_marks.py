import pytest

from . import consts
from . import models

COUNTRIES = pytest.mark.parametrize('country', consts.COUNTRIES)

INVOICE_ORIGINATORS = pytest.mark.parametrize(
    'originator', models.InvoiceOriginator,
)

INVOICE_STATUSES_WITH_CLEARED = pytest.mark.parametrize(
    'invoice_status, is_cleared',
    [
        ('init', False),
        ('holding', False),
        ('held', False),
        ('hold-failed', False),
        ('clearing', True),
        ('cleared', True),
        ('clear-failed', True),
        ('refunding', True),
    ],
)

PAYMENT_TYPES = pytest.mark.parametrize(
    'payment_type',
    [
        models.PaymentType.card,
        models.PaymentType.applepay,
        models.PaymentType.googlepay,
        models.PaymentType.badge,
        models.PaymentType.corp,
        models.PaymentType.cibus,
        models.PaymentType.sbp,
    ],
)

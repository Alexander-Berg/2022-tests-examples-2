import pytest

from . import consts
from . import models

DEPOT_COMPANY_TYPE = pytest.mark.parametrize(
    'depot_company_type, oebs_depot_id',
    [('franchise', ''), ('yandex', consts.OEBS_DEPOT_ID)],
)

RECEIPT_TYPES = pytest.mark.parametrize(
    'receipt_type', [models.ReceiptType.Payment, models.ReceiptType.Refund],
)

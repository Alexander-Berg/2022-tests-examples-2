# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_payments_shared import transactions as transactions_lib

from . import consts
from . import models


def make_callback_transaction(**kwargs) -> dict:
    return {
        'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
        'payment_type': models.PaymentType.card.value,
        **kwargs,
    }


def make_transaction(**kwargs) -> dict:
    return transactions_lib.make_transaction(**kwargs)


def make_operation(**kwargs) -> dict:
    return transactions_lib.make_operation(**kwargs)


def make_refund(**kwargs) -> dict:
    return transactions_lib.make_refund(**kwargs)


def flatten(list_of_lists):
    result = []
    for inner_list in list_of_lists:
        for elem in inner_list:
            result.append(elem)

    return result


def get_stq_event_id(
        operation_id,
        payment_id,
        invoice_originator=models.InvoiceOriginator.grocery,
        receipt_data_type=None,
):
    receipt_data_type = (
        receipt_data_type or invoice_originator.receipt_data_type
    )

    return (
        f'{invoice_originator.prefix}{operation_id}'
        + f'_{payment_id}_{receipt_data_type}'
    )

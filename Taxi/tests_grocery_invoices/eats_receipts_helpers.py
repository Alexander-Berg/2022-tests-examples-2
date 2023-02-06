from tests_grocery_invoices import consts


def is_eats_core_receipts(service):
    return service == consts.EATS_CORE_RECEIPTS


def eats_receipts_stq_source(service):
    if is_eats_core_receipts(service):
        return consts.EATS_CORE_SOURCE

    return service

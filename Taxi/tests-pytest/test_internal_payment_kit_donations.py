import pytest

from taxi.core import async
from taxi.internal.payment_kit import donations


_MISSING = object()


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('num_runs,avg_num_tlogs,container', [
    (10, 1, [1]),
    (10, 1.4, [1, 2]),
    (10, 2, [2]),
    (10, 2.99, [2, 3]),
])
def test_get_num_tlogs_to_process(num_runs, avg_num_tlogs, container):
    for _ in range(num_runs):
        num_tlogs = donations.get_num_tlogs_to_process(avg_num_tlogs)
        assert num_tlogs in container


def patch_update_donation_transactions(patch, eta, transactions_after):
    @patch(
        'taxi.internal.order_kit.invoice_handler.update_donation_transactions'
    )
    @async.inline_callbacks
    def update_donation_transactions(payable, log_extra=None):
        if isinstance(eta, Exception):
            raise eta
        if transactions_after is not None:
            payable.invoice_doc['billing_tech']['transactions'] = transactions_after
        async.return_value(eta)
        yield

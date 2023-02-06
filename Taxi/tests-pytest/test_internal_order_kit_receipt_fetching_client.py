import json

import pytest

from taxi.internal.receipt_fetching import client as receipt_client


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('order_ids', [
    ([]),
    (['801fb61ae4ca2b08be680e5c64eb7fc8', ]),
    (['801fb61ae4ca2b08be680e5c64eb7fc8', '801fb61ae4ca2b08be680e5c64eb7fc9']),
])
def test_receipts(areq_request, order_ids):
    def make_receipts_response(order_ids):
        receipts = []
        for order_id in order_ids:
            receipt = {
                'order_id': order_id,
                'receipt_url': 'https://buhta.kz/yt/{}'.format(order_id),
            }
            receipts.append(receipt)
        return receipts

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url == 'http://receipt-fetching.taxi.dev.yandex.net/receipts'

        order_ids = kwargs['json']['order_ids']
        receipts = make_receipts_response(order_ids)
        response = {'receipts': receipts}

        return areq_request.response(200, body=json.dumps(response))

    response = receipt_client.receipts(order_ids)
    assert response == make_receipts_response(order_ids)

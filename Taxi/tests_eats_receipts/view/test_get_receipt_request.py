import psycopg2


RECEIPT_REQUEST_HANDLER = '/api/v1/receipt_request'


async def test_get_receipt_request(load_json, pgsql, stq, taxi_eats_receipts):
    request = load_json('request.json')
    response = await taxi_eats_receipts.post(
        RECEIPT_REQUEST_HANDLER, json=request,
    )

    assert response.status_code == 204

    cursor = pgsql['eats_receipts'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    cursor.execute('SELECT * FROM eats_receipts.send_receipt_requests')
    receipt_request = cursor.fetchone()
    assert receipt_request['document_id'] == 'test_order/refund/create:100500'
    assert receipt_request['created_at'] is not None
    assert receipt_request['created_at'] == receipt_request['updated_at']
    assert receipt_request['status'] == 'created'
    assert receipt_request['user_info'] == '(mail_id,phone_id)'
    assert receipt_request['order_info'] == '(RU,card)'
    assert receipt_request['order_id'] == 'test_order'
    assert receipt_request['originator'] == 'eats-payments'

    assert stq.eats_send_receipt.times_called == 1

    # Idempotency test
    response = await taxi_eats_receipts.post(
        RECEIPT_REQUEST_HANDLER, json=request,
    )

    assert response.status_code == 204


async def test_get_receipt_malformed_request(
        load_json, pgsql, stq, taxi_eats_receipts,
):
    request = load_json('request.json')
    request['products'][0]['supplier_inn'] = '111'

    response = await taxi_eats_receipts.post(
        RECEIPT_REQUEST_HANDLER, json=request,
    )

    assert response.status_code == 400


async def test_get_receipt_malformed_inn(
        load_json, pgsql, stq, taxi_eats_receipts,
):
    request = load_json('request.json')
    # Invalid checksum of individual inn
    request['products'][0]['supplier_inn'] = '479753954665'

    request['products'][0]['supplier_inn_id'] = None

    response = await taxi_eats_receipts.post(
        RECEIPT_REQUEST_HANDLER, json=request,
    )

    assert response.status_code == 400
    assert response.headers['X-YaTaxi-Error-Code'] == '4000'


async def test_get_receipt_empty_inn_and_inn_id(
        load_json, pgsql, stq, taxi_eats_receipts,
):
    request = load_json('request.json')

    request['products'][0]['supplier_inn'] = None
    request['products'][0]['supplier_inn_id'] = None

    response = await taxi_eats_receipts.post(
        RECEIPT_REQUEST_HANDLER, json=request,
    )

    assert response.status_code == 400
    assert response.headers['X-YaTaxi-Error-Code'] == '4000'


async def test_get_receipt_no_inn_checksum_check(
        load_json, pgsql, stq, taxi_eats_receipts,
):
    request = load_json('request.json')

    # Invalid checksum of individual inn
    request['products'][0]['supplier_inn'] = '479753954665'

    response = await taxi_eats_receipts.post(
        RECEIPT_REQUEST_HANDLER, json=request,
    )

    assert response.status_code == 204

import base64
import hashlib
import hmac
import urllib.parse


def pg_response_to_dict(cursor):
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]
    return res


def create_receipt(
        park_id,
        driver_id,
        order_id,
        cashbox_id,
        external_id,
        status,
        order_price=None,
        order_end=None,
        task_uuid=None,
        url=None,
        details=None,
        fail_message=None,
        failure_id=None,
):
    return {
        'park_id': park_id,
        'driver_id': driver_id,
        'order_id': order_id,
        'cashbox_id': cashbox_id,
        'external_id': external_id,
        'status': status,
        'order_price': order_price,
        'order_end': order_end,
        'fail_message': fail_message,
        'task_uuid': task_uuid,
        'url': url,
        'details': details,
        'failure_id': failure_id,
    }


def compare_receipt(receipt, expected_receipt):
    for key, value in expected_receipt.items():
        assert receipt[key] == value, 'key {} ({} != {})'.format(
            key, value, receipt[key],
        )


def get_all_cashboxes(pgsql):
    cursor = pgsql['cashbox_integration'].cursor()
    cursor.execute('SELECT * from cashbox_integration.cashboxes')
    rows = pg_response_to_dict(cursor)
    cursor.close()
    return rows


def make_receipt_id(park_id, order_id):
    return f'{park_id}-{order_id}'


def make_receipt_id_signature(receipt_id):
    return base64.b64encode(
        hmac.new(
            b'todua_random_key',
            msg=receipt_id.encode(),
            digestmod=hashlib.sha256,
        ).digest(),
    ).decode()


def make_receipt_params(park_id, order_id):
    receipt_id = make_receipt_id(park_id, order_id)
    return {
        'receipt_id': receipt_id,
        'sign': make_receipt_id_signature(receipt_id),
    }


def get_receipt_url(park_id, order_id):
    return (
        'https://taximeter-core.tst.mobile.yandex.net'
        '/v1/parks/orders/receipt?{}'.format(
            urllib.parse.urlencode(make_receipt_params(park_id, order_id)),
        )
    )


def get_cashboxes_by_id(pgsql, park_id, ids):
    cursor = pgsql['cashbox_integration'].cursor()

    rows = []

    for cashbox_id in ids:
        cursor.execute(
            'SELECT * from cashbox_integration.cashboxes where '
            'park_id=\'{}\' AND id=\'{}\''.format(park_id, cashbox_id),
        )
        rows += pg_response_to_dict(cursor)

    return rows


def get_receipt_by_id(pgsql, park_id, order_id):
    cursor = pgsql['cashbox_integration'].cursor()

    cursor.execute(
        'SELECT * FROM cashbox_integration.receipts WHERE '
        'park_id=\'{}\' AND order_id=\'{}\''.format(park_id, order_id),
    )

    rows = pg_response_to_dict(cursor)
    assert len(rows) == 1

    return rows[0]

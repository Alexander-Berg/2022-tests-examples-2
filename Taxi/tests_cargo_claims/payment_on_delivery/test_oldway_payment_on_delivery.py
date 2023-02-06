import uuid

import pytest

from testsuite.utils import matching


SEARCH_DEFAULT_REQUEST = {'offset': 0, 'limit': 10}


def _get_claim_point_by_order(claim, visit_order):
    for point in claim['route_points']:
        if point['visit_order'] == visit_order:
            return point

    pytest.fail(f'No such visit_order {visit_order} in claim: {claim}')
    return None


@pytest.mark.parametrize(
    'handler, handler_type',
    [
        ('/api/integration/v2/claims/search', 'search'),
        ('/api/integration/v2/claims/search/active', 'search'),
        ('/api/integration/v2/claims/bulk_info', 'bulk_info'),
        ('/api/integration/v2/claims/bulk_info', 'bulk_info'),
        ('/api/integration/v2/claims/info', 'info'),
    ],
)
async def test_oldway_info(
        taxi_cargo_claims,
        enable_payment_on_delivery,
        create_segment_with_performer,
        get_claim_v2,
        get_default_headers,
        pgsql,
        handler,
        handler_type,
):
    """
        Check handlers OK on oldway payment_on_delivery data.

        This test is not very important,
        total oldway orders ~5000,
        last oldway order created 2021-03-21 17:45:29.322453+03.
    """
    # Create claim and fill with oldway data
    claim_info = await create_segment_with_performer()

    claim_id = claim_info.claim_id

    claim = await get_claim_v2(claim_id)

    claim_point_id = _get_claim_point_by_order(claim, visit_order=2)['id']

    cursor = pgsql['cargo_claims'].conn.cursor()
    cursor.execute(
        f"""
        INSERT INTO cargo_claims.payment_on_delivery
            (payment_ref_id, claim_point_id, client_order_id,
            cost, tax_system_code, customer_email_id,
            customer_phone_id, customer_full_name,
            customer_inn, invoice_link, claim_uuid)
        VALUES ('{uuid.uuid4().hex}', '{claim_point_id}', 'client_order_id_1',
            '10.10', 1, 'email_1_id',
            'phone_1_id', 'full_name_1', '1234567890',
            'https://ofd.yandex.ru/vaucher/0005312316002718/9410/2604520024',
            '{claim_id}');
    """,
    )

    cursor.execute(
        f"""
        INSERT INTO cargo_claims.items_fiscalization
            (item_id, vat_code, payment_subject,
            payment_mode, product_code, country_of_origin_code,
            customs_declaration_number, excise, claim_uuid)
        SELECT items.id, 1, 'commodity',
            'full_payment', 'product_code_1', 'RU',
            '1', '12.12', '{claim_id}'
        FROM cargo_claims.items
    """,
    )

    # call handler
    if handler_type == 'search':
        response = await taxi_cargo_claims.post(
            handler,
            json=SEARCH_DEFAULT_REQUEST,
            headers=get_default_headers(),
        )
    elif handler_type == 'bulk_info':
        response = await taxi_cargo_claims.post(
            handler,
            headers=get_default_headers(),
            json={'claim_ids': [claim_info.claim_id]},
        )
    elif handler_type == 'info':
        response = await taxi_cargo_claims.post(
            handler,
            params={'claim_id': claim_info.claim_id},
            headers=get_default_headers(),
        )
    else:
        assert False

    assert response.status_code == 200

    json = response.json()
    if handler_type in ('search', 'bulk_info'):
        response_claim = json['claims'][0]
    elif handler_type == 'info':
        response_claim = json
    else:
        assert False

    # Check for payment_on_delivery and item_fiscalization parts
    point = _get_claim_point_by_order(response_claim, visit_order=2)

    # drop unnecessary fields
    point['payment_on_delivery']['customer'].pop('personal_email_id', None)
    point['payment_on_delivery']['customer'].pop('personal_phone_id', None)
    point['payment_on_delivery']['customer'].pop('email', None)
    point['payment_on_delivery']['customer'].pop('phone', None)

    assert point['payment_on_delivery'] == {
        'client_order_id': 'client_order_id_1',
        'cost': '10.1000',
        'customer': {'full_name': 'full_name_1', 'inn': '1234567890'},
        'is_paid': False,
        'payment_ref_id': matching.AnyString(),
        'tax_system_code': 1,
        'invoice_link': (
            'https://ofd.yandex.ru/vaucher/0005312316002718/9410/2604520024'
        ),
    }

    assert claim['items'][0] == {
        'cost_currency': 'RUB',
        'cost_value': '10.40',
        'droppof_point': 2,
        'id': 1,
        'pickup_point': 1,
        'quantity': 3,
        'size': {'height': 0.5, 'length': 20.0, 'width': 5.8},
        'title': 'item title 1',
        'weight': 10.2,
    }

import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_activate_discount(taxi_corp_discounts, pgsql, load_json):
    body = load_json('activate_request.json')
    response = await taxi_corp_discounts.post(
        '/v1/discounts/activate', json=body,
    )
    assert response.status == 200
    assert response.json()['activated_at']

    cursor = pgsql['corp_discounts'].cursor()
    cursor.execute(
        'SELECT activated_at FROM corp_discounts.discount_links WHERE id = 1',
    )
    result = cursor.fetchone()[0]
    assert result

    # test that handler is idempotent (activated_at does not change)
    body = load_json('activate_request.json')
    response = await taxi_corp_discounts.post(
        '/v1/discounts/activate', json=body,
    )
    assert response.status == 200

    cursor = pgsql['corp_discounts'].cursor()
    cursor.execute(
        'SELECT activated_at FROM corp_discounts.discount_links WHERE id = 1',
    )
    new_result = cursor.fetchone()[0]
    assert new_result == result

    # make sure exactly one row was inserted into activation_log
    cursor.execute(
        'SELECT * FROM corp_discounts.activation_log WHERE link_id = 1',
    )
    assert len(cursor.fetchall()) == 1

import json

import pytest
from django import test as django_test


@pytest.mark.filldb(
    orders='recalc',
    commission_contracts='recalc',
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('data,order_ids,expected_costs', [
    (
        {
            'order_info': {
                'order_id': 'alias_1',
                'cost': 100,
            },
            'zendesk_ticket': '\t123\n'
        },
        ['id_1'],
        {100},
    ),
    (
        {
            'order_info': {
                'order_id': 'id_2',
                'cost': 600,
                'embedded_orders': [
                    {
                        'order_id': 'id_3',
                        'cost': 200,
                    },
                    {
                        'order_id': 'id_4',
                        'cost': 300,
                    },
                ]
            },
            'zendesk_ticket': '123',
            'ticket_type': 'startrack',
        },
        ['id_2', 'id_3', 'id_4'],
        {600, 200, 300}
    ),
])
def test_recalculate(data, order_ids, expected_costs):
    response = django_test.Client().post(
        '/api/commissions/recalculate/', json.dumps(data), 'application/json'
    )
    assert response.status_code == 400

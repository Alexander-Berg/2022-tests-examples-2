import pytest


TICKET_HEADER = 'X-Ya-Service-Ticket'

BAD_TICKET_ERROR = 'Bad tvm2 service ticket'

MISSING_TICKET_ERROR = 'missing or empty X-Ya-Service-Ticket header'

REQUEST_CALC_PAID_SUPPLY = {
    'point': [37.683, 55.774],
    'zone': 'spb',
    'categories': {},
    'modifications_scope': 'taxi',
}


def read_tvm_ticket(filename, load):
    try:
        for line in load(filename).splitlines():
            if not line.startswith('#'):
                return line.strip()
    except FileNotFoundError:
        pass
    return None


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'headers, error_message',
    [
        ({}, MISSING_TICKET_ERROR),
        ({TICKET_HEADER: ''}, MISSING_TICKET_ERROR),
        ({TICKET_HEADER: 'INVALID'}, BAD_TICKET_ERROR),
    ],
)
async def test_check_invalid_header(
        taxi_pricing_data_preparer, headers, error_message,
):
    response = await taxi_pricing_data_preparer.post(
        'v2/calc_paid_supply', headers=headers, json={},
    )
    assert response.status_code == 401
    resp = response.json()
    assert 'message' in resp
    assert resp['message'] == error_message


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_SERVICES={'mock': 300, 'pricing-data-preparer': 200},
    TVM_RULES=[{'src': 'mock', 'dst': 'pricing-data-preparer'}],
)
async def test_check_allowed(
        taxi_pricing_data_preparer, tvm2_client, taxi_config, load,
):
    tvm_services = taxi_config.get('TVM_SERVICES')
    tickets = {}
    for service_name, service_id in tvm_services.items():
        ticket = read_tvm_ticket(
            '{}_tvm2_ticket.txt'.format(service_name), load,
        )
        if ticket:
            tickets[service_id] = ticket

    tvm2_client.set_ticket(tickets)

    response = await taxi_pricing_data_preparer.post(
        'v2/calc_paid_supply',
        REQUEST_CALC_PAID_SUPPLY,
        headers={TICKET_HEADER: tickets[tvm_services['mock']]},
    )
    assert response.status_code == 200

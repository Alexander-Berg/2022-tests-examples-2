import pytest


# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq'
    '_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXD'
    'iiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848PW-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkHR3s'
)

# Generated via `tvmknife unittest service -s 2001716 -d 2001716`
DEBTS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggItJZ6ELSWeg'
    ':Ub6VhOZcj0V93-TSypyEqqwxTUs7uaaeb46PA'
    'HNiMnAuNrGXVbuR9wSfKvjTM_7defPpjqsiGf'
    'xeZLUdjcM8pVxLeXC-cE5O62YmXLyQawXU5IKB'
    'NFna0ZbvepJ69NeXag1hfSiqCXYi6Ih_v39fEjO8MWeSGGNsThNX9Ze9k1s'
)


@pytest.mark.config(
    TVM_ENABLED=True, TVM_RULES=[{'src': 'mock', 'dst': 'debts'}],
)
@pytest.mark.tvm2_ticket(
    {111: MOCK_SERVICE_TICKET, 2001716: DEBTS_SERVICE_TICKET},
)
async def test_internal_tvm2_create(debts_client, taxi_debts):
    await taxi_debts.invalidate_caches()
    patch = debts_client.make_patch(value='300', currency='RUB')

    headers = {'X-Ya-Service-Ticket': 'wrong'}
    response = await debts_client.send_patch(data=patch, headers=headers)
    assert response.status_code == 401

    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await debts_client.send_patch(data=patch, headers=headers)
    assert response.status_code == 200

import pytest


# Generated via `tvmknife unittest service -s 2001716 -d 2001716`
USERVER_SAMPLE_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggItJZ6ELSWeg:'
    'Ub6VhOZcj0V93-TSypyEqqwxTUs7uaaeb46PA'
    'HNiMnAuNrGXVbuR9wSfKvjTM_7defPpjqsiGf'
    'xeZLUdjcM8pVxLeXC-cE5O62YmXLyQawXU5IKB'
    'NFna0ZbvepJ69NeXag1hfSiqCXYi6Ih_v39fEjO8MWeSGGNsThNX9Ze9k1s'
)

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:'
    'Mq_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-h'
    'XDiiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848PW-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkHR3s'
)

# Generated via:
# tvmknife unittest user -d 42 -e test_yateam --scopes test:scope1,test:scope2
USER_TICKET1 = (
    '3:user:CA4Q__________9_GigKAggqEC'
    'oaC3Rlc3Q6c2NvcGUxGgt0ZXN0OnNjb3BlMiDShdjM'
    'BCgD:CfnUVumvRuqaW2blbN5v-njW73jd'
    '0G1c_vcNE-_8XQAadniAayTKrq6iLgE2weMgidW0oi'
    'eLdssjjyOIZDIqCy3gQyYslrYOiO17pIu'
    'vYXd0CTOdpJQdeFEBsnj8BqvhXWYJs7Y99gGYamKr8'
    '7hMeLUyippo4p_Ve3aJeuA1Syc'
)

# Generated via:
# tvmknife unittest user -d 424242 -u 1,2,3,4,5,6,999 -e test_yateam
USER_TICKET2 = (
    '3:user:CA4Q__________9_Gi8KAggBC'
    'gIIAgoCCAMKAggECgIIBQoCCAYKAwjnBwoECLLyGRCy'
    '8hkg0oXYzAQoAw:D8LFLrJhD9l8WFwdR'
    'HQreH0DEOTHMgeY6e5nIEX85swq0l3V0_h_EwK0s7su'
    'k8tUAGzBRYZqDQ5X6psBJHxMRduI5MdN'
    '04BzAPtv29t4NNmN3CnEMEDq4O2-M3DrBrVxlFU_rvk'
    'bIgRRF5TYIVznmXUCJYSPwx4eXAjA6Pz_Utw'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'userver-sample', 'dst': 'userver-sample'}],
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: 'ANOTHERTICKET'},
)
async def test_tvm2_service_auth_info1(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': USERVER_SAMPLE_SERVICE_TICKET}
    response = await taxi_userver_sample.get(
        'auth/get-source-service', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.json() == {
        'has-tvm-auth-info': True,
        'source-service-id': 2001716,
        'source-service-name': 'userver-sample',
    }


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_service_auth_info2(taxi_userver_sample):
    headers_set = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_userver_sample.get(
        'auth/get-source-service', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.json() == {
        'has-tvm-auth-info': True,
        'source-service-id': 111,
        'source-service-name': 'mock',
    }


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_user_auth_info1(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET1,
        'X-Yandex-UID': '42',
    }
    response = await taxi_userver_sample.get(
        'auth/get-source-user', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'has-tvm-auth-info': True,
        'source-user-default-id': 42,
        'source-user-ids': [42],
        'source-user-scopes': ['test:scope1', 'test:scope2'],
    }


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
    TVM_USER_TICKETS_ENABLED=True,
)
@pytest.mark.tvm2_ticket(
    {2001716: USERVER_SAMPLE_SERVICE_TICKET, 111: MOCK_SERVICE_TICKET},
)
async def test_tvm2_user_auth_info2(taxi_userver_sample):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Ya-User-Ticket': USER_TICKET2,
        'X-Yandex-UID': '424242',
    }
    response = await taxi_userver_sample.get(
        'auth/get-source-user', headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'has-tvm-auth-info': True,
        'source-user-default-id': 424242,
        'source-user-ids': [1, 2, 3, 4, 5, 6, 999, 424242],
        'source-user-scopes': [],
    }

import pytest


@pytest.mark.parametrize(
    ['body', 'status_code', 'created_by_corp_edo'],
    [
        pytest.param(
            {
                'client_id': 'client_1',
                'organization': 'market',
                'inn': '1503009020',
                'kpp': '773101001',
                'operator': 'sbis',
                'company_name': 'Amazon',
                'email': 'jeff@amazon.com',
                'comment': 'Hey! Join our edo!',
            },
            200,
            True,
            id='Everything ok',
        ),
        pytest.param(
            {
                'client_id': 'client_2',
                'organization': 'taxi',
                'inn': '1558904566',
                'kpp': '773901223',
                'operator': 'sbis',
                'company_name': 'Amazon',
                'email': 'bob@amazon.com',
                'comment': 'For this inn invite already exists in mock',
            },
            200,
            False,
            id='Uzedo returns 500',
        ),
    ],
)
@pytest.mark.config(
    CORP_EDO_OPERATOR_MAPPING={'diadoc': '2BM', 'sbis': '2BE'},
    CORP_EDO_ORGANIZATION_MAPPING={
        'market': 'yandex_test',
        'taxi': 'yandex_test',
    },
)
@pytest.mark.config(TVM_RULES=[{'src': 'corp-edo', 'dst': 'uzedo'}])
async def test_create_invitation(
        web_app_client,
        mock_uzedo,
        pgsql,
        body,
        status_code,
        created_by_corp_edo,
):
    response = await web_app_client.post('/v1/invitations/create', json=body)

    assert response.status == status_code
    if status_code != 200:
        return

    client: str = body['client_id']
    cursor = pgsql['corp_edo'].cursor()
    cursor.execute(
        f' SELECT status, created_by_corp_edo'
        f' FROM corp_edo.invitations'
        f' WHERE client_id = \'{client}\';',
    )
    record = cursor.fetchone()
    assert record[0] == 'WAITING_TO_BE_SEND'
    assert record[1] == created_by_corp_edo

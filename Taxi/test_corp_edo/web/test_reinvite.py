import pytest


@pytest.mark.pgsql('corp_edo', files=('invitations.sql',))
@pytest.mark.parametrize(
    ['body', 'expected_status', 'status_code'],
    [
        pytest.param(
            {
                'client_id': 'client_4',
                'operator': 'sbis',
                'organization': 'taxi',
            },
            'WAITING_TO_BE_SEND',
            200,
            id='Everything ok',
        ),
        pytest.param(
            {
                'client_id': 'client_999',
                'operator': 'sbis',
                'organization': 'market',
            },
            None,
            404,
            id='Invitation does not exist',
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
async def test_reinvite(
        taxi_corp_edo_web,
        mock_uzedo,
        pgsql,
        body,
        expected_status,
        status_code,
):
    response = await taxi_corp_edo_web.post(
        '/v1/invitations/reinvite', json=body,
    )

    assert response.status == status_code
    if status_code != 200:
        return

    client: str = body['client_id']
    cursor = pgsql['corp_edo'].cursor()
    cursor.execute(
        f' SELECT status'
        f' FROM corp_edo.invitations'
        f' WHERE client_id = \'{client}\';',
    )
    record = cursor.fetchone()
    assert record[0] == expected_status

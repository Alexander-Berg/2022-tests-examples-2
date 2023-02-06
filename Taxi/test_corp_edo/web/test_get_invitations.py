import pytest


@pytest.mark.pgsql('corp_edo', files=('invitations.sql',))
@pytest.mark.parametrize(
    ['client_id', 'expected'],
    [
        pytest.param(
            'client_1',
            [
                {
                    'id': 'fde0ae83c8324133b90f905ab4c6882d',
                    'client_id': 'client_1',
                    'organization': 'taxi',
                    'operator': 'diadoc',
                    'status': 'WAITING_TO_BE_SEND',
                    'created_by_corp_edo': True,
                    'edo_accepted': False,
                    'inn': '1558904566',
                    'kpp': '773901223',
                    'created_at': '2022-02-02T18:40:14.404023+03:00',
                    'updated_at': '2022-02-02T18:40:14.404023+03:00',
                    'synced_at': '2022-02-02T18:40:14.404023+03:00',
                },
            ],
            id='taxi-not-accepted-by-status',
        ),
        pytest.param(
            'client_3',
            [
                {
                    'client_id': 'client_3',
                    'created_at': '2022-02-02T18:40:14.404023+03:00',
                    'created_by_corp_edo': False,
                    'edo_accepted': False,
                    'id': '66977e9bd06342d6b499a3d083408e0d',
                    'inn': '1225672864',
                    'kpp': '776988931',
                    'operator': 'sbis',
                    'organization': 'taxi',
                    'status': 'FRIENDS',
                    'synced_at': '2022-02-02T18:40:14.404023+03:00',
                    'updated_at': '2022-02-02T18:40:14.404023+03:00',
                },
            ],
            id='taxi-not-accepted-by-sender',
        ),
        pytest.param(
            'client_5',
            [
                {
                    'id': '1a11330b335f424ebcc975eece5900bf',
                    'client_id': 'client_5',
                    'organization': 'taxi',
                    'operator': 'diadoc',
                    'status': 'FRIENDS',
                    'created_by_corp_edo': True,
                    'edo_accepted': True,
                    'inn': '1158904561',
                    'kpp': '713901221',
                    'created_at': '2022-02-02T18:40:14.404023+03:00',
                    'synced_at': '2022-02-02T18:40:14.404023+03:00',
                    'updated_at': '2022-02-02T18:40:14.404023+03:00',
                },
            ],
            id='taxi-accepted',
        ),
        pytest.param(
            'client_6',
            [
                {
                    'id': '57e49f167a274f7fa88eabfe1a264ff9',
                    'client_id': 'client_6',
                    'organization': 'market',
                    'operator': 'diadoc',
                    'status': 'FRIENDS',
                    'created_by_corp_edo': False,
                    'edo_accepted': True,
                    'inn': '1158904562',
                    'kpp': '713901222',
                    'created_at': '2022-02-02T18:40:14.404023+03:00',
                    'synced_at': '2022-02-02T18:40:14.404023+03:00',
                    'updated_at': '2022-02-02T18:40:14.404023+03:00',
                },
            ],
            id='market-accepted',
        ),
    ],
)
@pytest.mark.config(CORP_EDO_INVITATION_ACCEPTED_STATUSES=['FRIENDS'])
async def test_get_invitations(web_app_client, client_id, expected):
    result = await web_app_client.get(
        '/v1/invitations', params={'client_id': client_id},
    )

    assert result.status == 200

    body = await result.json()
    assert body['invitations'] == expected

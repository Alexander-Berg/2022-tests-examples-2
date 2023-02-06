import pytest

from corp_clients.stq import corp_sync_edo_invite


@pytest.mark.parametrize(
    ['invite_id', 'organization', 'status', 'firm_id'],
    [
        pytest.param(
            'external_id_1', 'taxi', 'FRIENDS', 13, id='existed_invite',
        ),
        pytest.param(
            'new_id', 'market', 'WAITING_TO_BE_SEND', 111, id='new_invite',
        ),
    ],
)
async def test_sync_edo_invite(
        db, stq3_context, stq, invite_id, organization, status, firm_id,
):
    await corp_sync_edo_invite.task(
        stq3_context,
        invite_id=invite_id,
        client_id='client_1',
        organization=organization,
        operator='diadoc',
        status=status,
    )

    edo_invites = await db.corp_client_edo_invites.find(
        {'invite_external_id': invite_id},
        projection={'_id': False, 'updated': False, 'created': False},
    ).to_list(None)

    assert len(edo_invites) == 1
    assert edo_invites[0] == {
        'invite_external_id': invite_id,
        'client_id': 'client_1',
        'status': status,
        'firm_id': firm_id,
        'operator': 'diadoc',
    }

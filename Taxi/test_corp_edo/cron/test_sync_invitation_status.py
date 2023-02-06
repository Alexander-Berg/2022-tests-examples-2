# pylint: disable=redefined-outer-name
import pytest

from corp_edo.generated.cron import run_cron


@pytest.mark.config(
    CORP_EDO_OPERATOR_MAPPING={'diadoc': '2BM', 'sbis': '2BE'},
    CORP_EDO_ORGANIZATION_MAPPING={
        'market': 'yandex_test',
        'taxi': 'yandex_test',
    },
    CORP_EDO_INVITATION_STATUS_SYNC_SETTINGS={'chunk_size': 1000},
)
@pytest.mark.config(TVM_RULES=[{'src': 'corp-edo', 'dst': 'uzedo'}])
@pytest.mark.pgsql('corp_edo', files=('invitations.sql',))
@pytest.mark.parametrize(
    ['expected_statuses'],
    [
        pytest.param(
            {
                'client_1': 'WAITING_TO_BE_SEND',
                'client_2': 'INVITED_BY_ME',
                'client_3': 'FRIENDS',
            },
        ),
    ],
)
async def test_sync_invitations(mock_uzedo, stq, pgsql, expected_statuses):
    await run_cron.main(
        ['corp_edo.crontasks.sync_invitation_status', '-t', '0'],
    )
    cursor = pgsql['corp_edo'].cursor()
    cursor.execute(
        f'SELECT client_id, status'
        f' FROM corp_edo.invitations'
        f' WHERE client_id = ANY(ARRAY{list(expected_statuses.keys())});',
    )
    records = cursor.fetchall()
    assert dict(records) == expected_statuses

    assert stq.corp_sync_edo_invite.times_called == 2
    stq_calls = sorted(
        [stq.corp_sync_edo_invite.next_call()['kwargs'] for _ in range(2)],
        key=lambda kwargs: kwargs['client_id'],
    )
    assert stq_calls == [
        {
            'client_id': 'client_2',
            'invite_id': '2e05c314788d49aa88e5e79f98de6ceb',
            'operator': 'sbis',
            'organization': 'taxi',
            'status': 'INVITED_BY_ME',
        },
        {
            'client_id': 'client_3',
            'invite_id': '66977e9bd06342d6b499a3d083408e0d',
            'operator': 'sbis',
            'organization': 'taxi',
            'status': 'FRIENDS',
        },
    ]

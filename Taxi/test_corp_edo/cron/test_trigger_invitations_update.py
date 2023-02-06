import pytest

from corp_edo.generated.cron import run_cron


@pytest.mark.config(
    CORP_EDO_ORGANIZATION_MAPPING={'market': 'yandex', 'taxi': 'taxi'},
    CORP_EDO_TRIGGER_UPDATE_CHUNK_SIZE=2,
)
@pytest.mark.pgsql('corp_edo', files=('invited_by_me_invitations.sql',))
async def test_trigger_invites(mock_uzedo, stq, pgsql):
    await run_cron.main(
        ['corp_edo.crontasks.trigger_invitations_update', '-t', '0'],
    )

    assert mock_uzedo.mock_update_status_yandex.times_called == 1
    assert mock_uzedo.mock_update_status_yandex.next_call()[
        'request'
    ].json == {'inviteIds': ['f689828f-3396-4d62-9aef-01661f098902']}

    assert mock_uzedo.mock_update_status_taxi.times_called == 2
    triggered_invites = set()
    for _ in range(mock_uzedo.mock_update_status_taxi.times_called):
        call = mock_uzedo.mock_update_status_taxi.next_call()['request'].json
        triggered_invites.update(set(call['inviteIds']))
    assert triggered_invites == {
        '009374a9-cc37-4331-911e-918924189b47',
        '5e31d437-1c82-4884-bde5-7587d6441361',
        '9323b4eb-ea63-4ffe-b987-7c36ef2d4d8f',
        'f28023bd-3c41-42da-85c6-1c8a8346c0b5',
    }


@pytest.mark.config(
    CORP_EDO_ORGANIZATION_MAPPING={
        'market': 'yandex_test',
        'taxi': 'yandex_test',
    },
    CORP_EDO_TRIGGER_UPDATE_CHUNK_SIZE=2,
)
@pytest.mark.pgsql('corp_edo', files=('invited_by_me_invitations.sql',))
async def test_trigger_invites_test_org(mock_uzedo, stq, pgsql):
    await run_cron.main(
        ['corp_edo.crontasks.trigger_invitations_update', '-t', '0'],
    )

    assert mock_uzedo.mock_update_status_yandex_test.times_called == 3
    triggered_invites = set()
    for _ in range(mock_uzedo.mock_update_status_yandex_test.times_called):
        call = mock_uzedo.mock_update_status_yandex_test.next_call()[
            'request'
        ].json
        triggered_invites.update(set(call['inviteIds']))
    assert triggered_invites == {
        '009374a9-cc37-4331-911e-918924189b47',
        '5e31d437-1c82-4884-bde5-7587d6441361',
        '9323b4eb-ea63-4ffe-b987-7c36ef2d4d8f',
        'f689828f-3396-4d62-9aef-01661f098902',
        'f28023bd-3c41-42da-85c6-1c8a8346c0b5',
    }

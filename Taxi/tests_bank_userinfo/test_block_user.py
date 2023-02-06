import pytest

from tests_bank_userinfo import utils

BUID = '7948e3a9-623c-4524-a390-9e4264d27a77'


async def test_no_buid(taxi_bank_userinfo, mockserver, pgsql):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/block_user',
        json={'buid': '7948e3a9-623c-4524-a390-9e4264d27a76'},
    )

    assert response.status_code == 404


@pytest.mark.config(BANK_USERINFO_BLOCKABLE_BUID_STATUSES=['FINAL'])
async def test_block_buid_blocked(
        taxi_bank_userinfo, mockserver, pgsql, stq, stq_runner,
):
    sessions_before_block = utils.select_buid_sessions(pgsql, BUID)
    buids_history_before_block = utils.select_buid_history(pgsql, BUID)
    assert len(sessions_before_block) == 3
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/block_user', json={'buid': BUID},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'BLOCKED', 'buid_status': 'BLOCKED'}
    assert utils.select_buid_status(pgsql, BUID) == 'BLOCKED'

    buids_history = utils.select_buid_history(pgsql, BUID)
    assert buids_history[0]['status'] == 'BLOCKED'
    assert buids_history[1:] == buids_history_before_block

    while stq.bank_userinfo_delete_sessions.has_calls:
        stq_call = stq.bank_userinfo_delete_sessions.next_call()
        if stq_call['kwargs'] is not None:  # missing if task rescheduled
            stq_kwargs = stq_call['kwargs']
            stq_kwargs.pop('log_extra')
            assert stq_kwargs == {'filter': {'buid': BUID}}
        await stq_runner.bank_userinfo_delete_sessions.call(
            task_id=stq_call['id'], kwargs=stq_kwargs,
        )

    assert utils.select_buid_sessions(pgsql, BUID) == []
    deleted_sessions = utils.select_buid_sessions(pgsql, BUID, deleted=True)
    assert deleted_sessions == sessions_before_block


@pytest.mark.config(BANK_USERINFO_BLOCKABLE_BUID_STATUSES=['NOT_FINAL'])
async def test_block_buid_not_blocked(taxi_bank_userinfo, mockserver, pgsql):
    sessions_before_block = utils.select_buid_sessions(pgsql, BUID)
    assert len(sessions_before_block) == 3
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/block_user', json={'buid': BUID},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'NOT_BLOCKED', 'buid_status': 'FINAL'}
    assert utils.select_buid_status(pgsql, BUID) == 'FINAL'
    assert utils.select_buid_sessions(pgsql, BUID) == sessions_before_block


@pytest.mark.config(BANK_USERINFO_BLOCKABLE_BUID_STATUSES=['NOT_FINAL'])
async def test_block_buid_already_blocked(
        taxi_bank_userinfo, mockserver, pgsql,
):
    utils.update_buid_status(pgsql, BUID, 'BLOCKED')
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/block_user', json={'buid': BUID},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'BLOCKED', 'buid_status': 'BLOCKED'}

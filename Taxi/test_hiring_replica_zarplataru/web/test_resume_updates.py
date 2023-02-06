import dataclasses

import pytest

# pylint: disable=import-only-modules,line-too-long
from hiring_replica_zarplataru.api.updated_resumes_cursor import (
    _fetch_updated_resumes,
)  # noqa: E501
from hiring_replica_zarplataru.api.updated_resumes_cursor import _unpack_cursor
from hiring_replica_zarplataru.internal import task_context


async def test_fetch_updated_with_gaps_in_cursor(web_context):
    @dataclasses.dataclass
    class MockGap:
        history_id: int
        timestamp: int

    ctx = task_context.Web(web_context, 'updated_resumes_cursor', {})
    cursor = _unpack_cursor(ctx, '')

    mock_gaps = [MockGap(11, 1562761279), MockGap(12, 1562761280)]

    cursor.gaps = {g.history_id: g for g in mock_gaps}
    await _fetch_updated_resumes(ctx, cursor)


async def test_empty_db_does_not_break_cursor(
        _step_first_fetch, get_resume_updates,
):
    step = await _step_first_fetch()
    next_chunk = await get_resume_updates(step.chunk['cursor'])
    assert next_chunk['cursor'] == step.chunk['cursor']


async def test_empty_db_returns_nothing(_step_first_fetch):
    step = await _step_first_fetch()
    assert not step.chunk['resumes']


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=False)
async def test_follow_cursor(_step_first_fetch, get_resume_updates):
    step = await _step_first_fetch('suitable_and_unsuitable.json')
    next_chunk = await get_resume_updates()
    has_data_first_time = bool(step.chunk['resumes'])
    than_nothing_left = bool(next_chunk['resumes'])
    assert has_data_first_time and than_nothing_left


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=False)
async def test_fetch_only_suitable(_step_first_fetch):
    step = await _step_first_fetch('suitable_and_unsuitable.json')
    assert len(step.chunk['resumes']) == 1  # only id=123 is suitable


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=False)
async def test_extracted_fields(_step_first_fetch, load_json):
    step = await _step_first_fetch('suitable_and_unsuitable.json')
    obj = {f['field']: f['value'] for f in step.chunk['resumes'][0]['fields']}
    filename = 'suitable_and_unsuitable_response_without_cursor.json'
    expected = {
        f['field']: f['value']
        for f in load_json(filename)['resumes'][0]['fields']
    }
    assert obj == expected


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=True)
async def test_follow_cursor_wf(_step_first_fetch, get_resume_updates):
    step = await _step_first_fetch('wide_funnel.json')
    next_chunk = await get_resume_updates()
    has_data_first_time = bool(step.chunk['resumes'])
    than_nothing_left = bool(next_chunk['resumes'])
    assert has_data_first_time and than_nothing_left


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=True)
async def test_fetch_only_suitable_wf(_step_first_fetch):
    step = await _step_first_fetch('wide_funnel.json')
    assert len(step.chunk['resumes']) == 1  # only id=123 is suitable


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
@pytest.mark.config(ZARPLATARU_WIDE_FUNNEL=True)
async def test_extracted_fields_wf(_step_first_fetch, load_json):
    step = await _step_first_fetch('wide_funnel.json')
    obj = {f['field']: f['value'] for f in step.chunk['resumes'][0]['fields']}
    filename = 'wide_funnel_without_cursor.json'
    expected = {
        f['field']: f['value']
        for f in load_json(filename)['resumes'][0]['fields']
    }
    assert obj == expected


@pytest.mark.config(ZARPLATARU_FETCH_RESUMES_ENABLED=True)
@pytest.mark.config(ZARPLATARU_BUY_CONTACTS_ENABLED=True)
async def test_invalid_phone_skipped(_step_first_fetch):
    # resume has 2 phones, one is invalid (empty)
    step = await _step_first_fetch('resume_with_invalid_phone.json')

    # resumes was processed
    assert len(step.chunk['resumes']) == 1

    # correct phone has been extracted
    obj = {f['field']: f['value'] for f in step.chunk['resumes'][0]['fields']}
    assert obj['phone'] == '+79790454883'


@pytest.fixture
def _step_first_fetch(step_buy_contacts, get_resume_updates):
    async def _wrapper(resumes_filename=None):
        prev_step_ = None
        if resumes_filename is not None:
            prev_step_ = await step_buy_contacts(resumes_filename)

        chunk_ = await get_resume_updates()

        class Step:
            prev_step = prev_step_
            chunk = chunk_

        return Step()

    return _wrapper

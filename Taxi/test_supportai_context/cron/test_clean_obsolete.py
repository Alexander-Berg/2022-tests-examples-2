# pylint: disable=redefined-outer-name
import pytest

from supportai_context.crontasks import clean_obsolete
from supportai_context.generated.cron import run_cron


@pytest.mark.now('2021-02-02T00:00:00')
@pytest.mark.pgsql('supportai_context', files=['sample.sql'])
@pytest.mark.config(
    SUPPORTAI_CONTEXT_PROJECT_SETTINGS={
        'default_history_store_time_in_days': 30,
        'chunk_size': 1,
        'delay_between_chunks_ms': 100,
        'projects': [
            {'project_id': 'configured', 'history_store_time_in_days': 15},
        ],
    },
)
async def test_clean_obsolete(web_app_client, monkeypatch):
    for project_id in ('demo', 'configured'):
        assert (
            await web_app_client.get(
                f'/v1/context?chat_id=new_chat&project_id={project_id}',
            )
        ).status == 200
        assert (
            await web_app_client.get(
                f'/v1/context?chat_id=old_chat&project_id={project_id}',
            )
        ).status == 200

    call_count = 0
    # pylint: disable=protected-access
    _delete_chunk = clean_obsolete._delete_context_meta_chunk

    async def delete_chunk(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return await _delete_chunk(*args, **kwargs)

    monkeypatch.setattr(
        clean_obsolete, '_delete_context_meta_chunk', delete_chunk,
    )

    await run_cron.main(
        ['supportai_context.crontasks.clean_obsolete', '-t', '0'],
    )

    assert call_count == 4

    for project_id in ('demo', 'configured'):
        assert (
            await web_app_client.get(
                f'/v1/context?chat_id=new_chat&project_id={project_id}',
            )
        ).status == 200
        assert (
            await web_app_client.get(
                f'/v1/context?chat_id=old_chat&project_id={project_id}',
            )
        ).status == 204

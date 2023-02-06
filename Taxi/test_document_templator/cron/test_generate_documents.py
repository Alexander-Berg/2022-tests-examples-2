# pylint: disable=redefined-outer-name
import datetime

import pytest
import pytz

from document_templator.generated.api import web_context
from document_templator.generated.cron import run_cron

NOW = '2020-01-01T01:00:00'


@pytest.mark.now(NOW)
@pytest.mark.config(
    DOCUMENT_TEMPLATOR_CRON_GENERATE_DOCUMENTS={'enabled': True, 'count': 2},
)
@pytest.mark.parametrize(
    'persistent_id, version, is_outdated_at, expected_data',
    (
        pytest.param(
            '000009999988888777774444',
            1,
            False,
            {
                'generated_text': 'content',
                'generated_at': None,
                'is_valid': True,
                'name': 'outdated_at',
                'persistent_id': '000009999988888777774444',
            },
            id='updated_only_outdated_at',
        ),
        pytest.param(
            '000009999988888777772222',
            2,
            False,
            {
                'generated_text': 'content',
                'generated_at': datetime.datetime.fromisoformat(NOW).replace(
                    tzinfo=pytz.utc,
                ),
                'is_valid': True,
                'name': 'outdated_at and not actual content',
                'persistent_id': '000009999988888777772222',
            },
            id='updated_full_document',
        ),
        pytest.param(
            '000009999988888777773333',
            1,
            False,
            {
                'generated_text': 'content',
                'generated_at': None,
                'is_valid': True,
                'name': 'actual',
                'persistent_id': '000009999988888777773333',
            },
            id='not_updated',
        ),
        pytest.param(
            '000009999988888777771111',
            1,
            True,
            {
                'generated_text': 'content',
                'generated_at': None,
                'is_valid': True,
                'name': 'last outdated_at',
                'persistent_id': '000009999988888777771111',
            },
            id='not_updated_because_2_in_config',
        ),
    ),
)
async def test_generate_documents(
        persistent_id, version, is_outdated_at, expected_data,
):
    await run_cron.main(
        ['document_templator.crontasks.generate_documents', '-t', '0'],
    )
    context = web_context.Context()
    await context.on_startup()

    query = """
    SELECT generated_text, is_valid, name, persistent_id, generated_at
    FROM document_templator.dynamic_documents
    WHERE
        persistent_id = $1
        AND version = $2
        AND NOT removed
        AND (outdated_at IS NOT NULL) = $3::BOOLEAN;
    """
    data = await context.pg.master.fetchrow(
        query, persistent_id, version, is_outdated_at,
    )
    assert dict(data) == expected_data


@pytest.mark.config(
    DOCUMENT_TEMPLATOR_CRON_GENERATE_DOCUMENTS={'enabled': False},
)
async def test_generate_documents_with_disabled_cron_task():
    await run_cron.main(
        ['document_templator.crontasks.generate_documents', '-t', '0'],
    )
    result = [
        (
            '000009999988888777772222',
            1,
            {
                'generated_text': 'not actual content',
                'is_valid': True,
                'name': 'outdated_at and not actual content',
                'persistent_id': '000009999988888777772222',
            },
        ),
    ]
    context = web_context.Context()
    await context.on_startup()
    query = """
    SELECT generated_text, is_valid, name, persistent_id
    FROM document_templator.dynamic_documents
    WHERE
        persistent_id = $1
        AND version = $2
        AND NOT removed
    """
    for persistent_id, version, expected_data in result:
        data = await context.pg.master.fetchrow(query, persistent_id, version)
        assert dict(data) == expected_data

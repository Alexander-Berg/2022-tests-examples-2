import asyncio

from supportai_reference_phrases import models as db_models
from supportai_reference_phrases.core import heartbeat
from supportai_reference_phrases.core import load
from supportai_reference_phrases.utils import constants


async def test_max_workers(web_context):
    _workers = await web_context.redis_.find_keys(
        heartbeat.WORKER_NAME.format(identifier='*'),
    )
    workers = len(_workers)

    assert workers == 1


async def test_load_matrix(web_context):
    async with web_context.pg.master_pool.acquire() as conn:

        version = await db_models.MatrixVersion.insert(
            web_context,
            conn,
            db_models.MatrixVersion(
                id=0,
                iteration=0,
                type=constants.DRAFT_NAME,
                project_slug='test',
            ),
        )

        _ = await db_models.MatrixRow.insert_bulk(
            web_context,
            conn,
            [
                db_models.MatrixRow(
                    id=0,
                    text=row[0],
                    topic=row[1],
                    vector=row[2],
                    type='addition',
                )
                for row in [('text', 'topic', [0.1, 0.1])]
            ],
            version_id=version.id,
        )

        await load.this(web_context, version)
        await asyncio.sleep(0.5)

        matrix = web_context.supportai_reference_phrases_cache.get(
            'test', constants.DRAFT_NAME,
        )

        assert matrix is not None

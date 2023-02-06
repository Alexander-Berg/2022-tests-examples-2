# pylint: disable=redefined-outer-name

import pytest

from supportai_reference_phrases import models as db_models
from supportai_reference_phrases.core import load
import supportai_reference_phrases.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from supportai_reference_phrases.utils import constants

pytest_plugins = [
    'supportai_reference_phrases.generated.service.pytest_plugins',
]


def pytest_configure(config):
    config.addinivalue_line('markers', 'supportai_reference_phrases_cache')


@pytest.fixture(autouse=True)
def _store(redis_store):
    return redis_store


@pytest.fixture(name='supportai_reference_phrases_cache', autouse=True)
async def _supportai_reference_phrases_cache(request, web_context):
    mark = request.node.get_closest_marker(
        name='supportai_reference_phrases_cache',
    )

    if mark is None:
        return

    version_to_load = []
    async with web_context.pg.master_pool.acquire() as conn:
        for key in ('release', 'draft'):
            type_ = mark.kwargs.get(key)

            if type_ is None:
                continue

            for project_slug, value in type_.items():
                version = await db_models.MatrixVersion.insert(
                    web_context,
                    conn,
                    db_models.MatrixVersion(
                        id=0, iteration=0, type=key, project_slug=project_slug,
                    ),
                )

                await db_models.MatrixRow.insert_bulk(
                    web_context,
                    conn,
                    [
                        db_models.MatrixRow(
                            id=0,
                            text='',
                            vector=phrase['vector'],
                            type='addition',
                            topic=phrase['topic'],
                        )
                        for phrase in value
                    ],
                    version_id=version.id,
                )

                version_2 = await db_models.MatrixVersion.get_latest_version(
                    web_context,
                    conn,
                    version.project_slug,
                    type_=version.type,
                )

                assert version_2.id == version.id
                assert version_2.iteration == version.iteration
                version_to_load.append(version)

            draft_versions = await db_models.MatrixVersion.get_latest_versions(
                web_context, conn,
            )
            release_versions = (
                await db_models.MatrixVersion.get_latest_versions(
                    web_context, conn, type_=constants.RELEASE_NAME,
                )
            )
            release_versions_id = {
                rv.id: rv.iteration for rv in release_versions
            }
            draft_versions_id = {dv.id: dv.iteration for dv in draft_versions}
            for version in version_to_load:
                if version.type == constants.RELEASE_NAME:
                    assert version.id in release_versions_id
                    assert release_versions_id[version.id] == version.iteration
                else:
                    assert version.id in draft_versions_id
                    assert draft_versions_id[version.id] == version.iteration

            await load.this(web_context, version)

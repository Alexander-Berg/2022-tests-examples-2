import pathlib

from clowny_alert_manager.internal.models import common
from clowny_alert_manager.internal.models import template


async def test_insert(web_context):
    templates = template.BareTemplates(
        t_1=template.BareTemplate(
            name='t_1',
            namespace='default',
            repo_meta=common.RepoMeta(
                file_path=pathlib.Path('t_1'),
                file_name='t_1',
                config_project='taxi',
            ),
        ),
        t_2=template.BareTemplate(
            name='t_2',
            namespace='default',
            repo_meta=common.RepoMeta(
                file_path=pathlib.Path('t_2'),
                file_name='t_2',
                config_project='taxi',
            ),
        ),
    )
    await template.TemplatesRepository.batch_upsert(
        context=web_context, db_conn=web_context.pg.primary, models=templates,
    )
    assert (
        len(
            await template.TemplatesRepository.fetch_many(
                context=web_context, db_conn=web_context.pg.primary,
            ),
        )
        == 2
    )

from clowny_alert_manager.internal.models import branch
from clowny_alert_manager.internal.models import common


async def test_insert(web_context):
    branches = branch.BareBranches(
        branch_1=branch.LinkedBareBranch(
            service_id=1,
            names=['branch_1'],
            clown_branch_ids=[],
            repo_meta=common.RepoMeta(
                file_name='branch_1.yaml',
                file_path=branch.pathlib.Path('branch_1.yaml'),
                config_project='taxi',
            ),
            namespace='default',
            basename='branch_1',
            juggler_host='branch_1',
        ),
        branch_2=branch.LinkedBareBranch(
            service_id=1,
            names=['branch_2'],
            clown_branch_ids=[],
            repo_meta=common.RepoMeta(
                file_name='branch_2.yaml',
                file_path=branch.pathlib.Path('branch_2.yaml'),
                config_project='taxi',
            ),
            namespace='default',
            basename='branch_2',
            juggler_host='branch_2',
        ),
    )
    await branch.BranchesRepository.batch_upsert(
        context=web_context, db_conn=web_context.pg.primary, models=branches,
    )
    assert (
        len(
            await branch.BranchesRepository.fetch_many(
                context=web_context, db_conn=web_context.pg.primary,
            ),
        )
        == 2
    )

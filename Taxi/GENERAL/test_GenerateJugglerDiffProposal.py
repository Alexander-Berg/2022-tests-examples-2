import asyncio

from clownductor.generated.cron import cron_context
from clownductor.internal.tasks.cubes import cubes_github
from clownductor.internal.tasks.cubes import cubes_run_recipes
from clownductor.internal.utils import types as ts


def _new(context: ts.WebContext, cube_cls):
    return cube_cls(
        context,
        {
            'status': 'in_progress',
            'retries': 0,
            'id': -1,
            'job_id': -1,
            'payload': None,
            'sleep_until': 0,
        },
        {},
        [],
        None,
    )


async def process(context: ts.WebContext):
    cube = _new(context, cubes_github.GenerateJugglerDiffProposal)
    await cube.update_from_handler(
        {
            'project_name': 'taxi-devops',
            'service_name': 'geotracks-admin',
            'env': 'stable',
            'branch_name': 'stable',
        },
    )

    diff_proposal = cube.payload['diff_proposal']
    print(diff_proposal)

    cube = _new(context, cubes_run_recipes.MetaStartDiffProposalWithPR)
    await cube.update_from_handler(
        {
            'st_ticket': None,
            'diff_proposal': diff_proposal,
            'automerge': True,
            'with_pr': False,
        },
    )

    print(cube.payload['job_id'])


async def main():
    context = cron_context.create_context()
    await context.on_startup()
    try:
        await process(context)
    finally:
        await context.on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())

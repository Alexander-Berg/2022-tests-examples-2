import argparse
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--service_id', type=int, default=199,
    )  # geotracks-admin service_id
    parser.add_argument(
        '--project_id', type=int, default=150,
    )  # geotracks-admin project_id
    parser.add_argument('--st_task', type=str, default=None)
    parser.add_argument('--strongbox_env', type=str, default='unstable')
    return parser.parse_args()


async def process(context: ts.WebContext, args):

    cube = _new(context, cubes_github.GenerateSecdistDiffProposal)
    await cube.update_from_handler(
        {
            'service_id': args.service_id,
            'project_id': args.project_id,
            'strongbox_env': args.strongbox_env,
            'skip_db': False,
        },
    )

    diff_proposal = cube.payload['diff_proposal']
    print(diff_proposal)

    cube = _new(context, cubes_run_recipes.MetaStartDiffProposalWithPR)
    await cube.update_from_handler(
        {
            'st_ticket': args.st_task,
            'diff_proposal': diff_proposal,
            'automerge': True,
            'with_pr': False,
        },
    )
    print(cube.payload['job_id'])


async def main():
    args = parse_args()
    context = cron_context.create_context()
    await context.on_startup()
    try:
        await process(context, args)
    finally:
        await context.on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())

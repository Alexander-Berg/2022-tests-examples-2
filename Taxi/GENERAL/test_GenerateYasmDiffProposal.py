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
    parser.add_argument('--service_name', type=str, default='geotracks-admin')
    parser.add_argument('--db_type', type=str, default='postgres')
    parser.add_argument('--new_service_ticket', type=str, default=None)
    return parser.parse_args()


async def process(context: ts.WebContext, args):

    cube = _new(context, cubes_github.GenerateYasmDiffProposal)
    await cube.update_from_handler(
        {
            'project_name': 'taxi-devops',
            'service_name': args.service_name,
            'env': 'stable',
            'cluster_id': 'test-cluster-id',
            'db_name': 'test-db',
            'db_type': args.db_type,
        },
    )

    diff_proposal = cube.payload['diff_proposal']
    print(diff_proposal)

    cube = _new(context, cubes_run_recipes.MetaStartDiffProposalWithPR)
    await cube.update_from_handler(
        {
            'st_ticket': args.new_service_ticket,
            'diff_proposal': diff_proposal,
            'automerge': True,
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

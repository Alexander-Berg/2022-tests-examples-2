import asyncio
import argparse

from clownductor.generated.cron import cron_context
from clownductor.internal.utils import types as ts
from clownductor.internal.tasks.cubes.meta import params as params_meta_cubes


BASE_URL = (
    'https://tariff-editor.taxi.yandex-team.ru'
    '/task-processor/providers/1/jobs/edit/{job_id}?provider_id=1'
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--service-id', type=int, required=True)
    parser.add_argument('--branch-id', type=int, required=True)
    parser.add_argument('--env', required=True)
    return parser.parse_args()


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


async def process(context: ts.WebContext, args):
    cube = _new(
        context, params_meta_cubes.MetaCubeStartChangeServiceInfoSystem,
    )
    await cube.update_from_handler(
        {
            'service_id': args.service_id,
            'branch_id': args.branch_id,
            'environment': args.env,
            'subsystems_info': {
                'service_info': {
                    'duty_group_id': {
                        'old': 'taxidutyrtcsupport',
                        'new': None,
                    },
                    'duty': {
                        'old': None,
                        'new': {
                            'abc_slug': 'taxidutyclownyplatform',
                            'primary_schedule': 'taxidutyrtcsupport',
                        },
                    },
                },
            },
            'need_updates': True,
        },
    )
    job_id = cube.payload['job_id']
    print('new job_id', job_id)
    print('see', BASE_URL.format(job_id=job_id))


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

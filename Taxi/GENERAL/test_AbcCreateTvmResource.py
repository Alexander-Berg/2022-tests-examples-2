import asyncio
import argparse
import os

from clownductor.generated.cron import cron_context
from clownductor.internal.utils import task_processor
from clownductor.internal.utils import types
from clownductor.internal.utils import postgres

ABC_CREATE_TVM_RESOURCE_RECIPE_NAME = 'AbcCreateTvmResource'


async def _process(
        context: cron_context.Context,
        args: argparse.Namespace,
        conn: types.Connection,
):
    smanager = context.service_manager
    service = await smanager.services.get_by_id(args.service_id, conn=conn)
    assert service, f'no service found for id {args.service_id}'
    project = await smanager.projects.get_by_id(
        service['project_id'], conn=conn,
    )
    assert project, f'no project found for id {service["project_id"]}'

    change_doc_id = task_processor.gen_change_doc_id(
        ABC_CREATE_TVM_RESOURCE_RECIPE_NAME,
        project.name,
        service['name'],
        args.env,
    )
    idempotency_token = task_processor.gen_idempotency_token(
        change_doc_id, os.environ.get('_SCRIPT_INFO_ID'),
    )

    job = await task_processor.create_job(
        context=context,
        initiator=os.environ.get('_SCRIPT_INFO_AUTHOR'),
        provider='clownductor',
        job_name=ABC_CREATE_TVM_RESOURCE_RECIPE_NAME,
        variables={
            'service_id': args.service_id,
            'project_name': project.name,
            'service_name': service['name'],
            'env': args.env,
            'abc_slug': (args.abc_slug or service['abc_service']),
            'tvm_name': args.tvm_name,
            'override_tvm_id': args.override_tvm_id,
            'override_tvm_resource_slug': args.override_tvm_resource_slug,
            'override_tvm_resource_name': args.override_tvm_resource_name,
            'new_secret_owners': (
                [args.tvm_extra_robot] if args.tvm_extra_robot else None
            ),
            'skip_db_record': args.skip_db_record,
            'tvm_extra_robot': args.tvm_extra_robot,
        },
        service_id=args.service_id,
        db_conn=conn,
        change_doc_id=change_doc_id,
        idempotency_token=idempotency_token,
    )
    print(job.job_id, job.request.remote_job_id)


def parse_args():
    def add_int(opt_name: str, required: bool = True):
        parser.add_argument(f'--{opt_name}', required=required, type=int)

    def add_str(opt_name: str, required: bool = True):
        parser.add_argument(f'--{opt_name}', required=required, type=str)

    parser = argparse.ArgumentParser()

    for name in ['tvm_name', 'env']:
        add_str(name)

    for name in [
            'abc_slug',
            'override_tvm_resource_slug',
            'override_tvm_resource_name',
            'tvm_extra_robot',
    ]:
        add_str(name, required=False)

    add_int('service_id')
    add_int('override_tvm_id', required=False)

    parser.add_argument('--skip_db_record', action='store_true', default=False)

    return parser.parse_args()


async def main():
    args = parse_args()
    context = cron_context.create_context()
    await context.on_startup()
    try:
        async with postgres.primary_connect(context) as conn:
            await _process(context, args, conn)
    finally:
        await context.on_shutdown()


if __name__ == '__main__':
    asyncio.run(main())

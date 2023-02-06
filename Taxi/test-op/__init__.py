# from typing import Sequence

import vh3
# from typing import List
# from .logic import do_the_job
# import sys
from vh3.decorator.operation_base import job_run_base
from vh3.graph.resource import ArcadiaFileResource


@vh3.decorator.operation(job_run_base, owner='art')
# @vh3.decorator.job_layer('8ad93656-0bf3-41da-9eda-60967905dd61')
@vh3.decorator.resources(
    ArcadiaFileResource(file_path='taxi/dmp/nirvana/ops/test-op/logic.py')
)
@vh3.decorator.job_command_from_function_body
@vh3.decorator.autorelease_to_nirvana_on_trunk_commit(
    version='https://nirvana.yandex-team.ru/alias/operation/dmp-test-op/0.0.6',  # Link to operation alias. It will work after operation will be packed.
    script_method='dmp_test_op',  # Path to operation. Because of "module" in conf.yaml - we can use relative path here.
    nirvana_quota='TAXIANALYTICS',  # Nirvana quota to run packing workflow with
    # The following arguments are not required, but may be useful for advanced configuration:
    ya_make_folder_path=None,  # By default tasklet searches for ya.make in directory with operation source. One can set path to another binary.
    ya_make_build_artifact_path=None,  # Parameter to point the artifact path. If None, tasklets parses ya.make in ya_make_folder_path. ya_make_folder_path is supposed to be a prefix of ya_make_build_artifact_path.
    # Sandbox build parameters that are used to build the artifact
    sandbox_token=None,  # must be provided if sandbox_group is not None!
    sandbox_group=None,
    sandbox_time_to_kill=None,
    sandbox_disk_limit=None,
    sandbox_memory_limit=None,
    build_type=None,
    clear_build=None,
    use_api_fuse=None,
    definition_flags=None
)
def dmp_test_op(
    some_value: vh3.String,
) -> vh3.Text[str]:
    """
    [DMP] Тестовая операция.

    Может быть на несколько строк.

    :param some_value: Некоторое тестовое значение.
      [[Текст из квадратных скобок. Tooltip]]
      Продолжение описания some_value.
    """

    import json
    with open('job_context.json') as f:
        context = json.load(f)
        parameters = context['parameters']

    from logic import do_the_job
    do_the_job(**parameters)


# В чате VH3 Hosts сказали, что это официальный "хак":
# https://t.me/c/1592960757/8548
dmp_test_op.prebuilt_signature.tags.names = frozenset(
    {
        'yt',
        'tables',
        'write_data',
        'taxi',
        'dmp'
    }
)

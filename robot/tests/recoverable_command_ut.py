from yatest.common import binary_path, execute as execute_binary, work_path
import yt.wrapper as yt

from os import environ as os_environ, remove as os_remove
from os.path import join as pj
from subprocess import PIPE
from sys import stderr
from time import sleep


META_PATH = '//tmp/TestMeta'
INPUT_TABLE = '//tmp/TestInput'
OUTPUT_TABLE = '//tmp/TestOutput'

latest_operation_id = None


def setup_module():
    yt.mkdir('//tmp', recursive=True)
    yt.write_table(INPUT_TABLE, [{'SomeField': 'Record 1'}])


def setup_function(function):
    yt.mkdir(META_PATH, recursive=True)


def teardown_function(function):
    yt.remove(META_PATH, force=True)
    if latest_operation_id:
        yt.abort_operation(latest_operation_id)


def read_operation_id_from_stdout(app):
    global latest_operation_id

    op_id = app.process.stdout.readline().strip().upper()

    assert op_id  # probably app has failed
    latest_operation_id = op_id
    return op_id


def run_binary(custom_args=[], get_op_2=False):
    cmd = [binary_path('robot/library/yt/tests/recoverable_command_ut/recoverable_command_ut')] + custom_args
    app = execute_binary(cmd, wait=False, stdout=PIPE, stderr=stderr, env=os_environ)

    try:
        op_1_id = read_operation_id_from_stdout(app)
        op_2_id = read_operation_id_from_stdout(app) if get_op_2 else None
        return [op_1_id, op_2_id]
    finally:
        app.terminate()


def run_dependency_test_scenario(custom_args, invalidate_dependency):
    first_version = run_binary(custom_args)
    assert first_version == run_binary(custom_args)

    invalidate_dependency()
    while not yt.get_operation_state(latest_operation_id).is_finished():
        sleep(1)

    second_version = run_binary(custom_args)
    assert first_version != second_version

    assert second_version == run_binary(custom_args)
    return second_version


def test_yt_table_dependency():
    def change_input_table_revision():
        yt.write_table(INPUT_TABLE, [{'SomeField': 'Record 2'}])

    run_dependency_test_scenario([], change_input_table_revision)


def test_yt_file_dependency():
    temp_yt_file = '//tmp/temp_yt_file'

    def change_yt_file_revision():
        yt.write_file(temp_yt_file, 'v2')

    try:
        yt.write_file(temp_yt_file, 'v1', force_create=True)
        run_dependency_test_scenario(['--yt-file', temp_yt_file], change_yt_file_revision)
    finally:
        yt.remove(temp_yt_file, force=True)


def test_local_file_dependency():
    local_file_name_1 = pj(work_path(), 'temp_local_file_name_1')
    local_file_name_2 = pj(work_path(), 'temp_local_file_name_2')

    with open(local_file_name_1, 'w') as file_1:
        file_1.write('content v1')

    with open(local_file_name_2, 'w') as file_2:
        file_2.write('content v2')

    def change_local_file_content():
        with open(local_file_name_1, 'w') as local_file:
            local_file.write('content v2')

    try:
        args_file_name_1 = ['--local-file', local_file_name_1]
        ids_file_name_1 = run_dependency_test_scenario(args_file_name_1, change_local_file_content)

        args_different_file_name_but_same_content = ['--local-file', local_file_name_2]
        assert ids_file_name_1 == run_binary(args_different_file_name_but_same_content)
    finally:
        os_remove(local_file_name_1)
        os_remove(local_file_name_2)


def test_cmd_config_dependency():
    custom_args = ['--operation-weight', '1.1']

    def change_operation_weight():
        custom_args[1] = '1.2'

    run_dependency_test_scenario(custom_args, change_operation_weight)


def test_mapper_state_dependency():
    custom_args = ['--mapper-state', 'abc']

    def change_mapper_state():
        custom_args[1] = 'abcd'

    run_dependency_test_scenario(custom_args, change_mapper_state)


def test_rerun_aborts_dependency():
    def abort_operation():
        yt.abort_operation(latest_operation_id)

    run_dependency_test_scenario([], abort_operation)


def test_recoverable_cmd_wait_for_completion():
    op_1_id, _ = run_binary()

    op_ids = run_binary(get_op_2=True)
    assert op_1_id == op_ids[0]
    assert op_ids == run_binary(get_op_2=True)


def test_multiple_cmd_independence():
    old_op_ids = run_binary(get_op_2=True)
    assert old_op_ids == run_binary(get_op_2=True)

    yt.abort_operation(old_op_ids[1])

    new_op_ids = run_binary(get_op_2=True)

    assert old_op_ids[0] == new_op_ids[0]
    assert old_op_ids[1] != new_op_ids[1]

    assert new_op_ids == run_binary(get_op_2=True)


def test_sort_is_not_invalidated():
    op_ids = run_binary(get_op_2=True)
    while yt.get_operation_state(op_ids[1]).is_running():
        sleep(3)

    assert op_ids == run_binary(get_op_2=True)

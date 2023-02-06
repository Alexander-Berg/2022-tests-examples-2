from favicon import yt

from robot.favicon.test.common import launch_local_favicon

from robot.library.python.common_test import run_safe
from robot.library.yuppie.modules.environment import Environment

import yatest.common

from os.path import join as pj
import logging
import os


def upload_table(filename, destination_table):
    with open(filename) as stream:
        yt.write_table(
            destination_table,
            stream,
            raw=True,
            format='yson',
            is_stream_compressed=True
        )


def run_command(cmd, name, cmd_env={}):
    stdout_file = yatest.common.output_path('{}.out'.format(name))
    stderr_file = yatest.common.output_path('{}.err'.format(name))
    logging.info('runnig %s: %s', name, cmd)
    with open(stdout_file, 'w') as stdout, open(stderr_file, 'w') as stderr:
        yatest.common.execute(cmd, stdout=stdout, stderr=stderr, env=cmd_env)
    return stdout_file, stderr_file


def make_and_validate_trie(local_favicon, attrs_table, smushable_tables, file_prefix=''):
    # cast instances of class Table from ytcpp to strings
    attrs_table = str(attrs_table)
    smushable_tables = list(map(str, smushable_tables))

    cmd_env = {'YT_PROXY': local_favicon.get_yt_proxy()}

    # when all targets finished we should create trie locally instead of sandbox, using make_wad_index bin
    # (make_trie targets and deploy targets are skipped in the test)
    # SandboxResourceName is not used in test-integration, take all Release sizes simultaneously

    attrs_trie_file = local_favicon.get_favicon_attrs_trie(prefix=file_prefix)
    icon_base_file = local_favicon.get_favicon_db(prefix=file_prefix)
    test_dir = os.getcwd()

    make_attrs_trie_command = ([local_favicon.get_make_wad_index_bin(), 'MakeIndex'] +
                               ['--server-name', local_favicon.get_yt_proxy()] +
                               ['--model', pj(test_dir, 'favicon_model')] +
                               ['--wad', attrs_trie_file] +
                               ['--attrs-table', attrs_table])
    run_command(make_attrs_trie_command, 'make_attrs_trie', cmd_env=cmd_env)

    make_icon_base_command = ([local_favicon.get_make_icon_base_bin()] +
                              ['--out', icon_base_file] +
                              smushable_tables)
    run_command(make_icon_base_command, 'make_icon_base', cmd_env=cmd_env)

    # check tries via favicond
    favicond_command = [local_favicon.get_favicon_runtime_bin(), '--check',
                        '--attrs', attrs_trie_file,
                        '--icons-base', icon_base_file]
    run_command(favicond_command, 'favicond', cmd_env=cmd_env)

    # read keys in format host@size from created trie file and diff the result
    trie_reader_command = [local_favicon.get_trie_reader_bin(), '--trie-file', attrs_trie_file]
    trie_reader_stdout, _ = run_command(trie_reader_command, 'trie_reader', cmd_env=cmd_env)

    return yatest.common.canonical_file(trie_reader_stdout)


def run_local_favicon_integration_pipeline(pipeline_function, yt_fixture, yql_fixture, working_subdir):
    env = Environment()
    test_dir = os.getcwd()
    local_favicon = launch_local_favicon(
        env,
        bin_dir=env.binary_path,
        favicon_dir=yatest.common.build_path('robot/favicon/packages/cm_binaries'),
        host_mirror='//home/favicon-robot/mirrors',
        prefix='//home/favicon-robot',
        tables_data=pj(test_dir, 'tables_data.tar'),
        yp_yt=yt_fixture,
        yql_port=yql_fixture.port,
        working_subdir=working_subdir
    )
    return run_safe(env.hang_test, pipeline_function, local_favicon)

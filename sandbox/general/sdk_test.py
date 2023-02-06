from sandbox.projects.common.arcadia import sdk_tested_parts as stp

import pytest

import os
import subprocess
import shlex
import tempfile
import shutil
import six

import yatest.common


def test_parse_flags():
    parse_flags = stp.parse_flags

    foo = parse_flags('-DFOO')
    foo_res = {'FOO': 'yes'}
    assert foo == foo_res

    foo_no = parse_flags('-DFOO=no')
    foo_no_res = {'FOO': 'no'}
    assert foo_no == foo_no_res

    with_hyphen = parse_flags('-Dflag-with-hyphen')
    with_hyphen_res = {'flag-with-hyphen': 'yes'}
    assert with_hyphen == with_hyphen_res

    with_hyphen_1337 = parse_flags('-Dflag-with-hyphen=1337')
    with_hyphen_1337_res = {'flag-with-hyphen': '1337'}
    assert with_hyphen_1337 == with_hyphen_1337_res

    bar_foo = parse_flags('-DBAR=-DFOO')
    bar_foo_res = {'BAR': '-DFOO'}
    assert bar_foo == bar_foo_res

    bar_val = parse_flags(' -DBAR=value ')
    bar_val_res = {'BAR': 'value'}
    assert bar_val == bar_val_res

    with pytest.raises(stp.InvalidFlag):
        bad_flags = '-f1'
        parse_flags(bad_flags)

    with pytest.raises(stp.InvalidFlag):
        bad_flags2 = 'word_must_be_captured'
        parse_flags(bad_flags2)

    quoted_flags = parse_flags('-DCFLAGS="-f1 -f2"')
    quoted_flags_res = {'CFLAGS': '-f1 -f2'}
    assert quoted_flags == quoted_flags_res

    two_flags = parse_flags("-DDISABLE_KIWI_JOBS -DTEAMCITY_RUN")
    two_flags_res = {'DISABLE_KIWI_JOBS': 'yes', 'TEAMCITY_RUN': 'yes'}
    assert two_flags == two_flags_res

    complex_flags = parse_flags('  -DCFLAGS="-f1 -f2 bar=foo"  -DFOO -DBAR=no ')
    complex_flags_res = {'CFLAGS': '-f1 -f2 bar=foo', 'FOO': 'yes', 'BAR': 'no'}
    assert complex_flags == complex_flags_res


@pytest.mark.parametrize('flags_str,expected', (
    ('DFOO', {'DFOO': 'yes'}),
    ('DFOO=no', {'DFOO': 'no'}),
    ('BAR=-DFOO', {'BAR': '-DFOO'}),
    (' BAR=value ', {'BAR': 'value'}),
    ('-f1', {'f1': 'yes'}),
    ('word_must_be_captured', {'word_must_be_captured': 'yes'}),
    ('CFLAGS="-f1 -f2"', {'CFLAGS': '-f1 -f2'}),
    ('DISABLE_KIWI_JOBS TEAMCITY_RUN', {'DISABLE_KIWI_JOBS': 'yes', 'TEAMCITY_RUN': 'yes'}),
    ('  CFLAGS="-f1 -f2 bar=foo"  FOO BAR=no ', {'CFLAGS': '-f1 -f2 bar=foo', 'FOO': 'yes', 'BAR': 'no'}),

))
def test_parse_simple_flags(flags_str, expected):
    assert stp.parse_flags(flags_str, d_flags_only=False) == expected


@pytest.mark.parametrize('report_config, def_flags, expected', [
    ({}, {'A': 'yes'}, {'A': 'yes'}),
    ({'autocheck_build_vars': ''}, '-DA=yes', {'A': 'yes'}),
    ({'autocheck_build_vars': []}, '-DA=yes', {'A': 'yes'}),
    ({'autocheck_build_vars': 'A=yes'}, {}, {'A': 'yes'}),
    ({'autocheck_build_vars': ['A=yes']}, '-DA=yes', {'A': 'yes'}),
    ({'autocheck_build_vars': 'A=yes'}, '-DB=no', {'A': 'yes', 'B': 'no'}),
    ({'autocheck_build_vars': 'A=yes;B=yes'}, '-DA=yes -DB=no', {'A': 'yes', 'B': 'no'}),
    ({'autocheck_build_vars': 'A=yes;B=yes;C=no'}, {'C': 'yes', 'D': 'yes'}, {'A': 'yes', 'B': 'yes', 'C': 'yes', 'D': 'yes'}),
    ({'autocheck_build_vars': ['A=yes', 'B=yes', 'C=no']}, {'C': 'yes', 'D': 'yes'}, {'A': 'yes', 'B': 'yes', 'C': 'yes', 'D': 'yes'}),
])
def test_merge_def_flags(report_config, def_flags, expected):
    assert stp.merge_def_flags(report_config, 'autocheck_build_vars', def_flags) == expected


@pytest.mark.parametrize('report_config, def_flags, expected', [
    ({}, {'A': 'yes'}, {'A': 'yes'}),
    ({'host_platform_flags': ''}, '-DA=yes', {'A': 'yes'}),
    ({'host_platform_flags': 'A=yes'}, '-DB=no', {'A': 'yes', 'B': 'no'}),
    ({'autocheck_build_vars': 'A=yes'}, '-DB=no', {'B': 'no'}),
])
def test_merge_host_def_flags(report_config, def_flags, expected):
    assert stp.merge_def_flags(report_config, 'host_platform_flags', def_flags) == expected


def test_get_size():
    get_size = stp.get_size
    assert 0 == get_size('')
    assert 0 == get_size('some_string')

    current_file_path = yatest.common.test_source_path("../sdk_test.py")
    current_dir_path = yatest.common.test_source_path()
    file_size = get_size(current_file_path)
    dir_size = get_size(current_dir_path)
    assert 0 != file_size
    assert 0 != dir_size
    assert isinstance(file_size, int)
    assert isinstance(dir_size, int)


def test_parse_test_params():
    parse_test_params = stp.parse_test_params

    simple = parse_test_params('key1=value1')
    simple_res = {'key1': 'value1'}
    assert simple == simple_res

    with_whitespaces = parse_test_params(' key2=value2  ')
    with_whitespaces_res = {'key2': 'value2'}
    assert with_whitespaces == with_whitespaces_res

    several_key_values = parse_test_params(' key1=value1  key2=value2 key3=value3')
    several_key_values_res = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
    assert several_key_values == several_key_values_res

    quoted_params = parse_test_params('key="-f1 -f2"')
    quoted_params_res = {'key': '-f1 -f2'}
    assert quoted_params == quoted_params_res


def test_validate_target_platform_flags():
    validate_platform_flags = stp.validate_platform_flags

    validate_platform_flags(None)
    validate_platform_flags('--target-platform=xxx-xxx-xxx')
    validate_platform_flags('--target-platform xxx-xxx-xxx')
    validate_platform_flags('--target-platform-flag foo=bar')
    validate_platform_flags('--target-platform=xxx-xxx-xxx --target-platform-flag foo=bar --target-platform-flag key=val')

    validate_platform_flags('--host-platform=xxx-xxx-xxx')
    validate_platform_flags('--host-platform xxx-xxx-xxx')
    validate_platform_flags('--host-platform xxx-xxx-xxx --target-platform=yyy-yyy-yyy --target-platform-flag foo=bar --target-platform-flag key=val')
    validate_platform_flags('--target-platform=clang39 --target-platform-flag=CFLAGS="-O0 -fsanitize=address -fsanitize-address-use-after-scope"')

    with pytest.raises(stp.InvalidTargetFlag):
        validate_platform_flags('--target-platform-flagS foo=bar')
    with pytest.raises(stp.InvalidTargetFlag):
        validate_platform_flags('--target-platform-definitions foo=bar')


def run_process(cmd, shell=False):
    """
    This method needs to emulate sandboxsdk.process.run_process method for test case
    """
    cmd_string = None
    if isinstance(cmd, basestring):
        if shell:
            cmd_string = cmd
        cmd = shlex.split(cmd)
    if cmd_string is None:
        cmd_string = ' '.join(six.moves.map(str, cmd))
    if shell:
        cmd = cmd_string
    proc = subprocess.Popen(cmd, shell=shell)
    proc.saved_cmd = cmd_string
    return proc


def are_processes_terminated(processes):
    for proc in processes:
        if proc.poll() is None:
            return False
    return True


def test_terminate_all():
    processes = [
        run_process(['sleep', '600']),
        run_process(['sleep', '600']),
    ]

    assert not are_processes_terminated(processes)
    stp.terminate_all(processes)
    assert are_processes_terminated(processes)


def test_wait_any_zero_exit_code():
    p1 = run_process(['sleep', '600'])
    p2 = run_process(['sleep', '3'])
    processes = [p1, p2]

    finished = stp.wait_any(processes, 10)
    assert are_processes_terminated(processes)
    assert finished == p2
    assert finished.returncode == 0


def test_wait_any_zero_exit_code_without_terminating():
    p1 = run_process(['sleep', '600'])
    p2 = run_process(['sleep', '3'])
    processes = [p1, p2]

    finished = stp.wait_any(processes, 10, need_terminate_all=False)
    assert not are_processes_terminated(processes)
    assert finished == p2
    assert finished.returncode == 0
    stp.terminate_all(processes)
    assert are_processes_terminated(processes)


def test_wait_any_timeout_case_1():
    p1 = run_process(['sleep', '600'])
    p2 = run_process('sleep 1 && exit 1', shell=True)
    processes = [p1, p2]

    finished = stp.wait_any(processes, 5)
    assert are_processes_terminated(processes)
    assert finished == p2
    assert finished.returncode == 1


def test_wait_any_timeout_case_2():
    processes = [
        run_process(['sleep', '600']),
        run_process(['sleep', '600']),
    ]

    with pytest.raises(stp.SubprocessTimeoutError):
        stp.wait_any(processes, 3)
    assert are_processes_terminated(processes)


def test_wait_any_all_failed():
    processes = [
        run_process('sleep 1 && exit 1', shell=True),
        run_process('sleep 1 && exit 1', shell=True),
    ]

    finished = stp.wait_any(processes, 10)
    assert are_processes_terminated(processes)
    assert finished.returncode == 1


def test_mkdirp():
    def make_and_check(path):
        stp.mkdirp(path)
        assert os.path.exists(path)
        assert os.path.isdir(path)

    root = tempfile.mkdtemp()
    make_and_check(root + '/tmp1')
    make_and_check(root + '/tmp1')

    make_and_check(root + '/tmp2/tmp1')
    make_and_check(root + '/tmp2')

    make_and_check(root + '/tmp3/tmp2/tmp1/t/t/t')
    make_and_check(root + '/tmp3/tmp2')
    make_and_check(root + '/tmp3')

    shutil.rmtree(root)


def test_make_unique_dir():
    root = tempfile.mkdtemp()

    tmp = os.path.join(root, 'tmp')

    stp.make_unique_dir(tmp)
    assert os.path.exists(tmp)
    assert os.path.isdir(tmp)

    stp.make_unique_dir(tmp)
    assert os.path.exists(tmp + '_1')
    assert os.path.isdir(tmp + '_1')

    stp.make_unique_dir(tmp)
    assert os.path.exists(tmp + '_2')
    assert os.path.isdir(tmp + '_2')

    shutil.rmtree(root)

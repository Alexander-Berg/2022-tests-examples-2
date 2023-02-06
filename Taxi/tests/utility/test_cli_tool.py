import os
import re
import subprocess as sb
import tempfile
from os.path import join


BASE = 'tests/utility/assets/cli/'
F = (BASE + '{}').format
C = (f'pahtest {BASE}' + '{}').format


def read_buffer(buff):
    line = buff.readline().decode()
    result = line
    while line:
        print('# ' + line.strip('\n'))
        line = buff.readline().decode()
        result += line
    return result


def test_full_case_success():
    """The most full case with several browsers, subtests and so on."""
    with tempfile.TemporaryDirectory() as dir:
        # - check output in a whole
        proc = sb.Popen(
            C('full.yml'), shell=True, stdout=sb.PIPE, stderr=sb.PIPE,
            env={**os.environ.copy(), 'SCREENS_DIR': dir}
        )

        # read stdout with realtime printing
        print('\n# --- Tap output ---')
        result = read_buffer(proc.stdout).strip()
        with open(F('full.out')) as file:
            expected = file.read().strip()
        assert expected == result

        # - two folders with screens for two browser
        screen_dirs = list(sorted(os.listdir(dir)))
        assert 2 == len(screen_dirs), screen_dirs
        assert screen_dirs[0].endswith('_full_chrome_800x600'), screen_dirs[0]
        assert screen_dirs[1].endswith('_full_firefox_800x600'), screen_dirs[1]

        # - every screen folder contains files
        chr, ff = [os.listdir(join(dir, d)) for d in screen_dirs]
        assert 6 == len(chr), list(sorted(chr))
        assert 6 == len(ff), list(sorted(ff))

        proc.communicate()
        assert 0 == proc.returncode


def test_full_case_with_fail():
    """The most full case with several browsers, subtests and so on."""
    with tempfile.TemporaryDirectory() as dir:
        # - check output in a whole
        proc = sb.Popen(
            C('full_failed.yml'), shell=True, stdout=sb.PIPE, stderr=sb.PIPE,
            env={**os.environ.copy(), 'SCREENS_DIR': dir}
        )

        # read stdout with realtime printing
        print('\n# --- Tap output ---')
        result = read_buffer(proc.stdout).strip()
        with open(F('full_failed.out')) as file:
            expected = file.read().strip()
        _assert_with_wait(expected, result)

        # - two folders with screens for two browser
        screen_dirs = list(sorted(os.listdir(dir)))
        assert 2 == len(screen_dirs), screen_dirs
        assert screen_dirs[0].endswith('_chrome_800x600'), screen_dirs[0]
        assert screen_dirs[1].endswith('_firefox_800x600'), screen_dirs[1]

        # - every screen folder contains one file for one failed test
        chr, ff = [os.listdir(join(dir, d)) for d in screen_dirs]
        assert 1 == len(chr), chr
        assert 1 == len(ff), ff

        proc.communicate()
        assert 1 == proc.returncode


def test_wrong_hub_url():
    for case in ['wrong_hub_url_single', 'wrong_hub_url_twice']:
        with tempfile.TemporaryDirectory() as dir:
            # - check output in a whole
            proc = sb.Popen(
                C(f'{case}.yml'), shell=True, stdout=sb.PIPE, stderr=sb.PIPE,
                env={**os.environ.copy(), 'SCREENS_DIR': dir}
            )

            # read stdout with realtime printing
            print('\n# --- Tap output ---')
            result = read_buffer(proc.stdout).strip()
            with open(F(f'{case}.out')) as file:
                expected = file.read().strip()
            assert expected == result, result

            proc.communicate()
            assert 1 == proc.returncode


def test_several_arguments_success():
    base = 'tests/utility/assets/several/'
    with tempfile.TemporaryDirectory() as dir:
        # - check output in a whole
        proc = sb.Popen(
            f'pahtest {base}first.yaml {base}second/',
            shell=True, stdout=sb.PIPE, stderr=sb.PIPE,
            env={**os.environ.copy(), 'SCREENS_DIR': dir}
        )

        # read stdout with realtime printing
        print('\n# --- Tap output ---')
        result = read_buffer(proc.stdout).strip()
        with open(f'{base}answer.out') as file:
            expected = file.read().strip()
        assert expected == result, result

        proc.communicate()
        assert 0 == proc.returncode


def test_several_arguments_failure():
    base = 'tests/utility/assets/several_fail/'
    with tempfile.TemporaryDirectory() as dir:
        # - check output in a whole
        proc = sb.Popen(
            f'pahtest {base}first_fail.yaml {base}second/',
            shell=True, stdout=sb.PIPE, stderr=sb.PIPE,
            env={**os.environ.copy(), 'SCREENS_DIR': dir}
        )

        # read stdout with realtime printing
        print('\n# --- Tap output ---')
        result = read_buffer(proc.stdout).strip()
        with open(f'{base}answer.out') as file:
            expected = file.read().strip()
        _assert_with_wait(expected, result), result

        proc.communicate()
        assert 1 == proc.returncode


def test_wait_attempts():
    with tempfile.TemporaryDirectory() as dir:
        # - check output in a whole
        proc = sb.Popen(
            C('wait_attempts.yml'),
            shell=True, stdout=sb.PIPE, stderr=sb.PIPE,
            env={**os.environ.copy(), 'SCREENS_DIR': dir}
        )

        # read stdout with realtime printing
        print('\n# --- Tap output ---')
        result = read_buffer(proc.stdout).strip()
        with open(F('wait_attempts.out')) as file:
            expected = file.read().strip()
        _assert_with_wait(expected, result), result

        proc.communicate()
        assert 1 == proc.returncode


def _assert_with_wait(expected: str, result: str):
    for should, got in zip(expected.split('\n'), result.split('\n')):
        if '# Waiting' in should:
            assert re.match(
                r'([\s]+)?# Waiting failed with [0-9]+ attempts', got
            )
        else:
            assert should == got

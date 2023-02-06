#!/usr/bin/env python3

import argparse
import concurrent.futures
import glob
import os
import subprocess
import typing


class LintResult(typing.NamedTuple):
    linter: str
    target: str
    output: str
    ret_code: int


FLAKE_CMD = [
    'flake8',
    '--import-order-style',
    'appnexus',
    '--application-package-names',
    'codegen, swaggen, taxi',
    '--no-teamcity',
    'true',
]

PYLINT_INIT_HOOK = (
    'import os.path; '
    'import sys; '
    'sys.path.append(os.path.join(\'{project_root}\', '
    '\'submodules/testsuite\'));'
    'sys.path.append(os.path.join(\'{project_root}\', '
    '\'submodules/codegen\'))'
)

PYLINT_CMD = [
    'pylint',
    '--load-plugins',
    'pylint_quotes',
    '--msg-template=\'{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}\'',
]

MYPY_CMD = ['mypy', '--ignore-missing-imports']

LINTER_CMD = {'flake8': FLAKE_CMD, 'pylint': PYLINT_CMD, 'mypy': MYPY_CMD}


def get_subdirs(directory):
    return next(os.walk(directory))[1]


def get_root_dir(rel_path, path_base):
    parts = rel_path.split(os.sep, 1)
    full_path = os.path.join(path_base, rel_path)
    if len(parts) == 1 and not os.path.isdir(full_path):
        return None
    return parts[0]


def get_repo_abs():
    script_dir_abs = os.path.abspath(os.path.dirname(__file__))
    repo_abs = os.path.abspath(os.path.dirname(script_dir_abs))
    return repo_abs


def get_packages(target, repo_abs):
    target_abs = os.path.abspath(target)
    packages = ['conftest']
    rel_path = os.path.relpath(target_abs, start=repo_abs)
    if not rel_path.startswith('..'):
        project = get_root_dir(rel_path, repo_abs)
        if project is None:
            return packages
        if project == 'taxi':
            packages.append('taxi')
        dirs = get_subdirs(os.path.join(repo_abs, project))
        packages.extend(dirs)
        return packages
    return packages


def get_files(path):
    expr = '%s/**/*.py' % path
    if not os.path.exists(path):
        return []
    if not os.path.isdir(path):
        return [path]
    return glob.glob(expr, recursive=True)


def run_linter(name, target):
    command = LINTER_CMD[name][:]

    files = get_files(target)
    if not files:
        return LintResult(name, target, 'No files, skipping...', 0)

    repo_abs = get_repo_abs()

    if name == 'flake8':
        packages = ','.join(get_packages(target, repo_abs))
        command.extend(['--application-import-names', packages])

    if name == 'pylint':
        command.extend(
            ['--init-hook', PYLINT_INIT_HOOK.format(project_root=repo_abs)],
        )

    command.extend(files)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding='utf-8',
    )
    output = ''
    try:
        output, _ = process.communicate()
    except OSError:
        pass
    return LintResult(name, target, output, process.returncode)


def tc_message_format(text):
    return (
        text.replace('|', '||')
        .replace('\'', '|\'')
        .replace('[', '|[')
        .replace(']', '|]')
        .replace('\n', '|n')
    )


def tc_test_format(result: LintResult):
    test_name = tc_message_format('%s.%s' % (result.linter, result.target))
    start_msg = '##teamcity[testStarted name=\'%s\']' % test_name
    formatted_text = tc_message_format(result.output)
    tc_message = 'Check with %s linter failed.' % result.linter
    fail_msg = (
        '##teamcity[testFailed name=\'%s\' '
        'message=\'%s\' details=\'%s\']'
        % (test_name, tc_message, formatted_text)
    )
    finish_msg = '##teamcity[testFinished name=\'%s\']' % test_name
    on_fail = [start_msg, fail_msg, finish_msg]
    on_success = [start_msg, finish_msg]
    out_text = '\n'.join(on_fail if result.ret_code else on_success)
    return out_text


def plain_format(result: LintResult):
    subs = (result.target, result.linter)
    start_msg = 'Checking %s with %s linter started.' % subs
    fail_msg = 'Fail, details:\n%s' % result.output
    finish_msg = 'Checking %s with %s linter is successful.' % subs
    return '\n'.join((start_msg, fail_msg if result.ret_code else finish_msg))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l',
        '--linter',
        help='Required linter type',
        choices=list(LINTER_CMD),
        default=list(LINTER_CMD),
        nargs='*',
    )
    parser.add_argument(
        '-t',
        '--teamcity',
        help='Adapt output to teamcity tests, ' 'default \'false\'',
        action='store_true',
    )
    parser.add_argument(
        '-j', '--jobs', default=4, help='Maximum thread count', type=int,
    )
    parser.add_argument(
        'targets',
        nargs='+',
        help='Targets to check, '
        'can be either directory or file. '
        'Each target spawns separate linter process',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    futures = []
    thread_pool = concurrent.futures.ThreadPoolExecutor(
        max_workers=int(args.jobs),
    )
    for linter in args.linter:
        for target in args.targets:
            futures.append(thread_pool.submit(run_linter, linter, target))

    status = 0
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        status = status or result.ret_code
        output = (
            tc_test_format(result) if args.teamcity else plain_format(result)
        )
        if output:
            print(output)

    exit(status)


if __name__ == '__main__':
    main()

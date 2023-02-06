# -*- coding: utf-8 -*-
import errno
import logging
import os
import psutil
import re
import shlex
import signal
import six
import time


class InvalidTargetFlag(ValueError):
    """
    Definition flag starts only with --target-platform or --target-platform-flag.
    """


class InvalidFlag(ValueError):
    """
    Definition flag starts only with -D.
    You should only use -D flags in sandbox tasks.
    """


class InvalidTestParam(ValueError):
    """
    Test params is pairs with '=' separator.
    For example 'key1=val1 key2=val2'
    """


class SubprocessTimeoutError(OSError):
    """
    The process is not kept within the allotted timeout
    """


def parse_flags(flags, d_flags_only=True):
    res = {}
    flags_re = re.compile(r'(?P<flag_name>{}\w(?:[\w-]*\w)?)(?P<flag_full_value>=(?P<flag_value>"[^"]+"|[^\s]+)"*)?'.format('-*' if d_flags_only else ''))
    for flag in flags_re.findall(flags or ''):
        value = flag[2] or 'yes'
        if len(value) > 1 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        if not flag[0].startswith('-D'):
            if d_flags_only:
                raise InvalidFlag(
                    'Flag "{0}" does not start with -D.\n'
                    'You should only use -D flags in sandbox tasks.\n'
                    'If you have any questions, please, contact devtools@.\n'.format(flag[0])
                )
            else:
                res[flag[0]] = value
        else:
            res[flag[0][2:]] = value
    return res


def merge_def_flags(report_config, report_config_key, def_flags):
    build_vars = report_config.get(report_config_key, [])
    if not isinstance(build_vars, list):
        build_vars = build_vars.split(';')
    build_vars = filter(None, build_vars)
    merged_def_flags = {}
    for build_var in build_vars:
        kv = build_var.split('=')
        if len(kv) == 1:
            merged_def_flags[kv] = 'yes'
        elif len(kv) == 2:
            merged_def_flags[kv[0]] = kv[1]
        else:
            logging.error('Bad value in "%s" field inside report config: %s', report_config_key, build_var)
    normalized_def_flags = parse_flags(def_flags) if isinstance(def_flags, six.string_types) else def_flags
    merged_def_flags.update(normalized_def_flags or {})
    return merged_def_flags


def parse_test_params(test_params):
    res = {}
    params = shlex.split(test_params)
    for param in params:
        if param:
            kv = param.split('=', 1)
            if len(kv) != 2 or not kv[0] or not kv[1]:
                raise InvalidTestParam(
                    'Test parameter "{}" should have format key=value'.format(param)
                )

            res[kv[0]] = kv[1]

    return res


def validate_platform_flags(flags):
    if not flags:
        return
    params = shlex.split(flags)
    skip_next = False
    for param in params:
        if skip_next:
            skip_next = False
            continue
        if param.startswith('--host-platform=') or \
                param.startswith('--target-platform=') or \
                param.startswith('--target-platform-flag=') or \
                param.startswith('--target-platform-test-type=') or \
                param.startswith('--target-platform-build-type='):
            continue
        if param in ('--host-platform', '--target-platform', '--target-platform-flag', '--target-platform-build-type', '--target-platform-test-type'):
            skip_next = True
            continue
        raise InvalidTargetFlag(
            'Target platform flag parameter "{}" should starts with --target-platform or --target-platform-flag'.format(param)
        )


def get_size(path):
    total_size = 0
    if os.path.isfile(path):
        return os.path.getsize(path)
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if not os.path.islink(full_path):
                    total_size += os.path.getsize(full_path)
    return total_size


def terminate_all(processes, timeout=10, kill_subtree=False, term_signal=None):
    terminating = []
    term_signal = term_signal or getattr(signal, 'SIGTERM', None)

    parent_procs = []
    for p in processes:
        if isinstance(p, psutil.Process):
            proc = p
        else:
            try:
                proc = psutil.Process(p.pid)
            except psutil.NoSuchProcess as e:
                logging.info('Process %s not found: %s', p, e)
                continue
        parent_procs.append(proc)

    if not kill_subtree:
        check_processes = parent_procs
    else:
        check_processes = []
        for proc in parent_procs:
            check_processes.append(proc)
            try:
                if hasattr(proc, 'get_children'):
                    check_processes += proc.get_children(recursive=True)
                elif hasattr(proc, 'children'):
                    check_processes += proc.children(recursive=True)
            except psutil.NoSuchProcess:
                continue

    for proc in check_processes:
        try:
            if term_signal:
                proc.send_signal(term_signal)
            else:
                proc.terminate()
            terminating.append(proc)
        except psutil.NoSuchProcess:
            logging.info('Process %s not found', proc)
        except psutil.AccessDenied:
            logging.info('Impossible to kill child process %s', proc)

    logging.info('Waiting for processes %s to finish (timeout=%s)', terminating, timeout)
    if not terminating:
        return

    start_time = time.time()
    _, alive = psutil.wait_procs(terminating, timeout=timeout)
    remaining_time = timeout - (time.time() - start_time)
    # Waiting for multiple processes does not consume all the time
    while alive and remaining_time > 0:
        logging.error('Still alive processes %s', alive)
        _, alive = psutil.wait_procs(alive, timeout=remaining_time)
        remaining_time = timeout - (time.time() - start_time)

    if alive:
        logging.error('Too long termination of processes %s, ignore them', alive)
        return alive


def ensure_terminate_all(processes, timeout=10, kill_subtree=False, term_signal=None, kill_signal=None, kill_timeout=10):
    term_signal = term_signal or getattr(signal, 'SIGTERM', None)
    alive = terminate_all(processes, kill_subtree=kill_subtree, timeout=timeout, term_signal=term_signal)
    if alive and kill_signal:
        alive = terminate_all(alive, kill_subtree=kill_subtree, timeout=kill_timeout, term_signal=kill_signal)
    return alive


def wait_any(processes, timeout, timeout_sleep=None, need_terminate_all=True, kill_subtree=False, terminate_timeout=10, kill_signal=None):
    timeout_sleep = timeout_sleep or 1
    start_time = time.time()
    finished_processes = []
    while len(finished_processes) != len(processes):
        for proc in processes:
            exit_code = proc.poll()
            if exit_code is not None:
                if proc not in finished_processes:
                    finished_processes.append(proc)
                    logging.debug('Process %s finished with exit code %s', proc.saved_cmd, proc.returncode)

                if exit_code == 0:
                    if need_terminate_all:
                        ensure_terminate_all(processes, kill_subtree=kill_subtree, timeout=terminate_timeout, kill_signal=kill_signal)
                    return proc

        time.sleep(timeout_sleep)
        if (time.time() - start_time) > timeout:
            ensure_terminate_all(processes, kill_subtree=kill_subtree, timeout=terminate_timeout, kill_signal=kill_signal)
            if finished_processes:
                return finished_processes[0]
            raise SubprocessTimeoutError('Processes {0} was interrupted by timeout {1}'.format(str(processes), timeout))

    return finished_processes[0]


def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

    return path


def make_unique_dir(path):
    if not os.path.exists(path):
        return mkdirp(path)

    index = 1
    while True:
        npath = '{}_{}'.format(path, index)
        if not os.path.exists(npath):
            return mkdirp(npath)
        index += 1

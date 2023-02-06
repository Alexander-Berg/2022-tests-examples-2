import argparse
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Text, Dict

import sources_root
from tools.service_utils import (
    build_service_pythonpath,
    collect_services,
    Executable,
    ServiceType,
)
import tools.vcs

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _service_sort_key(service):
    service_dir, service_yaml = service
    # dmp_suite tests are prioritized, others are sorted lexicographically for more consistent output
    return service_yaml['name'] != 'dmp_suite', service_yaml['name']


def temporary_directory(prefix):
    result = tempfile.mkdtemp(prefix=prefix)
    atexit.register(shutil.rmtree, result, ignore_errors=True)

    return result


def run_pytest(service_dir: Text,
               service_yaml: Dict,
               ext_pytest_args=None,
               report_dir=None,
               output=None,
    ):

    service_name = service_yaml['name']
    pythonpath = build_service_pythonpath(service_name)

    # специальная переменная для запуска корневых тестов
    testsuite = ''
    if service_dir == sources_root.ROOT_SERVICE:
        cwd = root_dir
        testsuite = 'root'
    else:
        cwd = os.path.join(root_dir, service_dir)

    env = dict(
        os.environ.copy(),
        PWD=cwd,
        PYTHONPATH=pythonpath,
        DMP_SERVICE_NAME=service_name,
        # с буферезацией pytest почему-то виснет на файле
        # test_eda_etl/layer/yt/cdm/food/demand/eda_user_appsession/checks_test.py
        # зависает относительно стабильно - 1 из 3 запусков локально
        PYTHONUNBUFFERED='1',
        DMP_TESTSUITE=testsuite,
    )

    pytest_args = ['pytest']
    slow = any(arg.startswith('slow') for arg in ext_pytest_args)

    # Для сервиса репликации параллелизация пока не поддерживается,
    # с ним надо разбираться отдельно.
    if service_dir != 'replication_rules':
        # Используем pytest-xdist, чтобы ускорить работу тестов
        num_processes = os.environ.get('PYTEST_PROCESSES', '8')
        if num_processes != '1':
            if slow:
                # В slow воркерах не работает xdist - зависает в некоторый момент.
                # починить это так и не удалось. Поэтому параллелим запуск
                # через pytest-parallel
                pytest_args += ['--workers', num_processes]

                # Тесты запускаются параллельно - возникает гонка по локальной
                # сборке whl и jar пакетов с плавающими багами:
                # - whl падает на самой сборке
                # - тесты ругаются на отсутствие файла в jar
                # Поэтому собираем во временной директории whl и jar пакеты
                # один раз и изменяем конфиги через переменную окружения
                # Перенести в conftest.py с ходу не получилось, так как
                # из-за параллельного запуска сессионные фикстуры pytest
                # инициализируются несколько раз.
                tmp_package_directory = temporary_directory(prefix='dmp-test-packages-')

                exitcode = build_packages(
                    tmp_package_directory, service_name, pythonpath, output
                )
                if exitcode:
                    return exitcode

                env['TAXIDWH_ENV_CONFIG'] = json.dumps(
                    {
                        'yt': {'project_package_path': tmp_package_directory},
                        'spark': {'local_jar_path': tmp_package_directory}
                    }
                )
            else:
                # В быстрых тестах pytest-parallel не работает, потому что
                # там отключен socket. А xdist как-то работает, поэтому используем его.
                pytest_args += ['-n', num_processes]

    tox_env = os.environ.get('TOX_ENV_NAME', '')

    if report_dir:
        test_report = (
                service_dir.strip(os.path.sep) +
                ('_' + tox_env if tox_env else '') +
                '.xml')
        # rewrite args on absolute paths
        pytest_args += ['--junitxml',
                        os.path.join(os.path.abspath(report_dir), test_report)]

    if tox_env:
        pytest_args += ['--junit-prefix', tox_env + '_' + service_name]

    if ext_pytest_args:
        if ext_pytest_args[0] == '--':
            ext_pytest_args = ext_pytest_args[1:]
        pytest_args += ext_pytest_args

    # Текущая директория – директория сервиса.
    # Надо указать pytest, что искать тесты надо в текущей директории.
    # В старых версиях pytest этого не требовалось, но в > 5.0 нужно.

    # amleletko: в conftest проставляются тестовые директории для сервисов
    # с '.' теряются тесты в tests/ директории
    # pytest_args += ['.']

    exitcode = subprocess.call(
        pytest_args,
        env=env,
        cwd=cwd,
        stdout=output,
        stderr=output
    )
    # skip test not found
    if exitcode == 5:
        exitcode = 0
    return exitcode


def build_packages(destination_dir,
                   service_name: Text,
                   pythonpath: Text,
                   output):

    tmp_build_directory = temporary_directory(prefix='dmp-test-bdist-')

    executable = Executable(
        service_name,
        pythonpath=pythonpath,
        output=output,
        checked_call=False
    )

    def log(msg):
        if output:
            output.write(msg.encode('utf8'))
        else:
            sys.stderr.write(msg)
    # Чтобы не было гонки во время параллельной сборки. Например, dmp_suite
    # используется в сборке нескольких пакетов.
    jar_build_directory = os.path.join(tmp_build_directory, 'jar')
    exitcode = executable.run_setup_py(
        ['build_spark', '-d', destination_dir],
        env=dict(
            GRADLE_OPTS=f'-Dorg.gradle.project.buildDir={jar_build_directory}'
        )
    )
    if exitcode:
        log('Could not build Spark jar package')
        return exitcode

    whl_build_directory = os.path.join(tmp_build_directory, 'whl')
    exitcode = executable.run_setup_py([
        'bdist_wheel',
        '--dist-dir', destination_dir,
        '--bdist-dir', whl_build_directory
    ])
    if exitcode:
        log('Could not build wheel package')
        return exitcode

    return 0


# hack: rewrite args on absolute paths
def rewrite_path_args(args):
    new_args = []
    for arg in args:
        if arg.startswith('-'):
            new_args.append(arg)
        elif os.path.exists(arg):
            new_args.append(os.path.abspath(arg))
        else:
            new_args.append(arg)
    return new_args


def main(report_dir=None, service_dir=None, service_type=None, pytest_args=None, rev=None):
    assert service_type is not None

    if pytest_args is None:
        pytest_args = []

    service_dir_map = {s['name']: s for s in collect_services(service_type)}

    if service_type == ServiceType.ETL.value:
        service_dir_map[sources_root.ROOT_SERVICE] = service_dir_map.get('dmp_suite')

    if service_dir:
        service_dir_map = {service_dir: service_dir_map[service_dir]}
    elif service_type == ServiceType.ETL.value and rev is not None:
        pytest_args += ['--rev', rev]
        try:
            changed_services = set(tools.vcs.get_changed_services(rev))
        except tools.vcs.VCSError:
            # this could happen in context where there are no `develop`
            # branch or there is no .git dir, e.g. in release build.
            # In this case changes are ignored and whole tests run
            # defaults to run all the tests
            pass
        else:
            changed_services.add(sources_root.ROOT_SERVICE)
            # tests should be run for changed services
            # only if we can reliably calculate changes
            # and service_dir was not set directly
            service_dir_map = {k: v for k, v in service_dir_map.items() if k in changed_services}

    def run_kwargs():
        for service_dir, service_yaml in sorted(service_dir_map.items(), key=_service_sort_key):
            yield dict(
                service_dir=service_dir,
                service_yaml=service_yaml,
                report_dir=report_dir,
                ext_pytest_args=pytest_args,
            )

    num_processes = int(os.environ.get('DMP_PYTEST_SERVICE_PARALLEL', 1))

    if num_processes == 1 or len(service_dir_map) == 1:
        exitcode = 0
        for kwargs in run_kwargs():
            pytest_exitcode = run_pytest(**kwargs)
            exitcode = int(any((exitcode, pytest_exitcode)))
    else:
        exitcode = int(any(run_concurrent(num_processes, run_kwargs())))

    sys.exit(exitcode)


def run_concurrent(workers: int, run_kwargs):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for kwargs in run_kwargs:
            # при параллельном запуске если сразу выводить stdout и stderr
            # в терминал, то вывод от разных сервисов будет перемешан
            # отправлять совсем в devnull все же не стоит
            tmp_output = tempfile.TemporaryFile(prefix='dmp-test-out')
            future = executor.submit(run_pytest, **kwargs, output=tmp_output)
            futures[future] = tmp_output

        for future in as_completed(futures):
            tmp_output = futures[future]
            try:
                tmp_output.seek(0)
                print(tmp_output.read().decode('utf-8', 'ignore'))
            finally:
                tmp_output.close()

            yield future.result()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-dir',
                        help='path for generated xml report. Ci tools (teamcity) '
                             'display tests count/status by this xml files')
    parser.add_argument('--dmp-service', help='name of dmp service')
    parser.add_argument('--dmp-service-type', default=ServiceType.ETL.value,
                        help='type of dmp service')
    parser.add_argument(
        '--rev',
        help='object (commit/branch) to get changes from',
    )
    parser.add_argument('pytest_args', nargs=argparse.REMAINDER,
                        help='custom args for pytest')
    args = parser.parse_args()

    main(
        args.report_dir,
        args.dmp_service,
        args.dmp_service_type,
        rewrite_path_args(args.pytest_args),
        args.rev,
    )

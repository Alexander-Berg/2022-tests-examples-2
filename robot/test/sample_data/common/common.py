import subprocess
import re
import logging
import os
from os.path import join as pj
import time

SVN_ROOT_REGEX = re.compile('Working Copy Root Path: ([^\n]+)')


def _is_arcadia_repo(path):
    result = os.path.exists(pj(path, 'ya')) and os.path.exists(pj(path, 'ya.make'))
    if not result:
        logging.info('Repository ' + path + ' doesn''t seem to be a valid arcadia root')
    return result


def _detect_arcadia_root_svn():
    try:
        result = subprocess.check_output(['svn', 'info'])
        result = SVN_ROOT_REGEX.search(result).group(1)
        if not _is_arcadia_repo(result):
            return ""
        logging.info('Found svn arcadia repository ' + result)
        return result
    except Exception:
        logging.info('Not a svn repository')


def _detect_arcadia_root_hg():
    try:
        result = subprocess.check_output(['ya', 'tool', 'hg', 'root']).strip()
        if not _is_arcadia_repo(result):
            return ""
        logging.info('Detected hg arcadia repository ' + result)
        return result
    except Exception:
        logging.info('Not a hg repository')
        return ""


def detect_arcadia_root():
    result = _detect_arcadia_root_svn()
    if not result:
        result = _detect_arcadia_root_hg()
    logging.info("found arcadia root at:" + result)
    return result


def build(arcadia_root, path, option=None):
    logging.info("building: " + path)
    cmd = [pj(arcadia_root, 'ya'), 'make', pj(arcadia_root, path)]
    if option is not None:
        cmd.append(option)
    subprocess.Popen(cmd).communicate()
    logging.info("done")


def build_rthub_package(arcadia_root, local_rthub_path, config):
    subprocess.Popen([pj(arcadia_root, local_rthub_path, 'local_rthub'),
                      '--cmd', 'build',
                      '--config', config]
                     ).communicate()


def start_ydb(arcadia_root, local_ydb, kikimr_driver, working_dir, kikimr_stable):
    logging.info("deploying local kikimr")
    subprocess.Popen([pj(arcadia_root, local_ydb, "local_ydb"),
                      "deploy",
                      "--ydb-working-dir", working_dir,
                      "--ydb-binary-path", pj(arcadia_root, kikimr_driver, "kikimr"),
                      "--ydb-udfs-dir", pj(arcadia_root, kikimr_stable)]).communicate()


def stop_ydb(arcadia_root, local_ydb, kikimr_driver, working_dir, kikimr_stable):
    logging.info("stopping local kikimr")
    subprocess.Popen([pj(arcadia_root, local_ydb, "local_ydb"),
                      "stop",
                      "--ydb-working-dir", working_dir,
                      "--ydb-binary-path", pj(arcadia_root, kikimr_driver, "kikimr"),
                      "--ydb-udfs-dir", pj(arcadia_root, kikimr_stable)]).communicate()
    time.sleep(5)
    logging.info("cleaning up local kikimr")
    subprocess.Popen([pj(arcadia_root, local_ydb, "local_ydb"),
                      "cleanup",
                      "--ydb-working-dir", working_dir,
                      "--ydb-binary-path", pj(arcadia_root, kikimr_driver, "kikimr"),
                      "--ydb-udfs-dir", pj(arcadia_root, kikimr_stable)]).communicate()


def build_package(arcadia_root, package_path, build_type):
    logging.info("building package")
    subprocess.Popen([pj(arcadia_root, 'ya'),
                      'package',
                      '--tar',
                      '--raw-package', package_path,
                      "--build", build_type]
                     ).communicate()


def download_rthub_data(arcadia_root, local_rthub_path, config, num_msg):
    logging.info("downloading data: " + num_msg)
    subprocess.Popen([pj(arcadia_root, local_rthub_path, 'local_rthub'),
                      '--cmd', 'download_data',
                      '--config', config,
                      '--num-of-urls-from-pq', num_msg]
                     ).communicate()


def run_rthub(arcadia_root, local_rthub_path, config):
    logging.info("running rthub")
    subprocess.Popen([pj(arcadia_root, local_rthub_path, 'local_rthub'),
                      '--cmd', 'run',
                      '--config', config]
                     ).communicate()


def patch_rthub_config(arcadia_root, local_rthub_path, config):
    logging.info("patching rthub config")
    subprocess.Popen([pj(arcadia_root, local_rthub_path, 'local_rthub'),
                      '--cmd', 'patch_config',
                      '--config', config,
                      '--num-of-urls-from-pq', '1']
                     ).communicate()


def find_built_package(package_name):
    logging.debug('Searching for package with name ' + package_name)
    for subdir in os.listdir('.'):
        if subdir.startswith(package_name):
            return subdir
    return None

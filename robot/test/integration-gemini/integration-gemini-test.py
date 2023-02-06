import json
import logging
import os
from os.path import join as pj
import subprocess as sub
from shutil import copyfile

import yatest.common
from yatest.common import network

from robot.jupiter.library.python.jupiter_util.env import is_port_free

from robot.gemini.pyclient.client_wrapper import GeminiClient
from robot.library.yuppie.modules.environment import Environment
from robot.jupiter.library.python.saas import RTYServer
from robot.jupiter.library.python.saas import Searchproxy
import robot.jupiter.test.common as jupiter_integration


TMP_DIR = yatest.common.work_path()

DATA_DIR = './data'

RTY_SERVER_DIR = 'rtyserver'

SEARCHPROXY_DIR = 'searchproxy'
SEARCHPROXY_WORKDIR = pj(SEARCHPROXY_DIR, 'work_dir')
SEARCHPROXY_CONFIG_DIR = pj(SEARCHPROXY_WORKDIR, 'configs')
SEARCHPROXY_SEARCHMAP = pj(SEARCHPROXY_CONFIG_DIR, 'searchmap.json')

SAAS_SHARD_DEPLOY_BUNDLE_DIR = yatest.common.binary_path('robot/jupiter/packages/saas_shard_deploy_bundle')
RUN_SH = pj(SAAS_SHARD_DEPLOY_BUNDLE_DIR, 'run.sh')
SAAS_BUILD_MK = 'saas_build.mk'
TEST_SHARD = '0-30'

RTY_BINARY = yatest.common.binary_path('saas/rtyserver/rtyserver')

SAMPLED_SHARDS = 'sampled_shards'

RTY_CONFIGS_SRC_DIR = 'saas/static_configs/gemini/rtyserver_configs'
RTY_CONFIG = 'rtyserver.conf-common'
RTY_QUERY_LANGUAGE = 'query-language'

SEARCHPROXY_BINARY = yatest.common.binary_path('saas/searchproxy/searchproxy')
SEARCHPROXY_CONFIGS_SRC_DIR = 'saas/static_configs/gemini/searchproxy_configs'
SEARCHPROXY_QUERY_LANGUAGE = 'query-language-searchproxy-default'
SEARCHPROXY_SEARCHPROXY_GEMINI_CONF = 'searchproxy-gemini.conf'
SEARCHPROXY_CONFIG = 'searchproxy.conf'

GEMINI_CONFIG_SRC_DIR = 'robot/gemini/configs'
GEMINI_CFG_FNAME = 'gemini.cfg'
GEMINI_SQUOTA_FNAME = 'squota.gemini.xml'

rtyserver_configs = {
    RTY_CONFIGS_SRC_DIR: [
        RTY_CONFIG,
        RTY_QUERY_LANGUAGE,
    ]
}

searchproxy_configs = {
    SEARCHPROXY_CONFIGS_SRC_DIR: [
        SEARCHPROXY_QUERY_LANGUAGE,
        SEARCHPROXY_SEARCHPROXY_GEMINI_CONF,
        SEARCHPROXY_CONFIG,
    ]
}

gemini_configs = {
    GEMINI_CONFIG_SRC_DIR: [
        GEMINI_CFG_FNAME,
        GEMINI_SQUOTA_FNAME,
    ]
}


def get_sampled_shards_path(lj, state):
    return pj(lj.get_prefix(), 'gemini', state, 'saas_index', SAMPLED_SHARDS)


def copy_configs(configs, dst_dir):
    for src_dir in configs:
        files = configs[src_dir]
        for file in files:
            src = yatest.common.source_path(pj(src_dir, file))
            dst = pj(dst_dir, file)
            copyfile(src, dst)


def run_command(cmd, stdout_fname, stderr_fname):
    out_file = open(stdout_fname, 'w+')
    err_file = open(stderr_fname, 'w+')

    logging.info('Command:\n\t{}'.format(' '.join(cmd)))
    proc = sub.Popen(cmd, stdout=out_file, stderr=err_file)

    proc.communicate()

    if proc.returncode != 0:
        raise Exception('Command {0} failed, see out in {1} and err in {2}'.format(cmd, stdout_fname, stderr_fname))

    return True


def run_gemini_stages_in_jupiter(lj, env):
    logging.info('Running gemini data preparation in jupiter graph')
    # Must be CM var, not just environment var
    # We have to disable it because we don't have shards_prepare's walrus in previous state
    lj.get_cm().set_var('INCREMENTAL_MODE', 'false')
    lj.get_cm().set_var('PudgeEnabled', 'false')

    lj.get_cm().check_call_target(
        'yandex.save_state', timeout=90 * 60, ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())
    lj.get_cm().check_call_target(
        'rt_yandex.run_meta.gemini_saas', timeout=60 * 60, ignore_failed_log_re=jupiter_integration.yandex_meta_graph_re())

    current_state = lj.get_current_state('rt_yandex')
    logging.info('Prepared state = %s', current_state)
    return current_state


def prepare_searchproxy_data(lj, state, data_root):
    searchproxy_data_dir = pj(data_root, SEARCHPROXY_DIR, DATA_DIR)
    logging.info('Preparing data for searchproxy in %s', searchproxy_data_dir)

    if not os.path.exists(searchproxy_data_dir):
        os.makedirs(searchproxy_data_dir)

    run_command(
        [
            'sh', RUN_SH,
            '-m', pj(data_root, SEARCHPROXY_DIR),
            '-f', SAAS_BUILD_MK,
            '-t', 'CastorTier',
            '-g', state,
            '-p', lj.get_prefix(),
            '-h', lj.get_yt().get_proxy(),
            '-o', DATA_DIR
        ],
        stdout_fname=pj(TMP_DIR, 'BuildCastorTier.out'),
        stderr_fname=pj(TMP_DIR, 'BuildCastorTier.err'),
    )


def prepare_base_data(lj, state, data_root):
    shard_id = get_shard_id(data_root)
    logging.info('Preparing index for rtyserver in %s', pj(data_root, RTY_SERVER_DIR, DATA_DIR))
    run_command(
        [
            'sh', RUN_SH,
            '-m', pj(data_root, RTY_SERVER_DIR),
            '-f', SAAS_BUILD_MK,
            '-s', shard_id,
            '-g', state,
            '-p', lj.get_prefix(),
            '-h', lj.get_yt().get_proxy(),
            '-o', DATA_DIR
        ],
        stdout_fname=pj(TMP_DIR, 'BuildIndex.out'),
        stderr_fname=pj(TMP_DIR, 'BuildIndex.err'),
    )


def prepare_request_urls(lj, state, data_root):
    logging.info('Preparing request plan')
    lj.get_yt().download(get_sampled_shards_path(lj, state), data_root, yt_format='json')


def get_shard_id(data_root):
    with open(pj(data_root, SAMPLED_SHARDS)) as infile:
        for s in infile:
            row = json.loads(s)
            if row['prefix'] == 1:
                return row['shard_id']


def check_consecutive_ports(port, num_free):
    '''
    Check if required number of ports starting from the given one are free
    :param port: port number to start from
    :param num_free: number of demanded free consecutive ports
    :return: True if given number consecutive ports are free, False otherwise
    '''
    for cur_port in range(port, port+num_free):
        if not is_port_free(cur_port):
            return False
    return True


def find_port_base():
    port_manager = network.PortManager()
    start_port = 3000
    while start_port < 65535:
        port = port_manager.get_port(start_port)
        if check_consecutive_ports(port, RTYServer.NUM_CONSECUTIVE_PORTS):
            return port

        start_port += RTYServer.NUM_CONSECUTIVE_PORTS


def run_rty_server(data_root):
    logging.info('Running RTYserver')

    work_dir = pj(data_root, RTY_SERVER_DIR, 'work_dir')

    logging.info('  work dir is %s', work_dir)

    config_dir = pj(work_dir, 'configs')

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    copy_configs(rtyserver_configs, config_dir)

    indexdir = pj(data_root, RTY_SERVER_DIR, DATA_DIR)
    logging.info('  index dir is %s', indexdir)

    port = find_port_base()
    logging.info('  selected port base as %s', str(port))

    rtyserver = RTYServer(
        binary=RTY_BINARY,
        service='gemini',
        base_port=port,
        work_dir=work_dir,
        index_dir=indexdir,
        config=pj(config_dir, RTY_CONFIG),
    )

    rtyserver.start()

    return rtyserver


def prepare_searchmap(data_root, rtyserver):
    config_dir = pj(data_root, SEARCHPROXY_CONFIG_DIR)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    searchmap_dst = pj(data_root, SEARCHPROXY_SEARCHMAP)
    logging.info('Preparing searchmap for searchproxy in %s', searchmap_dst)
    fout = open(searchmap_dst, 'w')
    fout.write(rtyserver.prepare_searchmap())
    fout.close()
    return searchmap_dst


def run_searchproxy(data_root):
    logging.info('Running searchproxy')

    prev_current_dir = os.getcwd()
    searchproxy_dir = pj(data_root, SEARCHPROXY_DIR)
    work_dir = pj(data_root, SEARCHPROXY_WORKDIR)
    config_dir = pj(data_root, SEARCHPROXY_CONFIG_DIR)

    logging.info('  work dir is %s', work_dir)

    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    copy_configs(gemini_configs, searchproxy_dir)
    copy_configs(searchproxy_configs, config_dir)

    searchproxy_config = pj(config_dir, SEARCHPROXY_CONFIG)

    port = find_port_base()
    logging.info('  selected port base as %s', str(port))

    os.chdir(searchproxy_dir)
    searchproxy = Searchproxy(
        binary=SEARCHPROXY_BINARY,
        service='gemini',
        base_port=port,
        work_dir=work_dir,
        config=searchproxy_config,
    )

    searchproxy.start()

    os.chdir(prev_current_dir)

    return searchproxy


def run_gemini_client(data_root, searchproxy):
    logging.info('Runnig gemini client')

    shard_id = get_shard_id(data_root)

    urls = []
    with open(pj(data_root, SAMPLED_SHARDS)) as infile:
        for s in infile:
            row = json.loads(s)
            if row['shard_id'] == shard_id and row['prefix'] == 1:
                urls.append(row['Url'])

    client = GeminiClient(type='weak', port=searchproxy.get_request_port(), host='localhost', user='any')
    res = client.run(urls)

    has_error = False
    for response in res:
        if 'Error' in response:
            logging.error('Url %s is %s', response['OriginalUrl'], response['Error'])

    if has_error:
        raise Exception('Gemini client recieved error(s) in response')


def process(lj, env):
    data_root = yatest.common.get_param('data', TMP_DIR)

    state = run_gemini_stages_in_jupiter(lj, env)

    prepare_request_urls(lj, state, data_root)
    prepare_searchproxy_data(lj, state, data_root)
    prepare_base_data(lj, state, data_root)


def test_diff(links):
    env = Environment(diff_test=True)
    cm_env = {
        'DeletionMode': 'aggressive',
        'Feedback.DupGroupLimit': '3',
    }

    # For debugging purposes we can skip jupiter and shard preparation phases.
    # to do this pass parameters
    #    --test-param mode='requests' --test-param data=$HOME/data
    # in the test invoke line
    partial_target = yatest.common.get_param('mode', 'all')  # values: 'all', 'requests', 'data'
    data_root = yatest.common.get_param('data', TMP_DIR)

    run_jupiter = False
    run_requests = False

    if partial_target == 'all':
        run_jupiter = True
        run_requests = True
    elif partial_target == 'requests':
        run_requests = True
    elif partial_target == 'data':
        run_jupiter = True

    if run_jupiter:
        with jupiter_integration.launch_local_jupiter(
            env,
            cm_env=cm_env,
            test_data='integration.tar',
            yatest_links=links,
        ) as local_jupiter:
            jupiter_integration.call_jupiter(env.hang_test, process, local_jupiter, env)

    if run_requests:
        rtyserver = run_rty_server(data_root)

        prepare_searchmap(data_root, rtyserver)

        searchproxy = run_searchproxy(data_root)

        run_gemini_client(data_root, searchproxy)

        searchproxy.stop()
        rtyserver.stop()

import os
import tarfile
import logging

from robot.cmpy.library.run import BinaryRun
from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.utils import read_token_from_file
from robot.cmpy.library.yt_tools import client

from os.path import join as pj


def _get_common_args():
    args = [
        '--pool', 'kwyt-test',
        # '--pool', 'kwyt-cloud',
        # '--pool-trees', 'cloud',
        '--use-yamr-for', '*'
    ]
    return args


# CM Targets


@cm_target
def check_prev_indexed_data(cfg):
    yt_client = client(cfg)
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))
    prod_rthub_sample = yt_client.get(pj(cfg.YtPrefix, cfg.Baseline.YtAttribute, 'sample'))
    if prod_rthub_sample == current_sample_state:
        yt_client.set(pj(cfg.YtPrefix, cfg.Baseline.YtAttribute, 'skip_index'), True)
        cleanup_yt_folder(yt_client, pj(cfg.SampleDstDir, 'baseline'))
        for t in yt_client.list(pj(cfg.SampleDstDir, 'test')):
            yt_client.copy(
                pj(cfg.SampleDstDir, 'test', t),
                pj(cfg.SampleDstDir, 'baseline', t)
            )
    else:
        yt_client.set(pj(cfg.YtPrefix, cfg.Baseline.YtAttribute, 'skip_index'), False)
        yt_client.set(pj(cfg.YtPrefix, cfg.Baseline.YtAttribute, 'sample'), current_sample_state)


def get_skip_flag(cfg):
    yt_client = client(cfg)
    return yt_client.get(pj(cfg.YtPrefix, cfg.Baseline.YtAttribute, 'skip_index'))


@cm_target
def prepare_data(cfg):
    yt_client = client(cfg)
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))
    hosts_data_path = pj(cfg.YtPrefix, 'test_data', current_sample_state, 'hosts')
    pages_data_path = pj(cfg.YtPrefix, 'test_data', current_sample_state, 'pages')

    # Prepare host table
    if not yt_client.exists(pj(hosts_data_path, 'zora--hosts')):
        if yt_client.exists(pj(hosts_data_path, 'robots')) and yt_client.exists(pj(hosts_data_path, 'status')):
            yt_client.run_merge(
                [
                    pj(hosts_data_path, 'robots'),
                    pj(hosts_data_path, 'status')
                ],
                pj(hosts_data_path, 'zora--hosts'),
                mode="sorted"
            )
        else:
            raise Exception("Hosts test data not found!")

    # Prepare pages tables
    for b in range(0, 32):
        bucket = str(b).zfill(3)
        if not yt_client.exists(pj(pages_data_path, bucket, 'zora--pages')):
            if yt_client.exists(pj(pages_data_path, bucket, 'data')):
                yt_client.move(
                    pj(pages_data_path, bucket, 'data'),
                    pj(pages_data_path, bucket, 'zora--pages')
                )
            else:
                raise Exception("Pages test data in bucket {} not found!".format(bucket))

    # Prepare app_docs tables
#    for b in range(0, 32):
#        bucket = str(b).zfill(3)
#        if not yt_client.exists(pj(app_docs_data_path, bucket, 'zora--app-docs')):
#            if yt_client.exists(pj(app_docs_data_path, bucket, 'data')):
#                yt_client.move(
#                    pj(app_docs_data_path, bucket, 'data'),
#                    pj(app_docs_data_path, bucket, 'zora--app-docs')
#                )
#            else:
#                raise Exception("AppDocs test data in bucket {} not found!".format(bucket))


def cleanup_yt_folder(yt_client, folder_path):
    lst = yt_client.list(folder_path, absolute=True)
    if lst:
        for t in lst:
            yt_client.remove(t)


@cm_target
def cleanup_destination_folders(cfg):
    yt_client = client(cfg)
    if not get_skip_flag(cfg):
        cleanup_yt_folder(yt_client, pj(cfg.SampleDstDir, 'baseline'))
    cleanup_yt_folder(yt_client, pj(cfg.SampleDstDir, 'test'))


def pack_data(cfg, target_path, compresslevel=5):
    data_tar_path = pj(target_path, 'data.tar.gz')
    if not os.path.exists(data_tar_path):
        data_tar = tarfile.open(data_tar_path, 'w:gz', compresslevel=compresslevel)
        work_dir = os.getcwd()
        os.chdir(pj(target_path, 'data'))
        for e in os.listdir(os.curdir):
            logging.info("Adding %s to %s", e, data_tar_path)
            data_tar.add(e)
        logging.info("Closing %s", data_tar_path)
        data_tar.close()
        logging.info("Done. %s is closed", data_tar_path)
        os.chdir(work_dir)
    else:
        logging.info("data.tar.gz exists. Skipping...")


@cm_target
def setup_rthub_build(cfg, target):
    subcfg = cfg[target]
    yt_client = client(cfg)
    hosts_target_path = pj(subcfg.HostsRTHubDir, yt_client.get(pj(cfg.YtPrefix, subcfg.YtAttribute, 'hosts_res_file_name')))
    pages_target_path = pj(subcfg.PagesRTHubDir, yt_client.get(pj(cfg.YtPrefix, subcfg.YtAttribute, 'pages_res_file_name')))
    if not get_skip_flag(cfg) or target == 'Test':
        pack_data(cfg, hosts_target_path)
        pack_data(cfg, pages_target_path)
        # pack_data(cfg, cfg[target].AppDocsRTHubDir)


def run_index_rthub(cfg, root_dir, target_prefix, config_file_name):
    if 'YT_TOKEN' not in os.environ:
        os.environ['YT_TOKEN_PATH'] = cfg.YtTokenPath
    if cfg.YdbTokenPath:
        os.environ['YDB_TOKEN'] = read_token_from_file(cfg.YdbTokenPath)
    return BinaryRun(
        pj(root_dir, 'tools', 'yt_run'),
        '-c', pj(root_dir, 'conf', 'conf-batch', config_file_name),
        '--proto', pj(root_dir, 'data', 'protos'),
        '--data-package', pj(root_dir, 'data.tar.gz'),
        '--target-prefix', target_prefix,
    )


@cm_target
def index_hosts_rthub(cfg, target):
    subcfg = cfg[target]
    yt_client = client(cfg)
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))

    if not get_skip_flag(cfg) or target == 'Test':
        hosts_data_prefix = pj(cfg.YtPrefix, 'test_data', current_sample_state, 'hosts')
        hosts_data_table_path = pj(hosts_data_prefix, 'rthub--hosts')
        if yt_client.exists(hosts_data_table_path):
            yt_client.remove(hosts_data_table_path)

        hosts_target_path = pj(subcfg.HostsRTHubDir, yt_client.get(pj(cfg.YtPrefix, subcfg.YtAttribute, 'hosts_res_file_name')))

        run_index_rthub(
            cfg, root_dir=hosts_target_path,
            target_prefix=hosts_data_prefix, config_file_name='hosts.pb.txt'
        ).add_args(*_get_common_args()).do()

        yt_client.move(
            hosts_data_table_path,
            pj(cfg.YtPrefix, 'test_data', target.lower(), 'rthub--hosts')
        )


@cm_target
def index_pages_rthub(cfg, target, bucket_number):
    subcfg = cfg[target]
    yt_client = client(cfg)
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))

    if not get_skip_flag(cfg) or target == 'Test':
        pages_data_prefix = pj(cfg.YtPrefix, 'test_data', current_sample_state, 'pages', bucket_number)
        pages_data_table_path = pj(pages_data_prefix, 'rthub--jupiter')
        if yt_client.exists(pages_data_table_path):
            yt_client.remove(pages_data_table_path)

        pages_target_path = pj(subcfg.PagesRTHubDir, yt_client.get(pj(cfg.YtPrefix, subcfg.YtAttribute, 'pages_res_file_name')))

        run_index_rthub(
            cfg, root_dir=pages_target_path,
            target_prefix=pages_data_prefix, config_file_name='pages.pb.txt'
        ).add_args(*_get_common_args()).do()

        yt_client.move(
            pages_data_table_path,
            pj(cfg.YtPrefix, 'test_data', target.lower(), 'rthub--pages_{}'.format(bucket_number))
        )


@cm_target
def index_app_docs_rthub(cfg, target, bucket_number):
    subcfg = cfg[target]
    yt_client = client(cfg)
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))

    if not get_skip_flag(cfg) or target == 'Test':
        app_docs_data_prefix = pj(cfg.YtPrefix, 'test_data', current_sample_state, 'app_docs', bucket_number)
        app_docs_data_table_path = pj(app_docs_data_prefix, 'rthub--app-docs-pages')
        if yt_client.exists(app_docs_data_table_path):
            yt_client.remove(app_docs_data_table_path)

        run_index_rthub(
            cfg, root_dir=subcfg.AppDocsRTHubDir,
            target_prefix=app_docs_data_prefix, config_file_name='appdocs.pb.txt'
        ).add_args(*_get_common_args()).do()

        yt_client.move(
            app_docs_data_table_path,
            pj(cfg.YtPrefix, 'test_data', target.lower(), 'rthub--appdocs_{}'.format(bucket_number))
        )


@cm_target
def merge_app_docs_to_pages(cfg, target, bucket_number):
    yt_client = client(cfg)
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))

    if not get_skip_flag(cfg) or target == 'Test':
        app_docs_indexed_table = pj(cfg.YtPrefix, 'test_data', target.lower(), 'rthub--appdocs_{}'.format(bucket_number))
        pages_data_path = pj(cfg.YtPrefix, 'test_data', current_sample_state, 'pages', bucket_number)
        if yt_client.exists(pj(pages_data_path, 'data')):
            yt_client.run_merge(
                [
                    pj(pages_data_path, 'data'),
                    app_docs_indexed_table
                ],
                pj(pages_data_path, 'zora--pages'),
                mode="sorted"
            )
            yt_client.remove(pj(pages_data_path, 'data'))
        else:
            raise Exception("Pages test data in bucket {} not found!".format(bucket_number))

# END CM Targets

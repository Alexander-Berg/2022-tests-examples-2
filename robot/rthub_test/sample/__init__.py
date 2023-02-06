#!/usr/bin/env python

from robot.cmpy.library.cmapi import CmApi
from robot.cmpy.library.run import BinaryRun
from robot.cmpy.library.target import cm_target, start, finish  # noqa
from robot.cmpy.library.yt_tools import client

from os.path import join as pj

# CM Targets


@cm_target
def check_sample_version(cfg):
    cmapi = CmApi()
    yt_client = client(cfg)
    new_sample_state = yt_client.get(pj(cfg.JupiterProdPrefix, '@jupiter_meta', 'sample_prev_state'))
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))
    if new_sample_state != current_sample_state:
        cmapi.launch_target("sample.finish", sync=True)


@cm_target
def get_urls_hosts_lists(cfg):
    yt_client = client(cfg)
    sample_state = yt_client.get(pj(cfg.JupiterProdPrefix, '@jupiter_meta', 'sample_prev_state'))
    yt_client.set(pj(cfg.YtPrefix, '@rthub_test_meta', 'new_sample'), sample_state)
    dst = pj(cfg.SampleDstDir, sample_state)
    yt_client.mkdir(dst)
    BinaryRun(
        pj(cfg.CmpyDir, 'sampler'),
        'filter',
        '--sample', 'nightly',
        cfg.JupiterProdPrefix,
        dst,
        "--server", cfg.YtProxy,
        "--token-path", cfg.YtTokenPath,
        "--pool", cfg.YtPool,
        "--sample-size", cfg.SampleSize
    ).do()


@cm_target
def copy_sample_delivery(cfg):
    yt_client = client(cfg)
    new_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'new_sample'))
    sample_delivery_path = pj(cfg.JupiterProdPrefix, 'sample', new_sample_state, 'nightly', 'delivery')
    dst_delivery_path = pj(cfg.YtPrefix, 'test_data', new_sample_state, 'delivery')

    yt_client.copy(sample_delivery_path, dst_delivery_path, recursive=True)


@cm_target
def sample_urls_data(cfg, bucket_number):
    yt_client = client(cfg)
    sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'new_sample'))
    dst = pj(cfg.SampleDstDir, sample_state)
    BinaryRun(
        pj(cfg.CmpyDir, 'sampler'),
        'pages',
        '--sample', 'nightly',
        '--shard', bucket_number,
        cfg.KwytYtPrefix,
        dst,
        "--server", cfg.YtProxy,
        "--token-path", cfg.YtTokenPath,
        "--pool", cfg.YtPool
    ).do()


@cm_target
def sample_hosts_robots_data(cfg):
    yt_client = client(cfg)
    sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'new_sample'))
    dst = pj(cfg.SampleDstDir, sample_state)
    BinaryRun(
        pj(cfg.CmpyDir, 'sampler'),
        'robots',
        '--sample', 'nightly',
        cfg.KwytYtPrefix,
        dst,
        "--server", cfg.YtProxy,
        "--token-path", cfg.YtTokenPath,
        "--pool", cfg.YtPool
    ).do()


@cm_target
def sample_hosts_status_data(cfg):
    yt_client = client(cfg)
    sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'new_sample'))
    dst = pj(cfg.SampleDstDir, sample_state)
    BinaryRun(
        pj(cfg.CmpyDir, 'sampler'),
        'status',
        '--sample', 'nightly',
        cfg.KwytYtPrefix,
        dst,
        "--server", cfg.YtProxy,
        "--token-path", cfg.YtTokenPath,
        "--pool", cfg.YtPool
    ).do()


@cm_target
def switch_samples(cfg):
    yt_client = client(cfg)
    new_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'new_sample'))
    current_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'))
    prev_sample_state = yt_client.get(pj(cfg.YtPrefix, '@rthub_test_meta', 'prev_sample'))

    if yt_client.exists(pj(cfg.SampleDstDir, prev_sample_state)) and prev_sample_state != current_sample_state:
        yt_client.remove(pj(cfg.SampleDstDir, prev_sample_state), recursive=True)

    yt_client.set(pj(cfg.YtPrefix, '@rthub_test_meta', 'prev_sample'), current_sample_state)
    yt_client.set(pj(cfg.YtPrefix, '@rthub_test_meta', 'current_sample'), new_sample_state)

    yt_client.set(pj(cfg.YtPrefix, '@prod_rthub_version', 'skip_index'), False)

# END CM Targets

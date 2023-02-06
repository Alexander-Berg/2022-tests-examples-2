#!/usr/bin/env python

# coding: utf-8

import fileinput
import os
import logging
import re
import shutil
import subprocess
from os.path import join as pj

RTHUB_TESTS_PATH = 'robot/rthub/test'
RTHUB_CONFS_PATH = 'robot/rthub/conf/conf-production'

RTHUB_CONFS = [
    {'conf': 'hosts.pb.txt',        'entries': 3001, 'topic': 'zora--hosts',        'client': 'rthub-test'},
    {'conf': 'sitemaps.pb.txt',     'entries': 500,  'topic': 'zora--sitemaps',     'client': 'rthub-test'},
    {'conf': 'images.pb.txt',       'entries': 50,   'topic': 'zora--images',       'client': 'rthub-test'},
    {'conf': 'images-fresh.pb.txt', 'entries': 40,   'topic': 'zora--images-fresh', 'client': 'images-rthub'},
    {'conf': 'appdocs.pb.txt',      'entries': 9,    'topic': 'zora--app-docs',     'client': 'rthub'},
    {'conf': 'pages.pb.txt',        'entries': 10,   'topic': 'zora--pages',        'client': 'rthub-test'},
    {'conf': 'pages-fresh.pb.txt',  'entries': 50,   'topic': 'zora--pages-fresh',  'client': 'rthub-test'},
]


def build_target(vcs_path, output_path=''):
    build_cmd = [
        'ya', 'make', '-r',
        vcs_path,
        '--checkout'
    ]
    if output_path:
        build_cmd.extend(['-o', output_path])
    subprocess.check_call(build_cmd)


def pull_data(vcs_root, config_path, pq_tool, configuration, dst_dir):
    cmd = [
        pq_tool,
        '--cmd', 'pull',
        '--config', config_path,
        '-d', dst_dir,
        '-l', str(configuration['entries']),
        '-t', configuration['topic'],
        '--client', configuration['client']
    ]

    p_out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    logging.warning(p_out[0].decode('utf-8'))


def upload_test_data(dir_to_upload):
    upload_cmd = [
        'ya', 'upload',
        '--sandbox', '--skynet',
        dir_to_upload,
        '--ttl', 'inf'
    ]

    logging.warning("Uploading data to sandbox...")
    p_out = subprocess.Popen(upload_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    res_id = ''
    for line in p_out[0].decode('utf-8').split('\n'):
        if 'Download link' in line:
            res_id = line.split('/')[-1]
    return res_id


def canonize_tests(vcs_root, conf):
    canonize_cmd = [
        'ya', 'make',
        '-tt', '-Z',
        pj(vcs_root, RTHUB_TESTS_PATH, conf, 'medium'),
        '--checkout'
    ]
    p_out = subprocess.Popen(canonize_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    logging.warning(p_out[0].decode('utf-8'))


def main():
    with os.popen('ya dump root') as f:
        vcs_root = f.read()
        logging.warning("Using {} as VCS root".format(vcs_root))

    work_dir = os.getcwd()
    tmp_dir = pj(work_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    pq_tool_path = pj(vcs_root, 'robot/rthub/tools/pq_tool')
    pq_tool_bin = pj(pq_tool_path, 'pq_tool')

    if not os.path.isfile(pq_tool_bin):
        logging.warning("Building pq_tool...")
        build_target(pq_tool_path)

    logging.warning("Building protos...")
    protos_path = pj(vcs_root, 'robot/rthub/packages/full_web_protos')
    protos_out = pj(tmp_dir, 'robot/rthub/packages/full_web_protos')
    build_target(protos_path, tmp_dir)

    for conf in RTHUB_CONFS:
        test_data_dir = pj(tmp_dir, 'test_data')
        if os.path.exists(test_data_dir):
            shutil.rmtree(test_data_dir)
        os.mkdir(test_data_dir)

        config_path = pj(tmp_dir, conf['conf'])
        shutil.copyfile(pj(vcs_root, RTHUB_CONFS_PATH, conf['conf']), config_path)
        with open(config_path, 'a') as f:
            f.write("ProtoPath: '{}'".format(protos_out))

        logging.warning("Pulling data for {} from {} topic".format(conf['conf'], conf['topic']))
        pull_data(vcs_root, config_path, pq_tool_bin, conf, test_data_dir)
        res_id = upload_test_data(test_data_dir)
        test_path = pj(vcs_root, RTHUB_TESTS_PATH, re.sub('\.pb\.txt', '', conf['conf']), 'medium', 'ya.make')

        logging.warning("Updating test data resource id in {}".format(test_path))
        f = fileinput.FileInput(test_path, inplace=True)
        for line in f:
            if '# test_data' in line:
                line = re.sub(r'sbr://[0-9].*$', 'sbr://{} # test_data'.format(res_id), line)
            print line,
        f.close()

    for conf in RTHUB_CONFS:
        logging.warning("Canonizing {} test".format(re.sub('\.pb\.txt', '', conf['conf'])))
        canonize_tests(vcs_root, re.sub('\.pb\.txt', '', conf['conf']))

    print("All done. Review and commit changes in $ARCADIA_ROOT/robot/rthub/test")
    p_out = subprocess.Popen(['svn', 'st', '-q', '{}/robot/rthub/test'.format(vcs_root)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    print("{}".format(p_out[0].decode('utf-8')))

if __name__ == '__main__':
    main()

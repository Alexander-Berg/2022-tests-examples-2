#!/usr/bin/env python

import sys
import yatest.common
import logging
import shutil
import os
import re

from os.path import join as pj
from BaseHTTPServer import BaseHTTPRequestHandler
from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.common.kikimr_runner import KikimrRunner
from robot.rthub.test.common.mds_runner import MdsRunner
from robot.rthub.test.turbo.medium.turbo_test_lib import turbo_test


class MdsMockHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.protocol_version = 'HTTP/1.1'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write("{}")


def create_test_config(file_path, port, namespace):
    config_content = '''PusherConfig {
    ServerName: "localhost"
    Port: __port__
    Namespace: "__namespace__"
}'''
    plugin_body = re.sub(r'__port__', str(port), config_content)
    plugin_body = re.sub(r'__namespace__', namespace, plugin_body)
    with open(file_path, 'w') as f:
        f.write(plugin_body)


def test_rthub_turbo_images():
    logger = logging.getLogger('rthub_test_logger')
    logger.info('rthub_test_turbo_images')
    table_yql = yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')
    data_yql = yatest.common.work_path('test_data/data.yql')

    rthub_bin = yatest.common.binary_path('robot/rthub/main/rthub')
    orig_config = yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-image-worker.pb.txt')
    udfs_path = yatest.common.build_path('robot/rthub/packages/full_turbo_udfs')
    proto_path = yatest.common.build_path('robot/rthub/packages/full_web_protos')
    libraries_path = yatest.common.source_path('robot/rthub/yql/libraries')
    queries_path = yatest.common.source_path('robot/rthub/yql/queries')
    test_data = yatest.common.work_path('test_data')
    output = yatest.common.work_path('output')

    mds_runner = MdsRunner(handler_class=MdsMockHandler)
    server_port = mds_runner.mds_server_port()

    # Gather resources
    res_dir = yatest.common.work_path('resources')
    if os.path.exists(res_dir):
        shutil.rmtree(res_dir)

    os.mkdir(yatest.common.work_path('resources'))
    turbo_config_path = pj(res_dir, 'mds_test')
    create_test_config(turbo_config_path, server_port, 'turbo')

    turbo_test.unpack_standard_resources(res_dir)

    kikimr_runner = KikimrRunner(table_yql, data_yql)
    kikimr_runner.setup()
    rthub_runner = RTHubRunner(rthub_bin, orig_config, test_data, output)

    rthub_runner.update_config(udfs_path, proto_path, res_dir,
                               libraries_path, queries_path, 0)

    rthub_runner.set_env_variable('KIKIMR_PROXY', kikimr_runner.get_endpoint())
    rthub_runner.set_env_variable('KIKIMR_DATABASE', "local")
    rthub_runner.set_env_variable('MDS_INFO_TABLE', "MdsInfoTable")
    rthub_runner.save_config()
    mds_runner.startup_mds_server()

    try:
        logger.info("Launching RTHub...")
        print >>sys.stderr, 'Output folder: ' + output
        rthub_runner.run_rthub(binary=False)
    finally:
        kikimr_runner.stop()
        mds_runner.shutdown_mds_server()

    diff_tool = yatest.common.binary_path('robot/rthub/tools/diff_tool/diff_tool')
    return yatest.common.canonical_dir(output, diff_tool=[diff_tool, "--config", rthub_runner.get_config()])

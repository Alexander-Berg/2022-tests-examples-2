from os.path import join as pj, isfile
import yatest.common

import shutil
import tarfile
import os
import os.path

from robot.rthub.test.common.rthub_runner import RTHubRunner
from robot.rthub.test.common.kikimr_runner import KikimrRunner

from google.protobuf import text_format


def unpack_standard_resources(res_dir):
    TurboTest.unpack_resources(yatest.common.build_path('robot/rthub/packages/resources/saas'), pj(res_dir, 'saas'), True)
    TurboTest.unpack_resources(yatest.common.source_path('robot/rthub/packages/resources/turbo-pages'), res_dir, True)
    TurboTest.unpack_resources(yatest.common.source_path('quality/functionality/turbo/page_linter/config'), res_dir, True)
    TurboTest.unpack_resources(yatest.common.work_path('.'), res_dir)


class TurboTest:
    def __enter__(self):
        self.kikimr_runner = KikimrRunner(self.table_yql, self.data_yql)
        self.kikimr_runner.setup()
        return self

    def __exit__(self, exp_type, exp_value, traceback):
        self.kikimr_runner.stop()

    def __init__(self, test_data=None, table_yql=None, data_yql=None, udfs_path=None, proto_path=None, libraries_path=None, queries_path=None, output=None, resources_dir=None, rthub_bin=None):
        self.test_data = test_data or yatest.common.work_path('test_data')

        self.table_yql = table_yql or yatest.common.source_path('robot/rthub/test/turbo/yql/table.yql')
        self.data_yql = data_yql or pj(self.test_data, 'data.yql')

        self.udfs_path = udfs_path or yatest.common.build_path('robot/rthub/packages/full_turbo_udfs')
        self.proto_path = proto_path or yatest.common.build_path('robot/rthub/packages/full_web_protos')
        self.libraries_path = libraries_path or yatest.common.source_path('robot/rthub/yql/libraries')
        self.queries_path = queries_path or yatest.common.source_path('robot/rthub/yql/queries')

        self.output = output or yatest.common.work_path('output')
        self.resources_dir = resources_dir or yatest.common.work_path('resources')
        self.rthub_bin = rthub_bin or yatest.common.binary_path('robot/rthub/main/rthub')

        if not os.path.exists(self.test_data):
            os.mkdir(self.test_data)
        if os.path.exists(self.resources_dir):
            shutil.rmtree(self.resources_dir)
        os.mkdir(self.resources_dir)

        if not os.path.exists(self.data_yql):
            open(self.data_yql, 'a').close()

    _default_environments = {
        'KIKIMR_DATABASE': "local",
        'MDS_INFO_TABLE': "mds",
        "AUTOPARSER_FLAGS_TABLE": "autoparser_flags",
        "FEED_HASHES_TABLE": "feed_hashes",
        "BUTTON_FILTER_TABLE": "top_filter",
        "YQL_CONFIG_NAME": "testing",
        "USE_JSON_COMPRESSION": "false",
        "TEST_TIMESTAMP": "0"
    }

    def run_rthub(self, env_dict, config, max_input_message_size=None):
        environments = self._default_environments.copy()
        environments["KIKIMR_PROXY"] = self.kikimr_runner.get_endpoint()
        environments.update(env_dict)

        rthub_runner = RTHubRunner(self.rthub_bin, config, self.test_data, self.output)
        rthub_runner.update_config(self.udfs_path, self.proto_path, self.resources_dir,
                                        self.libraries_path, self.queries_path, 6, max_input_message_size=max_input_message_size)

        for key, value in environments.items():
            rthub_runner.set_env_variable(key, value)

        rthub_runner.save_config()
        rthub_runner.run_rthub(binary=False)

    def run_rthub_parser(self, env_dict={}, max_input_message_size=None):
        self.run_rthub(env_dict, yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-rss-parser-worker.pb.txt'), max_input_message_size)

    def run_rthub_postprocess(self, env_dict={}):
        self.run_rthub(env_dict, yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-postprocess-worker.pb.txt.gen'))

    def run_rthub_images(self, env_dict={}):
        self.run_rthub(env_dict, yatest.common.source_path('robot/rthub/conf/conf-prestable/turbo-image-worker.pb.txt'))

    @staticmethod
    def restore_pb_from_file(filename, pb_type):
        result = []
        with open(filename, 'r') as f:
            items = f.read().split("===\n")
            for item in items:
                if not item:
                    break
                result.append(text_format.Parse(item, pb_type()))
        return result

    @staticmethod
    def save_pb_to_file(pb_list, path_to_file):
        with open(path_to_file, 'w+') as f:
            for pb in pb_list:
                f.write(str(pb))
                f.write("\n===\n")

    def unpack_standard_resources(self):
        unpack_standard_resources(self.resources_dir)

    @staticmethod
    def unpack_resources(resources_path, res_dir, ignore_nonexistent_source=False):
        if ignore_nonexistent_source and not os.path.exists(resources_path):
            return

        for arc in os.listdir(resources_path):
            if '.tar' in arc:
                with tarfile.open(pj(resources_path, arc), 'r') as t:
                    t.extractall(res_dir)
            elif os.path.exists(pj(res_dir, arc)):
                continue
            elif isfile(pj(resources_path, arc)):
                shutil.copy(pj(resources_path, arc), pj(res_dir, arc))
            else:
                shutil.copytree(pj(resources_path, arc), pj(res_dir, arc))

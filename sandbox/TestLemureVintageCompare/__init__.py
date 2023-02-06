import re
import json
import logging

from os import listdir
from utils import get_color_diffs_from_file
from os.path import join
from sandbox.projects import resource_types
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.paths import get_logs_folder, make_folder
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.parameters import ResourceSelector
from sandbox.projects.common.async_res_download import AsyncResDownloadTask


class TestLemurVintageCompare(AsyncResDownloadTask):
    type = 'TEST_LEMUR_VINTAGE_COMPARE'

    COUNTERS_FILE_RE = re.compile(r'vintage_map.counters.shard-(\d+).json')

    RECIPIENTS = ['abogutskiy', 'alexvin', 'zosimov']

    class DiffTool(ResourceSelector):
        name = 'diff_tool'
        description = 'Lemur counters diff tool'
        default_value = '180165464'
        resource_type = resource_types.LEMUR_COUNTERS_DIFF_TOOL
        required = False

    class LeftCompareResource(ResourceSelector):
        name = 'left_resource'
        description = 'Left resource to compare'
        resource_type = resource_types.TEST_LEMUR_VINTAGE_OUT
        required = True

    class RightCompareResource(ResourceSelector):
        name = 'right_resource'
        description = 'Right resource to compare'
        resource_type = resource_types.TEST_LEMUR_VINTAGE_OUT
        required = True

    input_parameters = [DiffTool, LeftCompareResource, RightCompareResource]

    RES_KEYS_ASYNC_DOWNLOAD = [DiffTool.name, LeftCompareResource.name, RightCompareResource.name]

    def _get_shard_number(self, f):
        m = self.COUNTERS_FILE_RE.search(f)
        if m:
            return str('%04d' % int(m.group(1)))
        return None

    def _get_counters_files(self, directory):
        counters_files = []
        for f in listdir(directory):
            if self.COUNTERS_FILE_RE.match(f):
                counters_files.append(f)
        return counters_files

    def _get_resource_revision(self, resource_id):
        GET_RESOURCE_REVISION_RE = re.compile(r'.*Revision\s*:\s*(\d+)')
        resource_description = channel.sandbox.get_resource(resource_id).description
        m = GET_RESOURCE_REVISION_RE.search(resource_description)
        if m:
            return m.group(1)
        return None

    def _get_mail_body(self, j):
        body = ""
        for s in sorted(j.keys()):
            body += "\n{}\n".format(s)
            for c in sorted(j[s].keys()):
                body += "  {}\n".format(c)
                for l in j[s][c]:
                    body += "    {}\n".format(l)
        return body

    def on_execute(self):
        if self.ctx[self.DiffTool.name] is None:
            if self.DiffTool.default_value is None:
                raise SandboxTaskFailureError("Incorrect Code...")
            else:
                self.ctx[self.DiffTool.name] = self.DiffTool.default_value

        logging.debug("Diff tool resource :{}".format(self.ctx[self.DiffTool.name]))
        logging.debug("Left compared resource :{}".format(self.ctx[self.LeftCompareResource.name]))
        logging.debug("Right compared resource :{}".format(self.ctx[self.RightCompareResource.name]))

        left_resource_revision = self._get_resource_revision(self.ctx[self.LeftCompareResource.name])
        if left_resource_revision is None:
            raise SandboxTaskFailureError("Couldn't get revision for left resource")

        right_resource_revision = self._get_resource_revision(self.ctx[self.RightCompareResource.name])
        if right_resource_revision is None:
            raise SandboxTaskFailureError("Couldn't get revision for right resource")

        logging.debug("Left resource revision: {}".format(left_resource_revision))
        logging.debug("Right resource revision: {}".format(right_resource_revision))

        procs = self.start_async_download()

        diff_tool = self.get_results_from_special_proc(procs, self.DiffTool.name)
        left_resource_dir = self.get_results_from_special_proc(procs, self.LeftCompareResource.name)
        right_resource_dir = self.get_results_from_special_proc(procs, self.RightCompareResource.name)

        logging.debug("Diff tool_binary: {}".format(diff_tool))
        logging.debug("Left resource dir: {}".format(left_resource_dir))
        logging.debug("Right resource dir: {}".format(right_resource_dir))

        left_counters_files = self._get_counters_files(left_resource_dir)
        right_counters_files = self._get_counters_files(left_resource_dir)
        if sorted(left_counters_files) != sorted(right_counters_files):
            raise SandboxTaskFailureError("Different counters files number in compared resources:"
                                          " {} VS {}".format(left_counters_files, right_counters_files))
        for f in left_counters_files:
            cmd = [diff_tool, join(left_resource_dir, f), join(right_resource_dir, f)]
            process.run_process(cmd, check=True, log_prefix=f, outputs_to_one_file=True, wait=True)

        main_json = {}
        logs_dir = get_logs_folder()
        for f in listdir(logs_dir):
            shard_number = self._get_shard_number(f)
            if shard_number:
                key = "Shard_{}".format(shard_number)
                diffs = get_color_diffs_from_file(join(logs_dir, f))
                if diffs:
                    main_json[key] = get_color_diffs_from_file(join(logs_dir, f))

        if main_json:
            subj = "Result for {}:#{} r{} vs r{}".format("TEST_LEMUR_VINTAGE_MAP_COMPARE", self.id, left_resource_revision, right_resource_revision)

            body = self._get_mail_body(main_json)
            channel.sandbox.send_email(self.RECIPIENTS, None, subj, body)

        test_out_dir = "test_out"
        make_folder(test_out_dir)
        test_out = join(test_out_dir, "test_out.json")

        with open(test_out, 'w') as f:
            json.dump(main_json, f, indent=4, sort_keys=True)

        out_resource = self.create_resource(
            description="{} Task:#{} Revisions:{}vs{}".format(self.type, self.id, left_resource_revision, right_resource_revision),
            resource_path=test_out_dir,
            resource_type=resource_types.TEST_LEMUR_VINTAGE_COMPARE_OUT
        )

        self.mark_resource_ready(out_resource.id)


__Task__ = TestLemurVintageCompare

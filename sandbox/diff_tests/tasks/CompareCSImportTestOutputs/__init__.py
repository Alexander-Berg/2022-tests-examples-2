import os
import sys
import StringIO
import logging

from sandbox.projects.common.BaseCompareYaMakeOutputsTask import BaseCompareYaMakeOutputsTask

from sandbox.projects.common.yabs.server.tracing import TRACE_WRITER_FACTORY
from sandbox.projects.yabs.sandbox_task_tracing import trace_entry_point
from sandbox.projects.yabs.sandbox_task_tracing.wrappers import subprocess


def fix_path(path):
    pytest = "/pytest/"
    py3test = "/py3test/"
    if pytest in path:
        return path.replace(pytest, py3test)
    elif py3test in path:
        return path.replace(py3test, pytest)
    else:
        return path


class CompareCsImportTestOutputs(BaseCompareYaMakeOutputsTask):

    @trace_entry_point(writer_factory=TRACE_WRITER_FACTORY)
    def compare(self, build_output1, build_output2, testing_out_stuff_dir):
        import sandboxsdk.svn
        sys.path.append(sandboxsdk.svn.Arcadia.get_arcadia_src_dir("arcadia:/arc/trunk/arcadia/contrib/deprecated/python/diff2html"))
        import diff2html

        output1 = os.path.join(build_output1, testing_out_stuff_dir)
        output2 = os.path.join(build_output2, testing_out_stuff_dir)

        # fix for comparing outputs between Py2 and Py3 tests
        if not os.path.exists(output1):
            output1 = fix_path(output1)
        if not os.path.exists(output2):
            output2 = fix_path(output2)

        result_dir1 = os.path.join(output1, "result")
        result_dir2 = os.path.join(output2, "result")

        # output dir exists but it not contains result dir
        if os.path.exists(output1) and os.path.exists(output2) and not os.path.exists(result_dir1) and not os.path.exists(result_dir2):
            logging.info("output dirs %s, %s exist but they not contain 'result' dir", output1, output2)
            return

        p = subprocess.popen_and_communicate(
            [
                "diff", "--unified=50", "-r",
                result_dir1,
                result_dir2
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        out = p.stdout
        err = p.stderr

        if p.returncode == 1:
            input = StringIO.StringIO(out)
            htmlOutput = StringIO.StringIO()
            diff2html.parse_input(input, htmlOutput, "diff.txt", None, None, None)
            return htmlOutput.getvalue()

        if p.returncode != 0:
            return err

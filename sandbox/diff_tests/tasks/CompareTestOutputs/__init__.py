import os
import logging

from sandbox import sdk2
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


class CompareTestOutputs(BaseCompareYaMakeOutputsTask):
    class Parameters(BaseCompareYaMakeOutputsTask.Parameters):
        unified_num = sdk2.parameters.Integer(
            'Output lines of unified context',
            default=10,
        )

    @trace_entry_point(writer_factory=TRACE_WRITER_FACTORY)
    def compare(self, build_output1, build_output2, testing_out_stuff_dir):
        test_out_rel_path = os.path.join(testing_out_stuff_dir, 'result')
        output1 = os.path.join(build_output1, test_out_rel_path)
        output2 = os.path.join(build_output2, test_out_rel_path)
        test_out_abs_path1 = os.path.join(build_output1, testing_out_stuff_dir)
        test_out_abs_path2 = os.path.join(build_output2, testing_out_stuff_dir)

        # fix for comparing outputs between Py2 and Py3 tests
        if not os.path.exists(test_out_abs_path1):
            output1 = fix_path(output1)
            test_out_abs_path1 = fix_path(test_out_abs_path1)
        if not os.path.exists(test_out_abs_path2):
            output2 = fix_path(output2)
            test_out_abs_path2 = fix_path(test_out_abs_path2)

        if os.path.exists(test_out_abs_path1) and not os.path.exists(output1) and os.path.exists(test_out_abs_path2) and not os.path.exists(output2):
            logging.info('"result" directory is not found in %s', testing_out_stuff_dir)
            return False

        p = subprocess.popen_and_communicate(
            [
                'diff',
                '-r',
                '-U', str(self.Parameters.unified_num),
                output1,
                output2,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out = p.stdout
        err = p.stderr

        if p.returncode == 0:
            return False
        elif p.returncode == 1:
            return out
        else:
            return err

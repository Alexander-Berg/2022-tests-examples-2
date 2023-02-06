# -*- coding: utf-8 -*-

from sandbox import sdk2
import sandbox.common.types.resource as ctr
import sandbox.projects.resource_types as rt

from sandbox.sdk2.helpers import subprocess as sp
from sandbox.projects.bsyeti.common import basic_releasers


class MakeBigbTestDataBin(rt.ARCADIA_PROJECT):
    """
    resource with make_bigb_test_data bin
    """

    releasable = True
    any_arch = True
    auto_backup = True
    releasers = basic_releasers
    release_subscribers = ["bsyeti-watcher"]


class BigbBenchmarkTestdata(sdk2.Resource):
    """
    data for bigb benchmarks
    """
    pass


class BigbEagleTestdata(sdk2.Resource):
    """
    data for eagle/canonize_ut test
    """
    pass


class BigbBuzzardTestdata(sdk2.Resource):
    """
    data for buzzard/b2b test
    """
    pass


class BigbTestData(sdk2.Resource):
    """
    files with sample of logs from logbroker to test bigb
    """

    any_arch = True
    auto_backup = True
    calc_md5 = True
    share = True
    releasable = True
    releasers = basic_releasers


class ResharderTestData(sdk2.Resource):
    """
    files with sample of logs to test resharder
    """


class CaesarTestData(sdk2.Resource):
    """
    files with sample of logs to test caesar
    """


class MakeBigbTestData(sdk2.Task):
    """
    task to make test data for bigb testing
    """
    class Requirements(sdk2.Requirements):
        cores = 1  # exactly 1 core
        ram = 8192  # 8GiB or less

    class Caches(sdk2.Requirements.Caches):
        pass  # means that task do not use any shared caches

    class Parameters(sdk2.Parameters):
        binary_id = sdk2.parameters.LastReleasedResource(
            'bsyeti make test data binary resource',
            resource_type=MakeBigbTestDataBin,
            state=(ctr.State.READY, ),
            required=True
        )

        startday = sdk2.parameters.String(
            'start log day (yyyymmdd)',
            required=True
        )

        endday = sdk2.parameters.String(
            'end log day (yyyymmdd)',
            required=True
        )

        input_dir = sdk2.parameters.String(
            'yt directory with logs tables',
            required=True
        )

    def on_execute(self):
        bin_res = sdk2.ResourceData(self.Parameters.binary_id)

        folder = "test_data"
        info_filder = "test_data/info"
        yt_data_folder = "test_data/yt_data"

        env = {
            "YT_PROXY": "hahn",
            "YT_TOKEN": sdk2.Vault.data("sec-01djab78jh9dvsymnjzwhk1mpf[yt_token]"),  # "zomb-yeti" secret from yav
            "TMP": ".",
            "TMPDIR": ".",
        }
        cmd = [
            str(bin_res.path) + "/make_bigb_test_data",
            "--output", folder,
            "--input", self.Parameters.input_dir,
            "--start", self.Parameters.startday,
            "--end", self.Parameters.endday,
        ]
        with sdk2.helpers.ProcessLog(self, logger="make_bigb_test_data") as l:
            sp.check_call(cmd, stdout=l.stdout, stderr=l.stderr, env=env)

        tmp_ts_filename = "max_timestamp"

        cmd = [
            str(bin_res.path) + "/lb2yt_data",
            "--input", folder,
            "--output", yt_data_folder,
            "--lb2yt", str(bin_res.path) + "/lb2yt_requests",
            "--max-ts-file", tmp_ts_filename,
        ]
        with sdk2.helpers.ProcessLog(self, logger="lb2yt_data") as l:
            sp.check_call(cmd, stdout=l.stdout, stderr=l.stderr, env=env)

        sp.check_call(['mkdir', info_filder])
        sp.check_call(['mv', tmp_ts_filename, "{info}/max_timestamp".format(info=info_filder)])

        BigbTestData(self, "Bigb test data", folder)

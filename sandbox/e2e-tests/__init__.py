import logging
from sandbox import sdk2
import sandbox.common.types.client as ctc
from sandbox.sdk2.helpers import subprocess as sp

from main import main


class TranscoderTestTask(sdk2.Task):

    class Requirements(sdk2.Requirements):
        pass

    class Parameters(sdk2.Parameters):
        max_restarts = 3
        kill_timeout = 5400

        with sdk2.parameters.Group("Lifetime parameters") as life_block:
            rtt_host = sdk2.parameters.String("Transcoder host", required=True)
            ffp_res_id = sdk2.parameters.Integer("Ffprobe binary resource id", required=True)
            ffmpeg_res_id = sdk2.parameters.Integer("Ffmpeg binary resource id", required=True)
            validator_res_id = sdk2.parameters.Integer("Hls media stream validator binary resource id", required=True)
            all_tests = sdk2.parameters.Bool("Launch all tests", required=True)
            run_mediastream_validator = sdk2.parameters.Bool("Run mediastreamvalidator", required=True)

        with sdk2.parameters.Group("Vault Parameters") as vault_block:
            rtt_token_vault_item_owner = sdk2.parameters.String("RTT token vault item owner", required=True)
            rtt_token_vault_item_name = sdk2.parameters.String("RTT token vault item name", required=True)

        with sdk2.parameters.Output:
            test_results = sdk2.parameters.JSON('test results', required=False)

    class TestsLaunchConfig:

        def __init__(self, rtt_host, rtt_token, ffmpeg_bin, ffprobe_bin, validator_bin, all_tests):
            self.rtt_host = rtt_host
            self.rtt_token = rtt_token
            self.ffmpeg_bin = ffmpeg_bin
            self.ffprobe_bin = ffprobe_bin
            self.validator_bin = validator_bin
            self.all_tests = all_tests

    def on_save(self):
        if self.Parameters.run_mediastream_validator:
            self.Requirements.client_tags = ctc.Tag.Group.OSX

    def on_execute(self):
        ffprobe_bin = str(sdk2.ResourceData(sdk2.Resource.find(id=self.Parameters.ffp_res_id).first()).path)

        ffmpeg_bin = str(sdk2.ResourceData(sdk2.Resource.find(id=self.Parameters.ffmpeg_res_id).first()).path)

        validator_bin = str(sdk2.ResourceData(sdk2.Resource.find(id=self.Parameters.validator_res_id).first()).path)

        rtt_host = self.Parameters.rtt_host

        rtt_token = sdk2.Vault.data(
            self.Parameters.rtt_token_vault_item_owner,
            self.Parameters.rtt_token_vault_item_name
        )

        config = self.TestsLaunchConfig(rtt_host,
                                        rtt_token,
                                        ffmpeg_bin,
                                        ffprobe_bin,
                                        validator_bin if self.Parameters.run_mediastream_validator else None,
                                        self.Parameters.all_tests)

        def run_cmd(args):
            with sdk2.helpers.ProcessLog(self, logger=logging.getLogger('cmd')) as pl:
                return sp.check_output(args, stderr=pl.stderr)

        main(self, config, run_cmd)

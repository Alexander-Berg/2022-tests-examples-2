# -*- coding: utf-8 -*-
import logging
import json

from sandbox.projects.websearch.begemot import parameters as bp
from sandbox.projects.websearch.begemot import resources as br
from sandbox.projects.websearch.begemot.tasks.GetBegemotResponses import GetBegemotResponses
from sandbox.projects.websearch.begemot.common.fast_build import ShardSyncHelper
from sandbox.sdk2.helpers import subprocess as sp
from sandbox import sdk2


class TestBegemotFreshDifference(GetBegemotResponses):
    """
        Check difference between two fresh data on queries.
    """
    UseTestedData = 0
    ShardPath = None

    class Parameters(GetBegemotResponses.Parameters):
        tested_fresh = bp.FreshResource()

    def _prepare_shard(self):
        if (self.ShardPath):
            return self.ShardPath
        shard_helper = ShardSyncHelper(self.Parameters.fast_build_config)
        data_path = str(self.path('data'))
        shard = shard_helper.sync_shard(data_path)
        self.ShardPath = shard
        return shard

    def _prepare_args(self, shard_path):
        begemot_eventlog_path = 'begemot.evlog'
        if (self.UseTestedData == 1):
            begemot_eventlog_path += "_test"
        args = (
            str(sdk2.ResourceData(self.Parameters.begemot_binary).path),
            '--data',
            shard_path,
            '--cache_size',
            str(self._get_cache_size_bytes()),
            '--test',
            '--log', begemot_eventlog_path,
        )
        br.BEGEMOT_EVENTLOG(self, 'Begemot eventlog', begemot_eventlog_path)

        if (self.UseTestedData == 1):
            args += ('--fresh', str(sdk2.ResourceData(self.Parameters.tested_fresh).path))
        else:
            args += ('--fresh', str(sdk2.ResourceData(self.Parameters.begemot_fresh).path))
        if self.Parameters.mlock:
            args += ('--mlock',)
        if self.Parameters.is_cgi:
            args += ('--cgi',)
        if self.Parameters.jobs:
            args += ('--jobs', str(self.Parameters.jobs))
        if self.Parameters.additional_jobs:
            args += ('--additional-jobs', str(self.Parameters.additional_jobs))
        if self.Parameters.test_jobs:
            args += ('--test-jobs', str(self.Parameters.test_jobs))
        return args

    def execute_cmd(self, cmd_params, log_name):
        logging.info('Run command: {}'.format(' '.join(cmd_params)))
        with sdk2.helpers.ProcessLog(self, logger=log_name) as l:
            sp.check_call(cmd_params, stdout=l.stdout, stderr=l.stderr)

    def on_enqueue(self):
        output_path = 'output.txt' if (self.UseTestedData == 0) else 'output_test.txt'
        output_descr = 'GetBegemotResponses output' if (self.UseTestedData == 0) else 'GetBegemotResponses_tested output'
        self.Context.out_resource_id = br.BEGEMOT_RESPONSES_RESULT(
            self,
            output_descr,
            output_path
        ).id

    def read_accepted_data(self, input_file):
        rules = []
        with open(input_file, "r") as f:
            for line in f.readlines():
                rules.append(json.loads(line)[0]["rules"]["Report"]["Rules"])

        accepted_data = []
        for result in rules:
            data = {}
            for rule in result:
                accepted = json.loads(rule)
                data[accepted["Name"]] = accepted
            accepted_data.append(data)
        return accepted_data

    def validate_data(self, prod_data, test_data, diff):
        n = len(prod_data)
        if (len(test_data) != n):
            return False

        for i in range(n):
            prod_result = prod_data[i]
            test_result = test_data[i]
            if (prod_result.keys() != test_result.keys()):
                diff.append([i, prod_result, test_result])
        return len(diff) == 0

    def on_execute(self):
        super(TestBegemotFreshDifference, self).on_execute()
        self.UseTestedData = 1
        self.on_enqueue()
        super(TestBegemotFreshDifference, self).on_execute()

        prod_data = self.read_accepted_data("output.txt")
        test_data = self.read_accepted_data("output_test.txt")

        diff = []
        if (not self.validate_data(prod_data, test_data, diff)):
            print json.dumps(diff, ensure_ascii=False, indent=4)
        else:
            print "Ok"

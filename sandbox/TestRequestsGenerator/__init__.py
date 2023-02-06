# -*- coding: utf-8 -*-
from sandbox import sdk2
import sandbox.common.types.client as ctc


from sandbox.projects.modadvert.common import modadvert
from sandbox.projects.modadvert import resource_types


class ModadvertRunTestRequests(modadvert.ModadvertBaseYtTask):

    name = "MODADVERT_RUN_TEST_REQUESTS"

    class Requirements(sdk2.Task.Requirements):
        client_tags = ctc.Tag.GENERIC

    class Parameters(modadvert.ModadvertBaseYtTask.Parameters):
        with sdk2.parameters.Group('Binary') as binary_group:
            binaries_resource = sdk2.parameters.Resource(
                'Resource with task binary',
                resource_type=resource_types.MODADVERT_RUN_TEST_REQUESTS_BINARY,
                required=True
            )

        workers_count = sdk2.parameters.Integer('Workers count', required=True, default=1)
        url = sdk2.parameters.String('Requests URL', required=True)
        log_table = sdk2.parameters.String(
            'Logging yt table path',
            required=True
        )
        max_rps = sdk2.parameters.Integer('Limit requests per second', required=False, default=100)
        max_requests = sdk2.parameters.Integer('Limit requests count', required=False, default=3000)
        table = sdk2.parameters.String('Table to fire with', required=True)

    def create_command(self):
        self.untar_resource(self.Parameters.binaries_resource)
        cmd = [
            './test_requests',
            '--workers-count', self.Parameters.workers_count,
            '--yt-proxy-url', self.Parameters.yt_proxy_url,
            '--url', self.Parameters.url,
            '--dst-table', self.Parameters.log_table,
            '--max-requests', self.Parameters.max_requests,
            '--max-rps', self.Parameters.max_rps,
            '--tables', self.Parameters.table
        ]

        return cmd

    def on_execute_inner(self):
        self.run_command(self.create_command(), log_prefix="main")

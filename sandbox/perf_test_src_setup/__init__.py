# -*- coding: utf-8 -*-

import logging
import json

from sandbox import sdk2
from sandbox.common.types.client import Tag
from sandbox.projects.vh.frontend.vh_base_test import VhBaseTest


class VhPerfTestSrcSetup(VhBaseTest):
    """
        Base test
    """

    class Requirements(VhBaseTest.Requirements):
        privileged = True
        client_tags = Tag.INTEL_E5_2650 & Tag.LXC & Tag.GENERIC
        execution_space = 10 * 1024
        required_ram = 16 * 1024

    class Parameters(VhBaseTest.Parameters):
        pass

    @sdk2.footer()
    def footer(self):
        if "num_sessions" not in self.Context:
            return None

        table = []
        for i in range(self.Context.num_sessions):
            table.append({
                "N session": i,
                "RPS": self.Context.requests_per_sec[i],
                "Fail rate": self.Context.fail_rates[i],
                "Not found rate": self.Context.notfound_rates[i],
            })

        return {
            "<h4>Executor stats</h4>": table,
        }

    def compare_shooting_result(self, stable_shooting_result, test_shooting_result, dolbilka_plan_creator_stable, dolbilka_plan_creator_test, raw_requests):
        logging.info("Start compare_shooting_result in perf_test_src_setup")
        stable_stats_file = None
        test_stats_file = None
        stable_path = sdk2.ResourceData(stable_shooting_result.Parameters.shooting_stats).path
        with open(str(stable_path), "r") as f:
            stable_stats_file = json.load(f)
        test_path = sdk2.ResourceData(test_shooting_result.Parameters.shooting_stats).path
        with open(str(test_path), "r") as f:
            test_stats_file = json.load(f)

        shooting_stats = [stable_stats_file, test_stats_file]
        self.fill_rps_ctx(shooting_stats, self.Context)

    @staticmethod
    def fill_rps_ctx(results, ctx):
        logging.info("Start fill_rps_ctx")

        def _get_rate(result, field_name):
            logging.info("Start _get_rate")
            try:
                rate = 0
                count = result.get(field_name, None)
                if count:
                    # reasonable request count order is k*10^5, so round up to 6 digits is OK
                    rate = round(float(count) / int(result['requests']), 6)
            except (ValueError, ZeroDivisionError, KeyError):
                rate = 2  # 200% of errorness in output
                logging.error(
                    ("rate calculation failed: {%s}, and {requests} requests"
                     % field_name).format(**result)
                )
            return rate

        requests_per_sec = []
        fail_rates = []
        notfound_rates = []
        for result in results:
            try:
                rps = float(result['rps'])
            except (ValueError, KeyError):
                rps = 0.0
            fail_rate = _get_rate(result, "service_unavailable")
            notfound_rate = _get_rate(result, "requests_not_found")
            requests_per_sec.append(rps)
            fail_rates.append(fail_rate)
            notfound_rates.append(notfound_rate)
        ctx.results = results
        ctx.num_sessions = len(requests_per_sec)
        ctx.requests_per_sec = requests_per_sec
        ctx.fail_rates = fail_rates
        ctx.notfound_rates = notfound_rates

# coding: utf-8

import logging
import collections

from sandbox import sdk2
from sandbox import common


class TestVaults(sdk2.Task):

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 2048
        disk_space = 15

        class Caches(sdk2.Requirements.Caches):
            pass  # no shared caches

    class Parameters(sdk2.Parameters):
        description = "Test fetching large number of vault records"
        kill_timeout = 180

    def on_execute(self):

        vaults = self.server.vault.read(owner=self.owner, limit=1000).get('items', [])
        logging.info("Total: %d vaults", len(vaults))

        counters = collections.Counter()

        with common.utils.Timer() as timer:
            with sdk2.Vault.batch:
                fs = [sdk2.Vault.data(vault["owner"], vault["name"]) for vault in vaults]

            for future in fs:
                try:
                    future.result()
                    counters["success"] += 1
                except Exception:
                    logging.error("failure", exc_info=True)
                    counters["failure"] += 1

        logging.info("Batch: %s, counters: %s", timer.secs, counters)

        counters = collections.Counter()

        with common.utils.Timer() as timer:
            for vault in vaults:
                try:
                    sdk2.Vault.data(vault["owner"], vault["name"])
                    counters["success"] += 1
                except Exception:
                    counters["failure"] += 1

        logging.info("Non-batch: %s, counters: %s", timer.secs, counters)

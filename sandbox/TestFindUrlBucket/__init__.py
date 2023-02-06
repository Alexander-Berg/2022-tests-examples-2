# -*- coding: utf-8 -*-

import logging

from sandbox.sandboxsdk import parameters

from sandbox.projects.common import utils
from sandbox.projects.common.search import findurl
from sandbox.projects.common.search import bugbanner
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.common import metrics_launch_manager as metrics_launcher


class MaxMissingDocsPerBasket(parameters.SandboxIntegerParameter):
    name = "max_missing_docs_per_basket"
    description = "Max amount of documents to send to FindUrl per query basket"
    default_value = 20


class MaxQueriesPerBasket(parameters.SandboxIntegerParameter):
    name = "max_queries_per_basket"
    description = "Max amount of queries taken from one basket"
    default_value = 50


class RunFindurl(parameters.SandboxBoolParameter):
    name = "run_findurl"
    description = "Manually run queries on betas, then try to FindUrl lost documents"
    sub_fields = {
        "true": [MaxMissingDocsPerBasket.name, MaxQueriesPerBasket.name]
    }
    default_value = False


class MetricsLaunchId(parameters.SandboxStringParameter):
    name = "metrics_launch_id"
    description = "Id of metrics launch to be used"
    default_value = u'aa8286385dc33880015dc47d7a660013'


class RunBisect(parameters.SandboxBoolParameter):
    name = "run_bisect"
    description = "Run bisect"
    default_value = True


class TestFindUrlBucket(bugbanner.BugBannerTask):
    """
        Testing FindUrlBucket. It's now too cumbersome to do it on local SB.
    """

    type = 'TEST_FIND_URL_BUCKET'

    input_parameters = (
        RunFindurl,
        MaxMissingDocsPerBasket,
        MaxQueriesPerBasket,
        MetricsLaunchId,
        RunBisect,
    )
    execution_space = 10 * 1024  # 10G

    def on_enqueue(self):
        pass

    def on_execute(self):
        logging.debug("Starting")
        """
        btws = []
        for query_text, sample_request, doc_position in (
            (
                "vk.com",
                "https://priemka.hamster.yandex.ru/yandsearch?&text=субару%20легаси%202006%20кузов&lr=65&rearr="
                "Personalization_off&no-tests=1&nocache=da&nocache=da&timeout=9999999&waitall=da",
                3,
            ),
            (
                "google.com",
                "https://priemka.hamster.yandex.ru/yandsearch?&text=субару%20легаси%202006%20кузов&lr=65&rearr="
                "Personalization_off&no-tests=1&nocache=da&nocache=da&timeout=9999999&waitall=da",
                7,
            ),
            (
                "barman",
                "https://priemka.hamster.yandex.ru/yandsearch?&text=субару%20легаси%202006%20кузов&lr=65&rearr="
                "Personalization_off&no-tests=1&nocache=da&nocache=da&timeout=9999999&waitall=da",
                4,
            ),
        ):
            host = utils.get_or_default(self.ctx, Host)
            logging.debug("Starting fort query %s", query_text)
            btw = findurl.FindUrl.BisectTaskWrapper(self, host, query_text, sample_request, doc_position)
            btw.run()
            btws.append(btw)
        for btw in btws:
            logging.debug("Final result %s", btw.get_result())
        """

        launcher = metrics_launcher.MetricsLauncher(
            oauth_token=self.get_vault_data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME)
        )
        # l_id = u'aa8286385ccd7db8015ccf197cc10504'
        l_id = utils.get_or_default(self.ctx, MetricsLaunchId)
        logging.debug("Using metrics launch id: %s", l_id)
        metrics_json_response = launcher.get_launch_info(l_id)
        stub_ticket_key = "UPREL-1836"

        if utils.get_or_default(self.ctx, RunFindurl):
            link = findurl.FindUrl().generate_result_site(
                self,
                findurl.FindUrl.compare_searches(
                    metrics_json_response,
                    utils.get_or_default(self.ctx, MaxMissingDocsPerBasket),
                    utils.get_or_default(self.ctx, MaxQueriesPerBasket),
                    run_bisect=utils.get_or_default(self.ctx, RunBisect),
                    current_sandbox_task=self,
                ),
                stub_ticket_key,
            )

            logging.debug(link)


__Task__ = TestFindUrlBucket

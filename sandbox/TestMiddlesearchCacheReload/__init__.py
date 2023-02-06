# -*- coding: utf-8 -*-

import logging
import time

from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk import paths

import sandbox.projects.websearch.middlesearch.resources as ms_resources
from sandbox.projects import resource_types
from sandbox.projects.common.middlesearch.response_patcher import response_patcher
from sandbox.projects.common.middlesearch import single_host
from sandbox.projects.common.base_search_quality import response_saver
from sandbox.projects.common.base_search_quality import response_diff
from sandbox.projects.common.base_search_quality import threadPool
from sandbox.projects.common.base_search_quality import basesearch_response_parser as brp
from sandbox.projects.common.base_search_quality.tree import htmldiff
from sandbox.projects.common import file_utils as fu
from sandbox.projects.common import error_handlers as eh

_RESPONSE_SAVER_PARAMS = response_saver.create_response_saver_params(
    queries_resource=[
        resource_types.PLAIN_TEXT_QUERIES,
        ms_resources.WebMiddlesearchPlainTextQueries,
        resource_types.IMAGES_MIDDLESEARCH_PLAIN_TEXT_REQUESTS,
        resource_types.VIDEO_MIDDLESEARCH_PLAIN_TEXT_REQUESTS,
    ]
)


class WaitTime(sp.SandboxIntegerParameter):
    name = "wait_time_to_invalidate_cache"
    description = 'Wait time to finish invalidation'
    default_value = 5 * 60


class TestMiddlesearchCacheReload(single_host.MiddlesearchSingleHostTask):
    """
        Тестирует обновление кеша (SEARCH-1007)
    """

    type = 'TEST_MIDDLESEARCH_CACHE_RELOAD'

    input_parameters = single_host.PARAMS + _RESPONSE_SAVER_PARAMS.params + threadPool.PARAMS + (WaitTime,)

    def on_enqueue(self):
        single_host.MiddlesearchSingleHostTask.on_enqueue(self)

        self.ctx["queries_id"] = self.create_resource(
            "queries, {}".format(self.descr),
            "queries.txt",
            resource_types.PLAIN_TEXT_QUERIES,
            arch='any',
        ).id

        for n in ["initial", "cached", "reloaded"]:
            self.ctx["{}_responses_id".format(n)] = self.create_resource(
                "{}_responses, {}".format(n, self.descr),
                "{}_responses.txt".format(n),
                resource_types.BASESEARCH_HR_RESPONSES,
                arch='any',
            ).id

    def init_search_component(self, search_component):
        search_component.disable_hybrid_cache()

    def _use_middlesearch_component(self, middlesearch):
        queries_resource = channel.sandbox.get_resource(self.ctx["queries_id"])
        #  исходные ответы
        logging.info("Start getting initial responses")
        start_time = time.time()
        self._get_responses(
            middlesearch, "initial_responses_id",
            patched_queries_resource=queries_resource
        )
        time_of_shooting = time.time() - start_time
        #  ответы, полученные c полным кешом + инвалидация кеша в конце
        logging.info("Start getting cached responses")
        self._get_responses(
            middlesearch, "cached_responses_id",
            on_end_get_responses=_wait_for_invalidate_cache_func(middlesearch, time_of_shooting)
        )
        #  ответы, полученные из кеша после инвалидации
        logging.info("Start getting reloaded responses")
        self._get_responses(middlesearch, "reloaded_responses_id")

        #  сравнение ответов из кеша и ответов после инвалидации (должны совпадать)
        cached_responses = brp.parse_responses(channel.sandbox.get_resource(self.ctx["cached_responses_id"]).path)
        reloaded_responses = brp.parse_responses(channel.sandbox.get_resource(self.ctx["cached_responses_id"]).path)
        diff_list = []
        if not brp.compare_responses(
            cached_responses, reloaded_responses,
            diff_indexes=diff_list,
        ):
            unstable_diff = channel.task.create_resource(
                "Unstable diff", "unstable_diff", resource_types.EXTENDED_INFO
            )
            paths.make_folder(unstable_diff.path)

            response_diff.write_html_diff(
                fu.read_lines(queries_resource.path),
                cached_responses, reloaded_responses,
                htmldiff.ChangedProps(),
                diff_list,
                diff_path=unstable_diff.path,
                use_processes=True,
            )
            eh.check_failed(
                "Wrong cache invalidation!\n"
                "see resource:{} for diff".format(unstable_diff.id)
            )

    def _get_responses(
        self, middlesearch, res_name,
        on_end_get_responses=None,
        patched_queries_resource=None,
    ):
        response_saver.save_responses(
            self.ctx,
            search_component=middlesearch,
            responses_resource=channel.sandbox.get_resource(self.ctx[res_name]),
            response_patchers=[response_patcher],
            on_end_get_responses=on_end_get_responses,
            need_dbgrlv=False,  # иначе не пишет запросы в кеш
            patched_queries_resource=patched_queries_resource,
        )


def _wait_for_invalidate_cache_func(middlesearch, sleep_time):
    def invalidate_and_wait():
        middlesearch.invalidate_cache()
        time.sleep(sleep_time)

    return invalidate_and_wait


__Task__ = TestMiddlesearchCacheReload

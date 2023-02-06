# -*- coding: utf-8 -*-

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.projects.common import utils
from sandbox.projects.common.base_search_quality import settings as bss
from sandbox.projects.common.base_search_quality import cgi_params
from sandbox.projects.common.search import components as sc

import sandbox.common.types.client as ctc


class TestBasesearchCgiParams(SandboxTask):
    """
        Обстреливает базовый поиск всеми возможными комбинациями cgi-параметров
        (их значения выбираются автоматически из макросов в файле
        search/request/treatcgi/treatcgi.cpp) и проверяет,
        что базовый поиск от этого не падает.

        В ответах поиска допускается код ответа HTTP 400 (Bad Request)
        и статус **GotError: YES** в ответе репорта. Таймаутов и прочих
        зависаний быть не должно.
    """
    type = 'TEST_BASESEARCH_CGI_PARAMS'
    client_tags = ctc.Tag.LINUX_PRECISE

    execution_space = bss.RESERVED_SPACE
    required_ram = 61 << 10

    input_parameters = sc.DefaultBasesearchParams.params + cgi_params.PARAMS

    @property
    def footer(self):
        return '<strong>RPS: <span style="color: #007f00;">{}</strong>'.format(self.ctx.get('rps'))

    def on_execute(self):
        basesearch = sc.get_basesearch()
        # stderr verification should be disabled for CGI parameters test
        # as it logs various exceptions there
        basesearch.use_verify_stderr = False

        self.init_search_component(basesearch)

        basesearch.start()
        basesearch.wait()

        def do_work():
            optimized = utils.get_or_default(self.ctx, cgi_params.CgiDiagonalMode)
            cgi_params.test_params(self.ctx, basesearch, optimized=optimized)

        basesearch.use_component(do_work)
        basesearch.stop()

    def init_search_component(self, search_component):
        """
            To be overridden in child tasks
        """
        pass


__Task__ = TestBasesearchCgiParams

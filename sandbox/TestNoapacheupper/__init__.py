# -*- coding: utf-8 -*-

import logging
import socket

import sandbox.common.types.client as ctc

from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.task import SandboxTask

from sandbox.projects import resource_types
from sandbox.projects.common.noapacheupper.request import save_requests
from sandbox.projects.common.noapacheupper.search_component import create_noapacheupper_params
from sandbox.projects.common.noapacheupper.search_component import get_noapacheupper
from sandbox.projects.common.search.requester import format_users_queries_line
from sandbox.projects.common.search.requester import Params as RequesterParams
from sandbox.projects.common.search.requester import Requester
from sandbox.projects.common.search.requester import sequence_binary_data


class Params:
    class ReportUrl(sp.SandboxStringParameter):
        name = 'report_url'
        description = 'Report url (default: https://hamster.yandex.ru/search?)'
        default_value = 'https://hamster.yandex.ru/search?'

    class UsersQueries(sp.LastReleasedResource):
        name = 'users_queries_resource_id'
        description = 'Users queries'
        resource_type = 'USERS_QUERIES'
        default_value = 0

    class AdditionalCgiParams(sp.SandboxStringParameter):
        name = 'additional_cgi_param'
        description = 'Addtional cgi params'
        default_value = ''

    class SeparateBuildRequests(sp.SandboxBoolParameter):
        """
            В случае valgrind-запусков noapache стрелять в него через report
            нельзя (noapache катастрофически слоупочит), поэтому по этой опции
            доступен режим предварительно подготовки запросов
            (лишний прогон, в процессе которого собираем прямые запросы к noapache, -
            вынимаем из eventlog (&dump=eventlog))
        """
        name = 'separate_build_requests'
        description = 'Separate stage for build requests'
        default_value = False

    lst = (
        ReportUrl,
        UsersQueries,
        AdditionalCgiParams,
        SeparateBuildRequests,
    )


class ReportRequester(Requester):
    # наследуемся от requester, чтобы направлять запросы не прямо в используемый компонент, а через report
    def __init__(self, report_url, params):
        super(ReportRequester, self).__init__()
        self.report_url = report_url
        self.params = params
        # получаем наш хост (для использования в параметре srcrwr)
        self.hostname = socket.gethostname()
        logging.info('redirect requests to UPPER:' + self.hostname)
        self.re_try_limit = 6

    def build_request(self, req):
        return self.report_url + format_users_queries_line(req) + \
            "&srcrwr=UPPER:{}:{}&{}".format(self.hostname, self.search_component.port, self.params)


def line_requests_iterator(fname):
    with open(fname) as f:
        for line in f:
            yield line.rstrip('\n')


class TestNoapacheupper(SandboxTask, object):
    """
        !!! DEPRECATED !!!
        Please, contact mvel@ to select correct test for noapacheupper
    """

    type = 'TEST_NOAPACHEUPPER'
    client_tags = ctc.Tag.LINUX_PRECISE  # Limit to precise to avoid GLIBC_2.14 linking bug
    input_parameters = create_noapacheupper_params().params + RequesterParams.lst + Params.lst

    def __init__(self, task_id=0):
        super(TestNoapacheupper, self).__init__(task_id)
        self.ctx['kill_timeout'] = 4 * 60 * 60

    def init_search_component(self, component):
        pass

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        channel.task = self

    def on_execute(self):
        if self.ctx[Params.SeparateBuildRequests.name]:
            common_url = "{}&{}".format(
                self.ctx[Params.ReportUrl.name],
                self.ctx[Params.AdditionalCgiParams.name],
            )
            reqs_fname = 'requests.txt'  # переколдованные запросы к noapache храним во временном файле
            save_requests(
                common_url,
                channel.task.sync_resource(self.ctx[Params.UsersQueries.name]),
                self.ctx[RequesterParams.RequestsLimit.name],
                reqs_fname,
            )
            self.create_resource(self.descr + ' reqs. for noapache', reqs_fname, resource_types.OTHER_RESOURCE)

            def req_iter():
                for data in sequence_binary_data(reqs_fname):
                    yield ('', data)

            rr = Requester()
            search_component = get_noapacheupper()
            self.init_search_component(search_component)  # hook for patching run command (use valgrind, etc...)
            rr.use(
                req_iter(),
                search_component,
                ctx=self.ctx,
            )
        else:
            rr = ReportRequester(
                self.ctx[Params.ReportUrl.name],
                self.ctx[Params.AdditionalCgiParams.name],
            )
            search_component = get_noapacheupper()
            self.init_search_component(search_component)  # hook for patching run command (use valgrind, etc...)
            rr.use(
                line_requests_iterator(channel.task.sync_resource(self.ctx[Params.UsersQueries.name])),
                search_component,
                ctx=self.ctx,
            )

        if rr.error:
            raise SandboxTaskFailureError(rr.error)


__Task__ = TestNoapacheupper

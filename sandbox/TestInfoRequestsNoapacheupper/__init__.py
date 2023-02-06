# -*- coding: utf-8 -*-

import re
import logging

from sandbox.sandboxsdk.errors import SandboxTaskFailureError

from sandbox.projects.common.noapacheupper.instance import Noapacheupper
from sandbox.projects.common.noapacheupper.search_component import create_noapacheupper_params
from sandbox.projects.common.noapacheupper.search_component import get_noapacheupper
from sandbox.projects.common.search.requester import Requester


class InfoRequester(Requester):
    def __init__(self):
        super(InfoRequester, self).__init__()
        self.info_errors = []
        self.info_requests = (
            ('/yandsearch?info=getconfig', self.on_getconfig),
            ('/yandsearch?info=checkconfig:read-only:1;deep:0', self.on_checkonfig),
            ('/yandsearch?info=sandboxtaskid', self.on_sandboxtaskid),
            ('/yandsearch?info=getrearrangeversion', self.on_getrearrangeversion),
        )
        # строим index handler-ов
        self.handlers_index = {}
        idx = 0
        for tp in self.info_requests:
            self.handlers_index[idx] = tp[1]
            idx += 1

    def use(self, search_component):
        requests_iterator = [tp[0] for tp in self.info_requests]
        super(InfoRequester, self).use(
            requests_iterator,
            search_component,
            process_count=1,
        )

    def use_component(self, search_component):
        search_component.check_simple_reqs()
        super(InfoRequester, self).use_component(search_component)

    def on_response(self, nreq, result):
        logging.debug('request[{}]: {}\nresult: {}'.format(nreq, self.in_fly[nreq], result))
        self.handlers_index[nreq](self.in_fly[nreq], result)
        super(InfoRequester, self).on_response(nreq, result)

    def on_getconfig(self, req, resp):
        required_lines = (
            '^ *MultiContextThreads +[1-9]+',
            '^ *MaxMultiContexQueueSize +[1-9]+',
        )
        req_re = {}
        for r in required_lines:
            req_re[r] = re.compile(r)
        for line in resp.split('\n'):
            for r, rm in req_re.iteritems():
                if rm.search(line) is not None:
                    del req_re[r]
                    break
        if len(req_re):
            require_re = ','.join(req_re)
            self.info_errors.append("for request {} in response not found regexps '{}' in :\n{}".format(req, require_re, resp))

    def on_checkonfig(self, req, resp):
        required_props = {
            'upper-linux-bin-md5',
            'upper-cfg-md5',
            'upper-rearrange-md5',
            'upper-path-revision'
        }
        for line in resp.split('\n'):
            for rp in required_props:
                if rp in line:
                    required_props.remove(rp)
                    break
        if len(required_props):
            props = ','.join(required_props)
            self.info_errors.append("for request {} in response not found required props '{}' in :\n{}".format(req, props, resp))

    def on_sandboxtaskid(self, req, resp):
        try:
            int(resp.rstrip('\n'))
        except Exception:
            self.info_errors.append("can not get sandbox task id for request {} in response:\n{}".format(req, resp))

    def on_getrearrangeversion(self, req, resp):
        required_info = {
            'RearrangeData:',
            'RearrangeDynamicData:',
        }
        for line in resp.split('\n'):
            for info in required_info:
                if line == info:
                    required_info.discard(info)
                    break
        if required_info:
            self.info_errors.append("can not find required info {} for request {} in response:\n{}".format(str(required_info), req, resp))


class TestInfoRequestsNoapacheupper(Noapacheupper):
    """
        Проверяем ответы noapache на info-запросы
    """
    type = 'TEST_INFO_REQUESTS_NOAPACHEUPPER'
    input_parameters = create_noapacheupper_params().params
    execution_space = 10 * 1024  # 10 Gb, Max usage is near 8 Gb

    def __init__(self, task_id=0):
        super(TestInfoRequestsNoapacheupper, self).__init__(task_id)
        self.ctx['kill_timeout'] = 1 * 60 * 60

    @staticmethod
    def get_input_parameters():
        params = create_noapacheupper_params().params
        return params

    def on_execute(self):
        search_component = get_noapacheupper()
        self.init_search_component(search_component)
        rr = InfoRequester()
        rr.use(search_component)
        # если обнаружили проблему(ы), фейлим таск
        if rr.info_errors:
            raise SandboxTaskFailureError(rr.info_errors)


__Task__ = TestInfoRequestsNoapacheupper

# -*- coding: utf-8 -*-

import logging
import json
import socket

from sandbox.projects.common.search.requester import Requester
from sandbox.projects.common.search.requester import format_users_queries_line

import methods


class ReportRequester(Requester):
    # наследуемся от requester, чтобы направлять запросы не прямо в используемый компонент, а через report
    def __init__(self, report_url, params, method_name, resource, method_arguments=''):
        super(ReportRequester, self).__init__()
        self.report_url = report_url
        self.params = params
        self.method = vars(methods)[method_name]
        self.method_arguments = method_arguments

        # Приклеиваем к запросу выхлоп и сохраняем в resource
        self.resource = resource

        # получаем наш хост (для использования в параметре srcrwr)
        self.hostname = socket.gethostname()
        logging.info('redirect requests to UPPER:' + self.hostname)
        self.re_try_limit = 6

    def build_request(self, req):
        return self.report_url + format_users_queries_line(req) + \
            "&srcrwr=UPPER:{}:{}&{}".format(self.hostname, self.search_component.get_port(), self.params)

    def on_response(self, nreq, resultJson):
        try:
            result = json.loads(resultJson)
            args = self.method_arguments
            output = self.method(result, args) if args else self.method(result)
            logging.debug('result[%s]: %s', nreq, output)
            self.resource[self.in_fly[nreq]] = output
            self.responses_counter += 1
        except ValueError:
            # it maybe cause of hamster
            logging.warning("json.load except ValueError, json is bad")
        del self.in_fly[nreq]


def line_requests_iterator(fname):
    with open(fname) as f:
        for line in f:
            yield line.rstrip('\n')

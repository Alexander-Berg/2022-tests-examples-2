# -*- coding: utf-8 -*-
"""
Загрузка в testing графов
Я.Здоровья (ya_health, ya_health_external)
из вертикали SHARED

Предпологается покоммитный запуск.
api загрузки добавляет testing_info в передаваемые данные.
В testing_info хранится информация о переопределении источников
и конфигурация, которая используется для resolving'a бэкендов

Предполагается, что задачка будет брать эти параметры прямиком из описания графа.
Это допустимо, т.к. конфиг графа - json и дополнительные поля допускаются
(информация из чата apphost-support)

Формат testing_info не задокументарован и выявлен с помощью консоли разработчика
Обновление графа: PUT https://apphost.n.yandex-team.ru/v1/graph/testing/SHARED::ya_health
"testing_info": {
    "collection": "production",
    "config": "SAS_SHARED_APP_HOST_HAMSTER",
    "srcrwr": {
      "YA_HEALTH_SAAS": "SHARED::YA_HEALTH_SAAS::"
    }
  }
"""

import json
import logging

import requests

import sandbox.common.errors
from sandbox import sdk2


class AppHostUploadGraphApi(object):
    BASE_URL = 'https://apphost.n.yandex-team.ru/v1/graph/testing'

    @classmethod
    def upload_graph_to_testing(cls, graph, vertical, testing_info):
        cls.validate_testing_info(testing_info)

        graph_name = graph['name']

        url = '{base_url}/{vertical}::{graph_name}'.format(
            base_url=cls.BASE_URL,
            vertical=vertical,
            graph_name=graph_name
        )

        request_payload = {
            'content': graph,
            'testing_info': testing_info
        }

        info_message = (
            'Trying to upload graph {graph_name} to testing of '
            'vertical {vertical} with testing_info {testing_info}'
        ).format(
            graph_name=graph_name,
            vertical=vertical,
            testing_info=testing_info
        )

        logging.info(info_message)
        logging.info('Request payload is: {}'.format(request_payload))
        r = requests.put(url, json=request_payload)
        if r.ok:
            logging.info('Upload graph - success')
        else:
            error_message = (
                'Failed to upload graph {graph_name} to testing '
                'of vertical {vertical} with response: {response}'
            ).format(
                graph_name=graph_name,
                vertical=vertical,
                response=r.content
            )
            raise sandbox.common.errors.TaskFailure(error_message)

    @classmethod
    def validate_testing_info(cls, testing_info):
        ok = (
            type(testing_info) is dict
            and 'config' in testing_info
            and 'collection' in testing_info
            and type(testing_info.get('srcrwr', {})) is dict
        )
        if not ok:
            raise sandbox.common.errors.TaskFailure(
                'Bad testing_info in graph. '
                'Please, specify correct testing_info. More details in task sources'
            )


class YaHealthUpdateTestingGraphs(sdk2.Task):
    class Parameters(sdk2.Parameters):
        revision = sdk2.parameters.String('Svn revision', required=True)

    def on_execute(self):
        graphs_folder = 'web/app_host/conf/graph_generator/vertical/SHARED'

        # todo maybe: we also can make them a params and make
        # todo: task more universal and usable in other verticals / graphs
        graph_arc_paths = [
            sdk2.svn.Arcadia.trunk_url(
                '{}/ya_health.json'.format(graphs_folder),
                revision=self.Parameters.revision
            ),
            sdk2.svn.Arcadia.trunk_url(
                '{}/ya_health_external.json'.format(graphs_folder),
                revision=self.Parameters.revision
            ),
        ]

        for graph_path in graph_arc_paths:
            self.upload_graph_to_testing(graph_path)

    @staticmethod
    def upload_graph_to_testing(graph_path):
        # type: (str) -> None
        graph_str = sdk2.svn.Arcadia.cat(graph_path)
        graph = json.loads(graph_str)
        logging.info('Got graph: {}'.format(graph_str))

        if 'testing_info' not in graph:
            raise sandbox.common.errors.TaskFailure(
                "Must specify testing_info in graph description. "
                "More details about format - in task code"
            )

        AppHostUploadGraphApi.upload_graph_to_testing(
            graph,
            'SHARED',
            graph['testing_info']
        )

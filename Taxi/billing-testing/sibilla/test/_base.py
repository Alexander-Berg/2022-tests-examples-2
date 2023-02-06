import copy

from sibilla import configuration
from sibilla import processing
from sibilla import query
from sibilla import utils
from sibilla.test import context
from sibilla.test import request


def create_query_sequence(query_template, storage: processing.Storage):
    """
    Из шаблона запроса и набора данных генерируем
    последовательность реальных запросов
    :param query_template:
    :param storage:
    :return:
    """
    if 'actual' in query_template:
        source = processing.Source(query_template['actual'], storage)
    else:
        source = processing.Source(query_template, storage)
    for response_data in source:
        yield request.Query(
            expected=query_template['expected']
            if 'expected' in query_template
            else None,
            **response_data,
        )


class BaseTest:
    def __init__(self, ctx: context.ContextData, name: str, **options):
        self._context = ctx
        self._options = options
        self._options['name'] = name
        self.wait: configuration.WaitSettings = configuration.WaitSettings(
            **self._options.get('wait', {}),
        )

    async def get_result(self, headers: dict, query_data: request.Query):
        raise Exception('Not implemented yet')

    def queries(self):
        for raw_body in query.load(self._options['query']):
            yield from create_query_sequence(raw_body, self._context.container)

    def __getattr__(self, item):
        return self._options.get(item)

    @property
    def result(self):
        return self._options.get('result')

    @property
    def name(self):
        return self._options['name']

    @property
    def headers(self):
        return self._options.get('headers', [])

    @property
    def url(self):
        return utils.prepare_url(self._options['url'])

    @property
    def method(self):
        return self._options['method'] if 'method' in self._options else 'post'

    @property
    def dump(self):
        """
        Return base test configuration
        :return:
        """
        return copy.deepcopy(self._options)

    @property
    def tvm_name(self):
        return self._options.get('tvm_name')

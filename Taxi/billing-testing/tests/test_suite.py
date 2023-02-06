# coding: utf8

from sibilla import processing
from sibilla import test


class ContextData:
    def __init__(self):
        self.container = processing.Storage()


def test_query_generator():
    test_data = {
        'name': 'name',
        'query': [{'json': {'data': 'test'}}],
        'result': {'status': 200, 'json': '@json'},
        'url': 'https://example.com',
    }
    test_obj = test.Test(ctx=ContextData(), **test_data)
    for query_res in test_obj.queries():
        assert query_res['json'] == test_data['query'][0]['json']

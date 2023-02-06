# -*- coding: utf-8 -*-
import logging
import os
import sys
import allure
import pytest
import common.env
from common.schema import get_schema_validator, validate_schema
from utils.yaml_parser import get_params
from utils.client import *
from utils.check_result import SmartCheck


logger = logging.getLogger(__name__)

CURRENT_PATH = ''
CURRENT_PASSED = 0
CURRENT_TOTAL = 0
PASSED_TESTS = []


def teardown_module():
    PASSED_TESTS.append(Passed_Test(CURRENT_PATH, CURRENT_PASSED, CURRENT_TOTAL))
    print('\n')
    print('PASSED TESTS')
    for items in PASSED_TESTS:
        print(items)

#для получения параметров и их нумерования
def params():
    return get_params(common.env.get_tests_path())


@pytest.fixture(scope='module')
def clear_globals():
    global CURRENT_TOTAL
    global CURRENT_PATH
    CURRENT_PATH = ''
    CURRENT_TOTAL = 0


def param_id(param):
    global CURRENT_TOTAL
    global CURRENT_PATH
    if param['config']['test_path'] != CURRENT_PATH:
        CURRENT_PATH = param['config']['test_path']
        CURRENT_TOTAL = 0
    else:
        CURRENT_TOTAL += 1
    return "params[{}] from {}".format(CURRENT_TOTAL, param['config']['test_path'])


#точка входа
@allure.feature('function_test_yaml')
@pytest.mark.parametrize('params', params(), ids=param_id)
def test_response(params, clear_globals):
    global CURRENT_PASSED
    global CURRENT_TOTAL
    #проверяем, что парсилка сработала как надо было
    check_params(params)
    config, get_params, result, schema, exception, meta = _parse_params(params)
    check_current_path(config['test_path'])
    CURRENT_TOTAL += 1
    client = choose_client(config)
    req = client.prepare_request(get_params)
    exceptions = []
    for i in range(common.env.retry_count() + 1): 
        response = client.send(req)
        headers = dict(response.headers)
        headers = dict((k.lower(), v) for k, v in headers.items())
        assert response, "Can't get response in {}".format(config['test_path'])
        if 'get_headers_only' in config and config['get_headers_only']:
            response = {}
        else:
            response = client.get_json(response)
        response['HEADERS'] = headers
        checker = SmartCheck(response, result, get_params, config['test_path'], schema, exception)
        try:
            checker.check()
            checker.check_schema()
            checker.raise_missed_exception()
            CURRENT_PASSED += 1
            break
        except Exception as e:
            if not checker.check_exception(e, exceptions):
                exceptions.append(e)
    if len(exceptions) == (common.env.retry_count() + 1):
        if 'xfail' in meta and meta['xfail']:
            pytest.xfail(reason='fail expected')
        pytest.fail(exceptions[-1])

def check_params(params):
    #тут обработка случая, когда пытаются запустить тест с неправильным названием
    if params == 'E':
        sys.exit()
    #тут проверяем, распарсился ли тест
    assert 'broken_test_marker' not in params, 'Something wrong with yaml file {}\nErrorText: {}'.format(params['test_path'], params['text'])
    #проверяем наличие блока meta с номером таска и описанием теста
    assert 'meta' in params, 'Block "meta" not found in {}'.format(params['config']['test_path'])
    assert 'task' in params['meta'], 'Field "task" not found in block "meta" in {}'.format(params['config']['test_path'])
    assert 'desc' in params['meta'], 'Field "desc" not found in block "meta" in {}'.format(params['config']['test_path'])


#парсилка для параметров, при добавлении нового блока в ямле, идти сюда
def _parse_params(params):
    config = params['config']
    meta = params['meta']
    if 'get_params' in params:
        get_params = params['get_params']
    else:
        get_params = {}
    if 'result' in params:
        result = params['result']
    else:
        result = None
    if 'schema' in params:
        schema = params['schema']
    else:
        schema = None

    exception = params.get('exception')
    return config, get_params, result, schema, exception, meta


def check_current_path(test_path):
    global CURRENT_PATH 
    global CURRENT_PASSED
    global CURRENT_TOTAL
    global PASSED_TESTS 
    if test_path != CURRENT_PATH:
        if CURRENT_PATH != '':
            PASSED_TESTS.append(Passed_Test(CURRENT_PATH, CURRENT_PASSED, CURRENT_TOTAL))
        CURRENT_PATH = test_path
        CURRENT_TOTAL = 0
        CURRENT_PASSED = 0


class Passed_Test():
    def __init__(self, path, passed, total):
        self.path = path
        self.passed = passed
        self.total = total
    

    def __str__(self):
        length = len(self.path) + len(str(self.passed)) + 1 + len(str(self.total)) + 1 + len('PASSED') + 2
        length = 110 - length
        return self.path + '.' * length + str(self.passed) + '/' + str(self.total) + ' PASSED'

# coding: utf8

import abc
import copy
import json
import logging
import os
import pprint

from sibilla import storage
from sibilla import utils

logger = logging.getLogger(__name__)

EVENT_TEST_START = 0  # testcase started
EVENT_TEST_COMPLETE = 1  # All tests in testcase are finished
EVENT_TEST_RESULT_SUCCESS = 2  # Test finished with expected result
EVENT_TEST_RESULT_FAIL = 3  # Test execution failed for some reason
EVENT_TEST_RESULT_ERROR = 4  # Test finished but with UNexpected result
EVENT_SUITE_START = 5  # testsuite execution started
EVENT_SUITE_FINISH = 6  # testsuite execution finished
EVENT_SUITE_RESULT_FAIL = 7  # testsuite failed
EVENT_SUITE_RESULT_SUCCESS = 8  # testsuite finished and all tests are OK

# EXECUTION SEQUENCE:
#   EVENT_SUITE_START
#     EVENT_TEST_START (set of)
#       EVENT_TEST_RESULT_(SUCCESS|FAIL|ERROR) (set of)
#     EVENT_TEST_COMPLETE
#   EVENT_SUITE_FINISH


class EventCollector(abc.ABC):
    def __init__(self):
        self.__loggers = []

    def add(self, event_handler: 'EventCollector'):
        self.__loggers.append(event_handler)

    async def log(self, event: int, *args, **kwargs):
        for loggers in self.__loggers:
            await loggers.log(event, *args, **kwargs)
        await self._append(event, args, kwargs)

    async def _append(self, event: int, args, kwargs):
        pass


class EventToScreen(EventCollector):
    def __init__(self):
        super().__init__()
        print('Start tests')
        self.__last_name = None
        self.__stat = {}
        self.__errors = []

    async def _append(self, event: int, args, kwargs):
        if event == EVENT_SUITE_START:
            print(
                'Start {name}\nSuite description: {description}'.format(
                    **kwargs,
                ),
            )
        elif event == EVENT_TEST_START:
            self.__stat[kwargs['name']] = {'ok': 0, 'error': 0, 'fail': 0}
            self.__last_name = kwargs['name']
            print('\n', end='')
        elif event == EVENT_TEST_RESULT_SUCCESS:
            name = kwargs['name']
            self.__stat[name]['ok'] += 1
        elif event == EVENT_TEST_RESULT_ERROR:
            name = kwargs['name']
            self.__stat[name]['error'] += 1
            self.__errors.append(
                {
                    'name': kwargs['name'],
                    'result': kwargs['result'],
                    'query': kwargs['query'],
                },
            )
        elif event == EVENT_TEST_RESULT_FAIL:
            name = kwargs['name']
            self.__stat[name]['fail'] += 1
        if event in [
                EVENT_TEST_RESULT_FAIL,
                EVENT_TEST_RESULT_ERROR,
                EVENT_TEST_RESULT_SUCCESS,
        ]:
            name = kwargs['name']
            print(
                '{name} - passed: {ok}, error: {error}, fail: {fail}'.format(
                    name=name,
                    ok=self.__stat[name]['ok'],
                    error=self.__stat[name]['error'],
                    fail=self.__stat[name]['fail'],
                ),
                end='\r',
            )
        if event in [EVENT_SUITE_FINISH]:
            print('\n', end='')
            if self.__errors:
                pprint.pprint(self.__errors)


class EventToFile(EventCollector):
    def __init__(self, save_path, glob: dict = None):
        super().__init__()
        self.__save_path = save_path
        self.__test_idx = 0
        self.__last_name = None
        self.__stat: dict = {}
        self.__current_dump: dict = {}
        self.__glob = glob or {}

    async def _append(self, event: int, args, kwargs):
        if event == EVENT_TEST_START:
            name = kwargs['name']
            test_body = kwargs['dump']
            if 'dump' in test_body:
                if 'result' in test_body:
                    del test_body['result']
                test_body['query'] = []
            self.__current_dump[name] = test_body
        elif event == EVENT_TEST_COMPLETE:
            self.__dump_test(kwargs['name'])
        elif event == EVENT_TEST_RESULT_SUCCESS:
            name = kwargs['name']
            response = kwargs['result']
            if 'dump' in self.__current_dump[name]:
                data = {
                    'actual': {
                        'json': copy.deepcopy(kwargs['query']['json']),
                        'data': copy.deepcopy(kwargs['query']['data']),
                    },
                    'expected': utils.build(
                        self.__current_dump[name]['dump']['response'],
                        response,
                        self.__glob,
                    ),
                }
                self.__current_dump[name]['query'].append(data)

    def __dump_test(self, name):
        logger.info('Prepare to save testsuite\'s bootstrap data: %s', name)
        if name in self.__current_dump is not None:
            dump = self.__current_dump[name]
            if 'dump' in dump:
                del dump['dump']
            logger.info('Save test %s', name)
            self.__test_idx = 0
            file_name = dump['name']
            fdesc = open(os.path.join(self.__save_path, file_name), 'w')
            json.dump(dump, fdesc, indent=4, sort_keys=True)
            del self.__current_dump[name]
        else:
            logger.critical('Test %s does not contain success tests', name)


class EventToStorage(EventCollector):
    def __init__(self, stg: storage.Storage):
        super().__init__()
        self.__stg = stg

    async def _append(self, event: int, args, kwargs):
        if event == EVENT_SUITE_START:
            self.__stg.start_session(
                name=kwargs['name'], description=kwargs['description'],
            )
        elif event == EVENT_TEST_START:
            self.__stg.start_testcase(name=kwargs.get('name', 'FIXME'))
        elif event == EVENT_TEST_RESULT_SUCCESS:
            expected = kwargs.get('expected', kwargs['query'].expected)
            self.__stg.add(
                request=kwargs['query']['json'],
                expected=expected,
                response=kwargs['result'],
                exc_info='',
                outcome=storage.Outcome.PASSED,
            )
        elif event == EVENT_TEST_RESULT_ERROR:
            expected = kwargs.get('expected', kwargs['query'].expected)
            self.__stg.add(
                request=kwargs['query']['json'],
                expected=expected,
                response=kwargs['result'],
                exc_info='',
                outcome=storage.Outcome.FAILED,
            )
        elif event == EVENT_TEST_RESULT_FAIL:
            expected = kwargs.get('expected', kwargs['query'].expected)
            self.__stg.add(
                request=kwargs['query']['json'],
                expected=expected,
                response={},
                exc_info=kwargs['error'],
                outcome=storage.Outcome.ERROR,
            )
        elif event == EVENT_TEST_COMPLETE:
            self.__stg.finish_session()

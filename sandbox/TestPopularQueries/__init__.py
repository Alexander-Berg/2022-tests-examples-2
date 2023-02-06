# -*- coding: utf-8 -*-

import os
import requests
import time
import json
from datetime import datetime

from sandbox import sdk2
from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk import process
from sandbox.common import errors

from sandbox.projects.common import decorators
from sandbox.projects.websearch.upper.fast_data.ExecutionTimeTracker import ExecutionTimeTracker

YT_PROXY = 'hahn.yt.yandex.net'
SCRAPER_OVER_YT_API = 'http://soyproxy.yandex.net/hahn/soy_api'
SOY_SUCCESS = ['completed']
SOY_RUNNING = ['running']
SOY_QUEUED = ['queued', 'resolving_resources']
SOY_GOOD = SOY_SUCCESS + SOY_RUNNING + SOY_QUEUED
OPERATION_ID_PREFIX = 'noapache-fast-data-test'
FETCH_TIMEOUT = 2000


def parse_time(time_str):
    return datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')


def modification_time(node):
    return parse_time(node.attributes['modification_time'])


class TestPopularQueries(ExecutionTimeTracker):
    """
        Прокачивает через сервис подготовленные запросы.
    """

    class Requirements(sdk2.Task.Requirements):
        environments = [
            environments.PipEnvironment('yandex-yt'),
            environments.PipEnvironment('yandex-yt-yson-bindings-skynet'),
        ]

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 1800
        soy_input_table = sdk2.parameters.String(
            'SoY input table',
            default='//home/search-runtime/smorivan/last_prepared/soy_noapache_fast_data',
            required=True,
        )
        output_dir = sdk2.parameters.String(
            'Output dir',
            default='//home/search-runtime/smorivan/output',
            required=True,
        )
        error_dir = sdk2.parameters.String(
            'Parse error dir',
            default='//home/search-runtime/smorivan/output_err',
            required=True,
        )
        keep_last_n = sdk2.parameters.Integer(
            'Number of test results to keep',
            default=100,
            required=True,
        )
        min_values = sdk2.parameters.Dict(
            'Minimal allowed feature values',
            default={
                'has_direct': 0.4,
                'has_docs': 0.99,
                'has_enough_docs': 0.99,
            },
            required=True,
        )
        max_fail_rate = sdk2.parameters.Float(
            'Maximal amount of failed requests',
            default=0.01,
            required=True,
        )
        queue_timeout = sdk2.parameters.Integer(
            'Maximal time in queue',
            default=300,
        )
        yt_pool = sdk2.parameters.String(
            'YT pool',
            default='upper_web_priemka',
            required=True,
        )
        yt_token_name = sdk2.parameters.String(
            'YT token name',
            default='yt_token',
            required=True,
        )

    class Context(ExecutionTimeTracker.Context):
        operation_id = None

    @property
    def stage_name(self):
        return 'test_popular_queries'

    def on_execute(self):
        self._create_operation()
        operation_result = self._wait_for_operation(self.Context.operation_id)
        self.Context.soy_output_table = operation_result['output_path']
        self.Context.soy_error_table = operation_result['error_path']
        self.set_info(
            'Soy output table: <a href="https://yt.yandex-team.ru/hahn/navigation?path={}">link</a>'.format(
                self.Context.soy_output_table
            ), do_escape=False
        )
        self.set_info('Parse results')
        environment = os.environ.copy()
        environment['YT_PROXY'] = YT_PROXY
        environment['YT_TOKEN'] = sdk2.Vault.data(self.Parameters.yt_token_name)
        feature_parser = os.path.join(os.path.dirname(__file__), 'parse_results.py')
        process.run_process(
            cmd=[
                '/skynet/python/bin/python',
                feature_parser,
                '--input-path', self.Context.soy_output_table,
                '--output-dir', self.Parameters.output_dir,
                '--error-dir', self.Parameters.error_dir,
                '--table-name', self.Context.operation_id,
            ],
            log_prefix='parser',
            wait=True,
            check=True,
            environment=environment,
        )
        self.set_info(
            'Output table: <a href="https://yt.yandex-team.ru/hahn/navigation?path={}/{}">link</a>'.format(
                self.Parameters.output_dir, self.Context.operation_id,
            ), do_escape=False
        )
        self.set_info(
            'Error table: <a href="https://yt.yandex-team.ru/hahn/navigation?path={}/{}">link</a>'.format(
                self.Parameters.error_dir, self.Context.operation_id,
            ), do_escape=False
        )
        self.set_info('Check feature values')
        self.Context.output_table = '{}/{}'.format(self.Parameters.output_dir, self.Context.operation_id)
        self.Context.error_table = '{}/{}'.format(self.Parameters.error_dir, self.Context.operation_id)
        self._remove_old()
        self._check_results(self.Context.output_table, [self.Context.soy_error_table, self.Context.error_table])

    def on_break(self, prev_status, status):
        if self.Context.operation_id:
            self._request_retry(
                'DELETE',
                '{}/abort?id={}'.format(SCRAPER_OVER_YT_API, self.Context.operation_id),
            )
            self.set_info('Operation {} aborted'.format(self.Context.operation_id))

    def _create_operation(self):
        self.Context.operation_id = '{}-{}'.format(OPERATION_ID_PREFIX, self.id)
        self.Context.save()
        operation_params = {
            'input_table': self.Parameters.soy_input_table,
            'pool': self.Parameters.yt_pool,
            'id': self.Context.operation_id,
            'fetch_timeout': 2000,
        }
        self._request_retry(
            'POST',
            '{}/create'.format(SCRAPER_OVER_YT_API),
            data=json.dumps(operation_params),
        )
        self.set_info('Operation successfully created')
        self.set_info(
            'Check operation status: <a href="{}/status?id={}">link</a>'.format(
                SCRAPER_OVER_YT_API,
                self.Context.operation_id,
            ), do_escape=False,
        )
        return self.Context.operation_id

    def _wait_for_operation(self, operation_id):
        start = time.time()
        while True:
            response = self._request_retry(
                'GET',
                '{}/status?id={}'.format(SCRAPER_OVER_YT_API, operation_id),
                check_operation_status=True,
            )
            operation_status = response['operation_status']
            if operation_status in SOY_SUCCESS:
                break
            elif operation_status in SOY_QUEUED:
                if time.time() - start > self.Parameters.queue_timeout:
                    raise errors.TaskFailure('Operation queue timeout')
            self.set_info('Operation status: {}'.format(operation_status))
            time.sleep(15)
        self.set_info('Operation completed')
        end = time.time()
        self.set_info('Execution time: {}'.format(end-start))
        return response

    def _remove_old(self):
        if self.Parameters.keep_last_n < 1:
            return
        from yt import wrapper as yw
        client = yw.YtClient(proxy=YT_PROXY, token=sdk2.Vault.data(self.Parameters.yt_token_name))
        output_tables = client.list(self.Parameters.output_dir, absolute=True, attributes=['locks', 'modification_time'])
        error_tables = client.list(self.Parameters.error_dir, absolute=True, attributes=['locks', 'modification_time'])
        output_tables = filter(lambda node: not node.attributes['locks'], output_tables)
        error_tables = filter(lambda node: not node.attributes['locks'], error_tables)
        output_tables.sort(key=modification_time)
        error_tables.sort(key=modification_time)
        for table in error_tables[:-self.Parameters.keep_last_n] + output_tables[:-self.Parameters.keep_last_n]:
            client.remove(table)

    def _check_results(self, result_path, error_paths):
        from yt import wrapper as yw
        client = yw.YtClient(proxy=YT_PROXY, token=sdk2.Vault.data(self.Parameters.yt_token_name))
        fail_rate = sum(client.row_count(path) for path in error_paths)/float(client.row_count(self.Parameters.soy_input_table))
        self.set_info('Fail rate: {:.3g}'.format(fail_rate))
        if fail_rate > self.Parameters.max_fail_rate:
            raise errors.TaskFailure('Fail rate is too high')
        result_table = client.read_table(result_path)
        sums = {}
        nums = {}
        for row in result_table:
            for key, value in row.items():
                if isinstance(value, str):
                    continue
                nums[key] = nums.get(key, 0) + 1
                sums[key] = sums.get(key, 0) + value
        averages = {key: float(sums[key])/nums[key] for key in sums}
        self.set_info('Average values:')
        failures = []
        for key, value in sorted(averages.items()):
            self.set_info('{}: {:.3g}'.format(key, value))
            if value < float(self.Parameters.min_values.get(key, value)):
                failures.append(key)
        if failures:
            raise errors.TaskFailure('\n'.join(['Failed checks:'] + [
                '{}: {}, required: {}'.format(key, averages[key], self.Parameters.min_values[key])
                for key in failures]))

    @decorators.retries(20, delay=3, backoff=1)
    def _request_retry(self, method, url, check_operation_status=False, **kwargs):
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        response_json = response.json()
        if response_json['status'] != 'ok' or \
                check_operation_status and response_json['operation_status'] not in SOY_GOOD:
            raise errors.TaskFailure('Operation failed with response: {}'.format(response_json))
        return response_json

#!/usr/bin/env python
# coding=utf-8           # -*- coding: utf-8 -*-

import json
import logging
from random import randint
import requests
import time

from sandbox import sdk2
import sandbox.common.types.task as ctt
import sandbox.common.types.notification as ctn
from sandbox.projects.common import task_env
from sandbox import common


def get_task(task_ticket):
    response = requests.get("http://ab.yandex-team.ru/api/task/{}".format(task_ticket))
    if response.status_code == 200:
        return response.json()
    else:
        print("Error while getting ticket: {0}, code: {1}, body: {2}", task_ticket, response.status_code, response.text)
        return {}


def get_regions(json_content):
    restrictions = json_content.get('restrictions')
    if restrictions:
        regions = restrictions.get('regions')
        if regions:
            return regions.split(',')
    return []

russia = u'225'


def check_country(regions_list, country):
    if u'' in regions_list:
        regions_list.remove(u'')
    # remove Earth (10000) as its redundant
    if u'10000' in regions_list:
        regions_list.remove(u'10000')
    return len(regions_list) == 0 or country in regions_list and ((u'-' + country) not in regions_list)


def need_shoot_on_russia(regions_list):
    return check_country(regions_list, russia)


class ActionsOutput:
    def __init__(self, raw_result):
        self.result = raw_result.json()

    # ActionsOutput
    def finished(self):
        return 'result_status_initialized' in self.result

    def failed(self):
        return 'result_status_failed' in self.result

    def get_id(self, id):
        if id is not None:
            return id
        if 'id' in self.result:
            return self.result['id']
        return None

    def get_result(self):
        return self.result

    def has_offset(self):
        return 'offset' in self.result

    def get_offset(self):
        return self.result.get('offset', 0)

    def get_tests(self):
        if 'meta-info' in self.result and 'test-results' in self.result['meta-info']:
            return self.result['meta-info']['test-results']
        return []

    # PopTaskOutput
    def has_error(self):
        return 'error' in self.result

    def pretty_print_error(self):
        logging.error(json.dumps(self.result, indent=4, sort_keys=True))
        if 'stackTrace' in self.result['error']:
            logging.error(self.result['error']['stackTrace'])
        elif 'message' in self.result['error']:
            logging.error(self.result['error']['message'])

    def has_task(self):
        return 'slots' in self.result or 'images' in self.result or 'tasks' in self.result

    def have_more(self):
        return 'haveMore' in self.result and self.result['haveMore']

    # WebhookRequestOutput
    def has_message(self):
        return 'message' in self.result

    def get_message(self):
        return self.result['message']

    def is_success(self):
        return self.result['success']


class ShooterClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.host_api = 'http://' + host + ':' + str(port)
        self.host_api_v1 = self.host_api + '/api-v1/'
        self.raw_result = None
        self.headers = {'Content-type': 'application/json'}
        self.actions_output = None
        self.log_level = 4
        self.last_saved_exception = None

    def print_raw_request(self):
        if self.raw_result is not None:
            logging.info(self.raw_result.content)

    def view_task_url(self, id):
        return self.host_api_v1 + "view-task?id={}".format(id)

    def actions_url(self, id):
        return self.host_api_v1 + "view-actions?id={}".format(id)

    def reports_url(self, id):
        return self.host_api + "/reports/" + id

    def post_impl(self, handler, data):
        return requests.post(self.host_api_v1 + handler, data=json.dumps(data), headers=self.headers)

    def post_with_retry(self, handler, data):
        raw_result = None
        for x in range(0, 20):
            try:
                self.last_saved_exception = None
                raw_result = self.post_impl(handler, data)
                if not raw_result.content.startswith('Backend timeout') and not raw_result.content.startswith('Backend unavailable'):
                    break
            except Exception as e:
                self.last_saved_exception = e
                pass
            time.sleep(x + 1)
        return raw_result

    def get_raw_result_or_raise_last_exception(self):
        if self.last_saved_exception is not None:
            raise self.last_saved_exception
        else:
            return self.raw_result

    def post(self, handler, data):
        self.raw_result = self.post_impl(handler, data)
        self.actions_output = ActionsOutput(self.raw_result)

    def post_and_print(self, handler, data, print_on_success=True, request_id=None):
        data["requestId"] = request_id or str(int(time.time() * 1000)) + "_" + str(randint(100000000, 999999999))
        try:
            self.raw_result = self.post_with_retry(handler, data)
            self.actions_output = ActionsOutput(self.get_raw_result_or_raise_last_exception())
        except:
            self.print_raw_request()
            raise
        if print_on_success:
            self.print_raw_request()

    def check_actions(self, id):
        data = {
            'id': id,
            'offset': self.actions_output.get_offset(),
            'log_level': self.log_level,
            'mode': 'text',
        }
        self.raw_result = self.post_with_retry('check-actions', data)
        self.actions_output = ActionsOutput(self.raw_result)

    def cancel_actions(self, id):
        data = {'id': id}
        self.post_impl('cancel-actions', data)

    def remove_task(self, id, error=None, error_url=None):
        try:
            data = {'taskId': id}
            if error:
                data['error'] = error
                if error_url:
                    data['errorUrl'] = error_url
            self.post_impl('remove-task', data)
        except Exception as e:
            logging.error("Exception while removing task: {}".format(e))


class LaunchZenExperimentTests(sdk2.Task):
    """
    Task for running zen shooting on testid flags.
    Use to test new experiment from ab.yandex-team.ru
    """

    class Requirements(task_env.TinyRequirements):
        pass

    class Parameters(sdk2.Parameters):
        description = "Zen experiment shooting"
        kill_timeout = 60 * 60  # Timeout 1 hour
        notifications = [
            sdk2.Notification(
                statuses=[
                    ctt.Status.FAILURE,
                    ctt.Status.EXCEPTION,
                    ctt.Status.TIMEOUT
                ],
                recipients=["zen-experiments@yandex-team.ru"],
                transport=ctn.Transport.EMAIL
            )
        ]

        # Task defined parameters
        experiment_ticket = sdk2.parameters.String("Experiment ticket", required=True)
        experiment_testid = sdk2.parameters.String("Experiment testid", required=True)
        experiment_flags = sdk2.parameters.Dict("Experiment flags", default={}, required=True)
        skip_test = sdk2.parameters.Bool("Skip test", default=True)
        timeout_seconds = sdk2.parameters.Integer("Ping timeout, seconds", default=30)
        base_url = sdk2.parameters.String(
            "Base shooter url",
            default="http://zen-shooter-master.kaizen.yandex-team.ru/api-v1"
        )
        slack_channel = sdk2.parameters.String("Slack report to", default="#experiments_release")
        author = sdk2.parameters.String("Experiment author")

    def on_save(self):
        self.Parameters.notifications = []
        self.Parameters.notifications.append(
            sdk2.Notification(
                statuses=[
                    ctt.Status.FAILURE,
                    ctt.Status.EXCEPTION,
                    ctt.Status.TIMEOUT
                ],
                recipients=["zen-experiments@yandex-team.ru"],
                transport=ctn.Transport.EMAIL
            )
        )
        if self.Parameters.author:
            self.Parameters.notifications.append(
                sdk2.Notification(
                    statuses=[
                        ctt.Status.EXECUTING,
                        ctt.Status.FAILURE,
                        ctt.Status.EXCEPTION,
                        ctt.Status.TIMEOUT
                    ],
                    recipients=[self.Parameters.author],
                    transport=ctn.Transport.EMAIL
                )
            )

    def shoot(self, countries_kind, author):
        base_url = self.Parameters.base_url
        testid = self.Parameters.experiment_testid
        if countries_kind != 'russia':  # Assume KUB always
            need_perf = True
            need_integration = False
            request = "on-defaults web production testids=" + testid + " kub preset=experiments warm_up_num=2000 shoot_num=500"
        else:
            need_perf = False
            need_integration = True
            request = "production testids=" + testid + " preset=experiments warm_up_num=4000 shoot_num=500"
        webhook_request_data = {
            "request" : request,
            "login" : "robot-zen-shooter",  # mandatory, could be some robot user name
            "need_perf" : need_perf,
            "need_integration" : need_integration,
            "base" : {  # some garbage section, just put any random git commit like this
                "ref" : "master",
                "sha" : "491563b569ce52b9c50a8318c9fa264515730578"
            },
            "head" : {  # some garbage section, just put any random git commit like this
                "ref" : "master",
                "sha" : "491563b569ce52b9c50a8318c9fa264515730578"
            },
            'use_case': 'release'  # will change in future
        }
        logging.info("Pushing task")
        shooter_client = ShooterClient("zen-shooter-master.kaizen.yandex-team.ru", 80)
        raw_result_content = None
        try:
            logging.info("Sending request: {}".format(json.dumps(webhook_request_data, indent=4, sort_keys=True)))
            shooter_client.post_and_print('webhook-request', webhook_request_data, print_on_success=False)
            logging.info("Got result")
            raw_result_content = shooter_client.get_raw_result_or_raise_last_exception()
            webhook_request_output = ActionsOutput(shooter_client.raw_result)
            if webhook_request_output.has_error():
                webhook_request_output.pretty_print_error()
                raise common.errors.TaskFailure(
                    "Shooting of testid {} failed. Error1".format(testid)
                )
            elif not webhook_request_output.is_success() and webhook_request_output.has_message():
                logging.error("Error: {}".format(webhook_request_output.get_message()))
                raise common.errors.TaskFailure(
                    "Shooting of testid {} failed. Error2".format(testid)
                )
            else:
                if webhook_request_output.has_message():
                    logging.error(webhook_request_output.get_message())
                result = shooter_client.raw_result.json()
                if 'taskIds' not in result:
                    logging.error("Not found taskIds in output")
                    raise common.errors.TaskFailure(
                        "Shooting of testid {} failed. Error3".format(testid)
                    )
                taskId = result['taskIds'][0]

        except Exception as e:
            logging.error("Exception during webhook-request: {}".format(e))
            if raw_result_content:
                logging.error(raw_result_content.content)
            raise common.errors.TaskFailure(
                "Shooting of testid {} failed. Error4".format(testid)
            )

        logging.info("Popping task")
        while True:
            shooter_client.post_and_print('pop-direct-task', {'taskId': taskId})
            pop_output = shooter_client.actions_output
            if pop_output.has_error():
                pop_output.pretty_print_error()
                raise RuntimeError("Failed to pop-task")
            if pop_output.has_task():
                break
            if not pop_output.have_more():
                logging.error("Lost task")
                raise common.errors.TaskFailure(
                    "Shooting of testid {} failed. Error5".format(testid)
                )

        logging.info("Popped task")
        pop_task_output = pop_output.get_result()
        if 'tasks' not in pop_task_output:
            logging.error("Not found tasks in pop-direct-task output")
            raise common.errors.TaskFailure(
                "Shooting of testid {} failed. Error6".format(testid)
            )

        task = pop_task_output['tasks'][0]
        if 'error' in task:
            task_id = task['taskId']
            if 'errorUrl' in task:
                text_error = task['error'] + " " + task['errorUrl']
            else:
                text_error = task['error']
            shooter_client.remove_task(task_id, "Failed to build: " + text_error)
            raise common.errors.TaskFailure(
                "Shooting of testid {} failed. Error7".format(testid)
            )

        logging.info("Running shoot on: {}, task id: {}".format(countries_kind, taskId))
        logging.info("Tasks: {}/view-task?id={}".format(base_url, taskId))
        logging.info("Actions: {}/view-actions?id={}".format(base_url, taskId))
        logging.info("Allure: {}/reports/{}".format(base_url.replace("/api-v1", ""), taskId))
        logging.info("Waiting for task")
        exit_code = None
        try:
            shooter_client.post_and_print('start-task-shooting', {'taskId': taskId})
            actions_output = shooter_client.actions_output
            if actions_output.has_error():
                actions_output.pretty_print_error()
                raise common.errors.TaskFailure(
                    "Shooting of testid {} failed. Error8".format(testid)
                )

            while True:
                actions_output = shooter_client.actions_output
                result = actions_output.get_result()
                if 'lines' in result:
                    for line in result['lines']:
                        logging.info(line.encode('utf-8'))
                if actions_output.finished():
                    if actions_output.failed():
                        exit_code = 1
                    else:
                        tests = actions_output.get_tests()
                        for test in tests:
                            if 'status' in test and 'path' in test and test['status'] != 'SKIPPED' and test['status'] != 'PASSED':
                                raise common.errors.TaskFailure(
                                    "Shooting of testid {} failed. Failed".format(testid)
                                )
                    break

                time.sleep(0.05)
                shooter_client.check_actions(taskId)

        except Exception as e:
            shooter_client.print_raw_request()
            logging.error("Exception: {}".format(e))
            try:
                shooter_client.cancel_actions(taskId)
            except Exception as e2:
                logging.error("Exception: {}".format(e2))
            shooter_client.remove_task(taskId, "Exception in python: " + str(e))
            raise

        if exit_code:
            shooter_client.remove_task(taskId, "Shooting failed")
            raise common.errors.TaskFailure(
                "Shooting of testid {} failed. Error9".format(testid)
            )
        else:
            shooter_client.remove_task(taskId)

    def shoot_tries(self, countries_kind, author, tries):
        num_tries = 0
        while True:
            try:
                self.shoot(countries_kind, author)
                return
            except Exception as e:
                if num_tries < tries:
                    logging.info("One more try: {}".format(tries))
                    time.sleep(60)
                    num_tries = num_tries + 1
                else:
                    raise e

    def on_execute(self):
        logging.info("Running with ticket: %s, testid: %s, flags: %s, skip: %s",
                     self.Parameters.experiment_ticket,
                     self.Parameters.experiment_testid,
                     str(self.Parameters.experiment_flags),
                     str(self.Parameters.skip_test))

        # immediate return if test should be skipped
        if self.Parameters.skip_test:
            return

        shoot = True
        author = ''

        task_content_json = get_task(self.Parameters.experiment_ticket)
        if task_content_json:
            shoot = need_shoot_on_russia(get_regions(task_content_json))
            author = task_content_json.get('author')

        logging.info("Need shoot: {0}".format(shoot))

        if shoot:
            self.shoot_tries("russia", author, 1)

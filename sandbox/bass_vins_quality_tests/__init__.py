# -*- coding: utf-8 -*-

import json
import logging
import requests

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from sandbox import sdk2
from sandbox.sandboxsdk.channel import channel
import sandbox.projects.common.error_handlers as eh

LOGGER = logging.getLogger('BassVinsQualityTestsTask')

BASS_PROD = "http://bass-prod.yandex.net/"
BASS_RC = "http://bass-rc.n.yandex-team.ru/"
VINS_HAMSTER = "http://yappy_vins_hamster_0.yappy-slots.yandex-team.ru/speechkit/app/pa/"

NIRVANA_API = 'https://nirvana.yandex-team.ru/api/public/v1/'

TARGET_NIRVANA_INSTANCE = "ca251a00-ded1-4d51-a77b-759ffb971cf0"
TARGET_NIRVANA_WORKFLOW = "13e78538-c570-4d82-aac1-5c7fa5e2ad71"
TARGET_NIRVANA_OPERATION = "operation-1536928832530-16"

WAIT_BEFORE_CHECK = 60 * 360  # In seconds


def clone_nirvana_instance(robot_nirvana_token=None):
    LOGGER.info("clone_nirvana_instance")
    if not robot_nirvana_token:
        LOGGER.info("lack of important fields")
        return None

    headers = {'Authorization': 'OAuth ' + robot_nirvana_token, 'Content-type': 'application/json'}
    data = {"jsonrpc": "2.0",
            "params": {"workflowInstanceId": TARGET_NIRVANA_INSTANCE}}

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(NIRVANA_API + 'cloneWorkflowInstance',
                     headers=headers,
                     json=json.dumps(data),
                     params=data['params'],
                     verify=False)

    LOGGER.info(str(r.status_code))
    if r.status_code == 200:
        result = r.json()
        LOGGER.info(str(result))
        run_id = result.get('result', 0)
        if run_id:
            return str(run_id)  # workflowInstanceId of the new instance

    return None


def update_nirvana_instance(robot_nirvana_token=None, target_bass=None, target_instance=None):
    LOGGER.info("update_nirvana_instance")
    if not (robot_nirvana_token and target_bass and target_instance):
        LOGGER.info("lack of important fields")
        return None

    api_operation = "setBlockParameters"
    headers = {'Authorization': 'OAuth ' + robot_nirvana_token, 'Content-type': 'application/json'}
    data = {"jsonrpc": "2.0",
            "method": api_operation,
            "id": TARGET_NIRVANA_WORKFLOW,
            "params": {"workflowInstanceId": target_instance,
                       "blocks": [{"code": TARGET_NIRVANA_OPERATION}],
                       "params": [{"parameter": "bass_url", "value": target_bass},
                                  {"parameter": "vins_url", "value": VINS_HAMSTER}]}}

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.post(NIRVANA_API + api_operation,
                      headers=headers,
                      json=data,
                      verify=False)

    LOGGER.info(str(r.status_code))
    if r.status_code == 200:
        result = r.json()
        LOGGER.info(str(result))
        run_id = result.get('result', -1)

        if run_id != -1:
            return str(run_id)

    return None


def start_nirvana_instance(robot_nirvana_token=None, target_bass=None, target_instance=None):
    LOGGER.info("start_nirvana_instance")
    if not (robot_nirvana_token and target_bass and target_instance):
        LOGGER.info("lack of important fields")
        return None

    headers = {'Authorization': 'OAuth ' + robot_nirvana_token, 'Content-type': 'application/json'}

    data = {"jsonrpc": "2.0",
            "params": {"workflowInstanceId": target_instance,
                       "workflowId": TARGET_NIRVANA_WORKFLOW}}

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.get(NIRVANA_API + 'startWorkflow',
                     headers=headers,
                     json=json.dumps(data),
                     params=data['params'],
                     verify=False)
    LOGGER.info(str(r.status_code))

    if r.status_code == 200:
        result = r.json()
        LOGGER.info(str(result))
        run_id = result.get('result', 0)
        if run_id:
            return str(run_id)

    return None


def is_nirvana_instance_finished(robot_nirvana_token=None, target_instance=None):
    LOGGER.info("is_nirvana_instance_finished")
    if not (robot_nirvana_token and target_instance):
        LOGGER.info("lack of important fields")
        return None

    api_operation = "getWorkflowSummary"
    headers = {'Authorization': 'OAuth ' + robot_nirvana_token, 'Content-type': 'application/json'}
    data = {"jsonrpc": "2.0",
            "method": api_operation,
            "id": TARGET_NIRVANA_WORKFLOW,
            "params": {"workflowInstanceId": target_instance,
                       "blocks": [{"code": TARGET_NIRVANA_OPERATION}]}}

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.post(NIRVANA_API + api_operation,
                      headers=headers,
                      json=data,
                      verify=False)

    LOGGER.info(str(r.status_code))
    if r.status_code == 200:
        result = r.json()
        LOGGER.info(str(result))
        result_info = result.get('result', 0)
        if result_info:
            result_status = result_info.get('result', 0)
            if str(result_status) == 'success':
                return True

    return None


def get_quality_score(robot_nirvana_token=None, target_instance=None):
    LOGGER.info("get_quality_score")
    if not (robot_nirvana_token and target_instance):
        LOGGER.info("lack of important fields")
        return None

    api_operation = "getBlockResults"
    headers = {'Authorization': 'OAuth ' + robot_nirvana_token, 'Content-type': 'application/json'}
    data = {"jsonrpc": "2.0",
            "method": api_operation,
            "id": TARGET_NIRVANA_WORKFLOW,
            "params": {"workflowInstanceId": target_instance,
                       "blocks": [{"code": TARGET_NIRVANA_OPERATION}]}}

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    r = requests.post(NIRVANA_API + api_operation,
                      headers=headers,
                      json=data,
                      verify=False)

    LOGGER.info(str(r.status_code))
    if r.status_code == 200:
        result = r.json()
        LOGGER.info(str(result))

        results_wrapper = result.get('result', 0)
        target_to_download = None
        if results_wrapper:
            for wrapped_result in results_wrapper:
                inner_results = wrapped_result.get('results', 0)
                if inner_results:
                    for item in inner_results:
                        endpoint = item.get('endpoint', 0)
                        if endpoint and (endpoint == 'quality'):
                            direct_path = item.get('directStoragePath')
                            if direct_path:
                                target_to_download = direct_path
        if target_to_download:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            r = requests.get(target_to_download,
                             verify=False)
            if r.status_code == 200:
                return r.text
    return None


def post_comment(robot_token=None, comment_text=None, ticket_target=None):
    if robot_token:
        content = {'text': comment_text}
        custom_headers = {'Content-Type': 'application/json',
                          'Accept': 'application/json',
                          'Authorization': 'OAuth ' + robot_token}
        target = 'https://st-api.yandex-team.ru/v2/issues/' + str(ticket_target) + '/comments'
        LOGGER.info(str(ticket_target))
        r = requests.post(target,
                          json=content,
                          headers=custom_headers)
        LOGGER.info(str(r.status_code))


def create_start_wrapping(bass_type=None, bass_url=None, nirvana_instance=None):
    result = "Quality tests VINS PROD vs " + bass_type + " (%%" + bass_url + "%%) started: "
    result += "https://nirvana.yandex-team.ru/flow/" + TARGET_NIRVANA_WORKFLOW + "/" + nirvana_instance
    return result


def create_score(bass_type=None, bass_url=None, nirvana_instance=None, result_score=None):
    result = "Quality score: %%" + str(result_score) + "%% "
    result += "for **VINS PROD vs " + bass_type + "** (%%" + bass_url + "%%) from quality tests: "
    result += "https://nirvana.yandex-team.ru/flow/" + TARGET_NIRVANA_WORKFLOW + "/" + nirvana_instance
    return result


def create_restart_wrapping(bass_type=None, bass_url=None, nirvana_instance=None):
    result = "After " + str(WAIT_BEFORE_CHECK / 60) + " minute(s) quality tests did not finish successfully. "
    result += "Consider restart or check the tests manually for this Nirvana run: "
    result += "**VINS PROD vs " + bass_type + "** (%%" + bass_url + "%%) from quality tests: "
    result += "https://nirvana.yandex-team.ru/flow/" + TARGET_NIRVANA_WORKFLOW + "/" + nirvana_instance
    return result


def log_and_check_wrapper(prod_status=None, rc_status=None):
    LOGGER.info(str(prod_status))
    LOGGER.info(str(rc_status))
    if prod_status and rc_status:
        return True
    return False


class BassVinsQualityTestsTask(sdk2.Task):
    '''
        Run Bass Vins Quality Tests
    '''

    class Parameters(sdk2.Task.Parameters):
        bass_url = sdk2.parameters.String('bass_url', default=BASS_RC, required=True)
        vins_url = sdk2.parameters.String('vins_url', default=VINS_HAMSTER, required=True)
        target_ticket = sdk2.parameters.String('target_ticket', default='ALICERELEASE-1', required=True)

    def check_exit(self):
        return self.Context.exit

    def force_exit(self):
        self.Context.exit = True

    def exit(self, wait_time):
        self.Context.exit = True
        raise sdk2.WaitTime(wait_time)

    def init_context(self):
        self.Context.exit = False
        self.Context.prod_bass_nirvana = None
        self.Context.rc_bass_nirvana = None

    def on_execute(self):
        target_url = self.Parameters.bass_url
        target_ticket = self.Parameters.target_ticket

        with self.memoize_stage.init_context:
            self.init_context()

        if target_url and target_ticket:
            LOGGER.info(str(target_url))
            LOGGER.info(str(target_ticket))
            # Nirvana tests
            try:
                robot_nirvana_token = channel.task.get_vault_data('BASS', 'robot_bassist_nirvana_oauth_token')
                robot_token = channel.task.get_vault_data('BASS', 'robot_bassist_startrek_oauth_token')
            except Exception as exc:
                eh.log_exception('Failed to get robot pass and token from vault', exc)
                robot_nirvana_token = False
                robot_token = False
            if not (robot_nirvana_token and robot_token):
                return

            if self.check_exit():
                prod_copy = self.Context.prod_bass_nirvana
                prod_score = None
                if prod_copy and is_nirvana_instance_finished(robot_nirvana_token, prod_copy):
                    prod_score = get_quality_score(robot_nirvana_token, prod_copy)
                    if prod_score:
                        post_comment(robot_token, create_score("BASS PROD", BASS_PROD, prod_copy, prod_score), target_ticket)
                if not prod_score:
                    post_comment(robot_token, create_restart_wrapping("BASS PROD", BASS_PROD, prod_copy), target_ticket)

                rc_copy = self.Context.rc_bass_nirvana
                rc_score = None
                if rc_copy and is_nirvana_instance_finished(robot_nirvana_token, rc_copy):
                    rc_score = get_quality_score(robot_nirvana_token, rc_copy)
                    if rc_score:
                        post_comment(robot_token, create_score("BASS RC", target_url, rc_copy, rc_score), target_ticket)
                if not rc_score:
                    post_comment(robot_token, create_restart_wrapping("BASS RC", target_url, rc_copy), target_ticket)

                return

            prod_copy = clone_nirvana_instance(robot_nirvana_token)
            rc_copy = clone_nirvana_instance(robot_nirvana_token)
            if not log_and_check_wrapper(prod_copy, rc_copy):
                return

            prod_upd = update_nirvana_instance(robot_nirvana_token, BASS_PROD, prod_copy)
            rc_upd = update_nirvana_instance(robot_nirvana_token, target_url, rc_copy)
            if not log_and_check_wrapper(prod_upd, rc_upd):
                return

            prod_run = start_nirvana_instance(robot_nirvana_token, BASS_PROD, prod_copy)
            rc_run = start_nirvana_instance(robot_nirvana_token, target_url, rc_copy)
            if not log_and_check_wrapper(prod_run, rc_run):
                return

            post_comment(robot_token, create_start_wrapping("BASS PROD", BASS_PROD, prod_copy), target_ticket)
            post_comment(robot_token, create_start_wrapping("BASS RC", target_url, rc_copy), target_ticket)
            self.Context.prod_bass_nirvana = prod_copy
            self.Context.rc_bass_nirvana = rc_copy
            self.exit(WAIT_BEFORE_CHECK)

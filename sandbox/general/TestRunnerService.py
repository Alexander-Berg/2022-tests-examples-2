import json

import requests
from deepdiff import DeepDiff

from sandbox.projects.music.MusicDiffTest.lib.models.TestCase import TestCase
from sandbox.projects.music.MusicDiffTest.lib.models.TestRun import TestRun
from sandbox.projects.music.MusicDiffTest.lib.services.InjectionService import InjectionService
from sandbox.projects.music.MusicDiffTest.lib.utils.helpers import test_step_url_preparator, curl_generator


class TestRunnerService:
    ALWAYS_BAD = [i for i in range(500, 520)]

    def __init__(self, test_run: TestRun, order=True):
        self.test_run = test_run
        self.order = order

    def launch_test_run(self):
        controllers = self.test_run.test_controllers

        for controller in controllers:
            results = []
            for test_case in controller.get_test_cases():
                test_case_result = self.perform_test(test_case, self.order)
                results.append({
                    "test_case": test_case.title,
                    "results": test_case_result
                })
            self.test_run.set_result_by_controller(
                controller.controller_name,
                results
            )

    def perform_test(self, test_case: TestCase, order: bool):
        results = []

        for test_step in test_case.test_steps:
            test_step = InjectionService.insert_dependencies(
                test_step,
                test_case.shared_data
            )

            test_step = InjectionService.insert_auth(
                test_step,
                test_case.users
            )

            request_url1, request_url2 = test_step_url_preparator(
                test_step
            )

            curl1, curl2 = curl_generator(
                request_url1,
                request_url2,
                test_step
            )

            response1, response2 = self._make_requests(test_step,
                                                       request_url1,
                                                       request_url2)

            print("Test done")
            headers1, headers2 = response1.headers, response2.headers
            status_code1, status_code2 = (response1.status_code,
                                          response2.status_code)

            try:
                response1 = response1.json()
            except ValueError:
                response1 = response1.text

            try:
                response2 = response2.json()
            except ValueError:
                response2 = response2.text

            diff_result_msg = {
                "id": test_step.order_id,
                "name": test_step.name,
                "curl1": curl1,
                "curl2": curl2,
                "method": test_step.request1.get('method').upper(),
                "status": None,
                "reason": None,
                "response1": response1,
                "response2": response2,
                "status_code1": status_code1,
                "status_code2": status_code2
            }

            if status_code1 != status_code2 or status_code1 in self.ALWAYS_BAD:
                msg = f"Status Codes: {status_code1} vs {status_code2}"
                diff_result_msg['status'] = 'Aborted'
                diff_result_msg['reason'] = msg
                results.append(diff_result_msg)
                break

            if test_step.expected_status_codes:
                if (status_code1 not in test_step.expected_status_codes or
                        status_code2 not in test_step.expected_status_codes):
                    msg = ("Status codes are not expected: "
                           f"{status_code1}/{status_code2} are not in "
                           f"expected list {test_step.expected_status_codes}")

                    diff_result_msg['status'] = 'Aborted'
                    diff_result_msg['reason'] = msg

                    results.append(diff_result_msg)
                    break

            try:
                excluded_paths_in_diff = ["root['invocationInfo']"]
                if test_step.ignore_paths:
                    excluded_paths_in_diff += test_step.ignore_paths

                result = DeepDiff(
                    response1,
                    response2,
                    ignore_order=order,
                    exclude_regex_paths=excluded_paths_in_diff
                ).to_json(indent=4, ensure_ascii=False)

            except Exception:
                diff_result_msg['status'] = 'Aborted'
                diff_result_msg['reason'] = 'Internal Diff Error'

                results.append(diff_result_msg)
                break

            if result.strip("{}"):
                diff_result_msg['status'] = 'Diff'
                diff_result_msg['reason'] = result

                results.append(diff_result_msg)
            else:
                diff_result_msg['status'] = 'Nodiff'
                diff_result_msg['reason'] = 'Requests matched'
                results.append(diff_result_msg)

            if test_step.extract:
                test_case.shared_data = InjectionService.extract_shared_data(
                    response1, response2,
                    headers1, headers2,
                    test_step.extract, test_case.shared_data)

        return results

    def _make_requests(self, test_step, url1, url2):

        method = test_step.request1.get('method').upper()

        if method == 'GET':
            response1 = requests.get(
                url1,
                headers=json.loads(test_step.request1.get('headers')),
                verify=False
            )
            response2 = requests.get(
                url2,
                headers=json.loads(test_step.request2.get('headers')),
                verify=False
            )
        elif method == 'POST':
            response1 = requests.post(
                url1,
                headers=json.loads(test_step.request1.get('headers')),
                data=test_step.request1.get('body'),
                verify=False
            )
            response2 = requests.post(
                url2,
                headers=json.loads(test_step.request2.get('headers')),
                data=test_step.request2.get('body'),
                verify=False
            )
        elif method == 'PUT':
            response1 = requests.put(
                url1,
                headers=json.loads(
                    test_step.request1.get('headers')),
                data=test_step.request1.get('body'),
                verify=False
            )
            response2 = requests.put(
                url2,
                headers=json.loads(
                    test_step.request2.get('headers')),
                data=test_step.request2.get('body'),
                verify=False
            )
        elif method == 'PATCH':
            response1 = requests.patch(
                url1,
                headers=json.loads(
                    test_step.request1.get('headers')),
                data=test_step.request1.get('body'),
                verify=False
            )
            response2 = requests.patch(
                url2,
                headers=json.loads(
                    test_step.request2.get('headers')),
                data=test_step.request2.get('body'),
                verify=False
            )
        elif method == 'DELETE':
            response1 = requests.delete(
                url1,
                headers=json.loads(test_step.request1.get('headers')),
                data=test_step.request1.get('body'),
                verify=False
            )
            response2 = requests.delete(
                url2,
                headers=json.loads(
                    test_step.request2.get('headers')),
                data=test_step.request2.get('body'),
                verify=False
            )
        else:
            raise ValueError("Method {} is not supported".format(method))
        return response1, response2

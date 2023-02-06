import logging
import json
from sandbox import sdk2
from sandbox.projects.common.juggler import jclient
import sandbox.common.types.task as ctt


class TestWalleProjects(sdk2.Task):
    """Run tests for Wall-E projects"""

    releasers = ['dldmitry']

    def on_execute(self):
        task_class = sdk2.Task['YA_MAKE']

        with self.memoize_stage.build:
            sub_task = task_class(
                self,
                description='run wall-e tests',
                targets='infra/rtc/walle_validator',
                test=True,
                build_type='release',
                use_aapi_fuse=True,
                aapi_fallback=True
            )
            sub_task.enqueue()
            raise sdk2.WaitTask([sub_task], ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)

        sub_task = self.find(task_class, status=ctt.Status.Group.FINISH).first()
        if sub_task is None:
            return
        elif sub_task.status == ctt.Status.FAILURE:
            testenv_resource = sdk2.Resource["TEST_ENVIRONMENT_JSON_V2"].find(task=sub_task).first()
            if testenv_resource is None:
                logging.info("testenv resource not found")
                return
            testenv_path = str(sdk2.ResourceData(testenv_resource).path)
            with open(testenv_path) as stream:
                testenv_results = json.load(stream)
            if not self._check_build_status(testenv_results):
                logging.info("tests build failed")
                return
            status, description = 'CRIT', 'rtc wall-e projects are invalid: {}'.format(self._get_build_description(testenv_results))
        else:
            status, description = 'OK', 'rtc wall-e projects are valid'

        jclient.send_events_to_juggler('test-walle-project', 'scheduler', status, description)

    def _check_build_status(self, results):
        results = [x for x in results["results"] if x["path"] == "infra/rtc/walle_validator/tests" and x["type"] == "build"]
        if results:
            return results[0]["status"] == "OK"
        else:
            return False

    def _get_build_description(self, results, max_len=500):
        tests = [
            x["subtest_name"] for x in results["results"]
            if x["path"] == "infra/rtc/walle_validator/tests" and x["type"] == "test" and x["status"] == "FAILED" and x.get("subtest_name")
        ]
        desc = ", ".join(tests)
        if len(desc) > max_len:
            desc = desc[:max_len] + "..."
        return desc

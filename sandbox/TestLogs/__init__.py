# -*- coding: utf-8 -*-

import json
import logging
import random
import requests
import time
# import os
from datetime import datetime

from sandbox.common.errors import TaskFailure
from sandbox.common.types import task as ctt
import sandbox.projects.common.binary_task as binary_task
from sandbox.projects.logs.GenerateICookie import GenerateICookie
from sandbox.projects.logs.KatiWrapper import KatiWrapper
from sandbox.projects.sandbox_ci.sandbox_ci_web4_hermione_e2e import SandboxCiWeb4HermioneE2E
from sandbox.projects.sandbox_ci.sandbox_ci_hermione_e2e_subtask import SandboxCiHermioneE2eSubtask
import sandbox.sdk2 as sdk2

from sandbox import common
from sandbox.projects.common.arcadia import sdk as arcadia_sdk
from sandbox.projects.common.apihelpers import get_last_resource_with_attrs

from sandbox.projects.logs.KatiWrapper.lib.tokens import get_secret, SANDBOX_ROBOT_MAKE_SESSIONS_SECRET_ID, YT_ROBOT_MAKE_SESSIONS_SECRET_ID

TEST_ID_PREFIX = "42424242"
SUFFIX_LEN = 11
HERMIONE_TASK_OWNER = 'SANDBOX_CI_SEARCH_INTERFACES'
HERMIONE_TASK_TYPE = 'SANDBOX_CI_WEB4_HERMIONE_E2E'
HERMIONE_RELEASE_TAG = 'RELEASE'

SRC_PATH = '//user_sessions/rt/pers/queues/pub/test_logs'
DST_PATH = '//home/userdata-dev/zsafiullin/staticTables/research'
OUTPUT_PREFIX = '//home/userdata-dev/zsafiullin/kati'
HIERARCHY_PATH = 'user_sessions/pub/search/daily'
REQID_RESOURCE_NAME = 'SANDBOX_CI_ARTIFACT'  # TODO change to 'REQID_ARTIFACT' below


class ReqidArtifact(sdk2.Resource):
    """
        JSON with reqids
    """
    auto_backup = True


def random_yuid():
    rand_suffix = str(random.randint(10**(SUFFIX_LEN-1), 10**SUFFIX_LEN))
    return TEST_ID_PREFIX + rand_suffix


def get_task_yt_prefix(params):
    dst_path = params['dst_path']
    task_id = params['task_id']
    return '{}/{}/'.format(dst_path, task_id)


def get_full_dst_path(params):
    date = params['date']
    prefix = get_task_yt_prefix(params)
    dst_full_path = prefix + '{}/{}/clean'.format(HIERARCHY_PATH, date)
    return dst_full_path


def get_reqids_from_file(path):
    f = open(path, 'r')
    lines = f.readlines()
    reqids_data = {}  # key - test name, value - reqid
    for i in range(0, len(lines), 2):
        test_name = lines[i].rstrip()
        reqid = lines[i + 1].rstrip()
        reqids_data[test_name] = reqid
    # TODO return full dict and combine reqids from common tests
    return list(reqids_data.values())


def dump(params):
    import yt.wrapper as yt
    from yt.wrapper import YtClient

    dst_full_path = get_full_dst_path(params)
    src = params['src']

    yt_token = get_secret(params['yt_token_secret_id'], params['yt_token_secret_name'])

    yt.config["proxy"]["url"] = "hahn.yt.yandex.net"
    yt.config["token"] = yt_token

    yt_client = YtClient(
        proxy='hahn',
        token=yt_token
    )

    with yt.Transaction(client=yt_client):
        # Create table and save vital attributes.
        yt_client.create(
            'table',
            dst_full_path,
            recursive=True,
            attributes={
            "optimize_for": yt.get_attribute(src, "optimize_for", default="lookup"),
            "schema": yt.get_attribute(src, "schema")}
        )

        # Dump table contents.
        yt_client.run_merge(
            source_table=src,
            destination_table=dst_full_path,
            mode='unordered',
            spec={'combine_chunks': True}
        )

        # Sort static table by key, subkey
        yt_client.run_sort(dst_full_path, sort_by=['key', 'subkey'])


def validate_diff_report(diff_report):
    from library.python import resource

    resource_content = resource.find('resources/metrics.json')
    resource_json = json.loads(resource_content)
    metrics = resource_json['metrics']

    if diff_report.has_diff():
        logging.debug("METRICS WITH DIFF:")
        logging.debug(diff_report.diff.keys())
    
    for metric_name in metrics:
        if metric_name in diff_report.diff:
            logging.debug("CRITICAL METRIC DIFF ({})".format(metric_name))
            return False

    logging.debug("NO DIFF")
    return True


class TestLogs(sdk2.Task, binary_task.LastBinaryTaskRelease):
    class Requirements(sdk2.Requirements):
        pass

    class Parameters(binary_task.LastBinaryReleaseParameters):
        trunk_beta_url = sdk2.parameters.String("Trunk revision beta url")
        branch_beta_url = sdk2.parameters.String("Branch revision beta url")
        yt_token_secret_id = sdk2.parameters.String(
            'YT token secret id',
            description='YT token secret id of robot for all the cypress stuff'
        )
        yt_token_secret_name = sdk2.parameters.String(
            'YT token secret name',
            description='YT token secret name of robot for all the cypress stuff'
        )
        yt_prefix_path = sdk2.parameters.String('Hahn cypress prefix path for storing static tables with sessions')

        sandbox_token_secret_id = sdk2.parameters.String(
            'Sandbox token secret id',
            description='Sandbox token secret id of robot for running hermione-e2e tasks',
            default='sec-01g02dcjabbha085e83qvcxggm',   # TODO replace with our robot token
        )
        sandbox_token_secret_name = sdk2.parameters.String(
            'Sandbox token secret name',
            description='Sandbox token secret name of robot for running hermione-e2e tasks',
            default='sandbox_token'
        )
        yt_pool = sdk2.parameters.String('YT Pool for running A/B tests (on Hahn)')
        push_tasks_resource = True

    def CreateGenerateICookieSubtask(self, yuids_count=1):
        # yuids = [random_yuid() for _ in range(yuids_count)]
        # yuids = ['4242424201020304050']
        yuids = ['4242424201627896936']
        logging.debug(yuids)
        task = GenerateICookie(
            self,
            yandexuids=yuids
        )
        task.enqueue()
        return task

    def CreateHermioneSubtask(self, base_hermione_task, is_trunk):
        """
        base_hermione_task - last released to prod version of task, has all required parameters
        beta_url - one of trunk_beta_url, branch_beta_url
        """

        beta_url = self.Parameters.trunk_beta_url
        if not is_trunk:
            beta_url = self.Parameters.branch_beta_url

        sandbox_token = get_secret(self.Parameters.sandbox_token_secret_id, self.Parameters.sandbox_token_secret_name)

        headers = {
            'Authorization': 'OAuth ' + sandbox_token,
            "Content-type": "application/json"
        }

        data = {
            "owner": HERMIONE_TASK_OWNER,
            "source": base_hermione_task.id
        }

        response = requests.post("https://sandbox.yandex-team.ru/api/v1.0/task", data=json.dumps(data), headers=headers)
        if not response.ok:
            raise TaskFailure("Hermione subtask clone failed")

        logging.debug(response.content)
        subtask_id = response.json()['id']

        logging.debug("CLONED SUBTASK ID")
        logging.debug(subtask_id)

        subtask = sdk2.Task[subtask_id]

        # Updating cloned subtask parameters
        subtask.Parameters.tags = []
        custom_params = {
            'send_comment_to_searel': False,
            'send_comment_to_issue': '',
            'is_release': False,
            'platforms': ['desktop'],
            'beta_domain': beta_url,
            'hermione_base_url': beta_url,
            'custom_opts': 'features/desktop/organic/organic.hermione.e2e.js',
            'environ': {
                'USE_ARC': 1,
                'user_sessions_logs_resource_getter_enabled': 'true',
                'user_sessions_logs_resource_uploader_enabled': 'true',
                'HERMIONE_URL_QUERY_EXP_FLAGS': 'csp_disable',
                'HERMIONE_URL_QUERY_CLCK_HOST': 'hamster.yandex.ru/clck?l7rwr=clck:hamster-clickdaemon-sas-yp-2.sas.yp-c.yandex.net:80/clck'
            }
        }
        custom_params_list = []
        for key, value in custom_params.iteritems():
            custom_params_list.append({'name': key, 'value': value})

        put_params_url = "https://sandbox.yandex-team.ru/api/v1.0/task/{task_id}/custom/fields".format(task_id=subtask_id)
        response = requests.put(put_params_url, data=json.dumps(custom_params_list), headers=headers)
        if not response.ok:
            raise TaskFailure("Hermione subtask parameters update failed")
        logging.debug(response.content)

        subtask.enqueue()
        if is_trunk:
            self.Context.trunk_hermione_subtask_id = subtask.id
        else:
            self.Context.branch_hermione_subtask_id = subtask.id
        return subtask

    def _get_latest_stable_abt_package_id(self):
        last_resource = get_last_resource_with_attrs(
            "AB_TESTING_YA_PACKAGE",
            {
                "released": "stable",
                "resource_name": "yandex-search-ab-testing",
            },
            all_attrs=True,
        )

        return last_resource.id if last_resource is not None else None

    def get_shell_abt(self):
        if common.system.inside_the_binary():
            logging.debug("inside_the_binary")
            return common.context.NullContextmanager(enter_obj="")
        else:
            return arcadia_sdk.mount_arc_path(
                "arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/", use_arc_instead_of_aapi=True
            )

    def get_reqids(self, hermione_task_id):
        subtasks = SandboxCiHermioneE2eSubtask.find(parent=sdk2.Task[hermione_task_id]).limit(100)
        logging.debug("HERMIONE SUBTASKS COUNT:")
        logging.debug(subtasks.count)
        reqids = []
        debug_ids = []
        for subtask in subtasks:
            logging.debug("YET ANOTHER SUBTASK ID")
            logging.debug(subtask.id)
            reqid_resource = sdk2.Resource.find(type=REQID_RESOURCE_NAME, attrs={'sandbox_task_id': subtask.id}).first()
            sync_path = str(sdk2.ResourceData(reqid_resource).path)
            cur_reqids = get_reqids_from_file(sync_path)
            reqids.extend(cur_reqids)
            debug_ids.append(subtask.id)
        logging.debug("SUBTASK IDS TO GET REQIDS FROM")
        logging.debug(debug_ids)
        return list(set(reqids))

    def on_create(self):
        self.Requirements.tasks_resource = sdk2.service_resources.SandboxTasksBinary.find(
            owner="zsafiullin",  # TODO change to any user_sessions robot
            attrs={"task_type": "TEST_LOGS"}
         ).first()

    def on_execute(self):
        self.Context.is_debug = False

        with self.memoize_stage.validate_params:
            self.Context.yt_prefix_path = self.Parameters.yt_prefix_path
            self.Context.yt_prefix_path = self.Context.yt_prefix_path.rstrip('/')

        with self.memoize_stage.generate_icookie:
            logging.debug("start on_execute GenerateICookie")
            generate_icookie_subtask = self.CreateGenerateICookieSubtask()
            logging.debug("created generate_icookie_subtask")
            raise sdk2.WaitTask([generate_icookie_subtask], ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)
            logging.debug("after WaitTask in GenerateICookie")

        with self.memoize_stage.run_hermione_tests:
            self.Context.start_time = time.time()

            base_hermione_task = sdk2.Task.find(task_type=SandboxCiWeb4HermioneE2E, status=(ctt.Status.SUCCESS), tags=[HERMIONE_RELEASE_TAG], children=True).order(-sdk2.Task.id).first()
            logging.debug("TASK ID %s", base_hermione_task.id)

            # trunk hermione
            trunk_hermione_subtask = self.CreateHermioneSubtask(base_hermione_task, is_trunk=True)

            # branch hermione
            branch_hermione_subtask = self.CreateHermioneSubtask(base_hermione_task, is_trunk=False)

            logging.debug("after creating 2 hermione subtasks")
            raise sdk2.WaitTask([trunk_hermione_subtask, branch_hermione_subtask], ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)

        with self.memoize_stage.collect_reqids:
            logging.debug("Collecting reqids")

            # end_time = time.time()
            # duration = int(end_time - self.Context.start_time)
            # logging.debug("DURATION %s", str(duration))

            if not self.Context.is_debug:
                self.Context.trunk_reqids = self.get_reqids(self.Context.trunk_hermione_subtask_id)
            else:
                self.Context.trunk_reqids = self.get_reqids(1276924250)

            logging.debug("TRUNK REQIDS")
            logging.debug(self.Context.trunk_reqids)

            if not self.Context.is_debug:
                self.Context.branch_reqids = self.get_reqids(self.Context.branch_hermione_subtask_id)
            else:
                self.Context.branch_reqids = self.get_reqids(1276924417)
            logging.debug("BRANCH REQIDS:")
            logging.debug(self.Context.branch_reqids)

        with self.memoize_stage.waiting_for_records:
            # waiting for records to appear in test_logs ordered table
            raise sdk2.WaitTime(5 * 60)  # 5 minutes

        with self.memoize_stage.dump_ordered_table:
            params = dict(
                task_id=str(self.id),
                date=datetime.today().strftime('%Y-%m-%d'),
                yt_pool=self.Parameters.yt_pool,
                yt_token_secret_id=self.Parameters.yt_token_secret_id,
                yt_token_secret_name=self.Parameters.yt_token_secret_name,
                src=SRC_PATH,
                dst_path=self.Context.yt_prefix_path
            )
            if self.Context.is_debug:
                params['date']='2022-04-13'
                params['task_id']='1276922617'

            dump(params)

        with self.memoize_stage.kati:
            def get_kati_subtask(params, reqids=None):
                if reqids is not None:
                    params['reqids'] = reqids
                kati_subtask = KatiWrapper(self, json_params=json.dumps(params))
                kati_subtask.enqueue()
                return kati_subtask

            logging.debug("STARTING KATI")

            trunk_kati_subtask = get_kati_subtask(params, self.Context.trunk_reqids)
            branch_kati_subtask = get_kati_subtask(params, self.Context.branch_reqids)

            self.Context.trunk_kati_subtask_id = trunk_kati_subtask.id
            self.Context.branch_kati_subtask_id = branch_kati_subtask.id

            raise sdk2.WaitTask([trunk_kati_subtask, branch_kati_subtask], ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=True)

        with self.memoize_stage.kati_diff:
            import quality.ab_testing.scripts.shellabt.shellabt as shellabt

            if sdk2.Task[self.Context.trunk_kati_subtask_id].status not in ctt.Status.Group.SUCCEED or \
                sdk2.Task[self.Context.branch_kati_subtask_id].status not in ctt.Status.Group.SUCCEED:
                    raise TaskFailure("Kati subtasks have failed. Try to rerun main task.")

            trunk_metrics_id = sdk2.Task[self.Context.trunk_kati_subtask_id].Parameters.metrics_id
            branch_metrics_id = sdk2.Task[self.Context.branch_kati_subtask_id].Parameters.metrics_id

            logging.debug("METRIC IDS:")
            logging.debug(trunk_metrics_id)
            logging.debug(branch_metrics_id)

            trunk_metrics_file = str(sdk2.ResourceData(sdk2.Resource[trunk_metrics_id]).path)
            branch_metrics_file = str(sdk2.ResourceData(sdk2.Resource[branch_metrics_id]).path)

            diff_report = shellabt.diff_suite_files(trunk_metrics_file, branch_metrics_file)
            if not validate_diff_report(diff_report):
                diff_html = diff_report.format_html()
                with open("diff.html", "w") as file:
                    file.write(diff_html)

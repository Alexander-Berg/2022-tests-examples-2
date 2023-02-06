# -*- coding: utf-8 -*

import json
import logging
import os
import requests

import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.errors import TaskFailure

from sandbox.projects.partner.settings import \
    ROBOT_PARTNER_SECRET
from sandbox.projects.partner.tasks.docker_hermione import DockerHermione
from sandbox.projects.partner.utils.arc import Arc


DEFAULT_BRANCH = 'trunk'
SOURCE_TYPE_BRANCH = 'branch'
SOURCE_TYPE_PRODUCTION = 'production'
SOURCE_TYPE_FRONT = 'Front'
SOURCE_TYPE_JAVA = 'Java'
SOURCE_TYPE_PERL = 'Perl'
SOURCE_TYPE = {
    SOURCE_TYPE_FRONT: {
        'path': 'adv/frontend/services/yharnam'
    },
    SOURCE_TYPE_JAVA: {
        'path': 'partner/java'
    },
    SOURCE_TYPE_PERL: {
        'path': 'partner/perl/partner2'
    },
}
PARTNER_ARC_PATH = 'arc/arcadia'
TEMPLATE_DEPS_PATH = 'test_deps/%s.json'


class PartnerPushTestRunner(sdk2.Task):
    name = "PARTNER_PUSH_TEST_RUNNER"

    class Requirements(sdk2.Task.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        description = 'Prepare data for hermione tests'

        with sdk2.parameters.Group('Branch settings') as branch_settings:
            source = sdk2.parameters.String(
                'Push initiator source',
                required=True,
                choices=[(s, s) for s in SOURCE_TYPE.keys()],
            )

            branch_name = sdk2.parameters.String(
                'Branch name',
                required=True,
            )

        # TODO: переименовать переменную на robot_partner_secret,
        # так как yav secret != "token" концептуально.
        # Внутри одного секрета может быть множество значений по ключу (токены, пароли и т.п)
        with sdk2.parameters.Group('Secrets') as secret_settings:
            arc_token = sdk2.parameters.YavSecret(
                'Arc OAuth token', default=ROBOT_PARTNER_SECRET
            )

        pull_request_id = sdk2.parameters.String(
            'Pull Request ID',
            required=False
        )

    def on_execute(self):
        deps = self.get_dependencies()
        self.run_tests(deps)

    def get_dependencies(self):
        logging.debug('get_dependencies')
        deps = self.Context.Dependencies
        if not deps or deps is ctm.NotExists:
            # Первичное заполнение, если не было заполнено до этого
            logging.debug('build deps')
            deps = self.get_dependencies_from_arcadia()

            # Если никаких зависимостей нет, используем дефолтные
            if not deps or deps is ctm.NotExists:
                logging.debug('use default deps')
                deps = {s: DEFAULT_BRANCH for s in SOURCE_TYPE.keys()}

            # Основная ветка тестируемого источника должна совпадать с параметрами
            deps[self.Parameters.source] = self.Parameters.branch_name

            # Сохранить результат
            self.Context.Dependencies = deps
            self.Context.save()
            self.set_info('Front: {}\nJava: {}\nPerl: {}'.format(deps[SOURCE_TYPE_FRONT], deps[SOURCE_TYPE_JAVA], deps[SOURCE_TYPE_PERL]))
        logging.debug(deps)
        return deps

    def get_dependencies_from_arcadia(self):
        path = SOURCE_TYPE[self.Parameters.source]['path']
        branch = self.Parameters.branch_name
        logging.debug('initialize arc')
        arc = Arc(path='.', token=self.get_arc_token())
        logging.debug('clone "%s" / "%s"' % (path, branch))
        try:
            arc.checkout(branch=branch)
            logging.debug('read deps')
            deps = self.read_json_file(os.path.join(PARTNER_ARC_PATH, path, TEMPLATE_DEPS_PATH % branch.split('/')[-1]))
            return deps
        finally:
            arc.finish()

    def get_arc_token(self):
        logging.debug('get_arc_token: getting arc token')
        if not self.Parameters.arc_token:
            raise Exception('Arc access token is missed')

        token = self.Parameters.arc_token.data()['arc_token']
        logging.debug('get_arc_token: success getting arc token')
        return token

    def get_arcanum_token(self):
        return self.Parameters.arc_token.data()['arcanum_token']

    def read_json_file(self, file_path):
        logging.debug('read_json_file: try to read "%s"' % file_path)
        if os.path.exists(file_path):
            logging.debug('read_json_file: open file "%s"' % file_path)
            with open(file_path, 'r') as file:
                logging.debug('read_json_file: decode file data')
                data = json.loads(file.read())
                return data
            logging.debug('read_json_file: impossible to read file')
        logging.debug('read_json_file: file does not exist')
        return None

    def notify_pull_request(self):
        task_id = self.Context.subtask_id
        pr_id = self.Parameters.pull_request_id
        arcanum_api_url = "https://arcanum.yandex.net/api/v1/pull-requests/%s/comments" % pr_id
        logging.debug("Start sending request to %s" % arcanum_api_url)
        try:
            requests.post(
                arcanum_api_url,
                params={'fields' : 'id,content,issue'},
                headers={
                    'Authorization' : 'OAuth %s' % self.get_arcanum_token(),
                    'Content-Type' : 'application/json',
                },
                json={
                    'content' : "Автотесты: https://sandbox.yandex-team.ru/task/%s" % task_id,
                    'issue' : False
                }
            )
            logging.info("Successfully notified PR %s about hermione task with id %s" % (pr_id, task_id))
        except Exception:
            logging.exception("Got error while notifying PR about hermione task")

    def run_tests(self, deps):
        if not deps or deps is ctm.NotExists:
            raise Exception('Deps are incorrect')

        task_id = self.Context.subtask_id
        if not task_id or task_id is ctm.NotExists:
            logging.debug('run_tests: task is not found in context, try to run new one')
            # Вместо прогона на транке используется прогон на production version для экономии ресурсов
            # Вместо дефолтной ветки фронта используется переданная ветка, чтобы можно было использовать эталоны из неё
            task = DockerHermione(
                self,
                frontend_source_type=SOURCE_TYPE_PRODUCTION if deps[SOURCE_TYPE_FRONT] == DEFAULT_BRANCH else SOURCE_TYPE_BRANCH,
                frontend_branch=self.Parameters.branch_name if deps[SOURCE_TYPE_FRONT] == DEFAULT_BRANCH else deps[SOURCE_TYPE_FRONT],
                java_source_type=SOURCE_TYPE_PRODUCTION if deps[SOURCE_TYPE_JAVA] == DEFAULT_BRANCH else SOURCE_TYPE_BRANCH,
                java_branch=deps[SOURCE_TYPE_JAVA],
                perl_source_type=SOURCE_TYPE_PRODUCTION if deps[SOURCE_TYPE_PERL] == DEFAULT_BRANCH else SOURCE_TYPE_BRANCH,
                perl_branch=deps[SOURCE_TYPE_PERL],
                mysql_source_type='latest',
                adfox_git_branch='pre-release-login',
            )
            task.enqueue()
            logging.debug('run_tests: create and run new task %d, wait for it' % task.id)
            self.Context.subtask_id = task.id
            self.Context.save()
            self.notify_pull_request()
            raise sdk2.WaitTask([task], ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)
        # TODO: в каком случае таска уже может быть в контексте?
        else:
            logging.debug('run_tests: task %d is in context' % task_id)
            task = sdk2.Task.find(id=task_id).limit(1).first()
            logging.debug('run_tests: task status is %s' % task.status)
            if task.status == ctt.Status.SUCCESS:
                logging.debug('run_tests: task successfully finished')
                report = task.Context.report_data
                if report['failed'] > 0:
                    raise TaskFailure('Tests failed')
            elif task.status in ctt.Status.Group.FINISH + ctt.Status.Group.BREAK:
                raise Exception('Test task failed')
            else:
                logging.debug('run_tests: task is not finished, continue waiting for')
                raise sdk2.WaitTask([task], ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)

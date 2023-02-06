# coding: utf-8
import json
import logging
import math
import os
import re
import shutil

import jinja2
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.errors import TaskError
from sandbox.common.utils import singleton_property
from sandbox.projects.sandbox_ci.resources import SANDBOX_CI_ARTIFACT
from sandbox.sdk2 import ResourceData

from sandbox.projects.partner.settings import \
    AUTOTEST_STANDS, \
    AutotestStandType, \
    AutotestBuildType
from sandbox.projects.partner.tasks.e2e_tests.misc.resources import \
    JSONReportResource, PartnerJSONReportResource
from sandbox.projects.partner.tasks.misc import exec_cmd
from sandbox.projects.partner.tasks.misc.partner_front_task_base import PartnerFrontTaskBase
from sandbox.projects.partner.utils.reporter import \
    SandboxReporter, \
    STATUSES_CLASSES

REPORT_PROJECT_PARTNER = 'partner'
REPORT_PROJECT_ADFOX = 'adfox-ui-interfaces'


def get_partner_stage_semaphore_id(url):
    return re.findall(r'https://(.*)\.beta\.partner\.yandex\.ru', url)[0]


def get_adfox_stage_semaphore_id(url):
    return re.findall(r'https://(.*)\.autotest\.yd\.adfox\.yandex\.ru', url)[0]


def get_partner_write_acquires_list(stages_url_list):
    return [
        get_partner_write_acquire(url) for url in stages_url_list
    ]


def get_partner_write_acquire(url):
    return configure_semaphore_by_name(
        'partner/autotest/write/%s' % get_partner_stage_semaphore_id(url)
    )


def get_partner_read_acquire(url):
    return configure_semaphore_by_name(
        'partner/autotest/read/%s' % get_partner_stage_semaphore_id(url)
    )


def configure_semaphore_by_name(name):
    return ctt.Semaphores.Acquire(
        name=name,
        capacity=1,
        weight=1
    )


def get_partner_read_acquires_list(stages_url_list):
    return [
        get_partner_read_acquire(url) for url in stages_url_list
    ]


def get_adfox_acquire(url):
    return configure_semaphore_by_name(
        'adfox/autotest/%s' % get_adfox_stage_semaphore_id(url)
    )


def get_read_acquires(stages, need_adfox=True):
    partner_acquires = get_partner_read_acquires_list(
        map(lambda s: s['partner_url'], stages)
    )
    adfox_acquires = [
        get_adfox_acquire(stage['adfox_url']) for stage in stages
    ] if need_adfox else []

    return partner_acquires + adfox_acquires


def get_write_acquires(stages, need_adfox=True):
    partner_acquires = [
        get_partner_write_acquire(stage['partner_url']) for stage in stages
    ]
    adfox_acquires = [
        get_adfox_acquire(stage['adfox_url']) for stage in stages
    ] if need_adfox else []

    return partner_acquires + adfox_acquires


def get_stands(side, build_type=AutotestBuildType.ANY, count=None):
    """
    side: AutotestStandType.{ADFOX,PARTNER,ANY}
    build_type: AutotestBuildType.{CI,RELEASE,ANY}
    count?: int
    """
    if side == AutotestStandType.ANY:
        allowed_stands = AUTOTEST_STANDS
    else:
        allowed_stands = [x for x in AUTOTEST_STANDS if x['type'] == side]

    if build_type != AutotestBuildType.ANY:
        allowed_stands = [x for x in allowed_stands if x['build_type'] == build_type]

    if count is not None and len(allowed_stands) < count:
        raise Exception('Insufficient number of stands, current %d' % len(allowed_stands))

    return allowed_stands[:count]


def get_all_adfox_stands(stand_name):
    return [x for x in AUTOTEST_STANDS if x['adfox_url'].startswith('https://%s' % stand_name)]


def get_stand_by_name(name):
    return next(x for x in AUTOTEST_STANDS if x['stage_name'] == name)


def get_stand_by_adfox_url(url):
    return next(x for x in AUTOTEST_STANDS if x['adfox_url'] == url)


def format_report_message(title, report_summary, report_url):
    return '{}: {} пройдено, {} упало.\nОтчет {}'.format(
        title,
        report_summary['passed'],
        report_summary['failed'],
        report_url
    )


def render_template(template, data, template_dir):
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        extensions=['jinja2.ext.do']
    ).get_template(template).render(data)


class HermioneReportLayer(PartnerFrontTaskBase):
    class Context(PartnerFrontTaskBase.Context):
        json_report_filepath = None
        report_data = None

    def make_report(self, additional_data=None, **attrs):
        logging.debug('HermioneReportLayer.make_report')

        report_attrs = dict(
            project=REPORT_PROJECT_PARTNER,
            tool='hermione',
            type='hermione-report',
            build_context='build',
            build_id=str(self.id),
            sandbox_task_id=self.id,
        )

        report_attrs.update(attrs)
        report_data = self.process_report(**report_attrs)
        if additional_data:
            report_data.update(additional_data)
        self.Context.report_data = report_data
        logging.debug('HermioneReportLayer.report_data')
        logging.debug(report_data)
        self.Context.save()

        self.make_finish_callback()

    def publish_report(self, file_path):
        ResourceData(
            PartnerJSONReportResource(
                self,
                'JSON Report',
                file_path
            )
        ).ready()

    def make_finish_callback(self):
        report_data = self.Context.report_data

        if not report_data:
            self.make_failure_callback('подробности в логах', self.task_url)
            return

        report_url = self.report_url
        title = self.report_message_title

        message = format_report_message(title, report_data, report_url)
        self.send_message(message)

    def process_report(self, **resource_attrs):
        logging.debug('HermioneReportLayer.process_report')

        report_dir = self.report_dir_path
        if not os.path.exists(report_dir):
            raise TaskError('Report was not generated')

        self.reporter.save_report(report_dir, self.report_description, **resource_attrs)

        return self.read_report_data()

    def read_report_data(self):
        report_path = self.Context.json_report_filepath
        logging.debug('HermioneReportLayer.read_report_data %s', report_path)

        statistics = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'retries': 0,
            'passed_percent': 0,
        }
        with open(report_path) as file:
            data = json.load(file)

            for key in data:
                statistics['total'] += 1

                if data[key]['status'] == 'skipped':
                    statistics['skipped'] += 1
                elif data[key]['status'] == 'success':
                    statistics['passed'] += 1
                elif data[key]['status'] == 'fail':
                    statistics['failed'] += 1

                if 'retries' in data[key]:
                    # В retries содержится массив из состояний всех запусков, поэтому минус 1
                    statistics['retries'] += len(data[key]['retries']) - 1
            statistics['passed_percent'] = math.floor(100.0 * statistics['passed'] / statistics['total']) \
                if statistics['total'] > 0 else 0
            return statistics

    def get_report_template_data(self):
        summary_data = self.Context.report_data

        logging.debug('summary_data')
        logging.debug(summary_data)
        if not summary_data:
            return None

        artifacts = self.reporter.get_artifacts_for_template()
        task_status = self.Context.task_status

        if task_status not in STATUSES_CLASSES:
            return ''

        template_data = dict(
            resources=artifacts,
            status_class=STATUSES_CLASSES[task_status],
            status_text=task_status,
        )
        template_data.update(summary_data)
        return template_data

    def download_autotests_screens(self, pl):
        # TODO не скачивать напрямую из Git LFS - публиковать в sandbox-ресурсы
        exec_cmd(['git-lfs', 'pull', '-I', 'test/autotests/screens'], pl)

    def download_screens_for_screenshooter(self, pl):
        # @see download_autotests_screens
        exec_cmd(['git-lfs', 'pull', '-I', 'test/screenshooter/screens'], pl)

    @sdk2.header()
    def report(self):
        logging.debug('HermioneReportLayer.report header')

        data = self.get_report_template_data()
        if not data:
            logging.warn('report header failed to get report template data')
            return

        return render_template('header.html', data, self.template_dir_path)

    @property
    def report_description(self):
        return 'Hermione HTML report'

    @property
    def report_dir_path(self):
        return os.path.join(os.getcwd(), 'test/autotests/hermione/shooter-reports/commonReport')

    @property
    def report_message_title(self):
        return 'Тестирование завершено'

    @property
    def report_url(self):
        res = self.reporter.get_artifacts_for_template()
        return res[0]['url'] + '/index.html' if res else None

    @property
    def template_dir_path(self):
        raise Exception('Template dir should be explicitly defined')

    @singleton_property
    def reporter(self):
        return SandboxReporter(self)

    def publish_json_report(self, json_report_path, branch, project=REPORT_PROJECT_PARTNER):
        """
        Публикация ресурсов report json.
        Копия файлов делается потому что нельзя публиковать файл одновременно в разных ресурсах.

        :param json_report_path:
        :type json_report_path
        :param branch: ветка исходников
        :type branch: str
        :param project: проект testcope
        :type project: str
        """
        logging.debug('Публикация ресурсов JsonReport: ' + json_report_path + '...')

        # ресурс для общих нужд
        testpalm_report_copy = json_report_path.replace('.json', '-testpalm.json')
        shutil.copyfile(json_report_path, testpalm_report_copy)
        res_type = JSONReportResource if project == REPORT_PROJECT_ADFOX else PartnerJSONReportResource

        ResourceData(res_type(
            self, 'JSON Report', testpalm_report_copy
        )).ready()

        # ресурс для TestCop
        testcop_report_copy = json_report_path.replace('.json', '-testcop.json')
        shutil.copyfile(json_report_path, testcop_report_copy)

        ResourceData(SANDBOX_CI_ARTIFACT(
            self, 'JSON Report - testcop', testcop_report_copy,
            tool='hermione', type='json-reporter', project=project, branch=branch
        )).ready()

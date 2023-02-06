import textwrap
import pytest

from sandbox.projects.yabs.release.version.version import ServerVersion
from sandbox.projects.yabs.qa.template_utils import get_template
from sandbox.projects.yabs.release.tasks.DeployYabsCS import TEMPLATES_DIR, ReportData, Events


def get_report_data(
        component_name='yabs_server',
        status=Events.deployment_succeeded,
        release_type='testing',
        major_version=641,
        minor_version=3,
        task_id=1267716164,
        task_type='DEPLOY_YABS_CS',
        project='yabscs',
        namespace=1,
        deployed_server_versions=None,
        deployed_cs_versions=None,
):
    return ReportData(
        task_id=task_id,
        task_type=task_type,
        component_name=component_name,
        status=status,
        release_type=release_type,
        major_version=major_version,
        minor_version=minor_version,
        project=project,
        namespace=namespace,
        deployed_cs_versions=deployed_cs_versions,
        deployed_server_versions=deployed_server_versions,
    )


class TestReportCSDeploymentStatusYachats(object):

    @pytest.mark.parametrize(
        'status', (
            Events.deployment_succeeded,
            Events.already_performed,
            Events.deployment_scheduled,
            Events.deployment_started
        )
    )
    def test_yachats(self, status):
        report_template_j2 = get_template('cs_deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        {icon} yabs_server r641-3 deployment to [yabscs1](https://yabscs1.n.yandex-team.ru/) {text}

        Sent by [DEPLOY_YABS_CS #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        '''.format(icon=status.value.icon, text=status.value.text)).lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=status).as_dict(transport='yachats', mentions=['igorock']))

    @pytest.mark.parametrize(
        ('status', 'explanation'),
        (
            (Events.deployment_timed_out, '@igorock please, finalize the deployment manually then restart this task by pressing the `Run` button'),
            (Events.deployment_failed, '@igorock please, perform the deployment manually, failure of this task will be ignored by release process, no additional action is required'),
            (Events.version_syncronization_temporary_failed, 'Task will wait for synchronization and will be restarted automatically'),
            (Events.version_syncronization_failed, '@igorock please, fix the version mismatch then restart this task by pressing the `Run` button'),
            (Events.namespace_selection_failed, '@igorock please, perform the deployment manually, failure of this task will be ignored by release process, no additional action is required'),
        )
    )
    def test_yachats_failed(self, status, explanation):
        report_template_j2 = get_template('cs_deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        {icon} yabs_server r641-3 deployment {text}

        ```
        Frontend versions:
          640-1.54321: 1 service
          641-3.12345: 2 services
        CS versions:
          Namespace 1: [640-1.54321]
          Namespace 2: [639-2.20000]
        ```
        {explanation}

        Sent by [DEPLOY_YABS_CS #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        '''.format(explanation=explanation, icon=status.value.icon, text=status.value.text)).lstrip('\n')

        deployed_server_versions = {
            ServerVersion(641, 3, 12345): ['stable', 'prestable'],
            ServerVersion(640, 1, 54321): ['prod'],
        }
        deployed_cs_versions = {
            '1': [ServerVersion(640, 1, 54321)],
            '2': [ServerVersion(639, 2, 20000)]
        }

        assert expected_text == report_template_j2.render(
            get_report_data(
                status=status,
                deployed_server_versions=deployed_server_versions,
                deployed_cs_versions=deployed_cs_versions,
                namespace=None,
            ).as_dict(transport='yachats', mentions=['igorock'])
        )


class TestReportCSDeploymentStatusTelegram(object):

    @pytest.mark.parametrize(
        'status', (
            Events.deployment_succeeded,
            Events.already_performed,
            Events.deployment_scheduled,
            Events.deployment_started
        )
    )
    def test_telegram(self, status):
        report_template_j2 = get_template('cs_deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        {icon} yabs\\_server r641\\-3 deployment to [yabscs1](https://yabscs1.n.yandex-team.ru/) {text}

        \\#deploy \\#yabs\\_server \\#r641 \\#r641\\_3
        Sent by [DEPLOY\\_YABS\\_CS \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        '''.format(icon=status.value.icon, text=status.value.text)).lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=status).as_dict(transport='telegram', mentions=['igorock']))

    @pytest.mark.parametrize(
        ('status', 'explanation'),
        (
            (Events.deployment_timed_out, '@igorock please, finalize the deployment manually then restart this task by pressing the `Run` button'),
            (Events.deployment_failed, '@igorock please, perform the deployment manually, failure of this task will be ignored by release process, no additional action is required'),
            (Events.version_syncronization_temporary_failed, 'Task will wait for synchronization and will be restarted automatically'),
            (Events.version_syncronization_failed, '@igorock please, fix the version mismatch then restart this task by pressing the `Run` button'),
            (Events.namespace_selection_failed, '@igorock please, perform the deployment manually, failure of this task will be ignored by release process, no additional action is required'),
        )
    )
    def test_telegram_failed(self, status, explanation):
        report_template_j2 = get_template('cs_deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        {icon} yabs\\_server r641\\-3 deployment {text}

        ```
        Frontend versions:
          640-1.54321: 1 service
          641-3.12345: 2 services
        CS versions:
          Namespace 1: [640-1.54321]
          Namespace 2: [639-2.20000]
        ```
        {explanation}

        \\#deploy \\#yabs\\_server \\#r641 \\#r641\\_3
        Sent by [DEPLOY\\_YABS\\_CS \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        '''.format(explanation=explanation, icon=status.value.icon, text=status.value.text)).lstrip('\n')

        deployed_server_versions = {
            ServerVersion(641, 3, 12345): ['stable', 'prestable'],
            ServerVersion(640, 1, 54321): ['prod'],
        }
        deployed_cs_versions = {
            '1': [ServerVersion(640, 1, 54321)],
            '2': [ServerVersion(639, 2, 20000)]
        }

        assert expected_text == report_template_j2.render(
            get_report_data(
                status=status,
                deployed_server_versions=deployed_server_versions,
                deployed_cs_versions=deployed_cs_versions,
                namespace=None,
            ).as_dict(transport='telegram', mentions=['igorock'])
        )

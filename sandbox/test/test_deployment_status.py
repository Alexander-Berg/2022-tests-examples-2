import textwrap
import pytest

from sandbox.projects.yabs.qa.template_utils import get_template
from sandbox.projects.yabs.release.tasks.DeployNannySnapshots import TEMPLATES_DIR, ReportData, Events, DeploymentLink


def get_report_data(
        component_name='yabs_server',
        deployment_id=None,
        dashboard_id='d',
        recipe_name='recipe',
        active_deployments=None,
        status=Events.deployment_succeeded,
        release_type='testing',
        major_version=641,
        minor_version=3,
        task_id=1267716164,
        task_type='YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS',
):
    return ReportData(
        task_id=task_id,
        task_type=task_type,
        component_name=component_name,
        status=status,
        release_type=release_type,
        major_version=major_version,
        minor_version=minor_version,
        deployment_id=deployment_id,
        dashboard_id=dashboard_id,
        recipe_name=recipe_name,
        active_deployments=active_deployments,
    )


class TestReportDeploymentStatusHtml(object):

    @pytest.mark.parametrize('status', (Events.deployment_succeeded, Events.deployment_rejected, Events.deployment_scheduled, Events.deployment_started))
    def test_html(self, status):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        {i} yabs_server r641-3 deployment <a href="https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1" target="_blank">recipe</a> to testing {t}

        Sent by <a href="http://sandbox.yandex-team.ru:8081/task/1267716164" target="_blank">YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS 1267716164</a>
        '''.format(i=status.value.icon, t=status.value.text)).lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=status, deployment_id='1').as_dict(transport='html', mentions=['igorock']))

    def test_html_deployment_precondition_failed(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U000026D4 yabs_server r641-3 deployment to testing cannot be started

        <a href="https://staff.yandex-team.ru/igorock" target="_blank">igorock</a> please, reject or finalize following deployments:
        <a href="https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/2" target="_blank">active_recipe</a>
        and then restart this task by pressing the `Run` button

        Sent by <a href="http://sandbox.yandex-team.ru:8081/task/1267716164" target="_blank">YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS 1267716164</a>
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(
            active_deployments=[
                DeploymentLink('active_recipe', '2', 'd'),
            ],
            status=Events.deployment_precondition_failed,
        ).as_dict(transport='html', mentions=['igorock']))

    def test_html_stalled(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U00002757 yabs_server r641-3 deployment <a href="https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1" target="_blank">recipe</a> to testing stalled

        <a href="https://staff.yandex-team.ru/igorock" target="_blank">igorock</a> please, check if everything is okay

        Sent by <a href="http://sandbox.yandex-team.ru:8081/task/1267716164" target="_blank">YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS 1267716164</a>
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=Events.deployment_stalled, deployment_id='1').as_dict(transport='html', mentions=['igorock']))

    def test_html_timed_out(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = u'''
\U00002757 \U0000231B yabs_server r641-3 deployment <a href="https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1" target="_blank">recipe</a> to testing timed out

<a href="https://staff.yandex-team.ru/igorock" target="_blank">igorock</a> please, finalize the deployment manually then restart this task by pressing the `Run` button

Sent by <a href="http://sandbox.yandex-team.ru:8081/task/1267716164" target="_blank">YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS 1267716164</a>
'''.lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=Events.deployment_timed_out, deployment_id='1').as_dict(transport='html', mentions=['igorock']))


class TestReportDeploymentStatusYachats(object):

    @pytest.mark.parametrize('status', (Events.deployment_succeeded, Events.deployment_rejected, Events.deployment_scheduled, Events.deployment_started))
    def test_yachats(self, status):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        {icon} yabs_server r641-3 deployment [recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1) to testing {text}

        Sent by [YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        '''.format(icon=status.value.icon, text=status.value.text)).lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=status, deployment_id='1').as_dict(transport='yachats', mentions=['igorock']))

    def test_yachats_deployment_precondition_failed(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U000026D4 yabs_server r641-3 deployment to testing cannot be started

        @igorock please, reject or finalize following deployments:
        [active_recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/2)
        and then restart this task by pressing the `Run` button

        Sent by [YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(
            active_deployments=[
                DeploymentLink('active_recipe', '2', 'd'),
            ],
            status=Events.deployment_precondition_failed,
        ).as_dict(transport='yachats', mentions=['igorock']))

    def test_yachats_stalled(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U00002757 yabs_server r641-3 deployment [recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1) to testing stalled

        @igorock please, check if everything is okay

        Sent by [YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=Events.deployment_stalled, deployment_id='1').as_dict(transport='yachats', mentions=['igorock']))

    def test_yachats_timed_out(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U00002757 \U0000231B yabs_server r641-3 deployment [recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1) to testing timed out

        @igorock please, finalize the deployment manually then restart this task by pressing the `Run` button

        Sent by [YABS_SERVER_DEPLOY_NANNY_SNAPSHOTS #1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=Events.deployment_timed_out, deployment_id='1').as_dict(transport='yachats', mentions=['igorock']))


class TestReportDeploymentStatusTelegram(object):

    @pytest.mark.parametrize('status', (Events.deployment_succeeded, Events.deployment_rejected, Events.deployment_scheduled, Events.deployment_started))
    def test_telegram(self, status):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        {icon} yabs\\_server r641\\-3 deployment [recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1) to testing {text}

        \\#deploy \\#yabs\\_server \\#r641 \\#r641\\_3
        Sent by [YABS\\_SERVER\\_DEPLOY\\_NANNY\\_SNAPSHOTS \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        '''.format(icon=status.value.icon, text=status.value.text)).lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=status, deployment_id='1').as_dict(transport='telegram', mentions=['igorock']))

    def test_telegram_deployment_precondition_failed(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U000026D4 yabs\\_server r641\\-3 deployment to testing cannot be started

        @igorock please, reject or finalize following deployments:
        [active\\_recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/2)
        and then restart this task by pressing the `Run` button

        \\#deploy \\#yabs\\_server \\#r641 \\#r641\\_3
        Sent by [YABS\\_SERVER\\_DEPLOY\\_NANNY\\_SNAPSHOTS \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(
            active_deployments=[
                DeploymentLink('active_recipe', '2', 'd'),
            ],
            status=Events.deployment_precondition_failed,
        ).as_dict(transport='telegram', mentions=['igorock']))

    def test_telegram_stalled(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U00002757 yabs\\_server r641\\-3 deployment [recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1) to testing stalled

        @igorock please, check if everything is okay

        \\#deploy \\#yabs\\_server \\#r641 \\#r641\\_3
        Sent by [YABS\\_SERVER\\_DEPLOY\\_NANNY\\_SNAPSHOTS \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=Events.deployment_stalled, deployment_id='1').as_dict(transport='telegram', mentions=['igorock']))

    def test_telegram_timed_out(self):
        report_template_j2 = get_template('deployment_status.j2', templates_dir=TEMPLATES_DIR)

        expected_text = textwrap.dedent(u'''
        \U00002757 \U0000231B yabs\\_server r641\\-3 deployment [recipe](https://nanny.yandex-team.ru/ui/#/services/dashboards/catalog/d/deployments/catalog/1) to testing timed out

        @igorock please, finalize the deployment manually then restart this task by pressing the `Run` button

        \\#deploy \\#yabs\\_server \\#r641 \\#r641\\_3
        Sent by [YABS\\_SERVER\\_DEPLOY\\_NANNY\\_SNAPSHOTS \\#1267716164](http://sandbox.yandex-team.ru:8081/task/1267716164)
        ''').lstrip('\n')

        assert expected_text == report_template_j2.render(get_report_data(status=Events.deployment_timed_out, deployment_id='1').as_dict(transport='telegram', mentions=['igorock']))

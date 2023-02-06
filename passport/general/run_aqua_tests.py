from datetime import (
    datetime,
    timedelta,
)
import logging
from time import sleep

from ci.tasklet.common.proto import service_pb2
from passport.backend.clients.aqua import (
    AquaClient,
    make_allure_report_link,
)
from passport.backend.tasklets.aqua.proto import schema_tasklet
from startrek_client import Startrek
from tasklet.services.yav.proto import yav_pb2


DEFAULT_RETRIES = 2
DEFAULT_TIME_TO_WAIT = timedelta(minutes=50).total_seconds()
DEFAULT_POLL_INTERVAL = 30


logger = logging.getLogger(__name__)


class RunAquaTestsImpl(schema_tasklet.RunAquaTestsBase):
    def create_progress(self, id, icon, url, text):
        progress = service_pb2.TaskletProgress()
        progress.job_instance_id.CopyFrom(self.input.context.job_instance_id)
        progress.id = id
        progress.module = icon
        progress.url = url
        progress.text = text
        return progress

    def update_progress(self, tasklet_progress):
        self.ctx.ci.UpdateProgress(tasklet_progress)

    def send_report_to_st_issue(self, issue_key, tests_title, test_results):
        msg_parts = [
            f'Запуск java-автотестов %%{tests_title}%%:',
        ]
        for i, test_result in enumerate(test_results):
            total_suites = test_result['suites']['total']
            passed_suites = test_result['suites']['passed']
            failed_suites = test_result['suites']['failed'] + test_result['suites']['revoked']

            if failed_suites:
                tests_status = f'!!(red)**не OK**!! (упало {failed_suites} наборов тестов из {total_suites})'
            else:
                tests_status = f'!!(green)**OK**!! (прошло {passed_suites} наборов тестов)'
            msg_parts.append(
                '  * ((%s %s)): %s. ((%s Allure-отчёт))' % (
                    test_result['launch_url'],
                    'Запуск' if i == 0 else f'Перезапуск {i}',
                    tests_status,
                    test_result['allure_report_url'],
                ),
            )

        self.post_comment_to_st(issue_key, '\n'.join(msg_parts))

    def post_comment_to_st(self, issue_key, comment):
        spec = yav_pb2.YavSecretSpec(uuid=self.input.context.secret_uid, key='startrek.token')
        oauth_token = self.ctx.yav.get_secret(spec).secret
        startrek_client = Startrek(
            useragent='Passport CI',
            base_url='https://st-api.yandex-team.ru',
            token=oauth_token,
        )
        startrek_client.issues[issue_key].comments.create(text=comment, params={'isAddToFollowers': False})

    def run(self):
        launch_id = None
        aqua_client = AquaClient()
        test_results = []
        tests_title = None
        poll_interval = self.input.config.poll_interval or DEFAULT_POLL_INTERVAL
        are_tests_ok = False

        for i in range(self.input.config.retries or DEFAULT_RETRIES):
            title_appendix = '' if i == 0 else ' %s' % (i + 1)

            if launch_id is None:
                pack_id = self.input.config.pack_id
                if not pack_id:
                    raise ValueError('Pack_id is not set')
                rv = aqua_client.launch_pack(pack_id)
            else:
                rv = aqua_client.restart_launch(launch_id, failed_only=True)

            launch_id = rv['id']
            launch_url = rv['launchUrl']
            tests_title = rv['pack']['name']

            aqua_progress = self.create_progress(
                id='run_%s_aqua' % i,
                icon='AQUA',
                url=launch_url,
                text='',  # обновится позже
            )
            self.update_progress(aqua_progress)

            time_to_wait = self.input.config.time_to_wait or DEFAULT_TIME_TO_WAIT
            start_datetime = datetime.now()

            logging.debug('Waiting for tests...')
            while datetime.now() - start_datetime < timedelta(seconds=time_to_wait):
                rv = aqua_client.get_launch_info(launch_id)
                complete_suites_count = rv['passedSuites'] + rv['failedSuites'] + rv['revokedSuites']
                are_tests_complete = complete_suites_count == rv['totalSuites']
                are_tests_ok = are_tests_complete and rv['failedSuites'] + rv['revokedSuites'] == 0

                aqua_progress.text = '%s%s (%s)' % (tests_title, title_appendix, rv['launchStatus'])
                aqua_progress.progress = complete_suites_count / rv['totalSuites']
                if are_tests_complete:
                    if are_tests_ok:
                        aqua_progress.status = service_pb2.TaskletProgress.Status.SUCCESSFUL
                    else:
                        aqua_progress.status = service_pb2.TaskletProgress.Status.FAILED
                self.update_progress(aqua_progress)

                if are_tests_complete:
                    break
                else:
                    sleep(poll_interval)
            else:
                aqua_progress.text += ' - не дождались окончания тестов'
                aqua_progress.status = service_pb2.TaskletProgress.Status.FAILED
                self.update_progress(aqua_progress)
                # Тесты идут слишком долго, прекращаем ждать. Тасклет не ломаем: может, перезапуск нас спасёт.

            allure_report_url = make_allure_report_link(launch_id)
            test_results.append(
                {
                    'suites': {
                        'failed': rv['failedSuites'],
                        'passed': rv['passedSuites'],
                        'revoked': rv['revokedSuites'],
                        'total': rv['totalSuites'],
                    },
                    'launch_url': launch_url,
                    'allure_report_url': allure_report_url,
                },
            )

            allure_progress = self.create_progress(
                id='run_%s_allure' % i,
                icon='ALLURE',
                url=allure_report_url,
                text='Allure report%s' % title_appendix,
            )
            self.update_progress(allure_progress)

            logging.debug('Waiting for allure report...')
            while datetime.now() - start_datetime < timedelta(seconds=time_to_wait):
                rv = aqua_client.get_launch_info(launch_id)
                if rv['launchStatus'] == 'REPORT_READY':
                    allure_progress.status = service_pb2.TaskletProgress.Status.SUCCESSFUL
                    self.update_progress(allure_progress)
                    break
                elif rv['launchStatus'] == 'REPORT_FAILED':
                    allure_progress.text += ' - произошла ошибка при построении отчёта'
                    allure_progress.status = service_pb2.TaskletProgress.Status.FAILED
                    self.update_progress(allure_progress)
                    break
                else:
                    sleep(poll_interval)
            else:
                allure_progress.text += ' - не дождались построения отчёта'
                allure_progress.status = service_pb2.TaskletProgress.Status.FAILED
                self.update_progress(allure_progress)
                # При невозможности построить отчёт не ломаем тасклет: данные можно и в Акве посмотреть,
                # хоть это и менее удобно.

            if are_tests_ok:
                # Тесты прошли, перезапуск не требуется
                break

        logger.debug('Test results: %s', test_results)
        st_issue = self.input.config.send_report_to_st_issue
        if st_issue:
            self.send_report_to_st_issue(st_issue, tests_title, test_results)

        if not are_tests_ok:
            raise RuntimeError('Some tests have failed')

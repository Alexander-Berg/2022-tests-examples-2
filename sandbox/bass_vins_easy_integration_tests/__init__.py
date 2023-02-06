# -*- coding: utf-8 -*-

import logging
import requests

import sandbox.projects.release_machine.core.task_env as task_env
from sandbox import sdk2
from sandbox.sandboxsdk.channel import channel
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper


logger = logging.getLogger('BassVinsEasyIntegrationTestTask')


def get_teamcity_link_mini(robot_pass=None, bass_url=None, vins_url=None):
    if robot_pass and bass_url and vins_url:
        config = {
            'buildType': {
                'id': 'VoiceServer_VinsDm_ManualIntegrationTesting'
            },
            'properties': {
                'property': [
                    {'name': 'yndx.license_server', 'value': '1'},
                    {'name': 'env.BASS_INTEGRATION_URL', 'value': bass_url},
                    {'name': 'env.VINS_INTEGRATION_URL', 'value': vins_url},
                    {'name': 'env.YENV_TYPE', 'value': 'development'}
                ]
            }
        }
        custom_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        r = requests.post('http://teamcity.yandex-team.ru/httpAuth/app/rest/buildQueue',
                          auth=('robot-bassist', robot_pass),
                          json=config,
                          headers=custom_headers)

        logger.info(str(r.status_code))
        if r.status_code == 200:
            result = r.json()
            logger.info(str(result))
            run_id = result.get('id', 0)
            base_text = 'https://teamcity.yandex-team.ru/viewLog.html?buildId='
            if run_id:
                base_text += str(run_id)
                return base_text
            else:
                return None
        else:
            return None
    else:
        return None


def create_combined_comment(bass_yappy, vins_hamster, bass_hamster, hamster_vs_hamster, hamster_vs_yappy):
    comment = '====Полуавтоматический запуск интеграционных тестов\n'
    comment += '//Полуавтоматический запуск происходит через выполнение Sandbox таска BASS_VINS_EASY_INTEGRATION_TESTS_TASK.//\n\n'

    if hamster_vs_yappy and vins_hamster and bass_yappy:
        part_hamster_vs_yappy = u'Запущен прогон интеграционных тестов по Yappy бете этого релиза: ' + hamster_vs_yappy + '\n'
        part_hamster_vs_yappy += u'<{Подробнее об используемых бетах для этого прогона интеграционных тестов под катом.\nIntegration tests VINS %%'
        part_hamster_vs_yappy += vins_hamster + '%% vs BASS %%' + bass_yappy + '%%\n}>\n\n'
        comment = comment + part_hamster_vs_yappy
    else:
        part_hamster_vs_yappy = u'Возникли проблемы с полуавтомтическим запуском прогона интеграционных тестов по Yappy бете этого релиза. '
        part_hamster_vs_yappy += 'Это могло произойти по разным причинам. Но эти же тесты всегда можно запустить вручную.\n'
        part_hamster_vs_yappy += u'<{Подробности ручного запуска под катом.\nИнструкция по запуску интеграционных тестов вручную: '
        part_hamster_vs_yappy += u'https://wiki.yandex-team.ru/Alice/backend/BASS-Release-Machine/Ruchnojj-zapusk-integracionnyx-testov-VINS-BASS/\n'
        part_hamster_vs_yappy += 'По инструкции можно прогнать интеграционные тесты против Yappy беты для этого релиза'
        if bass_yappy:
            part_hamster_vs_yappy += u' (в поле BASS url прописать %%' + bass_yappy + '%%)'
        part_hamster_vs_yappy += '.\n}>\n\n'
        comment = comment + part_hamster_vs_yappy

    if hamster_vs_hamster and vins_hamster and bass_yappy:
        part_hamster_vs_hamster = u'Для сравнения запущен прогон интеграционных тестов по хамстерам VINS и BASS: ' + hamster_vs_hamster + '\n'
        part_hamster_vs_hamster += u'<{Подробнее об используемых бетах для этого прогона интеграционных тестов под катом.\n'
        part_hamster_vs_hamster += 'Integration tests VINS %%' + vins_hamster + '%% vs BASS %%' + bass_hamster + '%%\n}>\n\n'
        comment = comment + part_hamster_vs_hamster
    else:
        part_hamster_vs_hamster = u'Возникли проблемы с полуавтомтическим запуском прогона интеграционных тестов по хамстерам BASS и VINS. '
        part_hamster_vs_hamster += u'Они бывают нужны для сравнения с прогоном интеграционных тестов по актуальной Yappy бете этого релиза. '
        part_hamster_vs_hamster += u'Полуавтомтический запуск мог не произойти по разным причинам. Но эти же тесты всегда можно запустить вручную, если в этом есть необходимость.\n'
        part_hamster_vs_hamster += u'<{Подробности ручного запуска под катом.\nИнструкция по запуску интеграционных тестов вручную: '
        part_hamster_vs_hamster += u'https://wiki.yandex-team.ru/Alice/backend/BASS-Release-Machine/Ruchnojj-zapusk-integracionnyx-testov-VINS-BASS/\n'
        part_hamster_vs_hamster += 'По инструкции можно прогнать интеграционные тесты против BASS hamster'
        if bass_hamster:
            part_hamster_vs_hamster += u' (в поле BASS url прописать %%' + bass_hamster + '%%)'
        part_hamster_vs_hamster += '.\n}>\n\n'
        comment = comment + part_hamster_vs_hamster

    return comment


def post_comment(robot_token=None, comment_text=None, ticket_target=None):
    if robot_token:
        content = {'text': comment_text}
        custom_headers = {'Content-Type': 'application/json',
                          'Accept': 'application/json',
                          'Authorization': 'OAuth ' + robot_token}
        target = 'https://st-api.yandex-team.ru/v2/issues/' + str(ticket_target) + '/comments'
        logger.info(str(ticket_target))
        r = requests.post(target,
                          json=content,
                          headers=custom_headers)
        logger.info(str(r.status_code))


class BassVinsEasyIntegrationTestsTask(sdk2.Task):
    '''
        Run Bass Vins Easy Integration Tests
    '''

    class Parameters(sdk2.Task.Parameters):
        release_number = sdk2.parameters.Integer('release_number', default=0, required=True)

    class Requirements(sdk2.Requirements):
        client_tags = task_env.TaskTags.all_rm & task_env.TaskTags.startrek_client
        environments = [
            task_env.TaskRequirements.startrek_client,
        ]

    def get_release_ticket(self):
        try:
            st_token = channel.task.get_vault_data('BASS', 'robot_bassist_startrek_oauth_token')
        except Exception as exc:
            eh.log_exception('Failed to get robot pass and token from vault', exc)
            st_token = False

        if not st_token:
            return 'ALICERELEASE-1'

        st_helper = STHelper(st_token)
        c_info = rmc.COMPONENTS['bass']()
        release_ticket = st_helper.find_ticket_by_release_number(self.Parameters.release_number, c_info).key
        return release_ticket

    def on_execute(self):
        release_number = self.Parameters.release_number

        target_ticket = None
        if release_number > 0:
            target_ticket = self.get_release_ticket()

        target_url = None
        if release_number > 0:
            target_url = 'http://alice-bass-rm-branch-{}.yappy.yandex.ru/'.format(release_number)

        if target_url and target_ticket:
            logger.info(str(target_url))
            logger.info(str(target_ticket))
            # TeamCity tests
            try:
                robot_pass = channel.task.get_vault_data('BASS', 'robot_bassist_password')
                robot_token = channel.task.get_vault_data('BASS', 'robot_bassist_startrek_oauth_token')
            except Exception as exc:
                eh.log_exception('Failed to get robot pass and token from vault', exc)
                robot_pass = False
                robot_token = False
            if robot_pass and robot_token:
                target_vins = 'http://yappy_vins_hamster_0.yappy-slots.yandex-team.ru/speechkit/app/pa/'
                hamster_bass = 'http://bass.hamster.alice.yandex.net/'

                teamcity_link = get_teamcity_link_mini(str(robot_pass), target_url, target_vins)
                logger.info(teamcity_link)

                hamster_link = get_teamcity_link_mini(str(robot_pass), hamster_bass, target_vins)
                logger.info(hamster_link)

                combined_comment = create_combined_comment(target_url, target_vins, hamster_bass, hamster_link, teamcity_link)
                post_comment(str(robot_token), combined_comment, target_ticket)

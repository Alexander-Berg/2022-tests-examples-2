# -*- coding: utf-8 -*-

import logging
import requests

import sandbox.projects.release_machine.core.task_env as task_env
from sandbox import sdk2
from sandbox.sandboxsdk.channel import channel
import sandbox.projects.common.error_handlers as eh
from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper


ALICE_BASS_RM_URL = 'http://alice-bass-rm.yappy.yandex.ru/'
BASS_HAMSTER_URL = 'http://bass.hamster.alice.yandex.net/'
VINS_HAMSTER_URL = 'http://yappy_vins_hamster_0.yappy-slots.yandex-team.ru/speechkit/app/pa/'
logger = logging.getLogger('BassVinsTestsTask')


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


def create_minimalist_comment(verbose_release_id, hamster_vs_hamster, hamster_vs_yappy):
    comment = '====' + verbose_release_id + u' доступен на alice-bass-rm (yappy)\n'
    comment += '<{Details\n\n'
    comment += u'**Проверить версию BASS на релизной бете:** %%curl "' + ALICE_BASS_RM_URL + u'version"%%\n'
    comment += '\n#|\n'
    comment += u'|| **Интеграционные тесты** | **TeamCity** ||\n'
    comment += '|| VINS (hamster) vs BASS (alice-bass-rm) | ' + hamster_vs_yappy + '||\n'
    comment += '|| VINS (hamster) vs BASS (hamster) | ' + hamster_vs_hamster + '||\n'
    comment += '|#\n\n'
    comment += '#|\n'
    comment += '|| **Beta** | **Url** ||\n'
    comment += '|| alice-bass-rm | %%' + ALICE_BASS_RM_URL + '%% ||\n'
    comment += '|| BASS hamster | %%' + BASS_HAMSTER_URL + '%%||\n'
    comment += '|| VINS hamster | %%' + VINS_HAMSTER_URL + '%%||\n'
    comment += '|#\n'
    comment += '}>'
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


class BassVinsTestsTask(sdk2.Task):
    '''
        Run Bass Vins Tests
    '''

    class Parameters(sdk2.Task.Parameters):
        component_name = sdk2.parameters.String('component_name', default='bass', required=True)
        bass_url = sdk2.parameters.String('bass_url', default='http://bass-rc.n.yandex-team.ru/', required=True)
        vins_url = sdk2.parameters.String('vins_url', default='http://yappy_vins_hamster_0.yappy-slots.yandex-team.ru/speechkit/app/pa/', required=True)
        target_ticket = sdk2.parameters.String('target_ticket', default='ALICERELEASE-1', required=True)
        release_number = sdk2.parameters.Integer('release_number', default=0, required=True)
        release_number_debug = sdk2.parameters.Integer('release_number_debug', default=0, required=True)
        release_number_extracted = sdk2.parameters.Integer('release_number_extracted', default=0, required=True)
        svn_ssh_url = sdk2.parameters.String('svn_ssh_url', default='', required=True)
        tag_number = sdk2.parameters.String('tag_number', default='no_tag', required=True)
        branch_number = sdk2.parameters.String('branch_number', default='no_branch', required=True)
        tag_num = sdk2.parameters.Integer('tag_num', default=0, required=True)
        branch_num = sdk2.parameters.Integer('branch_num', default=0, required=True)
        minimalistic_comments = sdk2.parameters.Integer('minimalistic_comments', default=0, required=True)
        verbose_release_id = sdk2.parameters.String('verbose_release_id', default='bass', required=True)

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
        c_info = rmc.COMPONENTS[self.Parameters.component_name]()
        release_ticket = st_helper.find_ticket_by_release_number(self.Parameters.release_number, c_info).key
        return release_ticket

    def on_execute(self):
        target_url = self.Parameters.bass_url
        target_ticket = self.Parameters.target_ticket
        target_vins = self.Parameters.vins_url
        release_number = self.Parameters.release_number
        release_number_debug = self.Parameters.release_number_debug
        verbose_release_id = self.Parameters.verbose_release_id

        if (release_number > 0) and (release_number_debug <= 0):
            target_ticket = self.get_release_ticket()

        if release_number_debug > 0:
            target_url = 'http://alice-bass-rm-branch-{}.yappy.yandex.ru/'.format(release_number_debug)
        elif release_number > 0:
            target_url = 'http://alice-bass-rm-branch-{}.yappy.yandex.ru/'.format(release_number)

        if target_url and target_ticket and target_vins:
            logger.info(str(target_url))
            logger.info(str(target_ticket))
            logger.info(str(target_vins))
            # TeamCity tests
            try:
                robot_pass = channel.task.get_vault_data('BASS', 'robot_bassist_password')
                robot_token = channel.task.get_vault_data('BASS', 'robot_bassist_startrek_oauth_token')
            except Exception as exc:
                eh.log_exception('Failed to get robot pass and token from vault', exc)
                robot_pass = False
                robot_token = False
            if robot_pass and robot_token:
                teamcity_link = get_teamcity_link_mini(str(robot_pass), target_url, target_vins)
                logger.info(teamcity_link)
                hamster_bass = 'http://bass.hamster.alice.yandex.net/'
                hamster_link = get_teamcity_link_mini(str(robot_pass), hamster_bass, target_vins)
                logger.info(hamster_link)
                combined_comment = create_minimalist_comment(verbose_release_id, hamster_link, teamcity_link)
                post_comment(str(robot_token), combined_comment, target_ticket)

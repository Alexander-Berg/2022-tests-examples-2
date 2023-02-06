# -*- coding: utf-8 -*-

import datetime
import json
import logging
import requests

import sandbox.projects.common.error_handlers as eh
import sandbox.projects.release_machine.core.task_env as task_env

from sandbox import sdk2
from sandbox.sandboxsdk.channel import channel


ALLOWED_SERVICES = ['BASS', 'VINS', 'hollywood', 'megamind', 'test']
ALLOWED_ST_QUEUES = ['ALICERELEASE', 'ALICERELTEST']
ALLOWED_TESTSUITES = ['alice', 'elari']

ASSESSORS_QUEUE = 'ALICEASSESSORS'

DEFAULT_ST_TICKET = 'ALICERELEASE-1'
DEFAULT_SERVICE = 'megamind'
DEFAULT_TESTSUITE = 'alice'

ST_API_URL = 'https://st-api.yandex-team.ru/v2/issues/'
TESTPALM_API_URL = 'https://testpalm-api.yandex-team.ru/'

MAD_HATTER_GROUP = 'WONDERLAND'
MAD_HATTER_ST_TOKEN = 'env.STARTREK_OAUTH_TOKEN'
MAD_HATTER_TESTPALM_TOKEN = 'env.TESTPALM_OAUTH_TOKEN'

LOGGER = logging.getLogger('BassRegressTestsTask')


def generate_headers(token=None):
    if token is None:
        return {}
    return {'Authorization': 'OAuth {}'.format(token),
            'Content-Type': 'application/json'}


# ticket = QUEUE-N, run - вида '5c00574c798633871cb92380' -- только номер от /alice/testrun/5c00574c798633871cb92380
def add_testrun_to_st(ticket, run, st_header):
    link_run = 'testrun/alice/' + run
    data = {"relationship": "relates", "key": link_run, "origin": "ru.yandex.testpalm"}
    raw_data = json.dumps(data, ensure_ascii=False, separators=(",", ": "))
    raw_data = raw_data.encode('utf-8')

    url = ST_API_URL + ticket + '/remotelinks?notifyAuthor=false&backlink=false'

    resp = requests.post(url, data=raw_data, headers=st_header)
    LOGGER.info('Request to {url} with body {body} completed with code {code}, text: {text}'.format(
        url=resp.request.url, body=resp.request.body, code=resp.status_code, text=resp.text))

    if not resp.json():
        resp = requests.post(url, data=raw_data, headers=st_header)
        LOGGER.info('Retry request to {url} with body {body} failed with code {code}, text: {text}'.format(
            url=resp.request.url, body=resp.request.body, code=resp.status_code, text=resp.text))
        return resp if resp.json() else []
    return resp


# title, suite_id - строка, tags - список строк, queue, num - строки 'QUEUE-NUM'
def create_run(suite_id, title, tags, ticket, alice_run_test_suite, st_header, testpalm_header):
    parentIssue = {"id": ticket, "trackerId": "Startrek"}

    params = {"include": "id,title"}
    payload = {
        "tags": tags,
        "title": title,
        "testSuite": {
            "id": suite_id
        },
        "parentIssue": parentIssue,
    }

    response = requests.post(alice_run_test_suite, json=payload, params=params, headers=testpalm_header)
    if response.status_code != 200:
        LOGGER.info("Unable to create testpalm run, code: {code}, body: {body}".format(code=response.status_code, body=response.text))
        return
    run = next(iter(response.json()), {})
    run_id = run['id']
    add_resp = add_testrun_to_st(ticket, run_id, st_header)
    # Accept 409 for workaround https://st.yandex-team.ru/ALICEINFRA-550#601802d25424701c040d69ff
    if add_resp == [] or not (add_resp.status_code == 201 or add_resp.status_code == 409):
        LOGGER.info('Can not add run into ticket')
        return []
    return run


def get_suites(release, alice_suite_url, testpalm_header):
    if release not in ALLOWED_SERVICES:
        LOGGER.info('Wrong release tag')
        return []

    params = {"include": "id,title,tags", "expression": '''{{"type": "EQ", "key": "tags", "value": "{tag}" }}'''.format(tag=release)}
    resp = requests.get(alice_suite_url, headers=testpalm_header, params=params)

    if not resp.text:  # не получили сьюты
        return []
    else:
        return resp.json()


def create_assessors_ticket(release, ticket, runs, st_header):
    runs_in_ticket = ''
    for el in runs:
        runs_in_ticket += el + '\n'
    description = u"Релиз " + release + '\n\n' + u"Релизный тикет " + ticket + '\n\n' + '**В конфиг колонок добавить флаги !!only_100_percent_flags,debug_mode,enable_full_rtlog!!**' + '\n\n' + u"Список ранов:\n\n" + '<[' + runs_in_ticket + ']>' # noqa
    description += '\n\n' + u"Инструкция по тестированию https://wiki.yandex-team.ru/alicetesting/assessors-and-alice/"
    if release == 'megamind':
        # VINS http://megamind-rc.alice.yandex.net/speechkit/app/pa/
        # BASS http://localhost:86/
        # Uniproxy wss://uniproxy.alice.yandex.net/uni.ws
        description += '\n\n' + u"Релизные урлы:\n**VINS** %%http://megamind-rc.alice.yandex.net/speechkit/app/pa/%%"
        description += u"\n**BASS** %%http://localhost:86/%%"
        description += u"\n**Uniproxy** %%wss://uniproxy.alice.yandex.net/uni.ws%%"

    data = {"queue": ASSESSORS_QUEUE, "type": "task", "summary": u"Тестирование релиза " + release + " " + ticket, "description": description, "parent": ticket}
    raw_data = json.dumps(data, ensure_ascii=False, separators=(",", ": "))
    raw_data = raw_data.encode('utf-8')

    resp = requests.post(ST_API_URL, data=raw_data, headers=st_header)

    if not resp.json():
        return []
    return resp


def get_item_title(release, item):
    if release == 'hollywood':
        return item['title']
    else:
        return item["title"][:item["title"].find(']') + 1]


# release, ticket - строки
def create_regress(release, ticket, testsuite, st_token, testpalm_token):
    # Example: {'Authorization': 'OAuth testpalm_token', "Content-Type": "application/json"}
    testpalm_header = generate_headers(testpalm_token)

    # Example: {'Authorization': 'OAuth st_token', "Content-Type": "application/json"}
    st_header = generate_headers(st_token)

    # Example: https://testpalm-api.yandex-team.ru/testrun/alice/create/
    alice_run_suite_url = TESTPALM_API_URL + "testrun/" + testsuite + "/create/"

    # Example: https://testpalm-api.yandex-team.ru/testsuite/alice/
    alice_suite_url = TESTPALM_API_URL + "testsuite/" + testsuite

    date = str(datetime.datetime.now())
    date = date[8] + date[9] + '.' + date[5] + date[6]

    default_title = ' ' + ticket + ': ' + release.upper() + ' ' + date

    suites = get_suites(release, alice_suite_url, testpalm_header)

    list_runs_for_assessors = []

    if not suites:
        LOGGER.info('Can not get suites by ' + release + ' release tag')
        return
    else:
        for item in suites:
            item_title = get_item_title(release, item)
            title = item_title + default_title  # сорян, некрасивый костыль
            tags = item["tags"]
            suite_id = item["id"]
            run = create_run(suite_id, title, tags, ticket, alice_run_suite_url, st_header, testpalm_header)
            if not run:
                LOGGER.info('Can not create run ' + title)
            else:
                run_id = run['id']
                list_runs_for_assessors.append(item_title + ' ' + 'https://testpalm.yandex-team.ru/' + testsuite + '/testrun/' + str(run_id))

    create_assessors_ticket(release, ticket, list_runs_for_assessors, st_header)
    return


def is_allowed_st_queue(target_ticket):
    for st_queue in ALLOWED_ST_QUEUES:
        st_prefix = st_queue + '-'
        if target_ticket.beginswith(st_prefix):
            return True
    return False


class BassRegressTestsTask(sdk2.Task):
    '''
        Run Bass Regress Tests
    '''

    class Parameters(sdk2.Task.Parameters):
        target_service = sdk2.parameters.String('target_service',
                                                default=DEFAULT_SERVICE,
                                                required=True)
        target_ticket = sdk2.parameters.String('target_ticket',
                                               default=DEFAULT_ST_TICKET,
                                               required=True)
        testsuite = sdk2.parameters.String('testsuite',
                                           default=DEFAULT_TESTSUITE,
                                           required=True)

    class Requirements(sdk2.Requirements):
        client_tags = task_env.TaskTags.all_rm & task_env.TaskTags.startrek_client
        environments = [
            task_env.TaskRequirements.startrek_client,
        ]

    def on_execute(self):
        target_service = self.Parameters.target_service
        target_ticket = self.Parameters.target_ticket
        testsuite = self.Parameters.testsuite

        if not (testsuite in ALLOWED_TESTSUITES):
            LOGGER.error('Requested testsuite is not allowed')
            return

        if not (target_service in ALLOWED_SERVICES):
            LOGGER.error('Requested service is not allowed')
            return

        try:
            st_token = channel.task.get_vault_data(MAD_HATTER_GROUP, MAD_HATTER_ST_TOKEN)
            testpalm_token = channel.task.get_vault_data(MAD_HATTER_GROUP, MAD_HATTER_TESTPALM_TOKEN)
        except Exception as exc:
            eh.log_exception('Failed to get tokens from vault', exc)
            st_token = False
            testpalm_token = False

        if (not st_token) or (not testpalm_token):
            LOGGER.error('Testpalm and ST tokens are required')
            return

        create_regress(target_service,  # Example: BASS
                       target_ticket,   # Example: ALICERELEASE-1
                       testsuite,       # Example: alice or elari
                       st_token,
                       testpalm_token)

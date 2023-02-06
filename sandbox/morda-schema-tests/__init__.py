# coding=utf-8

import requests
import datetime
import time
import logging
import re
import os

from subprocess import check_output, STDOUT
from pprint import pprint

from sandbox import sdk2
from sandbox.sdk2 import yav
from sandbox.sdk2 import service_resources

from sandbox.projects.common.arcadia import sdk as arcadia_sdk
from sandbox.projects.common.vcs import arc


MIN_API_SEARCH_VER_0 = 21
MIN_API_SEARCH_VER_1 = 21

ARC_PATH = 'arcadia-arc:/#trunk'
MORDA_PATH = 'portal/main/'

# GITHUB_API_BASE_URL = 'https://github.yandex-team.ru/api/v3'
ST_API_BASE_URL = 'https://st-api.yandex-team.ru/v2/issues'
YQL_API_BASE_URL = 'https://yql.yandex.net/api/v2/'
INFRA_API_BASE_URL = 'https://infra-api.yandex-team.ru/v1/events'
BB_API_BASE_URL = 'https://bitbucket.browser.yandex-team.ru/rest/api/1.0/projects/ML/repos/morda-schema/branches?limit=1000'

YQL_REQUEST_TEMPLATE_ADD_TICKET = """
USE hahn;
INSERT INTO
  `home/morda/schema-tests/tickets`(versions, ticket)
VALUES
  ("VERSIONS", "TASK");
"""

YQL_REQUEST_TEMPLATE_CHECK_VERSIONS = """
USE hahn;
SELECT ticket
FROM
  `home/morda/schema-tests/tickets`
WHERE versions like 'VERSIONS'
"""

YQL_REQUEST_TEMPLATE_MINING = """
$script = @@#py
import urllib.parse

cgi_params = ['zen_extensions', 'lang', 'informersCard', 'new_nav_panel', 'app_id', 'morda_ng']

def get_all_cgi_params(url):
    global cgi_param
    result = ''
    if url:
        params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        parsed = { }
        for k, v in params.items():
            parsed[k] = v[0]
        for cgi in cgi_params:
            if parsed.get(cgi) is not None:
                result += parsed.get(cgi) + '___'
            else:
                result += 'none___'
        return result
    else:
        return 'bad'

def get_yesterday():
    import datetime
    return str(datetime.date.today() - datetime.timedelta(days=1))
@@;

$get_all_cgi_params = Python3::get_all_cgi_params(Callable<(Utf8?)->Utf8>, $script);
$get_yesterday = Python3::get_yesterday(Callable<()->Utf8>, $script);

$is_yesterday = ($table_name) -> {
    return $table_name == $get_yesterday();
};

USE hahn;

$tmp =
SELECT request, $get_all_cgi_params(CAST(request AS Utf8)) as cgi_params
FROM FILTER(`home/logfeller/logs/morda-access-log/1d`, $is_yesterday)
WHERE request like '/portal/api/PATH/2%app_version_name=SCHEMA_VERSION%'
    AND request like '%app_platform=PLATFORM%'
    AND request not like '%srcrwr%'
    AND $get_all_cgi_params(CAST(request AS Utf8)) != 'bad'
LIMIT 500;

SELECT SOME(request)
FROM $tmp
GROUP BY cgi_params
LIMIT 10;
"""

schema_directory = {
    'android_pp': "function_tests/tests/schema/api_search_v2_android",
    'android_bro':"function_tests/tests/schema/api_yabrowser_android",
    'ios_pp':     "function_tests/tests/schema/api_search_v2_ios",
    'ios_bro':    "function_tests/tests/schema/api_yabrowser_ios",
}

regexp = {
    'android_pp':  re.compile('release/android/(\d+\.\d+)$'),
    'android_bro': re.compile('release/android/(\d+\.\d+)$'),
    'ios_pp':      re.compile('release/search_app_ios/(\d+\.\d+)$'),
    'ios_bro':     re.compile('release/browser_ios/(\d+(?:\.\d+){1,})$'),
}

platforms = ['android_pp', 'android_bro', 'ios_pp', 'ios_bro']

def get_yql_request_mining (version, platform):
    request = YQL_REQUEST_TEMPLATE_MINING
    request = re.sub(r'SCHEMA_VERSION', version, request)
    if platform == 'android_pp':
        request = re.sub(r'PATH', 'search', request)
        request = re.sub(r'PLATFORM', 'a', request) # Will match android, apad
    if platform == 'android_bro':
        request = re.sub(r'PATH', 'yabrowser', request)
        request = re.sub(r'PLATFORM', 'a', request) # Will match android, apad
    if platform == 'ios_pp':
        request = re.sub(r'PATH', 'search', request)
        request = re.sub(r'PLATFORM', 'i', request) # Will match iphone, ipad
    if platform == 'ios_bro':
        request = re.sub(r'PATH', 'yabrowser', request)
        request = re.sub(r'PLATFORM', 'i', request) # Will match iphone, ipad
    return request

def get_yql_request_add_task(name, task):
    request = YQL_REQUEST_TEMPLATE_ADD_TICKET
    request = re.sub(r'VERSIONS', name, request)
    request = re.sub(r'TASK', task, request)
    return request

def get_yql_request_check_versions(versions):
    request = YQL_REQUEST_TEMPLATE_CHECK_VERSIONS
    request = re.sub(r'VERSIONS', versions, request)
    return request

def make_yql_request(query, tokens):
    logging.info('Sending yql query:')
    logging.info(query)
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'YQL Sandbox (RUN_YQL task)',
        'Authorization': "OAuth {}".format(tokens['yql']),
        'Content-Type': 'application/json',
    })
    request = {
        'content': query,
        'action': 'RUN',
        'type': 'SQLv1'
    }
    response = session.post(
        YQL_API_BASE_URL + 'operations',
        json=request
    )
    if response.status_code != 200:
        logging.info('Failed to send yql request. Response status_code={}'.format(response.status_code))
        return None
    else:
        logging.info('Send ok! Response status_code={}'.format(response.status_code))
        yql_id = response.json()['id']
        return yql_id

def create_st_task(name, tokens, dropped):
    session = requests.Session()
    session.headers.update({
        'Authorization': "OAuth {}".format(tokens['startrek']),
        'Content-Type': 'application/json',
    })
    text = 'Добавление схема тестов для: {}.'.format(name)
    comment = ''
    if len(dropped) > 0:
        comment = ' Нет запросов для версий {}. Проверьте их.'.format(dropped)
    request = {
        'queue': 'HOME',
        'summary': text,
        'type': 2,
        'comment': comment
    }
    response = session.post(
        ST_API_BASE_URL,
        json=request
    )
    if response.status_code != 201:
        logging.info('Failed to create st task. Response status_code={}'.format(response.status_code))
        return None
    else:
        logging.info('Send ok! Response status_code={}'.format(response.status_code))
        logging.info(response.json()['key'])
        return response.json()['key']

def get_yql_results(yql_id, tokens):
    logging.info('Getting yql results for {}'.format(yql_id))
    results = {}
    get_session = requests.Session()
    get_session.headers.update({
        'User-Agent': 'YQL Sandbox (RUN_YQL task)',
        'Authorization': "OAuth {}".format(tokens['yql']),
    })

    # Waiting time limit = 20 min
    for i in range(120):
        logging.info('Results waiting cycle {} of 120'.format(i))
        response = get_session.get(
            'https://yql.yandex.net/api/v2/operations/{}/results?filters=DATA'.format(yql_id)
        )
        if response.status_code != 200:
            logging.info('Failed to send yql get request. Response status_code={}'.format(response.status_code))
        else:
            logging.info('Send ok! Response status_code={}'.format(response.status_code))
            logging.debug(response.json())
            if response.json()['status'] == 'ERROR':
                return None
            if response.json()['status'] == 'COMPLETED':
                return response.json()['data'][0]['Write'][0]['Data']
        time.sleep(10)
    return None

# Check if we already have task for selected versions
def do_we_have_task(task_name, tokens):
    logging.info('do_we_have_task, task name = {}'.format(task_name))
    query = get_yql_request_check_versions(task_name)
    yql_id = make_yql_request(query, tokens)
    if yql_id == None: return None
    results = get_yql_results(yql_id, tokens)
    logging.info('TASK RESULT: {}'.format(results))
    if results == None: return None
    return True if len(results) > 0 else False

def get_task_name(versions):
    task_name = ''
    for platform in sorted(versions):
        task_name += platform + ': '

        # Выкидываем пустые платформы
        if versions[platform]:
            task_name += ', '.join(sorted(versions[platform].keys())) + '. '
    return task_name

# Create startrek task and add info to yql table
def create_task_and_update_table(name, tokens, dropped):
    task = create_st_task(name, tokens, dropped)
    logging.info('TASK: {}'.format(task))
    if task == None: return None
    query = get_yql_request_add_task(name, task)
    make_yql_request(query, tokens)
    return task

def get_match_regexp(platform):
    return regexp.get(platform, None)

def get_morda_schema_directory(platform):
    return schema_directory.get(platform, None)

def get_uncovered_versions(platform, versions, path_arc, tokens):
    logging.info('Getting uncovered versions for {}'.format(platform))

    bb = requests.Session()
    bb.headers.update({
        'User-Agent': 'YQL Sandbox (RUN_YQL task)',
        'Authorization': "Bearer {}".format(tokens['bb']),
    })

    response = bb.get(
        BB_API_BASE_URL
    )

    if response.status_code != 200:
        logging.info('Failed to create st task. Response status_code={}'.format(response.status_code))
        return None
    else:
        logging.info('Send ok! Response status_code={}'.format(response.status_code))
        json = response.json()


        versions_with_test = {}

        # Get versions with schema tests
        morda_schema_directory = get_morda_schema_directory(platform)
        arcadia_dir = os.path.join(path_arc, morda_schema_directory)
        logging.info('Inspecting folder {}'.format(arcadia_dir))

        for path in os.listdir(arcadia_dir):
            match = re.search(r'tmp', path)
            if match is not None: continue

            if platform == 'android_bro':
                path = path[:len(path)-2] + path[len(path)-1:]

            version = re.sub(r'{}'.format(morda_schema_directory + '/'), '', path)
            splitted_version = re.split(r'\.', version)

            if int(splitted_version[0]) > MIN_API_SEARCH_VER_0 or (int(splitted_version[0]) == MIN_API_SEARCH_VER_0 and int(splitted_version[1]) >= MIN_API_SEARCH_VER_1):
                versions_with_test[version] = 1

        logging.info('We have versions: {}'.format(versions_with_test))

        match_regexp = get_match_regexp(platform)

        # Получаем все версии из BitBucket
        for branch in json['values']:
            branch_name = branch['displayId']
            logging.info('Branch name: {}'.format(branch_name))
            match = re.search(match_regexp, branch_name)
            if match is None:
                logging.info('Not match')
                continue

            version = match.group(1)
            logging.info('Matched version: {}'.format(version))
            splitted_version = re.split(r'\.', version)

            if int(splitted_version[0]) > MIN_API_SEARCH_VER_0 or (int(splitted_version[0]) == MIN_API_SEARCH_VER_0 and int(splitted_version[1]) >= MIN_API_SEARCH_VER_1):
                if not version in versions_with_test:
                    if platform == 'android_bro':
                        version = version[:len(version)-1] + '.' + version[len(version)-1]
                    versions[platform][version] = 1

def get_yql_mining_results (yql_ids_map, tokens):
    results = {}
    get_session = requests.Session()
    get_session.headers.update({
        'User-Agent': 'YQL Sandbox (RUN_YQL task)',
        'Authorization': "OAuth {}".format(tokens['yql']),
    })
    # Waiting time limit = 20 min
    for i in range(120):
        logging.info('Results waiting cycle {} of 120'.format(i))
        for version, yql_id in yql_ids_map.items():
            logging.info('Requesting results for version {}'.format(version))
            response = get_session.get(
                'https://yql.yandex.net/api/v2/operations/{}/results?filters=DATA'.format(yql_id)
            )
            if response.status_code != 200:
                logging.info('Failed to send yql get request. Response status_code={}'.format(response.status_code))
            else:
                logging.info('Send ok! Response status_code={}'.format(response.status_code))
                logging.debug(response.json())
                if response.json()['status'] == 'ERROR':
                    return None
                if response.json()['status'] == 'COMPLETED':
                    results[version] = response.json()['data'][0]['Write'][0]['Data']
                    del yql_ids_map[version]
            if len(yql_ids_map) == 0:
                return results
        time.sleep(10)
    if len(yql_ids_map) > 0:
        logging.info('Did not get results for some versions')
        return None
    return results

def mining_yql_requests (versions, yql_results, platform, tokens):
    all_versions = sorted(versions.keys())
    logging.info('ALL Versions for {} : {}'.format(platform, all_versions))
    # Sending yql requests and getting their ids
    yql_ids_map = {}
    for version in all_versions or []:
        query = get_yql_request_mining(version, platform)
        yql_id = make_yql_request(query, tokens)
        if yql_id == None:
            logging.info('Yql request failed, finishing job...')
            return None
        yql_ids_map[version] = yql_id
    logging.info(yql_ids_map)

    # Getting yql results
    yql_results_map = get_yql_mining_results(yql_ids_map, tokens)
    if yql_results_map == None:
        return None

    return yql_results_map

def create_morda_pr(yql_results, task, tokens, path_arc, self):
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H-%M')
    branch_name = '{}.{}.adding_schema_tests_{}'.format(date, task, time)

    logging.info('path_arc 2: {}'.format(path_arc))
    # arc.Arc().checkout(path_arc, branch_name, True)
    path = os.path.join(path_arc, 'function_tests/tests/schema')
    logging.info("Clone morda: {} {}".format(branch_name, path) )
    out = check_output('arc checkout -b {}'.format(branch_name), shell=True, cwd=path)
    logging.info("Clone morda end: {}".format(out))

    for platform in platforms:
        if yql_results.get(platform, None):

            yql_results_map = yql_results[platform]
            schema_path = get_morda_schema_directory(platform) + '/'
            for version, data in yql_results_map.items():
                full_path = path_arc + schema_path + '{}'.format(version)
                path = schema_path + '{}'.format(version)
                logging.info('Writing file {}'.format(path))
                with open(full_path, 'w') as the_file:
                    for row in data:
                        line = row[0][0]
                        logging.info(line)
                        the_file.write('{}\n'.format(line))
                    the_file.write('\n')
                    the_file.close()

    logging.info('adding all')
    out = check_output('arc add -v {}'.format(path_arc), shell=True, cwd=path_arc)
    logging.info('arc added: {}'.format(out))

    out = check_output("arc commit -a -m '{}: adding schema tests'".format(task), shell=True, cwd=path_arc)
    logging.info('arc commited: {}'.format(out))

    out = check_output("arc push", shell=True, cwd=path_arc)
    logging.info('arc pushed: {}'.format(out))

    try:
        out = check_output("arc pr c --push --no-edit --publish --no-code-review --json -m '{}: adding schema tests {}\nAdding schema tests'".format(task, time), shell=True, cwd=path_arc, stderr=STDOUT)
    except Exception as e:
        logging.info('arc pr create failed: {} / {}'.format(e.output.decode(), e))
        return
    logging.info('arc pr created: {}'.format(out))

def send_infra_message (task, tokens):
    # Waiting time limit = 1 hour
    for i in range(120):
        logging.info('Waiting before sending infra {} of 120'.format(i))
        time.sleep(30)
    session = requests.Session()
    session.headers.update({
        'Authorization': "OAuth {}".format(tokens['infra']),
        'Content-Type': 'application/json',
    })
    time_stamp = int(time.time())
    request = {
        'title': 'Создан таск на добавление схема тестов',
        'description': 'Дежурному по инфре необходимо проверить pr в этом таске и закоммитить, если schema-tests-simple зеленые',
        'environmentId': 4719,
        'serviceId': 3048,
        'type': 'maintenance',
        'severity': 'minor',
        'tickets': task,
        "startTime": time_stamp,
        "finishTime": time_stamp + 300,
    }
    response = session.post(
        INFRA_API_BASE_URL,
        json=request
    )
    if response.status_code != 200:
        logging.info('Failed to create st task. Response status_code={}'.format(response.status_code))
    else:
        logging.info('Send ok! Response status_code={}'.format(response.status_code))

def have_requests(yql_results):
    for platform in yql_results:
        if yql_results[platform]:
            return 1
    return 0

def get_dropped_versions(versions, yql_results):
    dropped = ''
    for platform in versions:
        if yql_results.get(platform, False):
            dropped_list = sorted(list(set(versions[platform].keys()) - set(yql_results[platform].keys())))
            if dropped_list:
                dropped += platform + ': ' + ', '.join() + '. '

    return dropped


class MordaSchemaTests(sdk2.Task):
    def on_create(self):
        logging.info('ON CREATE')
        self.Requirements.tasks_resource = service_resources.SandboxTasksBinary.find(
            owner="g:morda",
            attrs={"task_type": "MORDA_SCHEMA_TESTS"},
            # или attrs={"tasks_bundle": "<MY_BUNDLE_NAME>"},
        ).first()

    def on_execute(self):
        logging.info('ON EXECUTE')
        # Не выводим сообщения уровня DEBUG
        logging.getLogger("requests").setLevel(logging.WARNING)
        versions = {}

        # Достаем токены из секретницы
        secret = yav.Secret("sec-01g51zpzd3779ycjv0jh012186")
        tokens = {
            'startrek': secret.data()["STARTREK_OAUTH_TOKEN"],
            'yql':      secret.data()["YQL_OAUTH_TOKEN"],
            'infra':    secret.data()["INFRA_OAUTH_TOKEN"],
            'bb':       secret.data()["BITBUCKET"],
            'arc':      secret.data()["ARC_TOKEN"],
        }
        os.environ["ARC_TOKEN"] = tokens['arc']

        # Монтируем Аркадию
        with arcadia_sdk.mount_arc_path(ARC_PATH) as path_arc:
            logging.info('path_arc 1: {}'.format(path_arc))
            path_arc = os.path.join(path_arc, MORDA_PATH)

            # Собираем версии без тестов
            for platform in platforms:
                logging.info("== PLATFORM {}".format(platform))
                versions[platform] = {}
                get_uncovered_versions(platform, versions, path_arc, tokens)

            logging.info('VERSIONS: {}'.format(versions))

            # Проверяем - нет ли уже задачи на добавление найденных версий
            task_name = get_task_name(versions)
            have_task = do_we_have_task(task_name, tokens)
            logging.info('have task: {}'.format(have_task))
            if have_task == None or have_task == True: return

            logging.info('Don\'t have task')

            # Собираем запросы для найденных версий
            yql_results = {}
            for platform in platforms:
                # Не делаем запросы если нет версий
                if versions[platform]:
                    results = mining_yql_requests(versions[platform], yql_results, platform, tokens)
                    # Если запросы не найдены - пропускаем
                    if results == None or len(results) == 0: continue
                    yql_results[platform] = results

            logging.info('Requests: {}'.format(yql_results))

            if not have_requests(yql_results):
                logging.info('NO REQUESTS')
                return
            
            logging.info('HAVE REQUESTS!!!!')
            # Собираем имя задачи
            new_task_name = get_task_name(yql_results)
            logging.info('New task name: {}'.format(new_task_name))
            have_task = do_we_have_task(new_task_name, tokens)
            logging.info('have task: {}'.format(have_task))
            if have_task == None or have_task == True: return

            dropped = get_dropped_versions(versions, yql_results)
            task = create_task_and_update_table(new_task_name, tokens, dropped)

            logging.info('TASK_1: ' + str(pprint(dir(task))))
            if task == None: return
            logging.info('TASK_2')

            create_morda_pr(yql_results, task, tokens, path_arc, self)

        logging.info('Ready to create infra message')
        send_infra_message(task, tokens)

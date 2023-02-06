import json
import logging
import re
import requests

from sandbox import sdk2
from sandbox.sdk2 import yav
import sandbox.projects.common.environments as env

MIN_API_SEARCH_VER_0 = 21
MIN_API_SEARCH_VER_1 = 21
PUSH_AGENT_URL = 'http://portal-yasm.wdevx.yandex.ru:11005'

class MordaSchemaTestsCoverageCheck(sdk2.Task):
    """ Checking morda schema tests coverage and sending golovan signals. """

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 512
        disk_space = 100
        environments = [env.PipEnvironment("PyGithub", version="1.45")]

    def on_execute(self):
        from github import Github

        secret = yav.Secret("sec-01f23nrnkdzcdg1vc9kjpqy76h")
        token  = secret.data()["key"]
        g = Github(base_url="https://github.yandex-team.ru/api/v3", login_or_token=token)

        # Get versions from repo portal/morda-schema
        schema_repo = g.get_repo("portal/morda-schema")

        versions_in_repo_map = {}
        versions_in_repo = []
        for branch in schema_repo.get_branches():
            if re.match(r'release/android/\d+\.\d+$', branch.name):
                logging.info(branch.name)
                match = re.search(r'\d+\.\d+$', branch.name)
                if match is None:
                    continue
                version = match.group(0)
                splitted_version = re.split(r'\.', version)
                if int(splitted_version[0]) > MIN_API_SEARCH_VER_0 or (int(splitted_version[0]) == MIN_API_SEARCH_VER_0 and int(splitted_version[1]) >= MIN_API_SEARCH_VER_1):
                    versions_in_repo.append(float(version))
                    versions_in_repo_map[float(version)] = match.group(0)

        schemas_in_repo = sorted(list(set(versions_in_repo)))
        self.Context.schemas_in_repo = []
        for ver in schemas_in_repo:
            self.Context.schemas_in_repo.append(versions_in_repo_map[ver])

        # Get versions with schema tests
        morda_repo = g.get_repo("morda/main")

        versions_in_tests_map = {}
        versions_in_tests = []
        contents = morda_repo.get_contents("function_tests/tests/schema/api_search_v2_android")

        for content_file in contents:
            version = re.sub(r'function_tests/tests/schema/api_search_v2_android/', '', content_file.path)
            splitted_version = re.split(r'\.', version)
            if int(splitted_version[0]) > MIN_API_SEARCH_VER_0 or (int(splitted_version[0]) == MIN_API_SEARCH_VER_0 and int(splitted_version[1]) >= MIN_API_SEARCH_VER_1):
                versions_in_tests.append(float(version))
                versions_in_tests_map[float(version)] = version

        schemas_with_tests = sorted(list(set(versions_in_tests)))

        self.Context.schemas_with_tests = []
        for ver in schemas_with_tests:
            self.Context.schemas_with_tests.append(versions_in_tests_map[ver])

        # Versions with no tests
        logging.info(versions_in_repo)
        logging.info(versions_in_tests)
        schemas_missed = sorted(list(set(versions_in_repo) - set(versions_in_tests)))
        logging.info(schemas_missed)

        self.Context.schemas_missed = []
        for ver in schemas_missed:
            self.Context.schemas_missed.append(versions_in_repo_map[ver])

        # Sending signals
        signal_value = len(self.Context.schemas_missed)

        values = [{'name': 'api_search_schema_tests_coverage_android_tttt', 'val': signal_value}]
        data = [{
            'ttl': 2000,
            'tags': {
                'itype': 'mordaschema'
            },
            'values': values
        }]
        logging.info('Sending yasm signals:\n' + json.dumps(data, indent=4))
        response = requests.post(
            url=PUSH_AGENT_URL,
            json=data,
            timeout=5
        )
        if response.status_code != 200:
            logging.info('Failed to send yasm metrics. Response status_code={}'.format(response.status_code))
        else:
            logging.info('Send ok! Response status_code={}'.format(response.status_code))

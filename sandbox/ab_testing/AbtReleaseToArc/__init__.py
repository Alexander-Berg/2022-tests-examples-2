import os
import re
import logging
import time
import json
from sandbox.sdk2 import Task, parameters
from sandbox.sdk2 import ssh
from sandbox.sdk2.vcs.svn import Arcadia

ARCADIA_KEY_OWNER = 'AB-TESTING'
ARCADIA_KEY_NAME = 'sec-01dx1bdkxjy6h3yn85wfdbx3wp[ssh_key]'
ARCADIA_USER = 'robot-eksperimentus'


DEFAULT_USER = 'robot-eksperimentus'
CI_ROOT_PATH = 'quality/ab_testing/ci/'

TYPE_PATH_CONFIGS = 'configs/'
TYPE_PATH_SERVICES = 'services/'

ENV_PATH_DEV = 'dev/'
ENV_PATH_TESTING = 'testing/'
ENV_PATH_PRODUCTION = 'production/'

RELEASE_FILENAME = 'config.json'

RELEASE_TYPE_CONFIG = 'config'
RELEASE_TYPE_SERVICE = 'service'
RELEASE_TYPES = [
    RELEASE_TYPE_CONFIG,
    RELEASE_TYPE_SERVICE,
]

RELEASE_TYPES_PATHS = {
    RELEASE_TYPE_CONFIG: TYPE_PATH_CONFIGS,
    RELEASE_TYPE_SERVICE: TYPE_PATH_SERVICES,
}

RELEASE_ENV_DEV = 'dev'
RELEASE_ENV_TESTING = 'testing'
RELEASE_ENV_PRODUCTION = 'production'

RELEASE_ENVS = [
    RELEASE_ENV_DEV,
    RELEASE_ENV_TESTING,
    RELEASE_ENV_PRODUCTION,
]

RELEASE_ENVS_PATHS = {
    RELEASE_ENV_DEV: ENV_PATH_DEV,
    RELEASE_ENV_TESTING: ENV_PATH_TESTING,
    RELEASE_ENV_PRODUCTION: ENV_PATH_PRODUCTION,
}


class AbtReleaseToArcTask(Task):

    class Parameters(Task.Parameters):

        arcadia_base_url = parameters.String(
            'Arcadia base path to release',
            default_value=CI_ROOT_PATH,
            required=False,
        )

        with parameters.RadioGroup('environment') as release_env:
            release_env.values[RELEASE_ENV_DEV] = release_env.Value('development release')
            release_env.values[RELEASE_ENV_TESTING] = release_env.Value('testing release', default=True)
            release_env.values[RELEASE_ENV_PRODUCTION] = release_env.Value('production release')

        with parameters.RadioGroup('release type') as release_type:
            release_type.values[RELEASE_TYPE_CONFIG] = release_type.Value('release to config folder', default=True)
            release_type.values[RELEASE_TYPE_SERVICE] = release_type.Value('release to service folder')

        with release_type.value[RELEASE_TYPE_CONFIG]:
            release_config = parameters.String('config id to release', required=True)

        with release_type.value[RELEASE_TYPE_SERVICE]:
            release_service = parameters.String('service to release', required=True)

        release_json = parameters.JSON('release data', required=True)
        release_author = parameters.String('release author', default_value=DEFAULT_USER, required=False)
        release_description = parameters.String('commit description', default_value=None, required=False)

        with parameters.Output():
            committed_revision = parameters.String('committed revision', default_value='')
            commit_timestamp = parameters.Integer('commit timestamp')

    def _commit_text(self):
        description = self.Parameters.release_description
        if description:
            return "{description}\nSKIP_CHECK".format(description=description)

        type_part = self.Parameters.release_type
        env_part = self.Parameters.release_env
        author = self.Parameters.release_author

        proj_part = ''
        if self.Parameters.release_type == RELEASE_TYPE_CONFIG:
            proj_part = self.Parameters.release_config
        elif self.Parameters.release_type == RELEASE_TYPE_SERVICE:
            proj_part = self.Parameters.release_service
        else:
            raise ValueError('Unknown release type {}'.format(self.Parameters.release_type))

        return "Experiments release by @{} for {}:{} (environment {}) SKIP_CHECK".format(author, type_part, proj_part, env_part)

    def _release_path(self):
        type_part = RELEASE_TYPES_PATHS[self.Parameters.release_type]

        env_part = RELEASE_ENVS_PATHS[self.Parameters.release_env]
        if self.Parameters.release_env == RELEASE_ENV_DEV:
            env_part += self.author + '/'

        proj_part = ''
        if self.Parameters.release_type == RELEASE_TYPE_CONFIG:
            proj_part = self.Parameters.release_config
        elif self.Parameters.release_type == RELEASE_TYPE_SERVICE:
            proj_part = self.Parameters.release_service
        else:
            raise ValueError('Unknown release type {}'.format(self.Parameters.release_type))

        base_url = os.path.join(Arcadia.trunk_url(), self.Parameters.arcadia_base_url, type_part)
        relative_url = os.path.join(env_part, proj_part)
        return base_url, relative_url

    def _write_content(self, file_dir, filename, content):
        logging.info("creating directory '{}'...".format(file_dir))
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        file_path = os.path.join(file_dir, filename)
        is_new = not os.path.exists(file_path)
        logging.info("writting file '{}'...".format(file_path))
        with open(file_path, 'w') as f:
            f.write(content)

        return is_new, file_path

    def _commit_arc(self):
        base_url, relative_url = self._release_path()
        release_content = json.dumps(self.Parameters.release_json)
        filename = RELEASE_FILENAME
        proposed_url = os.path.join(base_url, relative_url, filename)
        logging.info("trying to commit release '{}' to '{}'".format(release_content, proposed_url))

        checkout_dir = str(self.path('arcadia'))
        logging.info("checking out Arcadia '{}' to '{}'...".format(base_url, checkout_dir))
        Arcadia.checkout(base_url, checkout_dir)
        logging.info('Arcadia is checked out')

        checkout_file_path = os.path.join(checkout_dir, relative_url)
        need_svn_add, file_path = self._write_content(checkout_file_path, filename, release_content)
        commti_text = self._commit_text()

        with ssh.Key(self, key_owner=ARCADIA_KEY_OWNER, key_name=ARCADIA_KEY_NAME):
            if need_svn_add:
                logging.info('adding to Arcadia...')
                Arcadia.add(file_path, parents=True)
            logging.info('committing to Arcadia...')
            timestamp = int(time.time())
            commit_output = Arcadia.commit(checkout_dir, commti_text, user=ARCADIA_USER)
        logging.info('successfully committed')

        committed_revision_match = re.findall(r"Committed revision ([0-9]+)", commit_output)

        if committed_revision_match:
                committed_revision = committed_revision_match[0]
                logging.info('committed release r{}'.format(committed_revision))

                self.Parameters.committed_revision = 'r{}'.format(committed_revision)
        else:
            logging.info('committed revision not found')

        self.Parameters.commit_timestamp = timestamp

    def on_execute(self):
        author = self.Parameters.release_author
        logging.info("Releasing experiments on behalf of @{} under @{}".format(author, self.author))
        self._commit_arc()

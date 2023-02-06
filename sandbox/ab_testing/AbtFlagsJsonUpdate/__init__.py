# -*- coding: utf-8 -*-

import six
import json
import logging
import time
import os.path
import re

from sandbox import sdk2

from sandbox.sandboxsdk import ssh
from sandbox.sandboxsdk.svn import Arcadia

from sandbox import common
import sandbox.common.types.misc as ctm

from sandbox.projects.common.nanny import nanny
from sandbox.projects.common import task_env
from sandbox.projects.common import decorators
from sandbox.projects.common import requests_wrapper
from sandbox.projects.common import file_utils
from sandbox.projects.resource_types.releasers import experiment_releasers


DEFAULT_ARCADIA_PATH = '/web/report/data/flags/experiments/'

ARCADIA_KEY_OWNER = 'AB-TESTING'
ARCADIA_KEY_NAME = 'robot-eksperimentus-ssh'
ARCADIA_USER = 'robot-eksperimentus'

STARTREK_KEY_OWNER = 'AB-TESTING'
STARTREK_KEY_NAME = 'robot-eksperimentus-startrek'

WEB_HOOK_URL = 'https://ab.yandex-team.ru/deploying/__nanny_web_hook__'

RESOURCE_CLASS_PREFIX = 'AbtFlagsJson'
RESOURCE_TYPE_PREFIX = 'ABT_FLAGS_JSON'


class AbtFlagsJson(sdk2.Resource):
    """
    Experiments flags for Report et al (see. USEREXP-4987, SERP-60105, SERP-60166, ...)
    """
    any_arch = True
    releasable = True
    auto_backup = True
    releasers = experiment_releasers + ['robot-eksperimentus', 'alextim27', ]


class AbtFlagsJsonTest(AbtFlagsJson):
    pass


class AbtFlagsJsonWeatherios(AbtFlagsJson):
    pass


class AbtFlagsJsonHealth(AbtFlagsJson):
    pass


class AbtFlagsJsonCollections(AbtFlagsJson):
    pass


class AbtFlagsJsonUslugi(AbtFlagsJson):
    pass


class AbtFlagsJsonSuburban_ios(AbtFlagsJson):
    pass


class AbtFlagsJsonSuburban_android(AbtFlagsJson):
    pass


class AbtFlagsJsonDistrict(AbtFlagsJson):
    pass


class AbtFlagsJsonQuasar(AbtFlagsJson):
    # USEREXP-8636
    pass


class AbtFlagsJsonSmart_home_ui(AbtFlagsJson):
    # USEREXP-9449
    pass


class AbtFlagsJsonSmart_tv_android(AbtFlagsJson):
    # USEREXP-9591
    pass


class AbtFlagsJsonUniproxy(AbtFlagsJson):
    # USEREXP-9686
    pass


class AbtFlagsJsonFintech(AbtFlagsJson):
    # USEREXP-9866
    pass


class AbtFlagsJsonBell(AbtFlagsJson):
    # USEREXP-9884
    pass


class AbtFlagsJsonTurboapp_checkout(AbtFlagsJson):
    # USEREXP-10125
    pass


class AbtFlagsJsonTurboapp_taxi(AbtFlagsJson):
    # USEREXP-10125
    pass


class AbtFlagsJsonTurboapp_refuel(AbtFlagsJson):
    # USEREXP-10125
    pass


class AbtFlagsJsonProducts(AbtFlagsJson):
    # USEREXP-11715
    pass


class AbtFlagsJsonWeather(AbtFlagsJson):
    # USEREXP-11142
    pass


class AbtFlagsJsonUpdate(nanny.ReleaseToNannyTask2, sdk2.Task):
    """
    Update flags.json resource
    """

    class Requirements(task_env.TinyRequirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        flags_json_url = sdk2.parameters.String(
            'flags.json URL',
            default='http://ab.yandex-team.ru/flags.json',
            required=False,
        )

        ticket = sdk2.parameters.String(
            'Deploy ticket',
            default='USEREXP-5292',  # it's a stub
            required=False,
        )

        arcadia_commit_url = sdk2.parameters.ArcadiaUrl(
            'SVN path to commit flags.json on release',
            default_value=Arcadia.trunk_url() + DEFAULT_ARCADIA_PATH,
            required=False,
        )

        webhook_urls = sdk2.parameters.List(
            'Web hook URLs',
            default=[WEB_HOOK_URL, ],
            required=False,
        )

        check_with_url_on_release = sdk2.parameters.Bool(
            'Check resource with flags.json URL on release',
            default=True,
            required=False,
        )

        services = sdk2.parameters.List(
            'Services',
            default=[],
            required=False,
        )

        resource_type = sdk2.parameters.String(
            'Resource type suffix',
            default='',
            required=False,
        )

    class Context(sdk2.Task.Context):
        version = 'none'
        ts_created = 'none'
        flags_json_path = ''

    @decorators.retries(max_tries=5, delay=5)
    def _download_flags_json(self):
        logging.info('Trying to fetch flags.json')
        url = self.Parameters.flags_json_url

        if not url:
            logging.warning('No url specified: return fake empty flags.json')
            return '{{"meta": {{"version": "fake", "ts_created": {}}}, "content": []}}'.format(int(time.time()))

        logging.info('Fetching flags.json from url %s', url)
        # prevent infinite timeout, take as raw bytes
        return requests_wrapper.get_r(url).content

    def _release_to_nanny(self, additional_parameters):
        logging.info('trying to release to Nanny...')

        st_ticket = self.Parameters.ticket
        version = self.Context.version
        ts_created = self.Context.ts_created
        comment = '{st_ticket}: Update flags.json to the version #{version}_{ts_created}'.format(
            st_ticket=st_ticket,
            version=version,
            ts_created=ts_created,
        )

        # USEREXP-7939
        resource_type = self.Parameters.resource_type.strip().upper().replace('-', '_')
        if resource_type:
            comment += ' [{}]'.format(resource_type)

        # USEREXP-6822
        services = self.Parameters.services
        if len(services) > 0:
            comment += ' [{}]'.format(', '.join(services))

        logging.debug('COMMENT = %s', comment)
        additional_parameters['release_subject'] = comment
        self.Context.webhook_type = 'RELEASE_WITH_TICKETS'
        if st_ticket:
            self.Context.startrek_ticket_ids = [st_ticket]
        nanny.ReleaseToNannyTask2.on_release(self, additional_parameters)

        logging.info('released to Nanny...')

    def _comment_st_ticket(self):
        logging.info('trying to comment Startreck ticket...')

        st_ticket = self.Parameters.ticket

        if not st_ticket:
            logging.info('no ticket specified - no need to comment')
            return

        try:
            token = sdk2.Vault.data(STARTREK_KEY_OWNER, STARTREK_KEY_NAME)
            st = common.rest.Client(
                base_url='https://st-api.yandex-team.ru/v2',
                auth=token
            )
            st.issues[st_ticket].comments.create(text=u'Начался процесс выкатки. Следите за сообщениями от Няни.')
        except Exception as e:
            logging.error(u'something wrong while commenting: %s', six.text_type(e))
        else:
            logging.info(u'ticket %s successfully commented', st_ticket)

    def _get_resource_flags_json(self):
        resource_type = RESOURCE_TYPE_PREFIX
        resource_type_suffix = self.Parameters.resource_type.strip().upper().replace('-', '_')
        if resource_type_suffix:
            resource_type += '_' + resource_type_suffix
        flags_json_resource = sdk2.Resource[resource_type].find(task=self).first()
        flags_json_resource_data = sdk2.ResourceData(flags_json_resource)
        flags_json_path = str(flags_json_resource_data.path)
        logging.info('Loading the resource from `%s`', flags_json_path)
        return open(flags_json_path).read()

    def _commit_to_arcadia(self):
        logging.info('Trying to commit flags.json')

        if not self.Parameters.arcadia_commit_url:
            logging.info('no url specified - no need to commit')
            return

        checkout_dir = str(self.path('arcadia'))

        logging.info('Checkouting Arcadia to %s', checkout_dir)
        Arcadia.checkout(self.Parameters.arcadia_commit_url, checkout_dir)

        flags_json_content = json.loads(self._get_resource_flags_json())
        new_flags_json_path = os.path.join(checkout_dir, 'flags.json')
        logging.info('Saving pretty copy of the resource to %s', new_flags_json_path)
        file_utils.json_dump(new_flags_json_path, flags_json_content, indent=4)

        ticket = self.Parameters.ticket

        logging.info('committing to Arcadia...')
        try:
            with ssh.Key(self, key_owner=ARCADIA_KEY_OWNER, key_name=ARCADIA_KEY_NAME):
                Arcadia.commit(
                    checkout_dir,
                    '{ticket}: flags.json updated to the version #{version}_{ts_created}\nSKIP_CHECK'.format(
                        ticket=ticket,
                        version=self.Context.version,
                        ts_created=self.Context.ts_created,
                    ),
                    user=ARCADIA_USER,
                )
        except Exception as e:
            logging.error(u'Something wrong while commiting: %s', six.text_type(e))
        else:
            logging.info('Successfully committed')

    def on_execute(self):
        resource_type_suffix = self.Parameters.resource_type.strip()

        resource_class_str = RESOURCE_CLASS_PREFIX + resource_type_suffix.capitalize().replace('-', '_')
        if resource_class_str not in globals():
            raise Exception('resource class {} not defined'.format(resource_class_str))
        resource_class = globals()[resource_class_str]

        resource_type = RESOURCE_TYPE_PREFIX
        if resource_type_suffix:
            resource_type += '_' + resource_type_suffix.upper().replace('-', '_')

        flags_json_content = self._download_flags_json()

        flags_json_meta = json.loads(flags_json_content)['meta']
        version = flags_json_meta.get('version', 'none')
        ts_created = flags_json_meta.get('ts_created', 'none')
        self.Context.version = version
        self.Context.ts_created = ts_created
        logging.info('flags.json version #%s_%s', version, ts_created)

        if not resource_type_suffix:
            resource_description = 'flags_json_{}_{}'.format(version, ts_created)
            resource_file = 'flags.json'
        else:
            resource_description = 'flags_json_{}_{}_{}'.format(resource_type_suffix.lower(), version, ts_created)
            resource_file = 'flags_{}.json'.format(resource_type_suffix.lower())

        logging.info('Creating resource %s in %s', resource_type, resource_file)
        resource = sdk2.ResourceData(resource_class(self, resource_description, resource_file))
        resource.path.write_bytes(flags_json_content)
        self.Context.flags_json_path = str(resource.path)
        logging.info('Making resource ready')
        resource.ready()

    def _check_flags_json_on_release(self):
        # USEREXP-6807
        original_flags_json = self._download_flags_json()
        this_flags_json = self._get_resource_flags_json()

        # USEREXP-7063
        r = re.compile(',["]ts_created["]:[0-9]{10}')

        if r.sub('', original_flags_json) != r.sub('', this_flags_json):
            raise Exception('flags.json in Adminka and in the resource don\'t match')

    def on_release(self, additional_parameters):
        logging.info('flags.json releasing...')
        if self.Parameters.check_with_url_on_release:
            self._check_flags_json_on_release()
        self._release_to_nanny(additional_parameters)
        self._comment_st_ticket()
        self._commit_to_arcadia()

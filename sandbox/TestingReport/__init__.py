# -*- coding: utf-8 -*-
import datetime
import json
import logging
import os
import requests
import uuid
import pytz

from sandbox import sdk2
from sandbox.common.types.resource import State
from sandbox.projects.abc.client import AbcClient
from sandbox.projects.release_machine import rm_notify
from sandbox.projects.common.testenv_client import TEClient
from sandbox.projects.yabs.qa.template_utils import get_template
from sandbox.projects.yabs.qa.resource_types import BS_RELEASE_TAR


DATE_FORMAT = "%Y.%m.%d %H:%M"
OK_CODE = u'\U00002705'
WARN_CODE = u'\U000026A0'
FAIL_CODE = u'\U00002757'


def get_testenv_resources_creation_time(database):
    def parse_testenv_resource_datetime(datetime_string):
        return datetime.datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")

    resources = TEClient.get_resources(database)
    logging.debug('Testenv resources: %s', resources)

    ok_resources = filter(lambda resource: resource["status"] == "OK", resources)
    logging.debug('Testenv OK resources: %s', ok_resources)

    return {
        resource["name"]: parse_testenv_resource_datetime(resource['resource_datetime'])
        for resource in ok_resources
    }


def get_func_oneshot_spec():
    return sdk2.Resource["YABS_SERVER_HOUSE_SPEC"].find(
        attrs={
            "good": 'True',
            'released_spec': 'True'
        },
        state=State.READY,
    ).order(-sdk2.Resource.id).first()


def get_oneshot_spec_resources_creation_time(spec):
    res = {}

    for key, spec_key in [
        ('YABS_SERVER_MYSQL_ARCHIVE_CONTENTS', 'mysql_archive_resource_id'),
        ('YABS_CS_INPUT_SPEC', 'cs_input_spec_resource_id'),
    ]:
        try:
            res[key] = sdk2.Resource[spec[spec_key]].created
        except Exception as exc:
            logging.exception(exc)
    for role in ('bs', 'bsrank', 'yabs'):
        try:
            res['YABS_SERVER_REQUEST_LOG_GZ_{}'.format(role.upper())] = sdk2.Resource[spec['ft_request_log_resource_id_map'][role]].created
            res['YABS_SERVER_REQUEST_LOG_GZ_{}_LOAD'.format(role.upper())] = sdk2.Resource[spec['stat_load_request_log_resource_id_map'][role]].created
            res['YABS_SERVER_REQUEST_LOG_GZ_{}_META_LOAD'.format(role.upper())] = sdk2.Resource[spec['meta_load_request_log_resource_id_map'][role]].created
        except Exception as exc:
            logging.exception(exc)

    return res


def get_resources_status(resource_age, now, thresholds=None):
    thresholds = thresholds or {}
    resource_statuses = {}

    for resource_name, resource_datetime in resource_age.items():
        age = now.replace(tzinfo=pytz.utc) - resource_datetime.replace(tzinfo=pytz.utc)
        if age < thresholds.get(resource_name, {}).get('WARN', datetime.timedelta(days=3)):
            resource_statuses[resource_name] = OK_CODE
        elif age < thresholds.get(resource_name, {}).get('CRIT', datetime.timedelta(days=4)):
            resource_statuses[resource_name] = WARN_CODE
        else:
            resource_statuses[resource_name] = FAIL_CODE

    return resource_statuses


def group_ammo_resources_by_datetime(resources):
    resources_by_datetime = {}
    for resource_name, resource_creation_time in resources.items():
        for role in ('BS', 'BSRANK', 'YABS'):
            if resource_name == 'YABS_SERVER_REQUEST_LOG_GZ_{}'.format(role):
                resources_by_datetime.setdefault('ft', {}).setdefault(resource_creation_time, []).append(role)
            elif resource_name == 'YABS_SERVER_REQUEST_LOG_GZ_{}_LOAD'.format(role):
                resources_by_datetime.setdefault('stat_load', {}).setdefault(resource_creation_time, []).append(role)
            elif resource_name == 'YABS_SERVER_REQUEST_LOG_GZ_{}_META_LOAD'.format(role):
                resources_by_datetime.setdefault('meta_load', {}).setdefault(resource_creation_time, []).append(role)
    return resources_by_datetime


def get_duty(task, abc_token):
    login = AbcClient(abc_token).get_current_duty_login(2409, schedule_slug='yabs_server_sandbox_tests_duty')
    try:
        mention = "[@{0}](https://telegram.me/{0})".format(rm_notify.get_mention(
            task,
            person=login,
        ))
    except Exception:
        mention = "{}@".format(login)
    return mention


class DailyYabsTestingReport(sdk2.Task):
    class Parameters(sdk2.Task.Parameters):
        chat_id = sdk2.parameters.String("Chat id", default="0/0/b4ee2c50-6e79-4693-9c9a-081a6f39b974")
        tokens = sdk2.parameters.YavSecret("YAV secret identifier", default="sec-01d6apzcex5fpzs5fcw1pxsfd5")
        custom_prefix = sdk2.parameters.String("Custom prefix", default="", multiline=True)
        custom_suffix = sdk2.parameters.String("Custom suffix", default="", multiline=True)

    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 512

        class Caches(sdk2.Requirements.Caches):
            pass  # Do not use any shared caches (required for running on multislot agent)

    def on_execute(self):
        tokens = self.Parameters.tokens.data()
        func_oneshot_spec = get_func_oneshot_spec()
        with open(str(sdk2.ResourceData(func_oneshot_spec).path)) as f:
            func_oneshot_spec_data = json.load(f)

        now = datetime.datetime.now(tz=pytz.utc)

        trunk_resources_creation_time = get_testenv_resources_creation_time('yabs-2.0')
        trunk_resources_data = {name: dt.strftime(DATE_FORMAT) for name, dt in trunk_resources_creation_time.items()}
        trunk_resources_status = get_resources_status(trunk_resources_creation_time, now)

        oneshot_spec_resources_creation_time = get_oneshot_spec_resources_creation_time(func_oneshot_spec_data)
        oneshot_spec_resources_data = {name: dt.strftime(DATE_FORMAT) for name, dt in oneshot_spec_resources_creation_time.items()}
        oneshot_spec_resources_status = get_resources_status(oneshot_spec_resources_creation_time, now)

        stat_ft_engine_version = sdk2.Resource[func_oneshot_spec_data["stat_bs_release_tar_resource_id"]].resource_version
        meta_ft_engine_version = sdk2.Resource[func_oneshot_spec_data["stat_bs_release_tar_resource_id"]].resource_version
        stable_stat_ft_engine_resource = BS_RELEASE_TAR.find(attrs={'released': 'stable', 'component_name': 'yabs_server'}, state=State.READY).order(-sdk2.Resource.id).first()
        stable_meta_ft_engine_resource = BS_RELEASE_TAR.find(attrs={'released': 'stable', 'component_name': 'yabs_server'}, state=State.READY).order(-sdk2.Resource.id).first()
        if not stable_meta_ft_engine_resource or stable_meta_ft_engine_resource.id < stable_stat_ft_engine_resource.id:
            stable_meta_ft_engine_resource = stable_stat_ft_engine_resource

        stable_meta_ft_engine_version = stable_meta_ft_engine_resource.resource_version
        stable_stat_ft_engine_version = stable_stat_ft_engine_resource.resource_version

        template = get_template("shm_report.html", os.path.dirname(__file__))
        message = template.render(
            trunk_resources_data=trunk_resources_data,
            trunk_resources_status=trunk_resources_status,
            oneshot_spec_resources_data=oneshot_spec_resources_data,
            oneshot_spec_resources_status=oneshot_spec_resources_status,
            date=datetime.datetime.now().strftime(DATE_FORMAT),
            stat_ft_engine_version=stat_ft_engine_version,
            stat_ft_engine_version_status=OK_CODE if stat_ft_engine_version == stable_stat_ft_engine_version else FAIL_CODE,
            meta_ft_engine_version=meta_ft_engine_version,
            meta_ft_engine_version_status=OK_CODE if meta_ft_engine_version == stable_meta_ft_engine_version else FAIL_CODE,
            trunk_ammo_resources=group_ammo_resources_by_datetime(trunk_resources_data),
            oneshot_spec_ammo_resources=group_ammo_resources_by_datetime(oneshot_spec_resources_data),
            duty=get_duty(self, tokens['abc_token']),
        )

        if self.Parameters.custom_prefix:
            message = self.Parameters.custom_prefix.strip() + '\n\n' + message

        if self.Parameters.custom_suffix:
            message = message + '\n\n' + self.Parameters.custom_suffix.strip()

        logging.debug(message)

        data = {
            "project": "YabsServerQA",
            "template": "default",
            "request_id": str(uuid.uuid4()),
            "abc_service": "yabs_server_sandbox_tests",
            "params": {
                "message": {
                    "string_value": message,
                },
            },
            "recipient": {
                "telegram": {
                    "chat_name": ["yabs_server_testing_chat"],
                    # For debug purposes please use commented recipient instead of prod task
                    # "internal": [{"login": "igorock"}],
                }
            }
        }
        logging.debug('Sending data:\n%s', json.dumps(data, indent=2))

        response = requests.post(
            'https://jns.yandex-team.ru/api/messages/send',
            json=data,
            headers={'Authorization': 'OAuth ' + tokens['juggler_token']}
        )

        if not response.ok:
            logging.error("Failed to post message: %s, %s", response.status_code, response.text)

        self.set_info(message)

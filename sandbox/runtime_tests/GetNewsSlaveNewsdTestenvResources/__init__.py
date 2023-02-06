import json
import urllib2
import time
import logging

from sandbox import sdk2
from sandbox.sandboxsdk import environments
from sandbox.sdk2.helpers import subprocess as sp, ProcessLog
from sandbox.projects.common.news import yappy as news_yappy
from sandbox.projects import resource_types
from sandbox.projects.news.runtime_tests.GetNewsApphostServiceRequests import GetNewsApphostServiceRequests
from sandbox.projects.RunScript import RunScript
from sandbox import common
import sandbox.projects.news.resources as resources


class GetNewsSlaveNewsdTestenvResources(sdk2.Task):
    environment = (
        environments.SvnEnvironment(),
    )

    class Requirements(sdk2.Task.Requirements):
        cores = 1
        disk_space = 10 * 1024
        ram = 2 * 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Context(sdk2.Task.Context):
        pass

    class Parameters(sdk2.Task.Parameters):
        indexer_hosts = sdk2.parameters.String(
            'List of hosts with production indexers',
            required=True
        )

    def get_active_host(self):
        active = None
        hosts = self.Parameters.indexer_hosts.split(',')
        for host in hosts:
            url = 'http://' + host + ':3000/state/active'
            try:
                response = urllib2.urlopen(url)
                status = response.read()
                if status is not None and int(status) == 1:
                    active = host
                    break
            except urllib2.HTTPError:
                pass
            except urllib2.URLError:
                pass
        if active is None:
            raise common.errors.TaskError('failed to find active indexer')
        else:
            logging.info('Active indexer host: {}'.format(active))

        return active

    def get_state(self):
        active_host = self.get_active_host()
        url = 'http://' + active_host + ':1985/dump'

        resource = resource_types.SLAVE_NEWSD_STATE(
            self,
            'slave_newsd state for tests',
            'slave_newsd_state.bin',
            ttl=30,
            slave_newsd_testenv_base="yes",
            timestamp=int(time.time()),
        )
        resource_data = sdk2.ResourceData(resource)

        self.Context.state_resource_id = resource.id

        with open(str(resource_data.path), 'wb') as fd:
            try:
                state = urllib2.urlopen(url)
                fd.write(state.read())
            except urllib2.HTTPError as e:
                raise common.errors.TaskError(
                    'Failed to fetch state from indexer: {}, {}'.format(str(e.code), str(e.read()))
                )
        resource_data.ready()

    def run_get_slave_requests_task(self):
        sub_task = GetNewsApphostServiceRequests(
            self,
            service_name='slave_newsd',
            graph_source_names='NEWS_SLAVE_NEWSD',
            notifications=self.Parameters.notifications,
            create_sub_task=False
        )
        sub_task.enqueue()
        self.set_info(
            "Starting subtask {} to collect slave_newsd requests".format(sub_task)
        )

    def run_get_arranged_requests_task(self):
        sub_task = GetNewsApphostServiceRequests(
            self,
            service_name='arranged',
            graph_source_names='ARRANGED',
            notifications=self.Parameters.notifications,
            create_sub_task=False
        )
        sub_task.enqueue()
        self.set_info(
            "Starting subtask {} to collect arranged requests".format(sub_task)
        )

    def run_get_zen_embeddings(self):
        task = sdk2.Task["RUN_SCRIPT"]
        sub_task = task(
            self,
            script_url="svn+ssh://zomb-sandbox-rw@arcadia.yandex.ru/arc/trunk/arcadia/yweb/news/runtime_scripts/get_zen_embeddings",
            cmdline="YT_TOKEN=$YT_TOKEN {binary}",
            named_resources={"binary": "1870503935"},
            vault_env="YT_TOKEN=NEWS:yt_token",
            save_as_resource={"zen_embeddings.txt": "type:NEWS_ZEN_EMBEDDINGS,attr:news_testenv_resource:True"},
            resources_ttl=28
        )
        sub_task.enqueue()
        self.set_info(
            "Starting subtask {} to collect zen embeddings".format(sub_task)
        )

    def on_execute(self):
        self.get_state()
        self.run_get_slave_requests_task()
        self.run_get_arranged_requests_task()
        self.run_get_zen_embeddings()

    def on_failure(self, prev_status):
        self.set_info("on_failure called")

    def on_break(self, prev_status, status):
        self.set_info("on_break called")

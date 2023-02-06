import json

from sandbox import sdk2
from sandbox.sandboxsdk import environments
from sandbox.sdk2.helpers import subprocess as sp, ProcessLog
from sandbox.projects.common.news import yappy as news_yappy
import sandbox.projects.news.resources as resources


class GetNewsApphostServiceResponses(sdk2.Task):

    environment = (
        environments.SvnEnvironment(),
    )

    class Requirements(sdk2.Task.Requirements):
        cores = 1
        disk_space = 1 * 1024
        ram = 2 * 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Context(sdk2.Context):
        responses = "void"
        service_config = "void"
        yappy_token = "void"
        beta_suffix = "void"

    class Parameters(sdk2.Task.Parameters):
        service_name = sdk2.parameters.String(
            'Name of the service to read config from yweb/news/runtime_yappy',
            required=True
        )

        binary_resource = sdk2.parameters.Resource(
            'Resource with binary of the service',
            required=True
        )

        state_resource = sdk2.parameters.Resource(
            'Resource with state for newsd and arranged',
            required=False
        )

        additional_res_tasks = sdk2.parameters.List(
            'Tasks with additional resources',
            required=False
        )

        additional_resourses = sdk2.parameters.List(
            'Additional resources',
            required=False
        )

        requests = sdk2.parameters.Resource(
            'Requests',
            resource_type=resources.NEWS_APPHOST_SERVICE_REQUESTS,
            required=True
        )

        wait_timeout = sdk2.parameters.Integer(
            'Time in seconds to wait for a beta to start',
            default=1800,
            required=True
        )

        graph_source_names = sdk2.parameters.List(
            'List of source names in graphs',
            required=True
        )

        apphost_requester = sdk2.parameters.Resource(
            'Resource with binary of apphost requester',
            required=True
        )

        keep_beta = sdk2.parameters.Bool(
            'Keep beta after testing',
            default=False
        )

    def get_service_responses(self, service_config, hostline):
        requester = sdk2.ResourceData(self.Parameters.apphost_requester)

        ammo = sdk2.ResourceData(self.Parameters.requests)

        if "port_offset" in service_config:
            hostline_splitted = hostline.split(':')
            host = hostline_splitted[:-1]
            port = hostline_splitted[-1]
            port = str(int(port) + int(service_config['port_offset']))
            hostline = ''.join(host) + ':' + port

        responses_data = sdk2.ResourceData(sdk2.Resource[self.Context.responses])

        with ProcessLog(self, 'requester.log') as pl:
            sp.check_call([
                str(requester.path),
                '--address', 'post://{}'.format(hostline),
                '--input', str(ammo.path),
                '--output', str(responses_data.path),
            ], stdout=pl.stdout, stderr=pl.stderr)

        responses_data.ready()
        self.Context.save()

    def on_enqueue(self):
        self.Context.responses = resources.NEWS_APPHOST_SERVICE_RESPONSES(self, "Responses for " + str(self.Parameters.service_name), self.Parameters.graph_source_names[0] + ".resp").id

    def on_execute(self):
        resources_to_deploy = []
        resources_to_deploy.append(self.Parameters.binary_resource.id)
        if self.Parameters.state_resource is not None:
            resources_to_deploy.append(self.Parameters.state_resource.id)

        for task in self.Parameters.additional_res_tasks:
            resources = list(sdk2.Resource.find(task=sdk2.Task.find(id=task).limit(1)).limit(10))
            for resource in resources:
                resources_to_deploy.append(resource)

        for resource in self.Parameters.additional_resourses:
            resources_to_deploy.append(int(resource))

        self.Context.service_config = self.load_service_config()
        self.set_info("Create beta {}, with resources {}".format(self.Context.service_config['beta_template'], resources_to_deploy))
        self.Context.yappy_token = sdk2.Vault.data('NEWS', 'yappy_token')
        self.Context.beta_suffix = 'beta' + str(self.id)
        self.Context.save()

        news_yappy.create_beta_from_template(self.Context.service_config, self.Context.beta_suffix, resources_to_deploy, self.Context.yappy_token, self.Parameters.wait_timeout)
        service_beta_hosts = news_yappy.get_beta_backends(self.Context.service_config, self.Context.beta_suffix, self.Context.yappy_token)

        self.get_service_responses(self.Context.service_config, service_beta_hosts[0])

        self.stop_testing()

    def stop_testing(self):
        if not self.Parameters.keep_beta:
            news_yappy.stop_and_delete_beta(self.Context.service_config, self.Context.beta_suffix, self.Context.yappy_token)

    def on_failure(self, prev_status):
        self.set_info("on_failure called")
        self.stop_testing()

    def on_break(self, prev_status, status):
        self.set_info("on_break called")
        self.stop_testing()

    def load_service_config(self):
        with ProcessLog(self, 'bash_magic.log') as pl:
            environments.SvnEnvironment().prepare()

            sp.check_call(
                ["bash", "-c", "svn cat svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/ya | python - clone"],
                stdout=pl.stdout, stderr=pl.stderr
            )

            sp.check_call(
                ["arcadia/ya", "make", "--checkout", "arcadia/yweb/news/runtime_scripts/yappy"],
                stdout=pl.stdout, stderr=pl.stderr
            )

            service_config = {}
            with open("arcadia/yweb/news/runtime_scripts/yappy/" + self.Parameters.service_name + ".json") as conf:
                service_config = json.load(conf)

            self.set_info("Full service config: " + str(json.dumps(service_config, indent=4)))
            return service_config

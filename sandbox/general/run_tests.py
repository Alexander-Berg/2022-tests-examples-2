import os
import httplib

import sandbox.common.types.misc as ctm
import sandbox.common.types.client as ctc
import sandbox.common.types.resource as ctr

import sandbox.projects.balancer.resources as balancer_resources
import sandbox.projects.common.nanny.nanny as nanny

from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk import paths
from sandbox.sandboxsdk import errors
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk import network
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.channel import channel
from sandbox.projects import resource_types
from sandbox.projects.common import apihelpers
from sandbox.projects.common.search.components import get_media_balancer

from sandbox import sdk2

class BalancerExecutableResourceParameter(parameters.LastReleasedResource):
    name = "balancer_executable_resource_id"
    description = "Balancer executable"
    resource_type = balancer_resources.BALANCER_EXECUTABLE


class ConfigArchiveResourceParameter(parameters.LastReleasedResource):
    name = 'config_archive_resource_id'
    description = 'Config archive'
    resource_type = resource_types.CONFIG_GENERATOR_GENERATED


class MediaTestBalancer(nanny.ReleaseToNannyTask, SandboxTask):

    dns = ctm.DnsType.DNS64
    client_tags = ctc.Tag.LINUX_PRECISE

    input_parameters = [
        BalancerExecutableResourceParameter,
        ConfigArchiveResourceParameter]

    @staticmethod
    def search_for_port(itr):
        for p in itr:
            if network.is_port_free(p):
                return p
        raise errors.SandboxTaskFailureError("Could not find free port for MR process")

    @staticmethod
    def _run_balancer(http_port, binary, config, opts={}):
        # run balancer
        balancer = get_media_balancer(http_port, binary, config, opts)
        balancer.start()
        balancer.wait()
        return balancer

    @staticmethod
    def test_http_request_one_method(
            hostname,
            port,
            method,
            http_path,
            expected_code,
            expected_data=None,
            headers={},
            expected_headers={}):
        connection = httplib.HTTPConnection(hostname, port)
        connection.request(method, http_path, headers=headers)
        response = connection.getresponse()
        if expected_code != response.status:
            raise errors.SandboxTaskFailureError(
                "Request '%s', method %s, expected code %d, got %d" %
                (http_path, method, expected_code, response.status))
        headers_dict = dict([(x[0].lower(), x[1]) for x in response.getheaders()])
        for expected_name, expected_value in expected_headers.iteritems():
            value = headers_dict.get(expected_name.lower(), None)
            if value != expected_value:
                raise errors.SandboxTaskFailureError(
                    "Request '%s', method '%s', expected header '%s' value %s, got %s")

        data = response.read()
        if expected_data is not None:
            if data != expected_data:
                raise errors.SandboxTaskFailureError(
                    "Request '%s', expected data\n'%s'\ngot\n'%s'\n" %
                    (http_path, expected_data, data))

        return data, headers_dict

    def test_http_request(
            self,
            port,
            http_path,
            expected_code,
            expected_data=None,
            headers={},
            expected_headers={},
            hostname=os.uname()[1],
            limit_size_in_kbytes=False,
            disable_headers_check=False):
        data, get_headers = self.test_http_request_one_method(
            hostname, port, 'GET', http_path, expected_code, expected_data, headers, expected_headers)

        if not disable_headers_check:
            _, head_headers = self.test_http_request_one_method(
                hostname, port, 'HEAD', http_path, expected_code, '', headers)
            content_length_key = 'content-length'
            head_headers.pop(content_length_key, None)
            get_headers.pop(content_length_key, None)
            if head_headers != get_headers:
                raise errors.SandboxTaskFailureError(
                    "Request %s, headers for HEAD and GET are different:\n%s\n%s\n" %
                    (http_path, head_headers, get_headers))

        if limit_size_in_kbytes:
            if data.__sizeof__() > (limit_size_in_kbytes * 1024):
                raise errors.SandboxTaskFailureError(
                    "Response length is larger than limit %s (kb). Requested url: %s" %
                    (limit_size_in_kbytes, http_path))
        return data, get_headers

    def graceful_shutdown(self, port):
        '''
            Test graceful shutdown
        '''
        self.test_http_request(
            port,
            '/admin?action=graceful_shutdown',
            httplib.OK,
            hostname='localhost',
            disable_headers_check=True)

    def check_stat_ruchka(self, port):
        '''
            Check statistic report. Output must be concise due to overhead parsing risks
        '''
        self.test_http_request(
            port,
            '/admin/events/call/report',
            httplib.OK,
            hostname='localhost',
            limit_size_in_kbytes=1024,
            disable_headers_check=True)

    def check_version_ruchka(self, port):
        '''
            Check version retrivial. This url using in loop.conf for checking that instance alive
        '''
        self.test_http_request(
            port,
            '/admin?action=version',
            httplib.OK,
            hostname='localhost',
            disable_headers_check=True)

    def _prepare_certs(self):
        certs_resource_id = apihelpers.get_last_resource(resource_types.TEST_SSL_CERTS)
        self.ctx['certs_path'] = channel.task.sync_resource(certs_resource_id)

    def on_enqueue(self):
        generator_resource = channel.sandbox.get_resource(self.ctx[ConfigArchiveResourceParameter.name])
        config_attributes = {
            'tag': generator_resource.attributes['tag']
        }

        self.ctx['config_resources'] = []
        config_resources = self._get_config_names()
        if not config_resources:
            raise errors.SandboxTaskFailureError(
                "You must select some of configuration options")
        for resource in config_resources:
            self._create_resource(
                '{} {}'.format(
                    self.descr,
                    resource),
                self._get_config_resource_path(str(resource)),
                resource,
                arch="any",
                attrs=config_attributes)
            self.ctx['config_resources'].append(str(resource))

    def prepare_task(self, cwd):
        '''
            Get ready binary and config: sync and extract resources
        '''
        tmpdir = os.path.join(cwd, 'tmp')
        # create dir for configs
        paths.make_folder(self._get_config_dir(), True)
        # binary
        if 'balancer_path' not in self.ctx:
            self.ctx['balancer_path'] = self.sync_resource(
                self.ctx[BalancerExecutableResourceParameter.name])
        # config
        if 'archive_path' not in self.ctx:
            self.ctx['archive_path'] = self.sync_resource(
                self.ctx[ConfigArchiveResourceParameter.name])
        # extract configs from gencfg tarball
        for resource_type in self.ctx['config_resources']:
            res = sdk2.Resource[resource_type].find(
                task_id=self.id
            ).first()
            if not res.state == ctr.State.READY:
                res_data = sdk2.ResourceData(res)
                config_path = 'generated/{0}/{1}'.format(
                    self._get_gencfg_dir(),
                    os.path.basename(str(res_data.path)))
                # extract config from gencfg tarball
                process.run_process(["tar",
                                     "-xzvf",
                                     self.ctx['archive_path'],
                                     config_path],
                                    log_prefix='tar',
                                    work_dir=tmpdir)
                paths.copy_path(
                    os.path.join(
                        tmpdir,
                        config_path),
                    str(res_data.path))
                res_data.ready()

    def on_execute(self):
        cwd = self.abs_path()
        # prepare stuff to work
        self.prepare_task(cwd)
        # traverse through all tests
        http_port = self.search_for_port(xrange(11000, 12000))
        for test_name, test_opts in self._get_tests().iteritems():
            # test each config
            for resource_type in self.ctx['config_resources']:
                self.set_info("Run test {0} for {1} config".format(test_name, str(resource_type)))
                res = sdk2.Resource[resource_type].find(task_id=self.id).first()
                res_data = sdk2.ResourceData(res)
                # we use different ports with purpose to have separated log
                # files for each test
                func = test_opts['func']
                opts = self._get_balancer_opts(http_port)
                # start balancer
                balancer = self._run_balancer(http_port, binary=self.ctx['balancer_path'],
                    config=str(res_data.path), opts=opts)
                # test handler
                func(http_port)
                # save logs to sandbox resource and shutdown balancer
                balancer.save_logs_resource()
                balancer.kill_softly()
                http_port = self.search_for_port(xrange(http_port + 10, 12000))
                self.set_info("Passed")

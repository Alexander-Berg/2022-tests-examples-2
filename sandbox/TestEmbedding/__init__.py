import base64
import json
import logging
import os
import requests
import subprocess
import time

from google.protobuf import text_format
import sandbox.common.rest
import sandbox.sdk2.parameters as parameters
from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.projects.common import network
from sandbox.projects.common.betas.beta_api import BetaApi
from sandbox.projects.release_machine import security as rm_sec
from sandbox.projects.websearch.basesearch.resources import EmbeddingStorageExecutable
from sandbox.projects.websearch.basesearch.resources import EmbeddingTestRequests
from sandbox.projects.websearch.basesearch.resources import DYNAMIC_MODELS_ARCHIVE_L1
from sandbox.projects.common.nanny.client import NannyClient
from sandbox.projects.common import binary_task


TRACKER_URL = 'http://vla-tracker-cajuper.n.yandex-team.ru'
EMBEDDING_STORAGE_NANNY_SERVICE_NAME = 'vla_jupiter_embedding_beta'
SERVER_CONFIG_NAME = 'server.cfg'
EMBEDDING_STORAGE_CONFIG_NAME = 'embedding_storage.cfg'
EMBEDDING_STORAGE_REPLICS_CONFIG_NAME = 'embedding_storage_replics.cfg'
INDEX_DIR = 'index_dir'
MODELS_NAME = 'models.archive'
NANNY_URL = 'https://nanny.yandex-team.ru'


class EmbeddingComponent():

    def __init__(self, task, binary_path, data_dir, index_dir, logger, models_path, eventlog_name):
        self.task = task
        self.binary_path = binary_path
        self.data_dir = data_dir
        self.index_dir = index_dir
        self.server_config_path = os.path.join(data_dir, SERVER_CONFIG_NAME)
        self.storage_config_path = os.path.join(data_dir, EMBEDDING_STORAGE_CONFIG_NAME)
        self.storage_replics_config_path = os.path.join(data_dir, EMBEDDING_STORAGE_REPLICS_CONFIG_NAME)
        self.models_path = models_path
        self.eventlog_path = os.path.join(data_dir, eventlog_name)
        self.logger = logger

    def start(self, timeout):
        self.port = network.get_free_port()
        command = [
            self.binary_path,
            '--port', str(self.port),
            '--embedding-storage-config', self.storage_config_path,
            '--embedding-storage-replics-config', self.storage_replics_config_path,
            '--index-dir', self.index_dir,
            '--log', self.eventlog_path,
            '--models-archive', self.models_path,
            '--server-config', self.server_config_path,
        ]
        self.component = subprocess.Popen(command)
        if not self.wait_for_start(self.port, timeout):
            raise Exception('Unable to start on port {}, waiting timeout reached'.format(self.port))
        return self.port

    def save_eventlog(self):
        resource = sdk2.service_resources.TaskLogs(
            task=self.task,
            description=self.eventlog_path[self.eventlog_path.rfind(self.data_dir):],
            path=self.eventlog_path,
        )
        sdk2.ResourceData(resource).ready()

    @staticmethod
    def wait_for_start(port, timeout=60 * 60):
        url = 'http://localhost:{}/unistat'.format(port)
        start = time.time()
        finish = start + timeout
        while time.time() < finish:
            try:
                subprocess.check_output(['curl', url])
                return True
            except Exception:
                time.sleep(1)
        return False

    def make_request(self, request_body, retries, request_number):
        request = 'http://localhost:{}/embedding_storage'.format(self.port)
        while retries:
            retries -= 1
            response = requests.post(request, data=request_body)
            if response.status_code // 100 != 5:
                proto = self.parse_response(response)
                if proto.HasField('ErrorInfo'):
                    self.logger.info('Error for request #{} with ErrorInfo: {}'.format(request_number, proto.ErrorInfo))
                    return
                if proto.NumInvertedIndexStorageUnanswers == 0:
                    return proto
        self.logger.info('Empty answer for request #{} on port {}'.format(request_number, self.port))

    @staticmethod
    def parse_response(response):
        from search.base_search.embedding_storage.protos.embedding_storage_response_pb2 import TEmbeddingStorageResponse
        proto = TEmbeddingStorageResponse()
        proto.ParseFromString(response.content)
        return proto


class PriemkaEmbeddingBinary(sdk2.Task, binary_task.LastBinaryTaskRelease):

    class Requirements(sdk2.Task.Requirements):
        ram = 4 * 1024
        disk_space = 300 * 1024

    class Context(sdk2.Task.Context):
        pass

    class Parameters(sdk2.Task.Parameters):
        first_binary = parameters.Resource(
            'First binary',
            resource_type=EmbeddingStorageExecutable,
            required=True,
        )
        second_binary = parameters.Resource(
            'Second binary',
            resource_type=EmbeddingStorageExecutable,
            required=True,
        )
        first_models_archive = parameters.Resource(
            'First models.archive',
            resource_type=DYNAMIC_MODELS_ARCHIVE_L1,
            required=False,
        )
        second_models_archive = parameters.Resource(
            'Second models.archive',
            resource_type=DYNAMIC_MODELS_ARCHIVE_L1,
            required=False,
        )
        proxy = parameters.String('YT proxy', default='hahn')
        logs_table = parameters.String('Table for getting requests')
        retries_on_request = parameters.Integer('Retries for each request', default=3)
        unanswers_threshold = parameters.Integer('Max percent of unanswers', default=1)
        different_unswers_threshold = parameters.Integer('Percent of logged different answers', default=0)
        number_of_requests = parameters.Integer('Number of requests', default=10000)
        wait_time = parameters.Integer('Time for wait hamster', default=60 * 60 * 3)
        tasks_archive_resource = binary_task.binary_release_parameters(stable=True)
        start_timeout = parameters.Integer("Time for embedding storage start", default=3 * 60 * 60) # 3 hourse

    logger = logging.getLogger('TASK_LOGGER')
    logger.setLevel(logging.DEBUG)


    def start_embedding(self, binary_param, data_dir, index_dir, models_param, logger, embedding_index, starting_timeout):
        binary_path = str(
            sdk2.ResourceData(
                sdk2.Resource[binary_param]
            ).path
        )
        models_path = str(sdk2.ResourceData(sdk2.Resource[models_param]).path) if models_param else os.path.join(data_dir, MODELS_NAME)
        embedding = EmbeddingComponent(self, binary_path, data_dir, index_dir, self.logger, models_path, 'eventlog{}'.format(embedding_index))
        try:
            port = embedding.start(starting_timeout)
            self.logger.info('Embedding#{} started on port {}'.format(embedding_index, port))
        except Exception as e:
            raise TaskFailure('Embedding#{} not started: {}'.format(embedding_index, e))
        return embedding

    def on_save(self):
        binary_task.LastBinaryTaskRelease.on_save(self)

    def on_execute(self):
        binary_task.LastBinaryTaskRelease.on_execute(self)
        first_embedding = None
        second_embedding = None
        try:
            self.logger.info('Checking hamster consistent')
            if not self.check_hamster_consistent():
                raise sdk2.WaitTime(self.Parameters.wait_time)
            self.logger.info('Hamster ready')

            data_dir = os.path.abspath('data')
            self.prepare_configs(data_dir)
            self.logger.info('Got production timestamp {}'.format(self.production_timestamp))
            self.download_shard()

            requests_bodies = self.get_requests()
            if not requests_bodies:
                raise TaskFailure('Fail to get requests')
            self.logger.info('Got {} requests'.format(len(requests_bodies)))
            self.save_requests(requests_bodies)

            first_embedding = self.start_embedding(self.Parameters.first_binary, data_dir, INDEX_DIR, self.Parameters.first_models_archive, self.logger, 1, self.Parameters.start_timeout)
            second_embedding = self.start_embedding(self.Parameters.second_binary, data_dir, INDEX_DIR, self.Parameters.second_models_archive, self.logger, 2, self.Parameters.start_timeout)

            from search.base_search.embedding_storage.protos.embedding_storage_request_pb2 import TEmbeddingStorageRequest  # noqa
            unanswers_counter = 0
            different_answers_counter = 0

            for i in range(len(requests_bodies)):
                body = requests_bodies[i]
                proto = TEmbeddingStorageRequest()
                proto.ParseFromString(base64.b64decode(body))
                proto.Partition = 0
                proto.Timestamp = self.production_timestamp
                bin_data = proto.SerializeToString()
                response1 = first_embedding.make_request(bin_data, self.Parameters.retries_on_request, i)
                response2 = second_embedding.make_request(bin_data, self.Parameters.retries_on_request, i)

                if response1 and response2:
                    diff = self.get_diff(response1, response2)
                    if diff:
                        self.logger.info('Not equal answer for request #{}'.format(i))
                        self.logger.info('Request:\n{}'.format(text_format.MessageToString(proto)))
                        self.logger.info('Diff:\n{}'.format(diff))
                        different_answers_counter += 1
                else:
                    unanswers_counter += 1

                if unanswers_counter * 100 > self.Parameters.number_of_requests * self.Parameters.unanswers_threshold:
                    raise TaskFailure('Unanswers treshold reached')
                if (
                    different_answers_counter * 100
                    > self.Parameters.number_of_requests * self.Parameters.different_unswers_threshold
                ):
                    raise TaskFailure('Different answers treshold reached')

            #if different_answers_counter > 0:
            #    raise TaskFailure('Found {} different answers'.format(different_answers_counter))
        except TaskFailure as error:
            raise error
        finally:
            if first_embedding:
                first_embedding.save_eventlog()
            if second_embedding:
                second_embedding.save_eventlog()

    def save_requests(self, requests_bodies):
        with open('requests', 'w') as out:
            for i in range(len(requests_bodies)):
                out.write('{}: {}\n'.format(i, requests_bodies[i]))
        requests_resource = EmbeddingTestRequests(
            task=self,
            description='Bodies of requests',
            path='requests'
        )
        sdk2.ResourceData(requests_resource).ready()

    def prepare_configs(self, data_dir):
        import search.base_search.daemons.import_basesearch_daemon as util
        import search.base_search.daemons.embedding_storage.import_embedding_storage.lib as config_maker
        import search.tools.devops.libs.nanny_services as nanny_services
        from google.protobuf import text_format
        from search.base_search.embedding_storage.protos.embedding_storage_config_pb2 import TEmbeddingStorageConfig

        NANNY_TOKEN = rm_sec.get_rm_token(self)
        nanny_client = NannyClient(NANNY_URL, NANNY_TOKEN)

        server_config_path = os.path.join(data_dir, SERVER_CONFIG_NAME)
        storage_config_path = os.path.join(data_dir, EMBEDDING_STORAGE_CONFIG_NAME)
        storage_replics_config_path = os.path.join(data_dir, EMBEDDING_STORAGE_REPLICS_CONFIG_NAME)

        instances = []
        for item in nanny_client.get_service_current_instances(EMBEDDING_STORAGE_NANNY_SERVICE_NAME)['result']:
            self.logger.info(item)
            instances.append(item['container_hostname'] + ':' + str(item['port']))

        #config_maker.set_hamster_port(instances)
        util.update_server_config(instances, server_config_path, rewrite_instances=True)
        config_maker.update_storage_configs(instances, storage_config_path, storage_replics_config_path)

        proto = TEmbeddingStorageConfig()
        text_format.Parse(open(storage_config_path, 'r').read(), proto)
        del proto.InvertedIndexStorageSourceOptions.TaskOptions.ConnectTimeouts[1:]
        proto.InvertedIndexStorageSourceOptions.TaskOptions.ConnectTimeouts[0] = '600ms'

        del proto.InvertedIndexStorageSourceOptions.TaskOptions.SendingTimeouts[1:]
        proto.InvertedIndexStorageSourceOptions.TaskOptions.SendingTimeouts[0] = '600ms'

        for i in range(len(proto.InvertedIndexStorageSourceOptions.HedgedRequestOptions.HedgedRequestTimeouts[1:])):
            proto.InvertedIndexStorageSourceOptions.HedgedRequestOptions.HedgedRequestTimeouts[i] = '10ms'

        proto.InvertedIndexStorageSourceOptions.TimeOut = '600ms'
        proto.LockMemory = True
        config_maker.write_message(proto, storage_config_path)

        session = nanny_services.get_session(NANNY_TOKEN)
        service = json.loads(
            nanny_services.get_service(service_id=EMBEDDING_STORAGE_NANNY_SERVICE_NAME, session=session).text
        )
        sandbox_client = sandbox.common.rest.Client()
        if not self.Parameters.first_models_archive or not self.Parameters.second_models_archive:
            models_rbtorrent = util.get_sandbox_resource_rbtorrent(service, sandbox_client, MODELS_NAME)
            util.download_rbtorrent(models_rbtorrent, '{}_{}'.format(MODELS_NAME, 1), data_dir)

        shard_name = util.info_request_rewrite_instances(instances, "get_shard_name")
        shard_timestamp = shard_name[shard_name.rfind('-') + 1:]
        self.production_timestamp = int(shard_timestamp)

    @staticmethod
    def get_shard_torrent(timestamp):
        import infra.callisto.deploy.tracker.client as tracker_client
        resource_name = 'EmbeddingWebTier0-0-0-{}'.format(timestamp)
        namespace = '/web/prod/yt/{}/EmbeddingWebTier0'.format(timestamp)
        resolved_resource = tracker_client.Client(TRACKER_URL).resolve_one(namespace, resource_name)
        return resolved_resource.rbtorrent

    def download_shard(self):
        torrent = self.get_shard_torrent(self.production_timestamp)
        self.logger.info('Start downloading shard from {}'.format(torrent))
        subprocess.check_call(['sky', 'get', '-d', INDEX_DIR, '-wup', torrent])
        subprocess.check_call(['chmod', 'a+rw', '-R', INDEX_DIR])

    @staticmethod
    def check_hamster_consistent():
        api = BetaApi.fromurl()
        return api.is_beta_consistent('hamster')

    @staticmethod
    def get_sorted_list_docs(proto):
        docs = list(proto.L1Docs)
        for i in range(len(docs)):
            docs[i].Relevance = round(docs[i].Relevance, 3)
            docs[i].DssmDotProduct = round(docs[i].DssmDotProduct, 5)
            docs[i].MatchedPantherTermsSum = round(docs[i].MatchedPantherTermsSum, 5)
            docs[i].MatchedPantherTermsMax = round(docs[i].MatchedPantherTermsMax, 5)
        docs.sort(key=lambda x: x.DocId)
        return docs

    def get_diff(self, response1, response2):
        docs1 = self.get_sorted_list_docs(response1)
        docs2 = self.get_sorted_list_docs(response2)
        if docs1 != docs2:
            with open('res1', 'w') as out:
                for doc in docs1:
                    out.write(str(doc) + '\n')
            with open('res2', 'w') as out:
                for doc in docs2:
                    out.write(str(doc) + '\n')
            pr = subprocess.Popen(['diff', 'res1', 'res2'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = pr.communicate()
            return result[0]

    def get_requests(self):
        import yt.wrapper as yt
        requests = []
        YT_TOKEN = sdk2.Vault.data('SEARCH-RELEASERS', 'yt_token_for_testenv')
        client = yt.YtClient(proxy=self.Parameters.proxy, token=YT_TOKEN)
        log_table = self.Parameters.logs_table
        if not log_table:
            log_table = self.get_last_table()
            self.logger.info('Requests will be recieved from {}'.format(log_table))
        for row in client.read_table(log_table):
            if '/embedding_storage' in row['event_data'] and row['event_type'] == 'SubSourceRequest':
                body = row['event_data'].split()[-1].strip()
                requests.append(body)
            if len(requests) == self.Parameters.number_of_requests:
                return requests
        return requests

    def get_last_table(self):
        import yt.wrapper as yt
        YT_TOKEN = sdk2.Vault.data('SEARCH-RELEASERS', 'yt_token_for_testenv')
        client = yt.YtClient(proxy=self.Parameters.proxy, token=YT_TOKEN)
        tables = list(client.search('//home/eventlogdata/WebTier0', node_type=['table']))
        if not tables:
            raise TaskFailure('Cannot get table with evenlog')
        tables.sort()
        if client.row_count(tables[-1]) < 100000:
            return max(tables, key=lambda x: client.row_count(x))
        return tables[-1]

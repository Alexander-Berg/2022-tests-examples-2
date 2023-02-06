# coding=utf-8
import logging

from sandbox.projects.common import binary_task
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.metrika import utils

from sandbox.projects.metrika.utils import settings
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.projects.metrika.utils.mixins import juggler_reporter
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.pipeline import pipeline
from sandbox.projects.metrika.utils.pipeline.contextable import Contextable
from sandbox.sdk2 import parameters
import sandbox.sdk2 as sdk2


class State(Contextable):
    def __init__(self, storage=None):
        super(State, self).__init__(storage)

    @property
    def config(self):
        return self._default_getter()

    @config.setter
    def config(self, value):
        self._default_setter(value)


@with_parents
class MetrikaCoreRestoreTestTransfers(
    pipeline.PipelineBaseTask, juggler_reporter.JugglerMultiReporterMixin, BaseConsoleMixin
):
    """
    Обновление трансферов тестинга из MDB в YT/LB.
    """

    class Requirements(pipeline.PipelineBaseTask.Requirements):
        disk_space = 1 * 1024
        ram = 512

    class Parameters(utils.CommonParameters):
        description = "Обновление трансферов тестинга из MDB в YT/LB."

        is_report_to_juggler = parameters.Bool(
            "Отправлять ли событие в Juggler",
            required=True,
            default_value=True,
            description="Должно быть выставлено, если производится регулярный запуск, например, из шедулера.",
        )

        with parameters.Group('transfer') as transfer_group:
            mysql_cluster = parameters.String(
                "MySql cluster name",
                default="test-mtacs-conv_main",
                required=True,
                description="MySql input cluster name",
            )
            mysql_input_endpoint = parameters.String(
                "MySql endpoint name",
                default="test-conv-main-mv-input",
                required=True,
                description="MySql input endpoint name",
            )
            tnx_output_endpoint = parameters.String(
                "Transactions output endpoint name",
                default="test-conv-main-mv-transactions",
                required=True,
                description="Transactions output endpoint name",
            )
            snapshot_output_endpoint = parameters.String(
                "Snapshot output endpoint name",
                default="test-conv-main-mv-snapshot",
                required=True,
                description="Snapshot output endpoint name",
            )
            tnx_transfer = parameters.String(
                "Transactions transfer name",
                default="test-conv-main-mv-transactions-log",
                required=True,
                description="Transactions transfer name",
            )
            snapshot_transfer = parameters.String(
                "Snapshot transfer name",
                default="test-conv-main-mv-snapshot",
                required=True,
                description="Snapshot transfer name",
            )

        with parameters.Group('cloud') as cloud_group:
            yc_dt_folder_id = parameters.String(
                "YC DT folder_id", default="foori5uktoh2v12cbltq", required=True, description="Yandex Cloud Data Transfer folder_id"
            )
            yt_materialized_view_control_path = parameters.String(
                "MV Control path",
                default="//home/metrika-core-test/materialized-views/control/",
                required=True,
                description="Materialized View test control directory path",
            )

        with parameters.Group("Секреты") as secrets_group:
            yc_token = parameters.YavSecret(
                'Cloud token',
                required=True,
                default='{}#ymdb_oauth_token'.format(settings.rma_yav_uuid),
                description="Секрет с токеном для доступа облаку",
            )
            yt_token = parameters.YavSecret(
                'YT token',
                required=True,
                default='{}#yt_oauth_token'.format(settings.rma_yav_uuid),
                description="Секрет с токеном для доступа к YT кластеру Markov",
            )
            conv_main_mysql_dt_password = parameters.YavSecret(
                'MySql password',
                required=True,
                default='{}#data_transfer'.format(settings.mdb_mysql_passwords_uuid),
                description="Пароль пользователя data_transfer от conv_main тестового mysql",
            )

        dry_run = parameters.Bool("Dry run", default=False, required=True, description="Dry run")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    juggler_host = None
    juggler_service = None

    def _juggler_predicate(self, status):
        return self.Parameters.is_report_to_juggler

    @property
    def pipeline_state(self):
        return State(self.Context.pipeline_state)

    class Context(pipeline.PipelineBaseTask.Context):
        pipeline_state = State().state

    @memoized_property
    def mdb_mysql_client(self):
        import metrika.pylib.yc.mysql as mdb

        return mdb.ManagedMySQL(token=self.Parameters.yc_token.value())

    @memoized_property
    def data_transfer_client(self):
        import metrika.pylib.yc.data_transfer as data_transfer

        return data_transfer.DataTransfer(
            folder_id=self.Parameters.yc_dt_folder_id, token=self.Parameters.yc_token.value()
        )

    def create_stages(self):
        return [
            (self.initialize, 'Инициализация'),
            (self.remove_old, 'Удаление старого эндпоинта и трансфера'),
            (self.create_new, 'Создание нового эндпоинта и трансфера'),
            (self.activate_log, 'Активация трансфера для лога'),
            (self.wait_for_log, 'Ожидание работы трансфера для лога'),
            (self.activate_snapshot, 'Активация трансфера для снепшота'),
            (self.wait_for_snapshot, 'Ожидание работы трансфера для снепшота'),
            (self.reload_command, 'Отправить в materialized-view-testing команду на пересчет'),
        ]

    def initialize(self):
        logging.info("Initialized: dry_run={}".format(self.Parameters.dry_run))
        return

    def get_mdb_mysql_by_name(self, name):
        return self.mdb_mysql_client.cluster_by_name(cluster_name=name, folder_id=self.Parameters.yc_dt_folder_id)

    def get_endpoint_by_name_and_check(self, name):
        endpoint = self.data_transfer_client.get_endpoint_by_name(name)
        if endpoint is None:
            raise RuntimeError('Can\'t find {}.'.format(name))
        else:
            return endpoint

    def get_transfer_by_name_and_check(self, name):
        transfer = self.data_transfer_client.get_transfer_by_name(name)
        if transfer is None:
            raise RuntimeError('Can\'t find {}.'.format(name))
        else:
            return transfer

    def activate_transfer(self, transfer, wait):
        op = transfer.activate()
        if wait:
            op.wait_for_done()
            op.verify()

    def wait_for_transfer_status(self, transfer, status, period):
        from metrika.pylib.yc.data_transfer import Transfer

        logging.info("Transfer {}:{} status = {}. Waiting for {}...".format(
            transfer.id, transfer.name, transfer.status, status))
        if transfer.status != status:
            raise sdk2.WaitTime(time_to_wait=period)
        elif transfer.status == Transfer.Status.ERROR:
            raise RuntimeError('Transfer {}:{} status is ERROR'.format(transfer.id, transfer.name))

    def create_input_endpoint(self):
        cluster = self.get_mdb_mysql_by_name(self.Parameters.mysql_cluster)
        logging.info(
            "Create input endpoint {} for cluster {}:{}".format(
                self.Parameters.mysql_input_endpoint, cluster.id, cluster.name
            )
        )
        if not self.Parameters.dry_run:
            self.data_transfer_client.create_endpoint(
                {
                    "folderId": self.data_transfer_client.folder_id,
                    "name": self.Parameters.mysql_input_endpoint,
                    "description": self.Parameters.mysql_input_endpoint,
                    "settings": {
                        "mysqlSource": {
                            "connection": {
                                "mdbClusterId": cluster.id,
                            },
                            "database": "conv_main",
                            "user": "data_transfer",
                            "password": {
                                "raw": self.Parameters.conv_main_mysql_dt_password.value(),
                            },
                            "includeTablesRegex": [
                                "^counters$",
                                "^ad_goals$",
                                "^ad_goals_urls$",
                            ],
                        },
                    },
                }
            )

    def create_transfer_log(self):
        source = self.get_endpoint_by_name_and_check(self.Parameters.mysql_input_endpoint)
        target = self.get_endpoint_by_name_and_check(self.Parameters.tnx_output_endpoint)
        logging.info(
            "Create transfer log {}:: {}:{} -> {}:{}".format(
                self.Parameters.tnx_transfer, source.id, source.name, target.id, target.name
            )
        )
        if not self.Parameters.dry_run:
            self.data_transfer_client.create_transfer(
                {
                    "sourceId": source.id,
                    "targetId": target.id,
                    "name": self.Parameters.tnx_transfer,
                    "description": self.Parameters.tnx_transfer,
                    "folderId": self.data_transfer_client.folder_id,
                    "type": "INCREMENT_ONLY",
                }
            )

    def create_transfer_snapshot(self):
        source = self.get_endpoint_by_name_and_check(self.Parameters.mysql_input_endpoint)
        target = self.get_endpoint_by_name_and_check(self.Parameters.snapshot_output_endpoint)
        logging.info(
            "Create transfer snapshot {}:: {}:{} -> {}:{}".format(
                self.Parameters.snapshot_transfer, source.id, source.name, target.id, target.name
            )
        )
        if not self.Parameters.dry_run:
            self.data_transfer_client.create_transfer(
                {
                    "sourceId": source.id,
                    "targetId": target.id,
                    "name": self.Parameters.snapshot_transfer,
                    "description": self.Parameters.snapshot_transfer,
                    "folderId": self.data_transfer_client.folder_id,
                    "runtime": {
                        "yt_runtime": {
                            "job_count": "1",
                            "yt_cluster": "YT_RUNTIME_CLUSTER_VANGA",
                            "ram": "4.0 GB",
                            "cpu": 4,
                        }
                    },
                    "type": "SNAPSHOT_AND_INCREMENT",
                }
            )

    def remove_old(self):
        transfers = [
            self.data_transfer_client.get_transfer_by_name(self.Parameters.tnx_transfer),
            self.data_transfer_client.get_transfer_by_name(self.Parameters.snapshot_transfer),
        ]
        for transfer in transfers:
            if transfer is None:
                continue
            logging.info("Deactivate and delete transfer {}:{}".format(transfer.id, transfer.name))
            if not self.Parameters.dry_run:
                op = transfer.deactivate()
                op.wait_for_done()

                op = transfer.delete()
                op.wait_for_done()
                op.verify()

        endpoints = [self.data_transfer_client.get_endpoint_by_name(self.Parameters.mysql_input_endpoint)]
        for endpoint in endpoints:
            if endpoint is None:
                continue
            logging.info("Deactivate and delete endpoint {}:{}".format(endpoint.id, endpoint.name))
            if not self.Parameters.dry_run:
                op = endpoint.delete()
                op.wait_for_done()
                op.verify()

    def create_new(self):
        self.create_input_endpoint()
        self.create_transfer_log()
        self.create_transfer_snapshot()

    def activate_log(self):
        transfer = self.get_transfer_by_name_and_check(self.Parameters.tnx_transfer)
        logging.info("activate log: {}:{}".format(transfer.id, transfer.name))
        if not self.Parameters.dry_run:
            self.activate_transfer(transfer, wait=False)

    def wait_for_log(self):
        from metrika.pylib.yc.data_transfer import Transfer

        transfer = self.get_transfer_by_name_and_check(self.Parameters.tnx_transfer)
        logging.info("wait for log: {}:{}".format(transfer.id, transfer.name))
        if not self.Parameters.dry_run:
            self.wait_for_transfer_status(transfer, Transfer.Status.RUNNING, 60)

    def activate_snapshot(self):
        transfer = self.get_transfer_by_name_and_check(self.Parameters.snapshot_transfer)
        logging.info("activate snapshot: {}:{}".format(transfer.id, transfer.name))
        if not self.Parameters.dry_run:
            self.activate_transfer(transfer, wait=False)

    def wait_for_snapshot(self):
        from metrika.pylib.yc.data_transfer import Transfer

        transfer = self.get_transfer_by_name_and_check(self.Parameters.snapshot_transfer)
        logging.info("wait for snapshot: {}:{}".format(transfer.id, transfer.name))
        if not self.Parameters.dry_run:
            self.wait_for_transfer_status(transfer, Transfer.Status.RUNNING, 600)

    def reload_command(self):
        import yt.wrapper as yt

        path = self.Parameters.yt_materialized_view_control_path + 'commands'
        logging.info('Adding reload command to {}'.format(path))
        client = yt.YtClient(proxy='markov', config={'backend': 'rpc', 'token': self.Parameters.yt_token.value()})
        with client.Transaction(type='tablet'):
            rows = client.select_rows('* FROM [{}]'.format(path))
            new_id = max(list(map(lambda x: x['id'], rows)) + [0]) + 1
            data = {
                'id': new_id,
                'cmd': 'NEW_VERSION',
                'done': False,
            }
            client.insert_rows(path, [data])
            logging.info("Added reload command: {}".format(data))

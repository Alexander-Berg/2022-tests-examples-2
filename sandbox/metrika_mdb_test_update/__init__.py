# coding=utf-8
import datetime
import json
import logging
import pprint

import sandbox.sdk2 as sdk2
from sandbox.common import fs
from sandbox.common.types.resource import RestartPolicy
from sandbox.common.utils import get_task_link
from sandbox.projects.common import binary_task
from sandbox.projects.common.decorators import memoized_property, memoize
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.admins.metrika_mdb_test_update.state import State, ClusterConglomerate
from sandbox.projects.metrika.core.metrika_core_restore_test_transfers import MetrikaCoreRestoreTestTransfers
from sandbox.projects.metrika.utils import settings, render
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.projects.metrika.utils.mixins import juggler_reporter
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.parameters import LastMySqlContainerResource
from sandbox.projects.metrika.utils.pipeline import pipeline
from sandbox.sdk2 import parameters


class MySqlDumps(sdk2.Resource):
    """
    Дампы которые нужно сохранить при подвозе бекапа в тестинг, нужен только для передачи данных между стадиями конвейера
    """
    executable = False
    auto_backup = False
    any_arch = True
    restart_policy = RestartPolicy.IGNORE
    share = False

    # Формат конфигурационного файла:
    # settings:
    #   restore_poll_period: 600
    # clusters:
    #   test-<cluster name>:
    #     folder_id: foori5uktoh2v12cbltq
    #     proto_cluster_id: <Идентификатор кластера прода>
    #     upgrade: True/False
    #     dumps:
    #         -
    #             db: <БД для дампа>
    #             tables:
    #                 - <таблица для дампа>
    #                 - <таблица для дампа>
    #     postprocess:
    #         - update ...
    #         - insert ...
    #     user: dba
    #     password:
    #         secret_id: sec-01ep6qbrjdxhpwrebchccqb8fz
    #         key: dba-password


def make_flat_topology(cluster):
    """
    убирает у всех реплик replication source - делает топологию кластера плоской
    """
    from metrika.pylib.yc.common import suppress_no_changes_detected

    hosts = cluster.list_hosts()
    logging.info("hosts:\n{}".format(pprint.pformat(hosts)))

    update_hosts_spec = {"updateHostSpecs": []}

    for host in hosts:
        if host.replication_source:
            update_hosts_spec["updateHostSpecs"].append(
                {
                    "hostName": host.name,
                    "updateMask": "replicationSource"
                }
            )

    logging.info("update hosts spec:\n{}".format(pprint.pformat(update_hosts_spec)))

    if not update_hosts_spec["updateHostSpecs"]:
        logging.info("No topology updates needed.")
        return

    # MDBSUPPORT-5554 - поштучно
    for update_host_spec in update_hosts_spec["updateHostSpecs"]:
        suppress_no_changes_detected(cluster.update_hosts, {"updateHostSpecs": [update_host_spec]})


def copy_topology(src_cluster, dst_cluster):
    """
    копирует топологию из исходного кластера в целевой
    поддержаны только реплики от реплик первого уровня
    целевой кластер должен быть плоским перед копированием
    """
    from metrika.pylib.yc.common import suppress_no_changes_detected
    old_hosts = src_cluster.list_hosts()
    new_hosts = dst_cluster.list_hosts()

    logging.info("old hosts:\n{}".format(pprint.pformat(old_hosts)))
    logging.info("new hosts:\n{}".format(pprint.pformat(new_hosts)))

    map_old = {}
    for host in old_hosts:
        if host.zone_id not in map_old:
            map_old[host.zone_id] = []
        map_old[host.zone_id].append(host.name)

    logging.info("map old hosts:\n{}".format(pprint.pformat(map_old)))

    names_map_old = {}
    for zone_id, hosts in map_old.items():
        for indx, host in enumerate(hosts, 1):
            names_map_old[host] = "{}-{}".format(zone_id, indx)

    logging.info("names map old:\n{}".format(pprint.pformat(names_map_old)))

    topology = {}
    for host in old_hosts:
        topology[names_map_old[host.name]] = names_map_old.get(host.replication_source, None)

    logging.info("topology:\n{}".format(pprint.pformat(topology)))

    # а теперь из topology получим настройки replicationSource для нового кластера
    names_map_new = {}
    for host in new_hosts:
        if host.zone_id not in names_map_new:
            names_map_new[host.zone_id] = []
        names_map_new[host.zone_id].append(host.name)

    logging.info("map new hosts:\n{}".format(pprint.pformat(names_map_new)))

    names_map_reverse_new = {}
    for zone_id, hosts in names_map_new.items():
        for indx, host in enumerate(hosts, 1):
            names_map_reverse_new["{}-{}".format(zone_id, indx)] = host

    logging.info("names reverse map new:\n{}".format(pprint.pformat(names_map_reverse_new)))

    update_hosts_spec = {"updateHostSpecs": []}

    for host, replication_source in topology.items():
        if replication_source:
            update_hosts_spec["updateHostSpecs"].append(
                {
                    "hostName": names_map_reverse_new[host],
                    "replicationSource": names_map_reverse_new[replication_source],
                    "updateMask": "replicationSource"
                }
            )

    logging.info("update hosts spec:\n{}".format(pprint.pformat(update_hosts_spec)))

    if not update_hosts_spec["updateHostSpecs"]:
        logging.info("No topology updates needed.")
        return

    # если мастер тот хост, что станет репликой от реплики, то убрать мастера на другой хост, который не будет репликой от реплики
    # иначе получается выстрел в ногу, который отстрелит все ноги кластера - MDBSUPPORT-5543
    current_old_master = next(iter(filter(lambda host: host.is_master, old_hosts)))
    new_master = names_map_reverse_new[names_map_old[current_old_master.name]]

    logging.info("Prevent shot in the leg - MDBSUPPORT-5543 - switch master")
    suppress_no_changes_detected(dst_cluster.start_failover, new_master)

    # MDBSUPPORT-5554 - поштучно
    for update_host_spec in update_hosts_spec["updateHostSpecs"]:
        suppress_no_changes_detected(dst_cluster.update_hosts, {"updateHostSpecs": [update_host_spec]})


@with_parents
class MetrikaMdbTestUpdate(pipeline.PipelineBaseTask, juggler_reporter.JugglerMultiReporterMixin, BaseConsoleMixin):
    """
    Обновление кластеров тестинга в MDB из бекапов прода.
    """

    class Requirements(pipeline.PipelineBaseTask.Requirements):
        disk_space = 100 * 1024
        ram = 64 * 1024

    class Parameters(utils.CommonParameters):
        description = "Подвоз бекапов в тестинг в MDB"

        container = LastMySqlContainerResource("Environment container resource", required=True)

        with parameters.CheckGroup("Имя кластера в MDB", required=True,
                                   description="Задаётся имя тестового кластера, в конце будет удалён.") as mdb_cluster_names:
            mdb_cluster_names.values['test-mtacs-adv_main'] = None
            mdb_cluster_names.values['test-mtacs-adv_rbac'] = None
            mdb_cluster_names.values['test-mtacs-conv_main'] = None
            mdb_cluster_names.values['test-mtacs-rbac'] = None
            mdb_cluster_names.values['test-mtacs-mobile'] = None
            mdb_cluster_names.values['test-mtacs-mobile-rbac'] = None

        is_report_to_juggler = parameters.Bool("Отправлять ли событие в Juggler", required=True, default_value=False,
                                               description="Должно быть выставлено, если производится регулярный запуск, например, из шедулера.")

        with parameters.Group('bishop') as bishop_group:
            bishop_program = parameters.String("Программа", default="metrika-mdb-test-update", required=True,
                                               description="Имя программы в bishop")
            bishop_environment = parameters.String("Окружение", default="metrika.sandbox.admin.production", required=True,
                                                   description="Имя окружения в bishop")

        with parameters.Group("Секреты") as secrets_group:
            bishop_token = parameters.YavSecret('Bishop token', required=True, default='{}#bishop_oauth_token'.format(settings.rma_yav_uuid),
                                                description="Секрет с токеном для доступа к bishop")
            yav_token = parameters.YavSecret('Vault token', required=True, default='{}#vault_oauth_token'.format(settings.rma_yav_uuid),
                                             description="Секрет с токеном для доступа к секретнице")
            yc_token = parameters.YavSecret('Cloud token', required=True, default='{}#ymdb_oauth_token'.format(settings.rma_yav_uuid),
                                            description="Секрет с токеном для доступа облаку")
            yp_token = parameters.YavSecret('YP token', required=True, default='{}#yp_token'.format(settings.rma_yav_uuid),
                                            description="Секрет с токеном для доступа к YP - API Deploy")
            yt_token = parameters.YavSecret('YT token', required=True, default='{}#yt_oauth_token'.format(settings.rma_yav_uuid),
                                            description="Секрет с токеном для доступа к YT кластеру Locke")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    juggler_host = None
    juggler_service = None

    def get_events(self):
        return [(None, mdb_cluster_name, None, None) for mdb_cluster_name in self.Parameters.mdb_cluster_names]

    def _juggler_predicate(self, status):
        return self.Parameters.is_report_to_juggler

    @property
    def pipeline_state(self):
        return State(self.Context.pipeline_state)

    class Context(pipeline.PipelineBaseTask.Context):
        pipeline_state = State().state

    @memoized_property
    def vault_client(self):
        import metrika.pylib.vault as vault
        return vault.VaultClient(auth_type="oauth", oauth_token=self.Parameters.yav_token.value())

    @memoized_property
    def mdb_mysql_client(self):
        import metrika.pylib.yc.mysql as mdb
        return mdb.ManagedMySQL(token=self.Parameters.yc_token.value())

    @memoized_property
    def bishop_client(self):
        from metrika.pylib.bishop import Bishop
        bishop_client = Bishop(token=self.Parameters.bishop_token.value())
        bishop_client._verify = False
        return bishop_client

    @memoized_property
    def deploy_client(self):
        from metrika.pylib.deploy.client import DeployAPI
        deploy_client = DeployAPI(token=self.Parameters.yp_token.value())
        return deploy_client

    @memoized_property
    def wiki_client(self):
        import library.python.wiki.wiki as wiki
        # можно использовать любой OAuth-токен
        return wiki.Wiki(oauth_token=self.Parameters.bishop_token.value())

    @memoized_property
    def config(self):
        import metrika.pylib.structures.dotdict as dotdict
        return dotdict.DotDict.from_dict(self.pipeline_state.config)

    @memoize
    def get_defaults_file(self, name):
        defaults_content = [
            '[client]',
            'password=' + self.vault_client.get_version(self.config.clusters[name].password.secret_id)["value"][self.config.clusters[name].password.key]
        ]

        defaults_file_path = self.path("{}.defaults".format(name))
        defaults_file_path.write_text("\n".join(defaults_content))
        return defaults_file_path.as_posix()

    def get_master_host(self, cluster_id):
        logging.debug("Get master host for {}".format(cluster_id))
        cluster = self.mdb_mysql_client.cluster_by_id(cluster_id)
        hosts = cluster.list_hosts()
        master = next(host for host in hosts if host.is_master)
        logging.debug("Master host for {} is {}".format(cluster_id, master.name))
        return master.name

    def create_stages(self):
        return [
            (self.initialize, 'Инициализация'),
            (self.validate, 'Валидация старого кластера'),
            (self.start_restore, 'Запуск восстановления нового кластера из бекапа'),
            (self.store_old_data, 'Сохрание данных из старого кластера'),
            (self.wait_for_restore, 'Ожидание восстановления нового кластера'),
            (self.post_process, 'Постобработка нового кластера'),
            (self.restart_haproxy, 'Рестарт haroxy'),
            (self.remove_old_cluster, 'Удаление старого кластера'),
            (self.recreate_testing_datatransfers, 'Пересоздать Data Transfer трансферы и эндпоинты для тестового materialized-view'),
        ]

    def initialize(self):
        """
        Получить конфиг из бишопа
        :return:
        """
        import metrika.pylib.config as config

        self.pipeline_state.config = config.get_yaml_config_from_bishop(
            program=self.Parameters.bishop_program,
            environment=self.Parameters.bishop_environment,
            token=self.Parameters.bishop_token.value(),
            vault_client=self.vault_client)

        self.pipeline_state.config.clusters = {k: v for k, v in self.pipeline_state.config.clusters.items() if k in self.Parameters.mdb_cluster_names}

    def validate(self):
        # проверяем, что кластер действительно testing
        # и что имеет haproxy
        for mdb_cluster_name in self.Parameters.mdb_cluster_names:
            cluster = self.mdb_mysql_client.cluster_by_name(mdb_cluster_name, self.config.clusters[mdb_cluster_name].folder_id)

            environment = cluster.labels.get('environment')
            if environment != 'testing':
                raise pipeline.PipelineAbortError("Cluster {} in unexpected environment {}".format(mdb_cluster_name, environment))
            if 'haproxy' not in cluster.labels:
                raise pipeline.PipelineAbortError("No haproxy label in cluster {}".format(mdb_cluster_name))

            conglomerate = ClusterConglomerate()
            conglomerate.cluster_name = mdb_cluster_name
            conglomerate.old_cluster_id = cluster.id
            conglomerate.haproxy = cluster.labels.haproxy
            self.pipeline_state.add_cluster_conglomerate(conglomerate)

    def start_restore(self):
        import udatetime

        # фиксируем момент времени, на который будет производиться восстановление бекапов кластеров
        target_time_stamp = udatetime.to_string(datetime.datetime.utcnow().replace(second=0, microsecond=0) - datetime.timedelta(minutes=5))
        logging.info("Target timestamp: {}".format(target_time_stamp))

        for conglomerate in self.pipeline_state.cluster_conglomerates:
            proto_mysql_cluster = self.mdb_mysql_client.cluster_by_id(self.config.clusters[conglomerate.cluster_name].proto_cluster_id)
            old_mysql_cluster = self.mdb_mysql_client.cluster_by_id(conglomerate.old_cluster_id)
            backups = proto_mysql_cluster.list_backups()
            last_backup = max(backups, key=lambda b: b.started_at)
            cluster_name = conglomerate.cluster_name

            if proto_mysql_cluster.version == '5.7':
                key_name = 'mysqlConfig_5_7'
            elif proto_mysql_cluster.version == '8.0':
                key_name = 'mysqlConfig_8_0'
            else:
                raise Exception("Unsupported version {}".format(proto_mysql_cluster.version))

            config_spec = {
                "backupId": last_backup.id,
                "name": cluster_name + "-new-{}".format(self.id),
                "time": target_time_stamp,
                "description": old_mysql_cluster.description,
                "labels": old_mysql_cluster.labels,
                "environment": self.config.settings.get("environment", "PRODUCTION"),
                "configSpec": {
                    "version": proto_mysql_cluster.version,
                    "soxAudit": True,
                    "access": old_mysql_cluster.data.config.access,
                    "resources": {
                        "resourcePresetId": old_mysql_cluster.data.config.resources.resourcePresetId,
                        "diskSize": proto_mysql_cluster.data.config.resources.diskSize,
                        "diskTypeId": old_mysql_cluster.data.config.resources.diskTypeId
                    },
                    key_name: old_mysql_cluster.user_config
                },
                "hostSpecs": [{"zoneId": host["zoneId"]} for host in old_mysql_cluster.hosts]
            }

            logging.debug("config_spec:\n{}".format(pprint.pformat(config_spec)))

            operation = self.mdb_mysql_client.restore(config_spec)
            conglomerate.restore_operation_id = operation.id
            conglomerate.new_cluster_id = operation.metadata.clusterId

            self.set_info('Новый тестовый кластер <a href="https://yc.yandex-team.ru/folders/{folder}/managed-mysql/cluster/{id}">{title}</a>'
                          .format(folder=self.config.clusters[cluster_name].folder_id, id=conglomerate.new_cluster_id, title=cluster_name), do_escape=False)

    def store_old_data(self):
        for conglomerate in self.pipeline_state.cluster_conglomerates:
            if "dumps" in self.config.clusters[conglomerate.cluster_name]:
                target_path = self.wd_path(conglomerate.cluster_name)
                fs.make_folder(target_path)
                for dump_info in self.config.clusters[conglomerate.cluster_name].dumps:
                    args = [
                        "mysqldump",
                        "--defaults-file=" + self.get_defaults_file(conglomerate.cluster_name),
                        "--set-gtid-purged=OFF",
                        "--result-file={}.sql".format(dump_info.db),
                        "--host=" + conglomerate.haproxy,
                        "--user=" + self.config.clusters[conglomerate.cluster_name].user,
                        "--databases", dump_info.db,
                        "--tables"
                    ]
                    args.extend(dump_info.tables)

                    self._execute_shell_and_check(args, cwd=target_path.as_posix())

                resource = MySqlDumps(self, '', target_path.as_posix(), ttl=7)
                sdk2.ResourceData(resource).ready()
                conglomerate.data_resource_id = resource.id

    def wait_for_restore(self):
        with self.memoize_stage.wait_for_restore(commit_on_entrance=False, commit_on_wait=False):
            operations = [self.mdb_mysql_client.get_operation(conglomerate.restore_operation_id) for conglomerate in self.pipeline_state.cluster_conglomerates]
            logging.debug("Restore operations:\n" + "\n".join([str(operation) for operation in operations]))
            failed_operations = [operation for operation in operations if not operation.is_successful]
            if failed_operations:
                raise Exception("\n".join([str(operation) for operation in failed_operations]))
            not_completed_operations = [operation for operation in operations if not operation.is_done]
            if not_completed_operations:
                raise sdk2.WaitTime(time_to_wait=self.config.settings.restore_poll_period)

    def post_process(self):
        for conglomerate in self.pipeline_state.cluster_conglomerates:
            # подгонку топологии нового кластера под старый тоже считаем идемпотентными
            new_mysql_cluster = self.mdb_mysql_client.cluster_by_id(conglomerate.new_cluster_id)
            old_mysql_cluster = self.mdb_mysql_client.cluster_by_id(conglomerate.old_cluster_id)

            make_flat_topology(new_mysql_cluster)
            copy_topology(old_mysql_cluster, new_mysql_cluster)

            # накатывание дампов и запросы считаем идемпотентными
            if "dumps" in self.config.clusters[conglomerate.cluster_name]:
                dumps_path = sdk2.ResourceData(MySqlDumps.find(id=conglomerate.data_resource_id).first()).path
                for dump_info in self.config.clusters[conglomerate.cluster_name].dumps:
                    logging.info("Processing dump {}.sql".format(dump_info.db))
                    args = [
                        "mysql",
                        "--defaults-file=" + self.get_defaults_file(conglomerate.cluster_name),
                        "--host=" + self.get_master_host(conglomerate.new_cluster_id),
                        "--user=" + self.config.clusters[conglomerate.cluster_name].user,
                        "--database=" + dump_info.db,
                        "-e", "SOURCE {}".format(dumps_path / "{}.sql".format(dump_info.db))
                    ]

                    self._execute_shell_and_check(args)

            if "postprocess" in self.config.clusters[conglomerate.cluster_name]:
                for cmd in self.config.clusters[conglomerate.cluster_name].postprocess:
                    logging.info("Processing postprocess command: {}".format(cmd))
                    args = [
                        "mysql",
                        "--defaults-file=" + self.get_defaults_file(conglomerate.cluster_name),
                        "--host=" + self.get_master_host(conglomerate.new_cluster_id),
                        "--user=" + self.config.clusters[conglomerate.cluster_name].user,
                        "-e", cmd
                    ]

                    self._execute_shell_and_check(args)

    def restart_haproxy(self):
        from metrika.pylib.yc.common import suppress_no_changes_detected
        import ylock
        manager = ylock.create_manager('yt', prefix='//home/metrika/infra', proxy='locke.yt.yandex.net', token=self.Parameters.yt_token.value())
        with manager.lock(self.type.name, block=False) as acquired:
            if acquired:
                logging.info("Lock aquired.")
                mdb_clusters_variable = self.bishop_client.variable.get("mdb_clusters", "metrika.deploy.infra.haproxy.haproxy-testing").data.value
                for conglomerate in self.pipeline_state.cluster_conglomerates:
                    canonical_cluster_name = conglomerate.canonical_cluster_name
                    mdb_clusters_variable[canonical_cluster_name] = conglomerate.new_cluster_id

                    new_cluster = self.mdb_mysql_client.cluster_by_id(conglomerate.new_cluster_id)
                    old_cluster = self.mdb_mysql_client.cluster_by_id(conglomerate.old_cluster_id)
                    # переименования - каждый в своей стадии
                    # иногда операции переименовния могут падать, но само переименование происходить
                    # самопроизвольно либо после вмешательства дежурного в MDB
                    # поэтому при повторе стадии конвейера возможна ошибка, которую мы тут и обработаем.
                    with self.memoize_stage_global["old_rename-{}".format(conglomerate.old_cluster_id)](commit_on_entrance=False):
                        suppress_no_changes_detected(old_cluster.update, config_spec={}, update_mask="name", name=conglomerate.cluster_name + "-old-{}".format(self.id))
                    with self.memoize_stage_global["new_rename-{}".format(conglomerate.new_cluster_id)](commit_on_entrance=False):
                        suppress_no_changes_detected(new_cluster.update, config_spec={}, update_mask="name", name=conglomerate.cluster_name)

                # bishop может быть ещё не знает о новых кластерах, нужно его простимулировать
                self.bishop_client.refresh_yc_clusters()

                self.pipeline_state.actual_mdb_clusters = mdb_clusters_variable
                logging.debug(pprint.pformat(mdb_clusters_variable))
                self.bishop_client.variable.update("mdb_clusters", "metrika.deploy.infra.haproxy.haproxy-testing", "json", json.dumps(mdb_clusters_variable))

                # HACK тут считаем, что у окружений стоит Auto Activation!
                self.deploy_client.stage.restart_workloads('haproxy-testing', [(conglomerate.canonical_cluster_name, 'haproxy-runner') for conglomerate in self.pipeline_state.cluster_conglomerates],
                                                           wait_seconds=self.config.settings.get("haproxy_restart_timeout", 600), comment="{} {}".format(self.type.name, get_task_link(self.id)))
                self.wiki_update()
            else:
                logging.info("Could not acquire lock. Wait for some time.")
                raise sdk2.WaitTime(time_to_wait=180)

    def remove_old_cluster(self):
        from requests import HTTPError
        # эту стадию можно/нужно ретраить до тех пор пока
        # либо не будет кластера с этим идентификатором,
        # либо операция оп удалению не завершится успехом
        # считаем, что операция удаления кластера не такая долгая, как создания, поэтому не будет ждать асинхроно и поллить.
        for conglomerate in self.pipeline_state.cluster_conglomerates:
            try:
                cluster = self.mdb_mysql_client.cluster_by_id(conglomerate.old_cluster_id)
            except HTTPError as e:
                logging.exception("Exception in cluster_by_id")
                if e.response.status_code == 403:
                    data = e.response.json()
                    if data.get('code') == 7:
                        logging.info(data.get('message'))
                        logging.warning("No cluster {} found.".format(conglomerate.old_cluster_id))
                    else:
                        raise
                else:
                    raise
            else:
                logging.info("Cluster {} will be deleted.".format(conglomerate.old_cluster_id))
                cluster.delete().wait_for_done().verify()

    def wiki_update(self):
        wiki_page_path = "jandexmetrika/operations/jekspluatacija-mysql-v-mdb/instances-test"
        wiki_page_title = "Инстансы - testing (тестинг)"
        solomon_cluster = "haproxy_deploy_test"
        solomon_cluster_monitor = "haproxy_monitor_test"
        environment = "testing"

        view = {
            "rows": [],
            "solomon_cluster": solomon_cluster,
            "solomon_cluster_monitor": solomon_cluster_monitor
        }

        actual_clusters = [self.mdb_mysql_client.cluster_by_id(cluster_id) for cluster_id in self.pipeline_state.actual_mdb_clusters.values()]

        logging.debug(pprint.pformat(actual_clusters))

        for cluster in sorted(actual_clusters, key=lambda c: c.name):
            if "haproxy" in cluster.labels and "environment" in cluster.labels and cluster.labels.environment == environment:
                logging.info("Processing cluster: %s %s", cluster.id, cluster.name)
                row = {
                    "id": cluster.id,
                    "folder_id": cluster.folder_id,
                    "name": cluster.name,
                    "base_name": cluster.name[5:] if cluster.name.startswith("test-") or cluster.name.startswith("prod-") else cluster.name,
                    "secret_id": cluster.labels.secret_id if "secret_id" in cluster.labels else "",
                    "haproxy": cluster.labels.haproxy if "haproxy" in cluster.labels else "",
                    "hosts": cluster.list_hosts(),
                    "databases": cluster.list_databases(),
                }

                view["rows"].append(row)

        self.wiki_client.rest_post(wiki_page_path, '',
                                   json.dumps({
                                       'title': wiki_page_title,
                                       'body': render("wiki.jinja2", {"view": view}),
                                   }))

    def recreate_testing_datatransfers(self):
        if 'test-mtacs-conv_main' not in self.Parameters.mdb_cluster_names:
            return

        child = MetrikaCoreRestoreTestTransfers(
            self,
            description='Child of {}'.format(self.id),
            owner=self.owner,
        )
        child.save()
        child.enqueue()
        # Не ждем завершения таски, так как оно не критично.
        # Если будут проблемы, то это отобразится на мониторинге, тогда таску рестартнут руками.

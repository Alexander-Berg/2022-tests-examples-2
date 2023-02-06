# coding=utf-8
import inspect
import logging
import os
import shutil
import tarfile

import jinja2

from sandbox import sdk2
from sandbox.common import errors, fs, itertools
from sandbox.common.mds.compression.base import CompressionType
from sandbox.common.types import resource as resource_types
from sandbox.common.types.misc import NotExists
from sandbox.common.urls import get_resource_link
from sandbox.projects.common import apihelpers
from sandbox.projects.common.decorators import retries
from sandbox.projects.metrika.java.utils import metrika_java_helper
from sandbox.projects.metrika.utils import arcanum_api, resource_types as metrika_resource_types, settings
from sandbox.sdk2 import resource

logger = logging.getLogger("tests-helper")
TEST_PREFIX = "test_"
STABLE_PREFIX = "stable_"


class MetrikaCoreOutputB2bTestData(resource.AbstractResource):
    name = "METRIKA_CORE_OUTPUT_B2B_TEST_DATA"
    share = True
    any_arch = True
    pack_tar = CompressionType.TGZ


class AppMetricaCoreOutputB2bTestData(resource.AbstractResource):
    name = "APPMETRICA_CORE_OUTPUT_B2B_TEST_DATA"
    share = True
    any_arch = True
    pack_tar = CompressionType.TGZ


class MetrikaCoreTestsHelper(object):

    @staticmethod
    def create_users(task, hostname=None):
        MetrikaCoreTestsHelper.add_user(task, "metrika", hostname)
        MetrikaCoreTestsHelper.add_user(task, "monitor", hostname)
        MetrikaCoreTestsHelper.add_user(task, settings.login, hostname)

        MetrikaCoreTestsHelper.script(task, "echo \"{0} ALL=(ALL) NOPASSWD: ALL\" | tee /etc/sudoers.d/{0}".format(settings.login), hostname)
        MetrikaCoreTestsHelper.shell(task, ["chmod", "440", "/etc/sudoers.d/{}".format(settings.login)], hostname)

        MetrikaCoreTestsHelper.shell(task, ["mkhomedir_helper", settings.login], hostname)
        MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", "/home/{}/.ssh".format(settings.login)], hostname)
        MetrikaCoreTestsHelper.shell(task, ["chmod", "740", "/home/{}/.ssh".format(settings.login)], hostname)
        MetrikaCoreTestsHelper.script(task, "echo \"{}\" | tee /home/{}/.ssh/authorized_keys".format(MetrikaCoreTestsHelper.get_resource("authorized_keys"), settings.login), hostname)
        MetrikaCoreTestsHelper.shell(task, ["chmod", "700", "/home/{}/.ssh/authorized_keys".format(settings.login)], hostname)
        MetrikaCoreTestsHelper.shell(task, ["chown", "-R", settings.login, "/home/{}/.ssh".format(settings.login)], hostname)

    @staticmethod
    def add_user(task, user, hostname=None):
        MetrikaCoreTestsHelper.script(task, "id -u {0} || adduser --disabled-password --gecos '' {0}".format(user), hostname)

    @staticmethod
    def add_tokens(task, hostname=None):
        MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", "/home/{}/.arcanum".format(settings.login)], hostname)
        MetrikaCoreTestsHelper.copy_secret_to_path(task, "arcanum-token", "/home/{}/.arcanum/token".format(settings.login), hostname=hostname)
        MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", "/etc/events-decryption-key"], hostname)
        MetrikaCoreTestsHelper.copy_secret_to_path(task, "events-decryption-key", "/etc/events-decryption-key/events_decryption_rsa_key.pem", hostname=hostname)
        MetrikaCoreTestsHelper.copy_secret_to_path(task, "bishop-token", "/etc/bishop_oauth_token.sh", hostname=hostname)
        environment = {
            "BISHOP_OAUTH_TOKEN": MetrikaCoreTestsHelper.get_secret("bishop-token"),
            "METRIKA_VAULT_TOKEN": MetrikaCoreTestsHelper.get_secret("yav-token")
        }
        MetrikaCoreTestsHelper.write_to_path(task, "\n".join(["{}={}".format(variable, token) for variable, token in environment.items()]), "/etc/environment", hostname)

    @staticmethod
    def add_metrika_xml(task, hostname=None):
        secrets = {"pg_dicts_password": MetrikaCoreTestsHelper.get_secret("postgresql-password")}
        metrika_xml = jinja2.Environment(loader=jinja2.BaseLoader()).from_string(MetrikaCoreTestsHelper.get_resource("metrika.xml.jinja2")).render(secrets)
        MetrikaCoreTestsHelper.write_to_path(task, metrika_xml, "/etc/metrika.xml", hostname)

    @staticmethod
    def load_resource(task, resource_id, path, name=None, tar=False, gz=False, hostname=None):
        resource_path = str(sdk2.ResourceData(sdk2.Resource[resource_id]).path)
        if hostname:
            MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", path], hostname)
            destination = "/tmp/archive" if tar or gz else os.path.join(path, name or "")
            MetrikaCoreTestsHelper.shell(task, ["rsync", "-r", resource_path, "root@{}:{}".format(hostname, destination)])
            if tar:
                MetrikaCoreTestsHelper.shell(task, ["tar", "-xvf", destination, "--directory", path], hostname)
            if gz:
                if name:
                    MetrikaCoreTestsHelper.script(task, "gzip -dkc {} > {}".format(destination, os.path.join(path, name)), hostname)
                else:
                    MetrikaCoreTestsHelper.shell(task, ["gzip", "-dk", destination, path], hostname)
        else:
            if tar:
                MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", path])
                MetrikaCoreTestsHelper.shell(task, ["tar", "-xvf", resource_path, "--directory", path])
            elif gz:
                MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", path])
                if name:
                    MetrikaCoreTestsHelper.script(task, "gzip -dkc {} > {}".format(resource_path, os.path.join(path, name)))
                else:
                    MetrikaCoreTestsHelper.shell(task, ["gzip", "-dk", resource_path, path])
            else:
                MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", path])
                if name:
                    shutil.copy(resource_path, os.path.join(path, name))
                else:
                    MetrikaCoreTestsHelper.shell(task, ["cp", "-rp", resource_path, path])

    @staticmethod
    def install_environment_packages(task, hostname=None):
        MetrikaCoreTestsHelper.shell(task, ["update-locale", "LANG=en_US.UTF-8"], hostname)
        MetrikaCoreTestsHelper.shell(task, ["apt-key", "adv", "--keyserver", "keyserver.ubuntu.com", "--recv-keys", "A1715D88E1DF1F24"], hostname)
        MetrikaCoreTestsHelper.copy_resource_to_path(task, "metrika.list", "/etc/apt/sources.list.d/metrika.list", hostname)
        MetrikaCoreTestsHelper.apt_get_install(task,
                                               [
                                                   "yandex-environment-testing",
                                                   "python-setuptools",
                                                   "openssh-server",
                                                   "python-mysqldb",
                                                   "python-pip",
                                                   "daemon",
                                                   "ydb"
                                               ],
                                               hostname)
        MetrikaCoreTestsHelper.script(task, "sed -i -E 's/#?MaxStartups.*/MaxStartups 100/' /etc/ssh/sshd_config", hostname)
        MetrikaCoreTestsHelper.script(task, "sed -i -e '/^MaxSessions.*/{s//MaxSessions 100/;:a;n;ba;q}' -e '$aMaxSessions 100' /etc/ssh/sshd_config", hostname)
        MetrikaCoreTestsHelper.shell(task, ["service", "ssh", "restart"], hostname)

    @staticmethod
    def configure_zookeeper(task, hostname=None):
        MetrikaCoreTestsHelper.apt_get_install(task, ["zookeeper3.6=3.6.2-metrika-2"], hostname)
        MetrikaCoreTestsHelper.copy_resource_to_path(task, "zookeeper.init.conf", "/etc/init/zookeeper-common.conf", hostname)
        MetrikaCoreTestsHelper.copy_resource_to_path(task, "zookeeper.environment", "/usr/share/zookeeper-3.6.2/conf/environment", hostname)
        MetrikaCoreTestsHelper.copy_resource_to_path(task, "zoo.cfg", "/usr/share/zookeeper-3.6.2/conf/zoo.cfg", hostname)
        try:
            MetrikaCoreTestsHelper.shell(task, ["service", "zookeeper-common", "restart"], hostname)
        finally:
            MetrikaCoreTestsHelper.shell(task, ["ls", "-la", "/etc/init"], hostname)
            MetrikaCoreTestsHelper.shell(task, ["service", "zookeeper-common", "status"], hostname)

    @staticmethod
    def apt_get_update(task, hostname=None):
        @retries(max_tries=3, exceptions=errors.TaskError)
        def apt_get_update():
            MetrikaCoreTestsHelper.shell(task, ["apt-get", "update", "-q=0"], hostname)

        try:
            apt_get_update()
        except errors.TaskFailure:
            logger.warn("apt-get update failed")

    @staticmethod
    def apt_get_install(task, packages, hostname=None):
        if not getattr(task, '_apt_updated', None):
            MetrikaCoreTestsHelper.apt_get_update(task, hostname)
            task._apt_updated = True

        cmd = ["apt-get", "install", "-q=0", "-y", "--force-yes"]
        cmd.extend(packages)
        MetrikaCoreTestsHelper.shell(task, cmd, hostname)

    @staticmethod
    def configure_mysql(task, hostname=None):
        MetrikaCoreTestsHelper.apt_get_install(task, ["percona-server-server-5.7", "percona-server-client-5.7", "percona-server-common-5.7"], hostname)
        MetrikaCoreTestsHelper.shell(task, ["service", "mysql", "stop"], hostname)
        arcanum = arcanum_api.ArcanumApi(token=sdk2.Vault.data(settings.owner, settings.arcanum_token))
        arcanum.get_blob("metrika/admin/somestuff/mysql-common-metrika-yandex/metrika.cnf")

        MetrikaCoreTestsHelper.write_to_path(task, arcanum.get_blob("metrika/admin/somestuff/mysql-common-metrika-yandex/metrika.cnf"), "/etc/mysql/conf.d/metrika.cnf", hostname)
        MetrikaCoreTestsHelper.write_to_path(task, MetrikaCoreTestsHelper.get_resource("sql_modes.cnf"), "/etc/mysql/conf.d/sql_modes.cnf", hostname)

        MetrikaCoreTestsHelper.script(task, '''
if [ ! -d "/opt/mysql" ]
then
    mysqld_safe --initialize-insecure
else
    echo "MySQL database already initialized"
fi
        ''', hostname)
        MetrikaCoreTestsHelper.shell(task, ["service", "mysql", "start"], hostname)

        MetrikaCoreTestsHelper.wait_mysql(task, hostname)

    @staticmethod
    def wait_mysql(task, hostname=None):
        initial_tick = 1
        max_tick = 5
        max_wait = 60

        def mysql_is_active():
            try:
                MetrikaCoreTestsHelper.script(task, 'tail -n 50 /var/log/mysql/mysql.log ; mysql -u root -e "SELECT @@version"', hostname)
                return True
            except Exception:
                return False

        if not itertools.progressive_waiter(initial_tick, max_tick, max_wait, mysql_is_active)[0]:
            raise errors.TaskFailure("mysql не стартовал")

    @staticmethod
    def add_mysql_user_metrika(task, location, hostname=None):
        MetrikaCoreTestsHelper.script(task, "mysql -u root -e \"grant all privileges on *.* to 'metrika'@'{}' identified by 'metrika';\"".format(location), hostname)

    @staticmethod
    def configure_counters_server(task, hostname=None):
        MetrikaCoreTestsHelper.install_stable_tarballs(task, ["counters-server"], hostname)
        MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", "/etc/counters-server/conf.d"], hostname)
        MetrikaCoreTestsHelper.copy_resource_to_path(task, "counters-server-config.xml", "/etc/counters-server/conf.d/config.xml", hostname)

    @staticmethod
    def configure_goals_server(task, hostname=None):
        MetrikaCoreTestsHelper.install_stable_tarballs(task, ["goals-server"], hostname)
        MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", "/etc/goals-server/conf.d"], hostname)
        # MetrikaCoreTestsHelper.copy_resource_to_path(task, "goals-server-config.xml", "/etc/goals-server/conf.d/config.xml", hostname)

    @staticmethod
    def configure_user_attr_server(task, hostname=None):
        MetrikaCoreTestsHelper.install_stable_packages(task, ["user-attr-server-metrika-yandex"], hostname)
        MetrikaCoreTestsHelper.copy_resource_to_path(task, "user-attr-server-config.xml", "/etc/user-attr-server/conf.d/config.xml", hostname)

    @staticmethod
    def _configure_clickhouse(task, cluster='mtgiga', data_dir=None, hostname=None):
        MetrikaCoreTestsHelper.install_cluster_packages(task, ["clickhouse-server", "clickhouse-common-static", "clickhouse-server-metrika"], cluster, hostname)
        MetrikaCoreTestsHelper.copy_resource_to_path(task, "clickhouse-server-config.xml", "/etc/clickhouse-server/users.d/config.xml", hostname)

        if data_dir:
            MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", "/opt/clickhouse"], hostname)
            MetrikaCoreTestsHelper.script(task, "cp -rf {}/* /opt/clickhouse".format(data_dir), hostname)
            MetrikaCoreTestsHelper.shell(task, ["chown", "-R", "clickhouse:clickhouse", "/opt/clickhouse"], hostname)
            MetrikaCoreTestsHelper.shell(task, ["chmod", "-R", "a+w", "/opt/clickhouse"], hostname)

        MetrikaCoreTestsHelper.shell(task, ["service", "clickhouse-server", "restart"], hostname)

    @staticmethod
    def configure_logbroker(task, hostname=None):
        kikimr_stable = apihelpers.get_last_resource_with_attribute(metrika_resource_types.BaseMetrikaBinaryResource, "resource_name", "kikimr_stable")
        lbk_recipe = apihelpers.get_last_resource_with_attribute(metrika_resource_types.BaseMetrikaBinaryResource, "resource_name", "lbk_recipe")

        MetrikaCoreTestsHelper.load_resource(task, kikimr_stable.id, "/usr/local/bin", "ydb-binary", hostname=hostname)
        MetrikaCoreTestsHelper.load_resource(task, lbk_recipe.id, "/usr/local/bin", "lbk_recipe", hostname=hostname)

    @staticmethod
    def configure_ydb(task, hostname=None):
        kikimr_stable = apihelpers.get_last_resource_with_attribute(metrika_resource_types.BaseMetrikaBinaryResource, "resource_name", "kikimr_stable")
        local_ydb = apihelpers.get_last_resource_with_attribute(metrika_resource_types.BaseMetrikaBinaryResource, "resource_name", "local_ydb")

        MetrikaCoreTestsHelper.load_resource(task, kikimr_stable.id, "/usr/local/bin", "ydb-binary", hostname=hostname)
        MetrikaCoreTestsHelper.load_resource(task, local_ydb.id, "/usr/local/bin", "local_ydb", hostname=hostname)

    @staticmethod
    def configure_yt(task, hostname=None):
        MetrikaCoreTestsHelper.apt_get_install(task, ["yandex-yt-python=0.10.11-0", "yandex-yt-local=0.0.92-0"], hostname)

        MetrikaCoreTestsHelper.load_resource(task, 2010806475, "/usr/local/bin", "ytserver-all", hostname=hostname)

    @staticmethod
    def configure_nginx(task, hostname=None):
        MetrikaCoreTestsHelper.apt_get_install(task, ["nginx=1.14.2-1.yandex.6"], hostname)

        MetrikaCoreTestsHelper.copy_resource_to_path(task, "bigb.conf", "/etc/nginx/sites-enabled/bigb.conf", hostname)

        MetrikaCoreTestsHelper.shell(task, ["service", "nginx", "restart"], hostname)

    @staticmethod
    def shell(task, shell, hostname=None):
        if hostname:
            shell = ["ssh", "{}@{}".format(settings.login, hostname), "sudo"] + shell
        return task._execute_shell_and_check(shell, logger=MetrikaCoreTestsHelper.get_logger())

    @staticmethod
    def script(task, script, hostname=None):
        if hostname:
            script = "ssh {}@{} sudo /bin/bash -xe <<'EOF'\n{}\nEOF".format(settings.login, hostname, script)
        return task._execute_script(script, logger=MetrikaCoreTestsHelper.get_logger())

    @staticmethod
    def get_logger():
        return "prepare_" + inspect.stack()[2][3]

    @staticmethod
    def copy_resource_to_path(task, resource_name, destination_path, hostname=None):
        MetrikaCoreTestsHelper.write_to_path(task, MetrikaCoreTestsHelper.get_resource(resource_name), destination_path, hostname)

    @staticmethod
    def get_resource(resource_name):
        resource_path = os.path.join(os.path.dirname(__file__), "resources", resource_name)
        return fs.read_file(resource_path)

    @staticmethod
    def copy_secret_to_path(task, key, destination_path, secret_id=settings.yav_uuid, hostname=None):
        MetrikaCoreTestsHelper.write_to_path(task, MetrikaCoreTestsHelper.get_secret(key, secret_id), destination_path, hostname)

    @staticmethod
    def get_secret(key, secret_id=settings.yav_uuid):
        return sdk2.yav.Secret(secret_id).data()[key]

    @staticmethod
    def write_to_path(task, string, destination_path, hostname=None):
        if hostname:
            local_path = "temp.file"
            with open(local_path, "w") as file:
                file.write(string)
            MetrikaCoreTestsHelper.shell(task, ["rsync", "-r", local_path, "root@{}:{}".format(hostname, destination_path)])
        else:
            with open(destination_path, "w") as destination_file:
                destination_file.write(string)

    @staticmethod
    def get_stable_package_version(package):
        stable_version = metrika_java_helper.MetrikaJavaHelper.get_stable_package_version(package)
        if not stable_version:
            raise errors.TaskError("Не удалось получить стабильную версию для пакета {}".format(package))
        return stable_version

    @staticmethod
    def install_stable_packages(task, packages, hostname=None):
        MetrikaCoreTestsHelper.install_packages(task, dict((package, MetrikaCoreTestsHelper.get_stable_package_version(package)) for package in packages), hostname)

    @staticmethod
    def install_cluster_packages(task, packages, cluster, hostname=None):
        MetrikaCoreTestsHelper.install_packages(task, dict((package, metrika_java_helper.MetrikaJavaHelper.get_package_version_on_cluster(package, cluster)) for package in packages), hostname)

    @staticmethod
    def install_packages(task, packages, hostname=None):
        if isinstance(packages, str):
            packages = [packages]
        elif isinstance(packages, dict):
            packages = ["{}={}".format(package, version) for package, version in packages.items()]

        MetrikaCoreTestsHelper.script(task, " ".join(["DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", "--force-yes"] + packages), hostname)

    @staticmethod
    def install_stable_tarballs(task, programs, hostname=None):
        MetrikaCoreTestsHelper.install_tarballs(task, dict((program, MetrikaCoreTestsHelper.get_stable_package_version(program)) for program in programs), hostname)

    @staticmethod
    def install_tarballs(task, programs, hostname=None):
        for program, version in programs.items():
            MetrikaCoreTestsHelper.install_tarball(task, program, version, hostname)

    @staticmethod
    def install_tarball(task, program, version, hostname=None):
        tarball_resource = sdk2.Resource.find(owner=settings.owner,
                                              type=metrika_resource_types.BaseMetrikaBinaryResource,
                                              state=resource_types.State.READY,
                                              attrs={"resource_name": program, "resource_version": version}).first()
        original_path = str(sdk2.ResourceData(tarball_resource).path)
        if hostname:
            MetrikaCoreTestsHelper.shell(task, ["tar", "-xzf", original_path, "-C", "/tmp/"])
            MetrikaCoreTestsHelper.shell(task, ["rsync", "-p", "/tmp/{}".format(program), "{}:/usr/bin/{}".format(hostname, program)])
        else:
            MetrikaCoreTestsHelper.shell(task, ["tar", "-xzf", original_path, "-C", "/usr/bin/"])

    @staticmethod
    def get_programs_under_b2b_tests(properties_text):
        properties = {property[:property.index("=")]: property[property.index("=") + 1:].strip() for property in properties_text.replace("\\\n", "").split("\n") if property}
        packages = [package.strip() for package in properties.get("b2b.stand.packages").split(",")]
        return {package.split("=")[0]: package.split("=")[1] if "=" in package else None for package in packages}

    @staticmethod
    def copy_folder(task, from_path, to_path, hostname=None):
        if hostname:
            MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", to_path])
            MetrikaCoreTestsHelper.copy_remote_data(task, os.path.join(from_path, ""), to_path, hostname)
        else:
            shutil.copytree(from_path, to_path)

    @staticmethod
    def copy_file(task, from_path, to_path, hostname=None):
        if hostname:
            MetrikaCoreTestsHelper.shell(task, ["mkdir", "-p", os.path.dirname(to_path)])
            MetrikaCoreTestsHelper.copy_remote_data(task, from_path, to_path, hostname)
        else:
            shutil.copy(from_path, to_path)

    @staticmethod
    def copy_remote_data(task, from_path, to_path, hostname):
        MetrikaCoreTestsHelper.shell(task, ["rsync", "-r", "root@{}:{}".format(hostname, from_path), to_path])

    @staticmethod
    def _save_mysql_data(task, path, databases, hostname=None):
        folder = os.path.join(path, "mysql")
        os.mkdir(folder)

        for database in databases:
            database_directory = os.path.join(folder, database)
            os.mkdir(database_directory)
            if databases.get(database):
                for table in databases.get(database):
                    dump_path = os.path.join(database_directory, table) + ".sql"
                    tmp_path = os.path.join("/tmp", table) + ".sql"
                    MetrikaCoreTestsHelper.script(task, "mysqldump-connect {} {} > {}".format(database, table, tmp_path if hostname else dump_path), hostname)
                    if hostname:
                        MetrikaCoreTestsHelper.copy_remote_data(task, tmp_path, dump_path, hostname)
            else:
                dump_path = os.path.join(database_directory, database) + ".sql"
                tmp_path = os.path.join("/tmp", database) + ".sql"
                MetrikaCoreTestsHelper.script(task, "mysqldump-connect {} > {}".format(database, tmp_path if hostname else dump_path), hostname)
                if hostname:
                    MetrikaCoreTestsHelper.copy_remote_data(task, tmp_path, dump_path, hostname)

    @staticmethod
    def _save_file_data(task, path, directories, hostname=None):
        folder = os.path.join(path, "files")
        os.mkdir(folder)

        for directory in directories:
            directory_path = os.path.join("/opt", directory)
            MetrikaCoreTestsHelper.copy_folder(task, directory_path, os.path.join(folder, directory), hostname)

    @staticmethod
    def copy_clickhouse_database(task, database, folder, hostname=None):
        clickhouse_path = "/opt/clickhouse"
        data_path = os.path.join(clickhouse_path, "data", database)
        if not hostname and not os.path.exists(data_path):
            logging.warning('%s dir doesn\'t exist', data_path)
            return

        MetrikaCoreTestsHelper.copy_folder(task, data_path, os.path.join(folder, "data", database), hostname)
        metadata_path = os.path.join(clickhouse_path, "metadata", database)
        MetrikaCoreTestsHelper.copy_folder(task, metadata_path, os.path.join(folder, "metadata", database), hostname)
        database_path = metadata_path + ".sql"
        MetrikaCoreTestsHelper.copy_file(task, database_path, os.path.join(folder, "metadata"), hostname)

    @staticmethod
    def _save_clickhouse_data(task, path, databases, hostname=None):
        folder = os.path.join(path, "clickhouse")
        os.mkdir(folder)

        MetrikaCoreTestsHelper.shell(task, ["service", "clickhouse-server", "stop"], hostname)

        for database in databases:
            MetrikaCoreTestsHelper.copy_clickhouse_database(task, database, folder, hostname)

        if hostname:
            MetrikaCoreTestsHelper.shell(task, ["service", "clickhouse-server", "start"], hostname)

    @staticmethod
    def _load_resources(task, resources_settings, resources=None, hostname=None):
        for resource_type, resource_settings in resources_settings.items():
            if resource_type in resources and resources[resource_type]:
                resource = sdk2.Resource[resources[resource_type]]
            else:
                resource = apihelpers.get_last_resource_with_attribute(
                    resource_type, resource_settings.get("attribute_name"), resource_settings.get("attribute_value"), owner=resource_settings.get("owner")
                )

            task.Context.resources[str(resource_type)] = resource.id

            MetrikaCoreTestsHelper.load_resource(
                task, resource.id, resource_settings.get("path"),
                name=resource_settings.get("name"), tar=resource_settings.get("tar"), gz=resource_settings.get("gz"),
                hostname=hostname
            )

    @staticmethod
    def _get_input_resources(task, resources_settings):
        for resource_type, resource_settings in resources_settings.items():
            if resource_type in [metrika_resource_types.MetrikaCoreB2bTestsData, metrika_resource_types.AppmetricaCoreB2bTestsData] and task.Parameters.use_custom_tests_data:
                resource = task.Parameters.custom_resource
            else:
                resource = apihelpers.get_last_resource_with_attribute(
                    resource_type,
                    resource_settings.get("attribute_name"),
                    resource_settings.get("attribute_value"),
                    owner=resource_settings.get("owner"))

            task.Context.resources[str(resource_type)] = resource.id

    @staticmethod
    def get_tests_output_resource_id(task_id, resource_type):
        return apihelpers.get_task_resource_id(task_id, resource_type)

    @staticmethod
    def get_last_tests_output_resource_id(packages_versions, resource_type, resources=None, dictionaries=None, **attributes):
        attributes.update(packages_versions)
        if dictionaries:
            attributes.update({"dictionaries": dictionaries})
        if resources:
            attributes.update(resources)
        last_resource_with_attrs = apihelpers.get_last_resource_with_attrs(resource_type, attributes, all_attrs=True)
        if last_resource_with_attrs:
            return last_resource_with_attrs.id

    @staticmethod
    def _try_to_get_tests_output_resource(
        task, arcadia_url, packages, resources, force, description,
        resource_type, task_cls,
        dictionaries=None, custom_host=None,
        **attributes
    ):
        resource_id = MetrikaCoreTestsHelper.get_last_tests_output_resource_id(
            packages, resource_type, resources=resources, dictionaries=dictionaries,
            task_release=MetrikaCoreTestsHelper._get_task_release(task), **attributes
        )
        if not resource_id or force:
            params = dict(
                description=" ".join([task.Parameters.description, description]),
                vcs=task.Parameters.vcs,
                arcadia_url=arcadia_url,
                arcadia_patch=task.Parameters.arcadia_patch,
                arcadia_path=task.Parameters.arcadia_path,
                fail_task_on_test_failure=task.Parameters.fail_task_on_test_failure,
                report_startrek=task.Parameters.report_startrek,
                issue_key=task.Parameters.issue_key,
                startrek_token=task.Parameters.startrek_token,
                packages=packages,
                resources=resources,
                use_custom_host=bool(custom_host),
                custom_host=custom_host
            )
            if dictionaries:
                params.update(dictionaries=dictionaries)
            return (task_cls, params)
        else:
            return resource_id

    @staticmethod
    def unzip_resource(resource_id, resource_path):
        resource_archive = str(sdk2.ResourceData(sdk2.Resource[resource_id]).path)
        with tarfile.open(resource_archive, "r:gz") as tar:
            tar.extractall(resource_path)

    @staticmethod
    def copy_files_data(from_path, prefix=""):
        MetrikaCoreTestsHelper.copy_content(from_path, "/opt", prefix)

    @staticmethod
    def copy_content(from_path, to_path, prefix=""):
        for item in os.listdir(from_path):
            source_path = os.path.join(from_path, item)
            if os.path.isdir(source_path):
                destination_path = os.path.join(to_path, prefix + item)
                shutil.rmtree(destination_path, ignore_errors=True)
                shutil.copytree(source_path, destination_path)
            if os.path.isfile(source_path):
                destination_path = os.path.join(to_path, prefix + item)
                shutil.copyfile(source_path, destination_path)

    @staticmethod
    def copy_clickouse_data(task, from_path, prefix=""):
        base_clickhouse_path = "/opt/clickhouse"

        from_data_path = os.path.join(from_path, "data")
        to_data_path = os.path.join(base_clickhouse_path, "data")
        MetrikaCoreTestsHelper.copy_content(from_data_path, to_data_path, prefix)

        from_data_path = os.path.join(from_path, "metadata")
        to_data_path = os.path.join(base_clickhouse_path, "metadata")
        MetrikaCoreTestsHelper.copy_content(from_data_path, to_data_path, prefix)

        for database in os.listdir(to_data_path):
            database_path = os.path.join(to_data_path, database)
            if os.path.isdir(database_path):
                MetrikaCoreTestsHelper.script(task, "find {} -type f -name '*.sql' -exec sed -i \"s/Merge('{}'/Merge('{}'/\" {{}} \\;".format(database_path, database.strip(prefix), database))

    @staticmethod
    def load_mysql_data(task, from_path, prefix=""):
        for database in os.listdir(from_path):
            MetrikaCoreTestsHelper.shell(task, ["mysql", "-u", "root", "-e", "create database {};".format(prefix + database)])
            database_path = os.path.join(from_path, database)
            for table in os.listdir(database_path):
                table_path = os.path.join(database_path, table)
                MetrikaCoreTestsHelper.script(task, "mysql -u root {} < {}".format(prefix + database, table_path))

    @staticmethod
    def _extract_tests_output_resources(task, test_resource_id, stable_resource_id, mysql=False, files=True):
        from metrika.pylib.utils import str_to_bool

        test_resource_path = "/opt/test_data"
        MetrikaCoreTestsHelper.unzip_resource(test_resource_id, test_resource_path)
        if str_to_bool(getattr(sdk2.Resource[test_resource_id], 'arcadia_b2b', False)):
            test_resource_path += "/output"

        stable_resource_path = "/opt/stable_data"
        MetrikaCoreTestsHelper.unzip_resource(stable_resource_id, stable_resource_path)
        if str_to_bool(getattr(sdk2.Resource[stable_resource_id], 'arcadia_b2b', False)):
            stable_resource_path += "/output"

        MetrikaCoreTestsHelper.copy_clickouse_data(task, os.path.join(test_resource_path, "clickhouse"), prefix=TEST_PREFIX)
        MetrikaCoreTestsHelper.copy_clickouse_data(task, os.path.join(stable_resource_path, "clickhouse"), prefix=STABLE_PREFIX)

        MetrikaCoreTestsHelper.shell(task, ["chown", "-R", "clickhouse:clickhouse", "/opt/clickhouse"])
        MetrikaCoreTestsHelper.shell(task, ["service", "clickhouse-server", "restart"])

        if mysql:
            MetrikaCoreTestsHelper.load_mysql_data(task, os.path.join(test_resource_path, "mysql"), prefix=TEST_PREFIX)
            MetrikaCoreTestsHelper.load_mysql_data(task, os.path.join(stable_resource_path, "mysql"), prefix=STABLE_PREFIX)

        if files:
            MetrikaCoreTestsHelper.copy_files_data(os.path.join(test_resource_path, "files"), prefix=TEST_PREFIX)
            MetrikaCoreTestsHelper.copy_files_data(os.path.join(stable_resource_path, "files"), prefix=STABLE_PREFIX)

    @staticmethod
    def _get_packages_under_b2b_tests(task, properties_path):
        with open(task.wd(properties_path)) as properties_file:
            return MetrikaCoreTestsHelper.get_programs_under_b2b_tests(properties_file.read())

    @staticmethod
    def _get_all_packages_versions(task, packages, properties_path):
        all_packages = MetrikaCoreTestsHelper._get_packages_under_b2b_tests(task, properties_path)
        all_packages.update(packages)
        for package in all_packages:
            if not all_packages[package]:
                all_packages[package] = MetrikaCoreTestsHelper.get_stable_package_version(package)
            elif "@" in all_packages[package]:
                all_packages[package] = metrika_java_helper.MetrikaJavaHelper.get_package_version_on_cluster(package, all_packages[package].replace("@", ""))
        return all_packages

    @staticmethod
    def _get_task_release(task):
        task_release = task.Parameters.binary_executor_release_type
        if task_release == "custom":
            task_release = "testing"
        return task_release

    @classmethod
    def _save_output_tests_data(cls, task, packages, resources, resource_type, resource_description, dictionaries=None, mysql=False, hostname=None):
        resource_path = str(task.path("output_resources"))
        os.mkdir(resource_path)

        cls.save_clickhouse_data(task, resource_path, hostname)
        if mysql:
            cls.save_mysql_data(task, resource_path, hostname)
        cls.save_file_data(task, resource_path, hostname)

        archive_path = shutil.make_archive("output_tests_data", "gztar", resource_path)

        attributes = dict(packages)
        if dictionaries:
            attributes.update({"dictionaries": dictionaries})
        attributes.update(resources)

        resource_type(
            task, resource_description, archive_path, ttl=90, pack_tar=CompressionType.NONE,
            arcadia_b2b=False, task_release=cls._get_task_release(task), **attributes
        )

    @classmethod
    def _get_scenarios_result(cls, task, resource_type):
        with task.memoize_stage.scenarios_execute(commit_on_entrance=False):
            if task.Parameters.use_custom_test_resource:
                task.Context.test_resource_id = sdk2.Resource[task.Parameters.test_resource].id

            if task.Parameters.use_custom_stable_resource:
                task.Context.stable_resource_id = sdk2.Resource[task.Parameters.stable_resource].id

            cls.get_input_resources(task)

        tasks = []
        if not task.Context.test_resource_id:
            params = dict(
                task=task, arcadia_url=task.Parameters.arcadia_url,
                packages=task.Context.test_packages_versions,
                clickhouse_resource=task.Parameters.test_clickhouse_resource,
                force=task.Parameters.force_test_scenario or task.Context.test_resource_task, description="test",
            )
            if task.Context.resources != NotExists:
                params.update(resources=task.Context.resources)
            if hasattr(task.Parameters, 'custom_host'):
                params.update(custom_host=task.Parameters.custom_host)
            if hasattr(task.Parameters, 'test_dictionaries'):
                params.update(dictionaries=task.Parameters.test_dictionaries)
            test_task_or_resource_id = cls.try_to_get_tests_output_resource(**params)
            if isinstance(test_task_or_resource_id, int):
                task.Context.test_resource_id = test_task_or_resource_id
            else:
                task.Context.test_resource_task = True
                tasks.append(test_task_or_resource_id)

        if not task.Context.stable_resource_id:
            params = dict(
                task=task, arcadia_url="arcadia-arc:/#trunk",
                packages=task.Context.stable_packages_versions,
                clickhouse_resource=task.Parameters.stable_clickhouse_resource,
                force=task.Parameters.force_stable_scenario or task.Context.stable_resource_task, description="stable",
            )
            if task.Context.resources != NotExists:
                params.update(resources=task.Context.resources)
            if hasattr(task.Parameters, 'test_dictionaries'):
                params.update(dictionaries="trunk")

            stable_task_or_resource_id = cls.try_to_get_tests_output_resource(**params)
            if isinstance(stable_task_or_resource_id, int):
                task.Context.stable_resource_id = stable_task_or_resource_id
            else:
                task.Context.stable_resource_task = True
                tasks.append(stable_task_or_resource_id)

        if tasks:
            subtasks = list(task.run_subtasks(tasks, subtasks_variable=task.Context.scenarios_task_ids))

        if task.Context.test_resource_task and not task.Context.test_resource_id:
            task.Context.test_resource_id = cls.get_tests_output_resource_id(subtasks.pop(0), resource_type)
        task.comment('<a href="{}">Test resource</a>'.format(get_resource_link(task.Context.test_resource_id)))

        if task.Context.stable_resource_task and not task.Context.stable_resource_id:
            task.Context.stable_resource_id = cls.get_tests_output_resource_id(subtasks.pop(0), resource_type)
        task.comment('<a href="{}">Stable resource</a>'.format(get_resource_link(task.Context.stable_resource_id)))

    @classmethod
    def _get_packages_versions(cls, task):
        if not task.Context.test_packages_versions:
            task.Context.test_packages_versions = cls.get_packages_versions(task, task.Parameters.test_packages)
        if not task.Context.stable_packages_versions:
            task.Context.stable_packages_versions = cls.get_packages_versions(task, task.Parameters.stable_packages)

    @classmethod
    def _get_different_url_packages_versions(cls, task, arcadia_url):
        if not task.Context.test_packages_versions:
            task.Context.test_packages_versions = cls.get_packages_versions(arcadia_url, task.Parameters.test_packages)
        if not task.Context.stable_packages_versions:
            task.Context.stable_packages_versions = cls.get_packages_versions("arcadia-arc:/#trunk", task.Parameters.stable_packages)

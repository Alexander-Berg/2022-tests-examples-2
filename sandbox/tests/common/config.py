import os
import json
import shutil
import tempfile
import textwrap
import functools
import multiprocessing as mp

import py
import pytest

from sandbox.common import config
import sandbox.common.types.client as ctc


# client tags for test client
CLIENT_TAGS = [ctc.Tag.GENERIC, ctc.Tag.POSTEXECUTE, ctc.Tag.LINUX_PRECISE, ctc.Tag.CORES16]


@pytest.fixture(scope="session")
def client_node_id(rest_session_login):  # rest_session_login used as source host for resources created from AgentR
    return rest_session_login


@pytest.fixture(scope="session")
def config_common_section(
    client_node_id, tests_path_getter, statistics_db_name, mds_port, s3_port, tvmtool_port, py3_sources_binary
):
    tmpl = textwrap.dedent("""
        version:
          current: 0
          actual: 0
        this:
          id: "{client_node_id}"
          dc: "unk"
        common:
          statistics:
            enabled: false
            database: {statistics_db_name}
          task:
            execution:
              disk_required: 60
              required_cores: {required_cores}
          zookeeper:
            enabled: false
          daemonize: true
          dirs:
            runtime: "{tests_dir}/run"
          installation: TEST
          mds:
            up:
              url: "http://localhost:{mds_port}"
              tvm_service: null
            dl:
              url: "http://localhost:{mds_port}"
            rb:
              url: "http://localhost:{mds_port}"
            s3:
              url: "http://localhost:{s3_port}"
              use_proxy: false
              idm:
                url: "http://localhost:{s3_port}"
          tvm:
            port: {tvmtool_port}
            access_token: "DEADBEEFDEADBEEFDEADBEEFDEADBEEF"
          py3_sources_binary: "{py3_sources_binary}"
          resources:
            backup_interval: 5
    """)
    return functools.partial(
        tmpl.format,
        client_node_id=client_node_id,
        statistics_db_name=statistics_db_name,
        tests_dir=tests_path_getter(),
        required_cores=mp.cpu_count(),
        mds_port=mds_port,
        s3_port=s3_port,
        tvmtool_port=tvmtool_port,
        py3_sources_binary=py3_sources_binary
    )


@pytest.fixture(scope="session")
def config_serviceq_section(serviceq_port, mongo_uri, tests_path_getter):
    tmpl = textwrap.dedent("""
        serviceq:
          log:
            root: "{tests_dir}/logs"
            level: "DEBUG"

          client:
            timeout: 30
            retry:
              sleep: 0.01

          server:
            server:
              port: {serviceq_port}
            allow_reset: true
            mongodb:
              connection_url: "{mongo_uri}"
            gc_interval: 0
            prequeue_timeout: 0
    """)
    return functools.partial(
        tmpl.format,
        tests_dir=tests_path_getter(),
        serviceq_port=serviceq_port,
        mongo_uri=mongo_uri,
    )


@pytest.fixture(scope="session")
def config_agentr_section(agentr_socket, tests_path_getter):
    tmpl = textwrap.dedent("""
        agentr:
          log:
            root: "{tests_dir}/logs"

          daemon:
            server:
              unix: "{agentr_socket}"
            db:
              temp: "${{client.dirs.run}}"
              path: "${{client.dirs.run}}/agentr.db"
          data:
            buckets: []
          statbox_push_client:
            config: "{tests_dir}/push-client.yaml"
    """)
    return functools.partial(
        tmpl.format,
        tests_dir=tests_path_getter(),
        agentr_socket=agentr_socket,
    )


@pytest.fixture(scope="session")
def config_proxy_section(tests_path_getter):
    tmpl = textwrap.dedent("""
        proxy:
          logging:
            handlers:
              file:
                filename: "{tests_dir}/proxy.log"
    """)
    return functools.partial(
        tmpl.format,
        tests_dir=tests_path_getter(),
    )


@pytest.fixture(scope="session")
def config_taskbox_section(taskbox_port, taskboxer_binary, work_id, tests_path_getter):
    tmpl = textwrap.dedent("""
        taskbox:
          log:
            root: "{tests_dir}/logs/taskbox"
          dirs:
            run: "/tmp/sandbox-test_taskbox_{work_id}"
          dispatcher:
            server:
              port: {taskbox_port}
            use_subproc: True
            kill_workers_on_stop: True
          worker:
            tasks_binary: {taskboxer_binary}
    """)
    return functools.partial(
        tmpl.format,
        tests_dir=tests_path_getter(),
        taskbox_port=taskbox_port,
        taskboxer_binary=taskboxer_binary,
        work_id=work_id,
    )


@pytest.fixture(scope="session")
def config_client_section(
    request, user, host, tests_path_getter, sandbox_tasks_dir, client_port, serviceapi_port, fileserver_port,
    fileserver_socket, phazotron_socket, rest_su_session_token,
):

    if request.config.getoption("--local-arcadia-user", None):
        arcadia_user = 'user: "{user}"'.format(user=user)
    else:
        arcadia_user = ""

    tmpl = textwrap.dedent("""
        client:
          tags: {tags}
          log:
            root: "{tests_dir}/logs"
            name: "client.log"
          xmlrpc_url: "http://{host}:{serviceapi_port}/sandbox/xmlrpc"
          rest_url: "http://{host}:{serviceapi_port}/api/v1.0"
          port: {client_port}
          idle_time: 0.01
          cgroup_available: {cgroup_available}

          tasks:
            code_dir: "{sandbox_tasks_dir}"
            data_dir: "{tasks_data_dir}"
            env_dir: "{tests_dir}/environment"

          dirs:
            run: "{tests_dir}/run"
            data: "{tests_dir}"
            liner: "{liner_dir}"  # Socket path should be less than 108 chars length

          skynet_key:
            path: "{tests_dir}/skynet.key"

          sandbox_user: null

          auth:
            oauth_token: {oauth_token}

          sdk:
            svn:
              use_system_binary: true
              confdir: "/home/{user}/.subversion"
              arcadia:
                trunk: "svn+ssh://{user}@arcadia.yandex.ru/arc/trunk/arcadia"
                rw:
                  empty: "setting"
                  {arcadia_user}
                ro:
                  empty: "setting"
                  {arcadia_user}
                cache_path:
                  sources: "{tests_dir}/srcdir"
                  tests_data: "{tests_dir}/testdata"

          phazotron:
            sockname: "{phazotron_socket}"

          agentr:
            enabled: false  # It will run by separate fixture

          fileserver:
            enabled: false
            port: {fileserver_port}
            timeout: 0.0001
            worker:
              unix: "{fileserver_socket}"

          auto_cleanup:
            free_space_threshold: 0
            hard_free_space_threshold: 0
    """)

    liner_dir = tempfile.mkdtemp(dir="/tmp")
    request.addfinalizer(lambda: shutil.rmtree(liner_dir))

    return functools.partial(
        tmpl.format,
        host=host,
        user=user,
        client_port=client_port,
        serviceapi_port=serviceapi_port,
        fileserver_port=fileserver_port,
        fileserver_socket=fileserver_socket,
        phazotron_socket=phazotron_socket,
        tests_dir=tests_path_getter(),
        sandbox_tasks_dir=sandbox_tasks_dir,
        arcadia_user=arcadia_user,
        tags=map(str, CLIENT_TAGS),
        cgroup_available=os.uname()[0] == "Linux",
        liner_dir=liner_dir,
        oauth_token=rest_su_session_token
    )


@pytest.fixture(scope="session")
def config_server_section(
    host, serviceapi_port, legacy_server_port, mongo_uri, statistics_db_name, sandbox_dir, tests_path_getter, abc_port
):
    tmpl = textwrap.dedent("""
        server:
          encryption_key: "00001111222233334444555566667777"
          autoreload: false
          log:
            root: "{tests_dir}/logs"
            name: "server.log"
            level: "DEBUG"
          api:
            port: {serviceapi_port}
            workers: 5
            enable_stats: false
          web:
            address:
              host: "{host}"
              port: {legacy_server_port}
            root_path: "{sandbox_dir}/web/templates"
            static:
              root_path: "{sandbox_dir}/web"
            threads_per_process: 25
            instances: 1
            session_timeout: 14
          upload:
            tmpdir: "{tests_dir}/upload"
          state_checker:
            ro_recheck_interval: 0
          profiler:
            enabled: false
            memory:
              port: null

          statistics:
            update_interval: 1

          services:
            log:
              root: "{tests_dir}/logs"

            mailman:
              enabled: false
              whitelist: null
              notify_real_users_only: false
              sender:
                regular: "sandbox-noreply@yandex-team.ru"  # Sender address to use in mailman
                urgent: "sandbox-urgent@yandex-team.ru"  # Address to send important e-mails from (SANDBOX-4366)

            code_updater:
              enabled: true

            core:
              enabled: true

            tasks_hosts_updater:
              enabled: false
              filter_enabled: true

            task_state_switcher:
              enabled: false

            task_status_notifier:
              enabled: false

            auto_restart_tasks:
              enabled: false

            task_queue_validator:
              enabled: false

            scheduler:
              enabled: false

            task_tags_checker:
              enabled: false

            resources_cleaner:
              enabled: false
              lifetime: 14  # Resource default life time in days

            packages_updater:
              enabled: false
              update_interval:
                meta: 30
                code: 3 # Code update interval in minutes

            statistics_updater:
              enabled: false

            statistics_processor:
              enabled: true
              database: "{statistics_db_name}"
              clickhouse:
                connection_url: null

            junk_cleaner:
              enabled: false

            serviceq:
              enabled: false

            group_synchronizer:
                enabled: false
                abc_api_url: "http://localhost:{abc_port}"

          mongodb:
            default_read_preference: "default"
            connection_url: "{mongo_uri}"

          auth:
            enabled: true
            oauth:
              token: "/fake/path/to/token"
              validation_ttl: 180

          autorestart:
            delay:
              - 0
              - 1
            timeout: 3
    """)

    return functools.partial(
        tmpl.format,
        host=host,
        serviceapi_port=serviceapi_port,
        legacy_server_port=legacy_server_port,
        tests_dir=tests_path_getter(),
        sandbox_dir=sandbox_dir,
        statistics_db_name=statistics_db_name,
        abc_port=abc_port,
        mongo_uri=mongo_uri,
    )


@pytest.fixture(scope="session")
def config_tvmtool(tests_path_getter):
    cfg = {
        "BbEnvType": 2,
        "clients": {
            "sandbox": {
                "secret": "fake_secret",
                "self_tvm_id": 2002826,
                "dsts": {
                    "yav": {
                        "dst_id": 2001357
                    },
                    "blackbox": {
                        "dst_id": 223
                    },
                }
            },
            "yav": {
                "secret": "fake_secret",
                "self_tvm_id": 2001357,
                "dsts": {}
            },
        }
    }

    cfg_path = py.path.local(tests_path_getter("etc", "tvm.conf"))
    with cfg_path.open("w", ensure=True) as fh:
        fh.write(json.dumps(cfg, indent=2))

    return str(cfg_path)


def config_saver(tests_path_getter, sections, name, **kwargs):
    cfg_path = py.path.local(tests_path_getter("etc", name))
    with cfg_path.open("w", ensure=True) as fh:
        for fill_section in sections:
            fh.write(fill_section(**kwargs))
    return str(cfg_path)


@pytest.fixture(scope="session")
def parametrized_config(
    tests_path_getter, config_common_section, config_client_section, config_server_section,
    config_serviceq_section, config_agentr_section, config_proxy_section, config_taskbox_section,
):
    return functools.partial(
        config_saver,
        tests_path_getter,
        [
            config_common_section, config_client_section, config_server_section,
            config_serviceq_section, config_agentr_section, config_proxy_section, config_taskbox_section,
        ]
    )


@pytest.fixture(scope="session")
def minimal_common_config(tests_path_getter, config_common_section):
    return functools.partial(config_saver, tests_path_getter, [config_common_section])


@pytest.fixture(scope="session")
def minimal_common_config_path(minimal_common_config):
    path = minimal_common_config("minimal-settings.yaml")
    os.environ["SANDBOX_CONFIG"] = path
    config.Registry().reload()
    return path


@pytest.fixture(scope="session")
def config_path(parametrized_config, tests_path_getter):
    path = parametrized_config("settings.yaml", tasks_data_dir=tests_path_getter("tasks"))
    os.environ["SANDBOX_CONFIG"] = path
    config.Registry().reload()
    return path


@pytest.fixture(scope="session")
def serviceq_config_path(tests_path_getter, config_common_section, config_serviceq_section):
    from sandbox.serviceq import config

    path = config_saver(
        tests_path_getter,
        [config_common_section, config_serviceq_section],
        "settings-serviceq.yaml",
    )
    os.environ["SANDBOX_SERVICEQ_CONFIG"] = path
    config.Registry().reload()
    return path


@pytest.fixture(scope="session")
def web_config_path(parametrized_config, tests_path_getter):
    return parametrized_config("settings-web.yaml", tasks_data_dir=tests_path_getter("tasks-web"))

import datetime
import json
import os
import shutil
import time
import yatest.common as yc

from passport.infra.recipes.common import log, start_daemon
from yatest.common import network


MISSING_LOG = "missing.log"
EMPTY_LOG = "empty.log"
SOME_LOG = "some.log"
HOURLY_LOG = "hourly.log"
STRESS_LOG = "stress.log"


class TestIntegral:
    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        log('Starting TestIntegral test')
        cls.pm = network.PortManager()

        try:
            with open('./tvmapi.port') as f:
                cls.tvm_port = int(f.read())
        except IOError:
            log('Could not find tvm port file: ./tvmapi.port')
            raise

        TestIntegral.setup_logs(cls)
        TestIntegral.setup_api(cls)
        TestIntegral.setup_agent(cls)

    def setup_logs(cls):
        # dir with original logs
        cls.log_source = yc.output_path('log_source')
        if os.path.isdir(cls.log_source):
            shutil.rmtree(cls.log_source)
        os.mkdir(cls.log_source)

        # output dir
        cls.log_storage = yc.output_path('storage/')
        if not os.path.isdir(cls.log_storage):
            os.mkdir(cls.log_storage)

        # config
        cls.log_instances = yc.output_path('instances/')
        if not os.path.isdir(cls.log_instances):
            os.mkdir(cls.log_instances)

        rotation_type = {
            SOME_LOG: "day",
            HOURLY_LOG: "hour",
        }
        env_type = {
            STRESS_LOG: "stress",
        }
        for filename in [MISSING_LOG, EMPTY_LOG, SOME_LOG, HOURLY_LOG, STRESS_LOG]:
            cfg = {
                "file": os.path.join(cls.log_source, filename),
                "host": ["localhost", "fake_host"],
            }
            if filename in rotation_type:
                cfg["rotation_type"] = rotation_type[filename]
            if filename in env_type:
                cfg["env"] = env_type[filename]
            with open(os.path.join(cls.log_instances, filename), 'w') as f:
                json.dump(cfg, f, indent=2)

        # create empty files for agent:
        # missing files will not be found with globs - so no logs will be pushed
        with open(os.path.join(cls.log_source, EMPTY_LOG), 'w') as f:
            f.write('')
        with open(os.path.join(cls.log_source, SOME_LOG), 'w') as f:
            f.write('')

    def setup_api(cls):
        config_path = yc.output_path('logstoreapi.conf')
        tvm_cache_dir = yc.output_path('api_tvm_cache')

        if not os.path.isdir(tvm_cache_dir):
            os.mkdir(tvm_cache_dir)
        if not os.path.isdir(cls.log_storage):
            os.mkdir(cls.log_storage)

        cls.api_http_port = cls.pm.get_tcp_port()

        config = {
            "http_daemon": {
                "listen_address": "localhost",
                "ports": [
                    {
                        "port": cls.api_http_port,
                    }
                ],
            },
            "logger": {
                "file": yc.output_path("api_common.log"),
                "level": "DEBUG",
                "print_level": True,
                "time_format": "_DEFAULT_",
            },
            "service": {
                "tvm": {
                    "self_tvm_id": 1000502,
                    "disk_cache": tvm_cache_dir,
                    "allowed_tvmids": [1000501],
                    "tvm_host": "http://127.0.0.1",
                    "tvm_port": cls.tvm_port,
                },
                "request_timeout__msecs": 1500,
                "aggregator": {
                    "buffer_limit__KB": 4096,
                    "memory_limit__MB": 20,
                },
                "logs_manager": {
                    "cleanup_period__sec": 1800,
                    "storage_path": cls.log_storage,
                    "envs": [
                        "testing",
                    ],
                },
            },
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        command = [
            yc.build_path('passport/infra/daemons/logstoreapi/daemon/logstoreapi'),
            '-c',
            config_path,
        ]

        cls.api = start_daemon(command, os.environ.copy(), cls.api_http_port, 300)

    def setup_agent(cls):
        config_path = yc.output_path('logstoreagent.conf')
        log_cache_dir = yc.output_path('agent_log_state_cache')
        tvm_cache_dir = yc.output_path('agent_tvm_cache')
        tvm_secret_path = yc.output_path('tvm.secret')

        if not os.path.isdir(log_cache_dir):
            os.mkdir(log_cache_dir)
        if not os.path.isdir(tvm_cache_dir):
            os.mkdir(tvm_cache_dir)
        with open(tvm_secret_path, 'w') as f:
            f.write("bAicxJVa5uVY7MjDlapthw")

        agent_http_port = cls.pm.get_tcp_port()

        config = {
            "http_daemon": {
                "listen_address": "localhost",
                "ports": [
                    {
                        "port": agent_http_port,
                    }
                ],
            },
            "logger": {
                "file": yc.output_path("agent_common.log"),
                "level": "DEBUG",
                "print_level": True,
                "time_format": "_DEFAULT_",
            },
            "service": {
                "dbpool_log": yc.output_path("agent_dbpool.log"),
                "tvm": {
                    "self_tvm_id": 1000501,
                    "self_secret_file": tvm_secret_path,
                    "disk_cache": tvm_cache_dir,
                    "tvm_host": "http://127.0.0.1",
                    "tvm_port": cls.tvm_port,
                    "dsts": {
                        "localhost": 1000502,
                        "fake_host": 1000502,
                    },
                },
                "pools": {
                    "get_timeout": 1000,
                    "connect_timeout": 50000,
                    "query_timeout": 50000,
                    "use_tls": False,
                    "port": cls.api_http_port,
                },
                "defaults": {
                    "env": "testing",
                    "chunk_size__KB": 128,
                    "chunk_collect_timeout__msec": 3000,
                    "compression_codec": "gzip",
                    "parallel_pushes_per_log": 4,
                    "rotation_type": "day",
                    "rotation_timeout__secs": 60,
                    "rotation_timeout_hard__secs": 120,
                },
                "hostname": "my.lucky.host",
                "skip_envs": ["stress"],
                "instances": cls.log_instances,
                "files_rescan_period__sec": 1,
                "cache_dir": log_cache_dir,
            },
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        command = [
            yc.build_path('passport/infra/daemons/logstoreagent/daemon/logstoreagent'),
            '-c',
            config_path,
        ]

        cls.agent = start_daemon(command, os.environ.copy(), cls.api_http_port, 300)

    @classmethod
    def teardown_class(cls):
        log('Closing TestIntegral test')
        cls.pm.release()
        cls.api.terminate()
        cls.agent.terminate()

    def test_push(self):
        with open(os.path.join(self.log_source, EMPTY_LOG), 'w') as f:
            f.write('')
            os.fsync(f.fileno())

        with open(os.path.join(self.log_source, SOME_LOG), 'w') as f:
            f.write('1. some very important message\n2.yes, very important\n3.no line break')
            os.fsync(f.fileno())

        with open(os.path.join(self.log_source, HOURLY_LOG), 'w') as f:
            f.write('1. hourly input\n')
            os.fsync(f.fileno())

        with open(os.path.join(self.log_source, STRESS_LOG), 'w') as f:
            f.write('1. stress input\n')
            os.fsync(f.fileno())

        daily_format = '%Y%m%d'
        hourly_format = '%Y%m%d%H'

        def get_log_filename(filename, time_format=daily_format):
            res = '%s/testing/%s/%s.' % (self.log_storage, self.log_source, filename)
            res += datetime.datetime.now().strftime(time_format)
            return res

        def check_file(filename, content, time_format=daily_format):
            filename = get_log_filename(filename, time_format)
            tries = 0
            while True:
                try:
                    with open(filename) as f:
                        assert f.read() == content
                    break
                except Exception:
                    tries += 1
                    if tries > 600:
                        raise
                    time.sleep(0.1)

        check_file(EMPTY_LOG, '')

        check_file(
            SOME_LOG,
            'my.lucky.host: 1. some very important message\nmy.lucky.host: 2.yes, very important\n',
        )

        check_file(
            HOURLY_LOG,
            'my.lucky.host: 1. hourly input\n',
            hourly_format,
        )

        assert not os.path.exists(get_log_filename(STRESS_LOG))

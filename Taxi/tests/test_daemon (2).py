import asyncio
import os
import random
import shutil
import signal

import pytest
import yaml

from datetime import datetime, timedelta

from lagg import lagg_daemon

from lagg.aggregate_metrics import TIMESTAMP_FORMAT
from lagg.metrics import metric, single_metric
from lagg.lagg_daemon import LaggDaemon, param_from_state_file

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


def prepare_dir_variables(test_data_dir):
    global TEST_DATA_DIR, TEST_LOG_FILE, TEST_STATE_FILE, TEST_CONFIG_FILE

    TEST_DATA_DIR    = test_data_dir
    TEST_LOG_FILE    = os.path.join(TEST_DATA_DIR, 'test.log')
    TEST_STATE_FILE  = os.path.join(TEST_DATA_DIR, 'state')
    TEST_CONFIG_FILE = os.path.join(TEST_DATA_DIR, 'config.yaml')


class DirTest:
    def __init__(self, test_dir):
        self.test_dir = test_dir

    def __enter__(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.mkdir(self.test_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.test_dir)


class LaggDaemonTest(LaggDaemon):
    def __init__(self, config_file):
        super().__init__(config_file)
        self.metrics = []
        self.waiting_time = 0.5

    def send_metrics(self, metrics):
        self.metrics.append(metrics)


async def test_read_log_lines(tap):
    prepare_dir_variables(os.path.join(TEST_DIR, 'test_dir_read_log_lines'))
    with tap.plan(5, 'Проверяем работу демона, в логе несколько секунд данных'):
        with DirTest(TEST_DATA_DIR):
            metric_name = 'avg_lag_event'
            config = {'logs': [{
                'file': TEST_LOG_FILE,
                'state': TEST_STATE_FILE,
                'metrics': [{
                    'name': metric_name,
                    'key': 'value',
                    'condition': {
                        'text': 'metric',
                        'name': 'lag_event'
                    },
                    'agg': 'avg'
                }]
            }]}

            with open(TEST_CONFIG_FILE, 'w') as f:
                yaml.dump(config, f)

            daemon = LaggDaemonTest(TEST_CONFIG_FILE)
            asyncio.create_task(daemon.start())

            # тестируем что ничего не случится, если отправим строку неправильного формата
            with open(TEST_LOG_FILE, 'a') as f:
                f.write('string not in required format\n')

            lag_list_1 = [('lag_event', random.random()) for _ in range(10)]
            lag_list_2 = [('lag_event', random.random()) for _ in range(10)]
            foo_list = [('foo', random.random()) for _ in range(5)]
            metric(TEST_LOG_FILE, *lag_list_1, *foo_list, timestamp=datetime.now() - timedelta(seconds=10))
            metric(TEST_LOG_FILE, *lag_list_2, timestamp=datetime.now() - timedelta(seconds=9))
            metric(TEST_LOG_FILE, ('foo', 1), timestamp=datetime.now() - timedelta(seconds=5))

            while len(daemon.metrics) < 2:
                await asyncio.sleep(0.1)

            tap.eq_ok(
                (daemon.metrics[0][0]['value'], daemon.metrics[0][0]['labels']),
                (sum([l[1] for l in lag_list_1]) / len(lag_list_1), {'sensor': metric_name}),
                'Метрики первой секунды')
            tap.eq_ok(
                (daemon.metrics[1][0]['value'], daemon.metrics[1][0]['labels']),
                (sum([l[1] for l in lag_list_2]) / len(lag_list_2), {'sensor': metric_name}),
                'Метрики второй секунды')

            pos = int(param_from_state_file(TEST_STATE_FILE, 'pos'))
            tap.eq_ok(pos, os.stat(TEST_LOG_FILE).st_size, 'Записалась pos равная размеру лога в стейт-файл')

            # напишем строку в лог с промежутком в секунду
            timestamp_str = (datetime.now() - timedelta(seconds=4)).strftime(TIMESTAMP_FORMAT)
            with open(TEST_LOG_FILE, 'a') as f:
                f.write(f'tskv\ttimestamp={timestamp_str}')
                await asyncio.sleep(1)
                f.write(f'\ttext=metric\tname=lag_event\tvalue=1\n')
            metric(TEST_LOG_FILE, ('foo', 1), timestamp=datetime.now() - timedelta(seconds=3))

            while len(daemon.metrics) < 3:
                await asyncio.sleep(0.1)

            tap.eq_ok(
                (daemon.metrics[2][0]['labels']['sensor'], daemon.metrics[2][0]['value']),
                (metric_name, 1),
                'Демон ждёт окончания строки лога')

            pos = int(param_from_state_file(TEST_STATE_FILE, 'pos'))
            tap.eq_ok(pos, os.stat(TEST_LOG_FILE).st_size, 'Записалась pos равная размеру лога в стейт-файл')

            daemon.stop()


async def test_read_complex_log_lines(tap):
    prepare_dir_variables(os.path.join(TEST_DIR, 'test_read_complex_log_lines'))
    with tap.plan(5, 'Проверяем работу демона, в логе несколько секунд данных с доп марками'):
        with DirTest(TEST_DATA_DIR):
            metric_name = 'avg_lag_event'
            config = {'logs': [{
                'file': TEST_LOG_FILE,
                'state': TEST_STATE_FILE,
                'metrics': [{
                    'name': metric_name,
                    'key': 'value',
                    'condition': {
                        'text': 'metric',
                        'name': 'lag_event'
                    },
                    'agg': 'avg'
                }]
            }]}

            with open(TEST_CONFIG_FILE, 'w') as f:
                yaml.dump(config, f)

            daemon = LaggDaemonTest(TEST_CONFIG_FILE)
            asyncio.create_task(daemon.start())

            # тестируем что ничего не случится, если отправим строку неправильного формата
            with open(TEST_LOG_FILE, 'a') as f:
                f.write('string not in required format\n')

            lag_list_1 = [random.random() for _ in range(5)]
            lag_list_2 = [random.random() for _ in range(5)]
            lag_list_3 = [random.random() for _ in range(5)]
            lag_list_4 = [random.random() for _ in range(5)]

            extra_labels_1 = {'label_1': 'label_1_1', 'label_2': 'label_2_1'}
            extra_labels_2 = {'label_1': 'label_2_1', 'label_2': 'label_2_2'}

            timestamp = datetime.now() - timedelta(seconds=8)
            for value in lag_list_1:
                single_metric(
                    TEST_LOG_FILE, name='lag_event', value=value, timestamp=timestamp,
                    extra_labels=','.join(extra_labels_1.keys()),
                    **extra_labels_1
                )

            for value in lag_list_2:
                single_metric(
                    TEST_LOG_FILE, name='lag_event', value=value, timestamp=timestamp,
                    extra_labels=','.join(extra_labels_2.keys()),
                    **extra_labels_2
                )

            timestamp = datetime.now() - timedelta(seconds=4)
            for value in lag_list_3:
                single_metric(
                    TEST_LOG_FILE, name='lag_event', value=value, timestamp=timestamp,
                    extra_labels=','.join(extra_labels_1.keys()),
                    **extra_labels_1
                )

            for value in lag_list_4:
                single_metric(
                    TEST_LOG_FILE, name='lag_event', value=value, timestamp=timestamp,
                    extra_labels=','.join(extra_labels_2.keys()),
                    **extra_labels_2
                )

            while sum([len(metrics) for metrics in daemon.metrics]) < 4:
                await asyncio.sleep(0.1)

            tap.eq_ok(
                (daemon.metrics[0][0]['value'], daemon.metrics[0][0]['labels']),
                (
                    sum([l for l in lag_list_1]) / len(lag_list_1),
                    {'sensor': metric_name, **extra_labels_1}
                ),
                'Метрики первой группы марок первой секунды')
            tap.eq_ok(
                (daemon.metrics[0][1]['value'], daemon.metrics[0][1]['labels']),
                (
                    sum([l for l in lag_list_2]) / len(lag_list_2),
                    {'sensor': metric_name, **extra_labels_2}
                ),
                'Метрики второй группы марок первой секунды')
            tap.eq_ok(
                (daemon.metrics[1][0]['value'], daemon.metrics[1][0]['labels']),
                (
                    sum([l for l in lag_list_3]) / len(lag_list_3),
                    {'sensor': metric_name, **extra_labels_1}
                ),
                'Метрики первой группы марок первой секунды')
            tap.eq_ok(
                (daemon.metrics[1][1]['value'], daemon.metrics[1][1]['labels']),
                (
                    sum([l for l in lag_list_4]) / len(lag_list_4),
                    {'sensor': metric_name, **extra_labels_2}
                ),
                'Метрики второй группы марок первой секунды')

            pos = int(param_from_state_file(TEST_STATE_FILE, 'pos'))
            tap.eq_ok(pos, os.stat(TEST_LOG_FILE).st_size, 'Записалась pos равная размеру лога в стейт-файл')

            daemon.stop()


async def test_log_rotation(tap):
    prepare_dir_variables(os.path.join(TEST_DIR, 'test_dir_log_rotation'))
    with tap.plan(5, 'Проверяем ротацию лога'):
        with DirTest(TEST_DATA_DIR):
            metric_name = 'avg_lag_event'
            config = {'logs': [{
                'file': TEST_LOG_FILE,
                'state': TEST_STATE_FILE,
                'metrics': [{
                    'name': metric_name,
                    'key': 'value',
                    'condition': {
                        'text': 'metric',
                        'name': 'lag_event'
                    },
                    'agg': 'max'
                }]
            }]}

            with open(TEST_CONFIG_FILE, 'w') as f:
                yaml.dump(config, f)

            daemon = LaggDaemonTest(TEST_CONFIG_FILE)
            asyncio.create_task(daemon.start())

            # пишем 10 строк метрик в лог
            lag_list_1 = [('lag_event', random.random()) for _ in range(10)]
            metric(TEST_LOG_FILE, *lag_list_1, timestamp=datetime.now() - timedelta(seconds=10))

            # подождём немного, чтобы файл успел прочитаться
            await asyncio.sleep(1)

            inode = int(param_from_state_file(TEST_STATE_FILE, 'inode'))
            tap.eq_ok(inode, os.stat(TEST_LOG_FILE).st_ino, 'Записалась правильная inode в стейт-файл')

            # удаляем лог
            os.remove(TEST_LOG_FILE)

            # снова пишем 10 строк метрик в лог и одну строку след секунды
            metric(TEST_LOG_FILE, *lag_list_1, timestamp=datetime.now() - timedelta(seconds=9))
            metric(TEST_LOG_FILE, ('foo', 1), timestamp=datetime.now() - timedelta(seconds=8))
            # ждём пока метрики обработаются
            while len(daemon.metrics) < 2:
                await asyncio.sleep(0.1)

            tap.eq_ok(
                (daemon.metrics[0][0]['labels']['sensor'], daemon.metrics[0][0]['value']),
                (metric_name, max([l[1] for l in lag_list_1])),
                'Метрики старого лога отправились')
            tap.eq_ok(
                (daemon.metrics[1][0]['labels']['sensor'], daemon.metrics[1][0]['value']),
                (metric_name, max([l[1] for l in lag_list_1])),
                'Метрики нового лога отправились')

            pos = int(param_from_state_file(TEST_STATE_FILE, 'pos'))
            tap.eq_ok(pos, os.stat(TEST_LOG_FILE).st_size, 'Записалась pos равная размеру лога в стейт-файл')
            inode = int(param_from_state_file(TEST_STATE_FILE, 'inode'))
            tap.eq_ok(inode, os.stat(TEST_LOG_FILE).st_ino, 'Поменялась inode в стейт-файле')

            daemon.stop()


async def test_name_key_agg_key(tap):
    prepare_dir_variables(os.path.join(TEST_DIR, 'test_dir_name_key_agg_key'))
    with tap.plan(3, 'Проверяем опции name_key и agg_key'):
        with DirTest(TEST_DATA_DIR):
            config = {'logs': [{
                'file': TEST_LOG_FILE,
                'state': TEST_STATE_FILE,
                'metrics': [{
                    'name_key': 'name',
                    'key': 'value',
                    'condition': {
                        'text': 'metric',
                    },
                    'agg_key': 'agg'
                }]
            }]}

            with open(TEST_CONFIG_FILE, 'w') as f:
                yaml.dump(config, f)

            daemon = LaggDaemonTest(TEST_CONFIG_FILE)
            asyncio.create_task(daemon.start())

            metric_name = 'lag_event'
            lag_list_1 = [(metric_name, random.random()) for _ in range(10)]
            metric(TEST_LOG_FILE, *lag_list_1, timestamp=datetime.now() - timedelta(seconds=10), agg='min')
            metric(TEST_LOG_FILE, ('foo', 1), timestamp=datetime.now() - timedelta(seconds=8))

            while len(daemon.metrics) < 1:
                await asyncio.sleep(0.1)

            tap.eq_ok(
                (daemon.metrics[0][0]['labels']['sensor'], daemon.metrics[0][0]['value']),
                (metric_name, min([l[1] for l in lag_list_1])),
                'Метрики правильно считаются')

            pos = int(param_from_state_file(TEST_STATE_FILE, 'pos'))
            tap.eq_ok(pos, os.stat(TEST_LOG_FILE).st_size, 'Записалась pos равная размеру лога в стейт-файл')

            metric(TEST_LOG_FILE, *lag_list_1, timestamp=datetime.now() - timedelta(seconds=6))
            metric(TEST_LOG_FILE, ('foo', 1), timestamp=datetime.now() - timedelta(seconds=4))

            while len(daemon.metrics) < 3:
                await asyncio.sleep(0.1)

            tap.eq_ok(
                (daemon.metrics[2][0]['labels']['sensor'], daemon.metrics[2][0]['value']),
                (metric_name, sum([l[1] for l in lag_list_1])),
                'Если нет agg_key в логе, то sum берётся')

            daemon.stop()


@pytest.mark.parametrize('sig', [signal.SIGINT, signal.SIGTERM])
async def test_stop_by_signal(tap, sig):
    prepare_dir_variables(os.path.join(TEST_DIR, 'test_stop_by_signal'))
    with tap.plan(2, 'Остановка демона по сигналу'):
        with DirTest(TEST_DATA_DIR):
            config = {'logs': [{
                'file': TEST_LOG_FILE,
                'state': TEST_STATE_FILE,
                'metrics': [{
                    'name_key': 'name',
                    'key': 'value',
                    'condition': {
                        'text': 'metric',
                    },
                    'agg_key': 'agg'
                }]
            }]}

            with open(TEST_CONFIG_FILE, 'w') as f:
                yaml.dump(config, f)

            metric(TEST_LOG_FILE, ('foo', 1), timestamp=datetime.now() - timedelta(seconds=3))

            daemon = lagg_daemon.start_daemon(
                TEST_CONFIG_FILE,
                loop=asyncio.get_event_loop()
            )
            await asyncio.sleep(.5)

            tap.ok(daemon.is_running_daemon, 'daemon started')

            os.kill(os.getpid(), sig)

            tap.ok(not daemon.is_running_daemon, 'daemon stopped')

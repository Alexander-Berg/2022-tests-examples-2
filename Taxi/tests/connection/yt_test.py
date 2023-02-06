import copy
import contextlib
import ctypes
import logging
import multiprocessing
import threading

import mock
import pytest
from datetime import timedelta
from typing import List

from dmp_suite import yt
from dmp_suite import datetime_utils as dtu
from dmp_suite.common_utils import deep_update_dict
from connection.yt import (
    get_yt_client, patch_yt_client, _YTClientProxy,
    _yt_client_settings, patch_yt_client_settings,
    get_default_yt_cluster, get_yt_cluster_proxy,
    get_transfer_manager_client, Cluster,
)
from test_dmp_suite.yt.utils import random_yt_table


logger = logging.getLogger("YT connection tests")


# NOTE: фикстура вызывала блок finally только после завершения всех тестов
# что приводило к спецэффектам
@contextlib.contextmanager
def setup_client(new_proxy):
    with mock.patch('connection.yt._yt_client_proxy', new_proxy):
        del get_yt_client().__wrapped__
        try:
            yield
        finally:
            del get_yt_client().__wrapped__


def create_patched_factory(clients):
    def patched_factory():
        client_mock = mock.MagicMock()
        clients.append(client_mock)
        return client_mock
    return patched_factory


def yt_list(yt_path):
    get_yt_client().list(yt_path)


# Используем os.getpid() чтобы отличить запуски в разных процессах
class TestGetYtClient:

    @contextlib.contextmanager
    def setup_client(self):
        clients: List[mock.MagicMock] = []
        with setup_client(_YTClientProxy(create_patched_factory(clients))):
            yield clients

    def test_cached(self):
        with self.setup_client() as clients:
            assert get_yt_client() is get_yt_client()
            assert get_yt_client().__wrapped__ is get_yt_client().__wrapped__
            assert get_yt_client().__wrapped__ is clients[0]
            assert len(clients) == 1

    def test_thread_safe(self):
        with self.setup_client() as clients:
            yt_list('//test')
            assert len(clients) == 1
            clients[0].list.assert_called_once_with('//test')

            thread = threading.Thread(target=yt_list, args=('//test2',))
            thread.start()
            thread.join()

            assert len(clients) == 2
            assert clients[0] is not clients[1]
            clients[0].list.assert_called_once_with('//test')
            clients[1].list.assert_called_once_with('//test2')

    def test_capture_client_variable(self):
        with self.setup_client() as clients:
            ytc = get_yt_client()
            yt_list('//test')
            ytc.list('//test_direct_call')
            # клиент должен быть только один
            # не зависимо от способа вызова метода list
            assert len(clients) == 1
            expected_call_ytc_0 = [mock.call('//test'), mock.call('//test_direct_call')]
            assert clients[0].list.call_args_list == expected_call_ytc_0

            def yt_list_thread(yt_path):
                ytc.list(yt_path)

            thread = threading.Thread(target=yt_list_thread, args=('//test2',))
            thread.start()
            thread.join()

            assert len(clients) == 2
            assert clients[0] is not clients[1]
            assert clients[0].list.call_args_list == expected_call_ytc_0
            clients[1].list.assert_called_once_with('//test2')

    def test_process_safe(self):
        with self.setup_client() as clients:
            yt_list('//test')
            assert len(clients) == 1
            clients[0].list.assert_called_once_with('//test')

            subprocess_assertion = multiprocessing.Value(ctypes.c_bool, False)

            def yt_list_proc(assertion):
                ytc = get_yt_client()
                ytc.list('//test2')
                # если бы использовалась копия YT клиента из род. процесса
                # то был бы дополнительный вызов с аргументом  `//test`
                assertion.value = (ytc.list.call_args_list == [mock.call('//test2')])

            proc = multiprocessing.Process(target=yt_list_proc, args=(subprocess_assertion,))
            proc.start()
            proc.join()

            # клиент созданный в дочернем процессе в родительском не виден
            assert len(clients) == 1
            clients[0].list.assert_called_once_with('//test')
            # явно проверяем на True, чтобы исключить ложно положительное срабатывание
            assert subprocess_assertion.value is True

    def test_proxy_setter_exception(self):
        with self.setup_client():
            with pytest.raises(AttributeError):
                get_yt_client().__wrapped__ = object()

            with pytest.raises(AttributeError):
                assert get_yt_client().__wrapped__
                get_yt_client().__wrapped__ = object()


class TestPatchYtClient:
    client_1 = 1
    client_2 = 2

    def setup_client(self):
        return setup_client(_YTClientProxy(lambda: self.client_1))

    def test_cached_local_client(self):
        with self.setup_client():
            client_proxy = get_yt_client()
            assert client_proxy.__wrapped__ == self.client_1

            with patch_yt_client(lambda: self.client_2):
                assert client_proxy.__wrapped__ == self.client_2

            assert client_proxy.__wrapped__ == self.client_1

    def test_cached_nonlocal_client(self):
        with self.setup_client():
            assert get_yt_client().__wrapped__ == self.client_1

            with patch_yt_client(lambda: self.client_2):
                assert get_yt_client().__wrapped__ == self.client_2

            assert get_yt_client().__wrapped__ == self.client_1

    def test_thread(self):
        with self.setup_client():
            assert get_yt_client().__wrapped__ == self.client_1
            thread_client_wrapped = None

            with patch_yt_client(lambda: self.client_2):

                def set_thread_client():
                    nonlocal thread_client_wrapped
                    thread_client_wrapped = get_yt_client().__wrapped__

                thread = threading.Thread(target=set_thread_client)
                thread.start()
                thread.join()

            assert thread_client_wrapped == self.client_2
            assert get_yt_client().__wrapped__ == self.client_1

    def test_capture_client_variable(self):
        with self.setup_client():
            client = get_yt_client()
            assert client.__wrapped__ == self.client_1
            thread_client_wrapped = None

            with patch_yt_client(lambda: self.client_2):
                def set_thread_client():
                    nonlocal thread_client_wrapped
                    thread_client_wrapped = client.__wrapped__

                thread = threading.Thread(target=set_thread_client)
                thread.start()
                thread.join()

            assert thread_client_wrapped == self.client_2
            assert client.__wrapped__ == self.client_1

    def test_process_safe(self):
        with self.setup_client():
            assert get_yt_client().__wrapped__ == self.client_1
            subprocess_client = multiprocessing.Value(ctypes.c_ulonglong, 0)

            with patch_yt_client(lambda: self.client_2):
                def set_client(client):
                    client.value = get_yt_client().__wrapped__

                proc = multiprocessing.Process(target=set_client, args=(subprocess_client,))
                proc.start()
                proc.join()

            assert subprocess_client.value == self.client_2
            assert get_yt_client().__wrapped__ == self.client_1


@mock.patch('connection.yt.settings', mock.MagicMock(return_value='dummy'))
@pytest.mark.parametrize(
    "cont_1, cont_2",
    [
        (
            {'table_writer': {'max_row_weight': 1024 * 1024 * 32}},
            {'table_writer': {'max_row_weight': 1024, 'upload_replication_factor': 10}}
        ),
    ]
)
def test_yt_settings_nesting(cont_1, cont_2):
    """
    1. On each level assert that _yt_client_settings is
    correctly updated by patch_yt_client_settings(...).
    2. Checks that get_yt_client() returns updated client.
    """
    true_cont_1 = copy.deepcopy(cont_1)
    true_cont_2 = copy.deepcopy(cont_1)
    deep_update_dict(true_cont_2, cont_2)

    _client = get_yt_client()  # proxy

    def _check_nest_config(expected):
        nonlocal _client
        for k, v in expected.items():
            assert _client.config[k] == v
        assert _yt_client_settings.config == expected

    _check_nest_config({})
    with patch_yt_client_settings(config=cont_1):
        _check_nest_config(true_cont_1)
        with patch_yt_client_settings(config=cont_2):
            _check_nest_config(true_cont_2)
        _check_nest_config(true_cont_1)
    _check_nest_config({})


def _side_get_cluster(_):
    return _yt_client_settings.get_cluster() or 'default_cluster'


@mock.patch('connection.yt.settings', mock.MagicMock(side_effect=_side_get_cluster))
def test_yt_settings_cluster():
    assert 'default_cluster' == get_yt_client().config["proxy"]["url"].split('.')[0]
    with patch_yt_client_settings(cluster='new_cluster'):
        assert 'new_cluster' == get_yt_client().config["proxy"]["url"].split('.')[0]
        assert 'new_cluster' == get_yt_cluster_proxy().split('.')[0]
    assert 'default_cluster' == get_yt_client().config["proxy"]["url"].split('.')[0]


@pytest.mark.slow('arnold')
def test_transfer_manager_client():

    # проверка нужна на случай, если внутри пакетов yt
    # что-то снова изменится, а версии пакетов не будут
    # соответствовать друг другу.

    logger.debug("Starting transfer manager client test. ")

    tm_client = get_transfer_manager_client()
    yt_client = get_yt_client()

    @random_yt_table
    class HahnTable(yt.YTTable):
        date = yt.Date(sort_key=True)
        string = yt.String()

    @random_yt_table
    class ArnoldTable(yt.YTTable):
        date = yt.Date(sort_key=True)
        string = yt.String()

    hahn_meta = yt.resolve_meta(HahnTable)
    arnold_meta = yt.resolve_meta(ArnoldTable)
    data = [{'date': '2012-01-01', 'string': "TestString0101"}]

    logger.debug(f"Hahn target path is {hahn_meta.target_path()}. "
                 f"Arnold target path is {arnold_meta.target_path()}. ")

    try:
        with patch_yt_client_settings(cluster=Cluster.HAHN):
            yt_client.create(
                type='table',
                path=hahn_meta.target_path(),
                attributes=hahn_meta.attributes(),
                recursive=True,
            )
            yt_client.write_table(hahn_meta.target_path(), data)

        with patch_yt_client_settings(cluster=Cluster.ARNOLD):
            # Создаем временную таблицу на Арнольде вручную,
            # чтобы затем почистить, т.к. в рамках сессии
            # фикстуры conftest никак не затрагивают Арнольд.

            expiration_time = dtu.utcnow() + timedelta(days=1)
            yt_client.create(
                type='table',
                path=arnold_meta.target_path(),
                attributes=dict(
                    hahn_meta.attributes(),
                    expiration_time=dtu.format_datetime_microseconds(expiration_time),
                ),
                recursive=True,
            )

        tm_client.add_task(
            source_cluster=Cluster.HAHN.value,
            source_table=hahn_meta.target_path(),
            destination_cluster=Cluster.ARNOLD.value,
            destination_table=arnold_meta.target_path(),
            sync=True,
        )

        with patch_yt_client_settings(cluster=Cluster.ARNOLD):
            assert data == list(yt_client.read_table(arnold_meta.target_path()))

    finally:
        with patch_yt_client_settings(cluster=Cluster.ARNOLD):
            if yt_client.exists(arnold_meta.target_path()):
                yt_client.remove(arnold_meta.target_path(), recursive=True, force=True)

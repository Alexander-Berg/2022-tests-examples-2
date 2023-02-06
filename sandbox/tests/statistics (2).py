import pytest
import httplib
import requests

import common

import yasandbox.controller
import yasandbox.manager.tests


class TestStatistics(object):
    def test__db_statistics(self, json_api_url):
        ret = requests.get(json_api_url + '/db/current_op').json()
        assert isinstance(ret, dict)

    def test__db_size(self, json_api_url):
        ret = requests.get(json_api_url + '/db/size').json()
        assert isinstance(ret, dict)

    def test__enqueued_tasks_statistics(self, json_api_url):
        ret = requests.get(json_api_url + '/tasks/enqueued/cpu_preferences').json()
        assert isinstance(ret, dict)

    def test__storages_resources_statistics(self, json_api_url):
        ret = requests.get(json_api_url + '/storage/size').json()
        assert isinstance(ret, dict)

    def test__tasks_enqueue_time(self, json_api_url):
        ret = requests.get(json_api_url + '/tasks/enqueued/queue_time').json()
        assert isinstance(ret, dict)


class TestSignals(object):
    @pytest.mark.usefixtures("server")
    def test__post_signal(
        self, task_manager, rest_session, rest_session_login, rest_su_session, task_session
    ):
        data = [dict(something="something-else")]
        signal_name = "ping_pong_ching_chong"
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.statistics[signal_name](data)
        assert ex.value.status == httplib.FORBIDDEN

        tid = yasandbox.manager.tests._create_task(task_manager).id
        task_session(rest_session, tid, rest_session_login)

        for session in (rest_session, rest_su_session):
            session.statistics[signal_name](data)

    def test__server_signal_handler(self, settings, signals_db):
        data = [dict(something="something-else")]
        signal_name = "ping_pong_ching_chong"
        common.statistics.ServerSignalHandler().handle(signal_name, data)
        assert signals_db[signal_name].count() == 1

# import json
import os
import requests
import time

from passport.infra.recipes.common import log
from passport.infra.daemons.push_subscription.ut.common import PushSubsctiptionFixture


class TestPushSubsctiption:
    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        log('Starting PushSubsctiption test')

        cls.srv = PushSubsctiptionFixture()

    @classmethod
    def teardown_class(cls):
        log('Closing PushSubsctiption test')
        cls.srv.stop()

    def check_ip(self, url):
        res = requests.post(url, data="")
        assert res.status_code == 200, res.text
        assert (
            res.text
            == """{"status":"error","errors":["ip.empty"]}
"""
        )

        res = requests.post(url, data="", headers={"Ya-Consumer-Client-Ip": "127"})
        assert res.status_code == 200, res.text
        assert (
            res.text
            == """{"status":"error","errors":["ip.invalid"]}
"""
        )

        res = requests.post(url, data="", headers={"Ya-Consumer-Client-Ip": "127.0.0.1"})
        assert res.status_code == 200, res.text
        assert "ip." not in res.text

    def check_required_args(self, url, args):
        current_array = []
        for arg in args:
            current_array.append(arg)

            form = {arg: "kek" for arg in current_array}
            res = requests.post(url, data=form, headers={"Ya-Consumer-Client-Ip": "127.0.0.1"})
            assert res.status_code == 200, res.text
            assert "%s.empty" % arg not in res.text

    def check_auth_errs(self, url, form):
        common_headers = {"Ya-Consumer-Client-Ip": "127.0.0.1"}
        res = requests.post(url, data=form, headers={"Ya-Consumer-Client-Ip": "127.0.0.1"})
        assert res.status_code == 200, res.text
        assert (
            res.text
            == """{"status":"error","errors":["authorization.empty"]}
"""
        )

        common_headers = {"Ya-Consumer-Client-Ip": "127.0.0.1", "Ya-Consumer-Authorization": "OAuth kek"}
        res = requests.post(url, data=form, headers=common_headers)
        assert res.status_code == 200, res.text
        assert (
            res.text
            == """{"status":"error","errors":["oauth_token.invalid"]}
"""
        )

    def test_ping(self):
        url = 'http://127.0.0.1:%d/ping' % self.srv.http_port

        res = requests.get(url)
        assert res.status_code == 200
        assert res.text == "Pong"

    def test_subscribe(self):
        url = 'http://127.0.0.1:%d/1/bundle/push/subscribe/' % self.srv.http_port

        self.check_ip(url)
        self.check_required_args(url, ["app_id", "app_platform", "deviceid", "device_token"])

        form = {
            "app_platform": "foo",
            "deviceid": "lol",
            "device_token": "device_token",
        }
        res = requests.post(url + '?app_id=kek', data=form, headers={"Ya-Consumer-Client-Ip": "127.0.0.1"})
        assert res.status_code == 200, res.text
        assert (
            res.text
            == """{"status":"error","errors":["push_api.app_platform_unsupported"]}
"""
        )

        form = {
            "app_id": "kek",
            "app_platform": "android",
            "deviceid": "lol",
            "device_token": "device_token",
        }
        self.check_auth_errs(url, form)

        common_headers = {
            "Ya-Consumer-Client-Ip": "127.0.0.1",
            "Ya-Consumer-Authorization": "OAuth AQAAAADue-GoAAAI22_eZKnwukAEhLSCzDr5FHk",
        }

        res = requests.post(url, data=form, headers=common_headers)
        assert res.status_code == 200, res.text
        assert (
            res.text
            == """{"status":"ok"}
"""
        )

    def test_unsubscribe(self):
        url = 'http://127.0.0.1:%d/1/bundle/push/unsubscribe/' % self.srv.http_port

        self.check_ip(url)
        self.check_required_args(url, ["app_id", "deviceid", "uid"])

        form = {
            "app_id": "kek",
            "deviceid": "lol",
            "uid": 123,
        }
        res = requests.post(url, data=form, headers={"Ya-Consumer-Client-Ip": "127.0.0.1"})
        assert res.status_code == 200, res.text
        assert (
            res.text
            == """{"status":"ok"}
"""
        )

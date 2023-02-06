import time
from typing import Any, Dict
from noc.ci.salt_percent_deploy.proto.salt_percent_deploy_pb2 import PackageInfo
from noc.ci.salt_percent_deploy.src import prepare_salt_template, JugglerAPI
import mock


class TestTemplateMutation:
    def test_change_percent(self) -> None:
        """
        Check that we don't remove packages.
        """
        template = """sentinel: 100500+uuid
packages:
  - name: vim
    version:
      old: '2:8.0.1453-1ubuntu1.4'
      new: '2:8.0.1453-1ubuntu1.6'
    percent: 50
    dc: iva"""

        packages = {
            "valve-ui": ("1.0.0-100500", PackageInfo(percents={"man": 40})),
        }
        with mock.patch("uuid.uuid4", lambda: "next-uuid"):
            data, _ = prepare_salt_template(template, packages=packages)

        expected = """sentinel: 100500+next-uuid
packages:
  - name: vim
    version:
      old: 2:8.0.1453-1ubuntu1.4
      new: 2:8.0.1453-1ubuntu1.6
    percent: 50
    dc: iva
  - name: valve-ui
    version:
      new: 1.0.0-100500
    percent: 40
    dc: man
"""

        assert expected == data

    def test_change_percent_leave_old(self) -> None:
        """
        Check that we don't remove "old" field.
        """
        template = """sentinel: 1005001+uuid
packages:
  - name: valve-ui
    version:
      old: 1.0.0-100400
      new: 1.0.0-100450
    percent: 20
    dc: man"""

        packages = {"valve-ui": ("1.0.0-100500", PackageInfo(percents={"man": 40}))}
        with mock.patch("uuid.uuid4", lambda: "next-uuid"):
            data, _ = prepare_salt_template(template, packages=packages)

        expected = """sentinel: 1005001+next-uuid
packages:
  - name: valve-ui
    version:
      old: 1.0.0-100400
      new: 1.0.0-100500
    percent: 40
    dc: man
"""

        assert expected == data

    def test_change_percent_update_old(self) -> None:
        """
        Check that we update "old" field if finished with this DC.
        """
        template = """sentinel: 1005002+uuid
packages:
  - name: valve-ui
    version:
      old: 1.0.0-100400
      new: 1.0.0-100450
    percent: 20
    dc: man"""

        packages = {"valve-ui": ("1.0.0-100500", PackageInfo(percents={"man": 100}))}
        with mock.patch("uuid.uuid4", lambda: "next-uuid"):
            data, _ = prepare_salt_template(template, packages=packages)

        expected = """sentinel: 1005002+next-uuid
packages:
  - name: valve-ui
    version:
      old: 1.0.0-100500
      new: 1.0.0-100500
    percent: 100
    dc: man
"""

        assert expected == data

    def test_change_sentinel(self) -> None:
        """
        Check that we update "old" field if finished with this DC.
        """
        template = """sentinel: 100+uuid
packages:
  - name: valve-ui
    version:
      old: 1.0.0-100400
      new: 1.0.0-100450
    percent: 20
    dc: man"""

        real_sotka = "146"
        packages = {"valve-ui": ("1.0.0-100500", PackageInfo(percents={"man": 100}))}
        with mock.patch("uuid.uuid4", lambda: "next-uuid"):
            data, new_sentinel = prepare_salt_template(
                template, packages=packages, revision=real_sotka
            )
        assert real_sotka + "+next-uuid" == new_sentinel

        expected = """sentinel: 146+next-uuid
packages:
  - name: valve-ui
    version:
      old: 1.0.0-100500
      new: 1.0.0-100500
    percent: 100
    dc: man
"""

        assert expected == data


class TestJugglerRawEventCheck:
    def test_juggler_stale_event_is_not_ok(self) -> None:
        raw_event: Dict[str, Any] = {
            "items": [
                {
                    "host": "music-stable-connector-man2-1273-man-music-stable-con-696-28252.gencfg-c.yandex.net",
                    "service": "subscribe.4xx",
                    "instance": "",
                    "status": "OK",
                    "description": "OK",
                    "digest": "",
                    "received_time": 1579584742,  # too stale: Tue Jan 21 12:32:22 PM +07 2020
                    "tags": [],
                    "heartbeat": 731,
                }
            ],
            "limit": 20,
            "total": 1,
            "meta": {"_backend": "eubdlirw2mjrvwbf.vla.yp-c.yandex.net"},
            "response_too_large": False,
        }
        event = JugglerAPI._to_raw_event(raw_event["items"][0])
        with mock.patch.object(JugglerAPI, "_get_raw_events", lambda *_: event):
            j = JugglerAPI(oauth_token="my-token")
            desc, ok = j.is_ok("some-host", "some-service")
            assert "STALE" in desc and not ok

    def test_juggler_fresh_event_is_ok(self) -> None:
        raw_event: Dict[str, Any] = {
            "items": [
                {
                    "host": "iva-valve1.net.yandex.net",
                    "service": "valve",
                    "instance": "",
                    "status": "OK",
                    "description": "OK",
                    "digest": "",
                    "received_time": time.time(),
                    "tags": ["bundle-monrun_salt_valve"],
                    "heartbeat": 59,
                }
            ],
            "limit": 20,
            "total": 1,
            "meta": {"_backend": "sgvaxg3buwn3tzlz.myt.yp-c.yandex.net"},
            "response_too_large": True,
        }
        event = JugglerAPI._to_raw_event(raw_event["items"][0])
        with mock.patch.object(JugglerAPI, "_get_raw_events", lambda *_: event):
            j = JugglerAPI(oauth_token="my-token")
            desc, ok = j.is_ok("some-host", "some-service")
            assert "STALE" not in desc and ok

    def test_juggler_not_ok_event_is_not_ok(self) -> None:
        raw_event: Dict[str, Any] = {
            "items": [
                {
                    "host": "iva-valve1.net.yandex.net",
                    "service": "valve",
                    "instance": "",
                    "status": "CRIT",
                    "description": "OK",
                    "digest": "",
                    "received_time": time.time(),
                    "tags": ["bundle-monrun_salt_valve"],
                    "heartbeat": 59,
                }
            ],
            "limit": 20,
            "total": 1,
            "meta": {"_backend": "sgvaxg3buwn3tzlz.myt.yp-c.yandex.net"},
            "response_too_large": True,
        }
        event = JugglerAPI._to_raw_event(raw_event["items"][0])
        with mock.patch.object(JugglerAPI, "_get_raw_events", lambda *_: event):
            j = JugglerAPI(oauth_token="my-token")
            desc, ok = j.is_ok("some-host", "some-service")
            assert "STALE" not in desc and not ok

# encoding: utf-8

from __future__ import absolute_import, unicode_literals

import requests
import responses

from sandbox.common import hardware


CONDUCTOR_RESPONSE_OK = """
<data>
    <item>
        <id>309488</id>
        <group>search_instrum-sandbox_lxc_share_generic</group>
        <fqdn>sandbox216.search.yandex.net</fqdn>
        <datacenter>iva5</datacenter>
        <root_datacenter>iva</root_datacenter>
        <short_name>sandbox216.search</short_name>
        <description>тест тест тест</description>
    </item>
</data>
"""
CONDUCTOR_RESPONSE_NOT_FOUND = "No hosts found"


class TestHostInfo(object):

    def test__dc(self, monkeypatch):

        host = "sandbox216.search.yandex.net"
        base_url = hardware.HostInfo.CONDUCTOR_API_URL

        with responses.RequestsMock() as mk:
            mk.add("GET", "{}/hosts/{}".format(base_url, host), CONDUCTOR_RESPONSE_OK, status=200)
            assert hardware.HostInfo.dc(host) == "iva5"

        with responses.RequestsMock() as mk:
            mk.add("GET", "{}/hosts/{}".format(base_url, "foobar"), CONDUCTOR_RESPONSE_NOT_FOUND, status=404)
            assert hardware.HostInfo.dc("foobar") == "unk"

        def get_failure(*_, **__):
            raise requests.ConnectionError
        monkeypatch.setattr(requests, "get", get_failure)
        assert hardware.HostInfo.dc(host) == "unk"

    def test__has_ssd(self):
        host = "sandbox216.search.yandex.net"
        base_url = hardware.HostInfo.BOT_API_URL

        ssd_response = b"900321276 HDD Samsung-MZ-7PD4800/0DA(SM843) (480GB/SATA/SSD/2.5) S/N:S15TNEAD707688"
        with responses.RequestsMock() as mk:
            mk.add("GET", "{}/consistof.php?name={}".format(base_url, host), ssd_response, status=200)
            assert hardware.HostInfo.has_ssd(host)

        no_ssd_response = b"127920 HDD Hitachi-HUA722020ALA330 (2000GB/SATA/7.2K/3.5) S/N:YGG1HX1A"
        with responses.RequestsMock() as mk:
            mk.add("GET", "{}/consistof.php?name={}".format(base_url, host), no_ssd_response, status=200)
            assert not hardware.HostInfo.has_ssd(host)

        not_found_response = b"err: not found"
        with responses.RequestsMock() as mk:
            mk.add("GET", "{}/consistof.php?name={}".format(base_url, host), not_found_response, status=200)
            assert not hardware.HostInfo.has_ssd(host)

    def test__neighbours(self, monkeypatch):

        def fake_dc(_, host):
            return {"h1": "sas", "h2": "vla", "h3": "iva", "h4": "iva"}[host]

        class Host(object):
            fqdn = "h4"
            dc = "iva"

        monkeypatch.setattr(hardware.HostInfo, "dc", classmethod(fake_dc))

        assert hardware.HostInfo.neighbours(Host, ["h1", "h2", "h3", "h4"]) == ["h4", "h3", "h1", "h2"]

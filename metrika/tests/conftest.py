import logging
import pytest
import yatest.common
import metrika.pylib.config as lib_config
import metrika.admin.brb.server.lib.utils.its_client as its
import metrika.admin.brb.server.lib.views.front_handlers as fh
import mock
import asynctest as at
from infra.awacs.proto import api_pb2
import base64
import json
import hashlib
import datetime as dt

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope="module")
def config():
    config_file = yatest.common.source_path('metrika/admin/brb/server/tests/config.yaml')
    config = lib_config.get_yaml_config_from_file(config_file)
    return config


@pytest.fixture(scope="module")
def list_namespaces():
    namespaces_file = yatest.common.source_path('metrika/admin/brb/server/tests/namespaces.txt')
    with open(namespaces_file, 'rb') as f:
        namespaces = f.read()
    resp = api_pb2.ListNamespacesResponse().FromString(namespaces)

    def dummy_listnamespaces(*args, **kwargs):
        return resp
    return dummy_listnamespaces


@pytest.fixture(scope="module")
def list_balancers():
    balancers_file = yatest.common.source_path('metrika/admin/brb/server/tests/balancers.json')
    with open(balancers_file, 'rb') as f:
        encoded_balancers = json.loads(f.read())
    balancers = {}
    for ns in encoded_balancers:
        balancers[ns] = api_pb2.ListBalancersResponse().FromString(base64.decodebytes(encoded_balancers[ns].encode('ascii')))

    def dummy_listbalancers(*args, **kwargs):
        ns_id = args[0]
        return balancers[ns_id]
    return dummy_listbalancers


class dummyITSClient(object):
    def __init__(self, list_balancers, list_namespaces):
        self.namespace_statuses = {}
        self.balancer_statuses = {}
        self.all_namespaces = [x.meta.id.replace('.', '_') for x in list_namespaces().namespaces]
        self.namespaces_with_its = ['metrika_yandex_ru',
                                    'internalapi_mtrs_yandex_ru',
                                    'mtproxy2d-production_metrika_yandex_net',
                                    'appmetrica_yandex_ru',
                                    'api_appmetrica_yandex_ru',
                                    'api-metrica_yandex_net',
                                    'api-audience_yandex_ru',
                                    'radar_yandex_ru',
                                    'audience_yandex_ru']
        for ns in self.namespaces_with_its:
            self.namespace_statuses[ns] = [200, "{}", None]
            for dc in ['sas', 'vla', 'man']:
                self.balancer_statuses[f"{ns}_{dc}"] = [200, "{}", None]

    def _parse_location(self, location):
        parts = location.split('/')
        namespace = None
        dc = None
        if len(parts) == 2:
            namespace = parts[-1]
        if len(parts) == 4:
            dc = parts[-1]
            namespace = parts[-3]
        return namespace, dc

    async def get(self, location):
        ns, dc = self._parse_location(location)
        etag = None
        if ns not in self.namespaces_with_its:
            logging.debug(f"ITS REQ GET: {ns} not in {self.namespaces_with_its}")
            status = 404
            response = ""
        else:
            if dc:
                status, response, etag = self.balancer_statuses.get(f"{ns}_{dc}")
            else:
                status, response, etag = self.namespace_statuses.get(ns, [404, "", None])
        logging.debug(f"ITS REQ GET return: {status} {response} {location} {etag}")
        return {"status": status, "response": response, "location": location, "etag": etag}

    async def open(self, location, etag):
        ns, dc = self._parse_location(location)
        if ns not in self.namespaces_with_its:
            status = 404
            response = ""
        else:
            if dc:
                status = 204
                response = ""
                status, response, version = self.balancer_statuses.get(f"{ns}_{dc}")
                if etag != version:
                    status = 412
                else:
                    self.balancer_statuses[f"{ns}_{dc}"] = [200, "{}", None]
            else:
                status = 404
                response = ""
        return {"status": status, "response": response, "location": location}

    async def close(self, location):
        version = hashlib.md5(str(dt.datetime.now()).encode("utf-8")).hexdigest()[0:24]
        ns, dc = self._parse_location(location)
        if ns not in self.namespaces_with_its:
            status = 403
            response = ""
            version = None
        else:
            if dc:
                status = 200
                response = json.dumps({"path": f"balancer/{ns}/{dc}/{dc}/service_balancer_off",
                                       "user_value": "to_upstream, -1\nswitch_off, 1\n",
                                       "formatted_value": "to_upstream, -1\nswitch_off, 1\n"})
                resp_to_set = json.dumps({f"balancer/{ns}/{dc}/{dc}/service_balancer_off": {"value": "to_upstream, -1\nswitch_off, 1\n",
                                                                                            "version": f"{version}"}})
                self.balancer_statuses[f"{ns}_{dc}"] = [200, resp_to_set, version]
            else:
                status = 404
                response = ""
                version = None
        return {"status": status, "response": response, "location": location, "etag": version}


@pytest.fixture(scope="module")
def dummy_its(list_balancers, list_namespaces):
    return dummyITSClient(list_balancers, list_namespaces)


class dummyJugglerClient(object):
    def __init__(self, *args, **kwargs):
        pass

    async def set_downtime(self, *args, **kwargs):
        dt_id = hashlib.md5(str(dt.datetime.now()).encode("utf-8")).hexdigest()[0:24]
        return {"downtime_id": dt_id}

    async def remove_downtime(self, *args, **kwargs):
        return {"downtimes": []}


@pytest.fixture(scope="module")
def dummy_juggler():
    return dummyJugglerClient()

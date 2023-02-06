#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File with different routines to hold tests on expected_destinations
"""
from __future__ import print_function

import time

from nile.api.v1 import clusters
from requests import request


cluster = clusters.Hahn()


def query_from_record_v1(record):
    return {
        'routes_info': [
            [
                obj['source']['full_text'],
                obj['source']['lon'],
                obj['source']['lat'],
                obj['destinations']['full_text'],
                obj['destinations']['lon'],
                obj['destinations']['lat'],
                obj['created'],
            ]
            for obj in record.routes_info
        ],
        'source': {
            'point': [
                record.last_route['source']['lon'],
                record.last_route['source']['lat'],
            ],
            'full_text': record.last_route['source']['full_text'],
        },
        'time': record.time,
    }


def query_from_record_v2(record):
    return {
        'history': [
            {
                "source": obj['source'],
                "destination": (
                    obj['destinations'] if obj['destinations']['lon'] else None
                ),
                "created": obj['created'],
            }
            for obj in record.routes_info
        ],
        'source': record.last_route['source'],
        'time': record.time,
    }


versions = {
    "vladvo_v1": {
        "query_from_record": query_from_record_v1,
        "target_host": "http://vladvo.haze.yandex.net/expected_destinations",
    },
    "vladvo_v2": {
        "query_from_record": query_from_record_v2,
        "target_host": (
            "http://vladvo.haze.yandex.net/v2.0/expected_destinations"),
    },
    "dev_v1": {
        "query_from_record": query_from_record_v1,
        "target_host": "http://ml.taxi.dev.yandex.net/expected_destinations",
    },
    "dev_v2": {
        "query_from_record": query_from_record_v2,
        "target_host": (
            "http://ml.taxi.dev.yandex.net/v2.0/expected_destinations"),
    },
    "tst_v1": {
        "query_from_record": query_from_record_v1,
        "target_host": "http://ml.taxi.tst.yandex.net/expected_destinations",
    },
    "tst_v2": {
        "query_from_record": query_from_record_v2,
        "target_host": (
            "http://ml.taxi.tst.yandex.net/v2.0/expected_destinations"),
    },
    "load_075": {
        "query_from_record": query_from_record_v2,
        "target_host": (
            "http://target075i.load.yandex.net/v2.0/expected_destinations"),
        "headers": {
            "Host": "ml.taxi.dev.yandex.net",
        },
    },
}

ammos_table_path = '//home/taxi_ml/suggest/golden_set/set_second_half_feb_2018'


def prepare_queries(version, i_from, i_to):
    print("Preparing queries for {}".format(version))
    query_from_record = versions[version]["query_from_record"]
    ammos = cluster.read(ammos_table_path)[i_from:i_to]
    print("Data loaded from YT")
    queries_obj = {i + i_from: query_from_record(record)
                   for i, record in enumerate(ammos)}
    import json
    json.dump(
        queries_obj, open("queries_{}_{}.json".format(i_from, i_to), mode="w"))


def prepare_ammo(version, i_from, i_to, handler_name):
    print("Preparing ammo for {}".format(version))
    f = open("ammo_{}_{}_{}.txt".format(version, i_from, i_to), mode="w")
    query_from_record = versions[version]["query_from_record"]
    ammos = cluster.read(ammos_table_path)[i_from:i_to]
    print("Data loaded from YT")
    print("[Host: ml.taxi.dev.yandex.net]\n"
          "[Content-type: application/json]\n[User-agent: tank]", file=f)
    import json
    for record in ammos:
        query = query_from_record(record)
        query_string = json.dumps(query)
        print(len(query_string), handler_name, file=f)
        print(query_string, file=f)
    f.close()


def test_mlaas(version, i_from, i_to, return_features=False):
    print("Started testing {} from {} to {}".format(version, i_from, i_to))
    query_from_record = versions[version]["query_from_record"]
    target_host = versions[version]["target_host"]
    headers = versions[version].get("headers", None)
    print("Target host:", target_host)
    if return_features:
        print("Getting features")
    ammos = cluster.read(ammos_table_path)[i_from:i_to]
    print("Data loaded from YT")
    for i, record in enumerate(ammos):
        real_i = i + i_from
        response_code = -1
        try:
            req_params = {
                "json": query_from_record(record),
            }
            if headers:
                req_params["headers"] = headers
            if return_features:
                req_params["params"] = {"features": 1}
            for sleep_seconds in [1, 2]:
                response = request("post", target_host, **req_params)
                response_code = response.status_code
                if response_code == 200:
                    break
                time.sleep(sleep_seconds)
            if response_code == 200:
                response.json()
        finally:
            print("{} : {}".format(real_i, response_code))
    print("Testing finished")


test_mlaas("load_075", 0, 1000, False)

# prepare_ammo("dev_v2", 0, 100, "/v2.0/expected_destinations")

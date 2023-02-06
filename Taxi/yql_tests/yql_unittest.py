import json
import os
import subprocess

from library.python import resource
from yql.api.v1.client import YqlClient
import yatest.common

from taxi.antifraud.food_geocheat_detection.lib import run_yql_geocheat_detection


def test_geocheat_detection_basic(yql_api, yt):
    yt = yt.yt_wrapper

    path = {}
    for entity in ["courier_status_coordinate", "courier_shift_events", "order", "place", "geotracks"]:
        path[entity] = "//tmp/%s" % entity

        yt.write_table(
            yt.TablePath(path[entity], attributes={"schema": json.loads(resource.find("%s_schema" % entity))}),
            json.loads(resource.find("%s_data" % entity)),
        )

    path["output_orders"] = "//tmp/output_orders"
    path["output_orders_with_images"] = "//tmp/output_orders_with_images"
    path["output_shifts"] = "//tmp/output_shifts"
    # output_orders_table_data = json.loads(resource.find("output_orders_data"))
    # output_shifts_table_data = json.loads(resource.find("output_shifts_data"))

    client = YqlClient(
        server="localhost",
        port=yql_api.port,
        db="plato"
    )

    run_yql_geocheat_detection(
        client,
        path["courier_status_coordinate"],
        path["courier_shift_events"],
        path["order"],
        path["place"],
        [path["geotracks"]],
        path["output_orders"],
        path["output_orders_with_images"],
        path["output_shifts"],
        "2020-02-26",
    )

    return (
        list(yt.read_table(yt.TablePath(path["output_orders"]), format="json")),
        list(yt.read_table(yt.TablePath(path["output_shifts"]), format="json")),
    )


def test_binary(yql_api, yt):
    yt = yt.yt_wrapper

    yt.create("map_node", "//tmp/binary")
    path = {}
    for entity in ["courier_status_coordinate", "courier_shift_events", "order", "place", "geotracks"]:
        path[entity] = "//tmp/binary/%s" % entity

        yt.write_table(
            yt.TablePath(path[entity], attributes={"schema": json.loads(resource.find("%s_schema" % entity))}),
            json.loads(resource.find("%s_data" % entity)),
        )

    path["output_orders"] = "//tmp/output_orders"
    path["output_orders_with_images"] = "//tmp/output_orders_with_images"
    path["output_shifts"] = "//tmp/output_shifts"
    # output_orders_table_data = json.loads(resource.find("output_orders_data"))
    # output_shifts_table_data = json.loads(resource.find("output_shifts_data"))

    binpath = yatest.common.binary_path("taxi/antifraud/food_geocheat_detection/bin/food_geocheat_detection")
    options = {
        "-y": "yql_token",
        "--cluster": yt.config["proxy"]["url"],
        "--courier-status-coordinate-table": path["courier_status_coordinate"],
        "--courier-shift-events-table": path["courier_shift_events"],
        "--order-table": path["order"],
        "--place-table": path["place"],
        "--geotracks-table": path["geotracks"],
        "--output-orders-table": path["output_orders"],
        "--output-orders-with-images-table": path["output_orders_with_images"],
        "--output-shifts-table": path["output_shifts"],
        "--date": "2020-02-26",
    }
    options_list = [item for pair in options.iteritems() for item in pair]
    command = [binpath] + options_list
    with open(options["-y"], "w") as f:
        f.write("blablabla")

    env = dict(os.environ, YQL_SERVER="localhost", YQL_PORT=str(yql_api.port), YQL_DB="plato")

    process = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
    process.communicate()
    rc = process.returncode
    assert rc == 0

    return (
        list(yt.read_table(yt.TablePath(path["output_orders"]), format="json")),
        list(yt.read_table(yt.TablePath(path["output_shifts"]), format="json")),
    )

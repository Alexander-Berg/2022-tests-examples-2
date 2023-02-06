import json

from library.python import resource
from yql.api.v1.client import YqlClient
from yt.yson.convert import yson_to_json
import cyson
import yatest.common

from taxi.antifraud.device_data.lib import run_stage_prepare_geopoints, run_stage_process_geopoints, run_stage_find_collusion


def test_stage_prepare_geopoints(yql_api, yt):
    yt = yt.yt_wrapper

    tables = set(table.split(".")[0] for table in resource.iterkeys() if table.endswith(".data.yson"))

    path = {}
    for entity in tables:
        path[entity] = "//tmp/stage1_%s" % entity

        schema = yson_to_json(cyson.loads(resource.find("%s.schema.yson" % entity)))
        data = resource.find("%s.data.yson" % entity)

        yt.write_table(
            yt.TablePath(path[entity], attributes={"schema": schema}),
            data,
            format="yson",
            raw=True,
        )
    path["table_output"] = "//tmp/stage1_%s" % "table_output"

    client = YqlClient(
        server="localhost",
        port=yql_api.port,
        db="plato"
    )

    run_stage_prepare_geopoints(
        client,
        table_gaid=path["table_gaid"],
        table_geologs=path["table_geologs"],
        table_idfa=path["table_idfa"],
        table_mm_public=path["table_mm_public"],
        table_order_events=path["table_order_events"],
        table_output=path["table_output"],
    )

    result = list(yt.read_table(
        yt.TablePath(path["table_output"]),
        format="yson",
    ))

    result_path = yatest.common.output_path("prepare_geopoints_output.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=4)
    return yatest.common.canonical_file(result_path, local=False)


def test_run_stage_process_geopoints(yql_api, yt):

    yt = yt.yt_wrapper

    input_data = resource.find("table_output_prepared.data.yson")
    input_schema = yson_to_json(cyson.loads(resource.find("table_output_prepared.schema.yson")))
    input_path = "//tmp/stage2_table_input"

    yt.write_table(
        yt.TablePath(input_path, attributes={"schema": input_schema}),
        input_data,
        format="yson",
        raw=True,
    )

    output_path = "//tmp/stage2_table_output"

    run_stage_process_geopoints(
        yt,
        table_input=input_path,
        table_output=output_path,
    )

    result = list(yt.read_table(
        yt.TablePath(output_path),
        format="yson",
    ))

    result_path = yatest.common.output_path("process_geopoints_output.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=4)
    return yatest.common.canonical_file(result_path, local=False)


def test_run_stage_find_collusion(yql_api, yt):

    yt = yt.yt_wrapper

    path = {}
    for entity in ["table_output_processed", "table_dm_order", "table_xaron"]:
        path[entity] = "//tmp/stage3_%s" % entity

        schema = yson_to_json(cyson.loads(resource.find("%s.schema.yson" % entity)))
        data = resource.find("%s.data.yson" % entity)

        yt.write_table(
            yt.TablePath(path[entity], attributes={"schema": schema}),
            data,
            format="yson",
            raw=True,
        )

    output_path = "//tmp/stage3_table_output"

    client = YqlClient(
        server="localhost",
        port=yql_api.port,
        db="plato"
    )

    run_stage_find_collusion(
        client,
        table_processed=path["table_output_processed"],
        table_dm_order=path["table_dm_order"],
        table_xaron=path["table_xaron"],
        table_collusion=output_path,
    )

    result = list(yt.read_table(
        yt.TablePath(output_path),
        format="yson",
    ))

    result_path = yatest.common.output_path("find_collusion_output.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=4)
    return yatest.common.canonical_file(result_path, local=False)

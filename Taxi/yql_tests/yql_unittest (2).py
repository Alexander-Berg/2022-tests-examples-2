import collections
import json
import os
import subprocess

from library.python import resource
from yql.api.v1.client import YqlClient
import yatest.common

from taxi.antifraud.geo_markup.lib import stage_prepare_geopoints, stage_process_geopoints, stage_recombine_by_userid


def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, long):
        return int(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


def test_stage_prepare_geopoints_basic(yql_api, yt):
    yt = yt.yt_wrapper

    input_table_path = "//tmp/stage_prepare_geopoints_basic_input"
    input_table_data = json.loads(resource.find("stage_prepare_geopoints_basic_input"))
    input_table_schema = json.loads(resource.find("stage_prepare_geopoints_basic_schema"))

    output_table_path = "//tmp/stage_prepare_geopoints_basic_output"
    output_table_data = json.loads(resource.find("stage_prepare_geopoints_basic_output"))

    yt.write_table(
        yt.TablePath(input_table_path, attributes={"schema": input_table_schema}),
        input_table_data,
    )

    client = YqlClient(
        server="localhost",
        port=yql_api.port,
        db="plato"
    )

    stage_prepare_geopoints(client, [input_table_path], output_table_path, "2020-01-26")

    assert convert(list(yt.read_table(output_table_path))) == convert(output_table_data)


def test_stage_process_geopoints_basic(yt):
    yt = yt.yt_wrapper

    input_table_path = "//tmp/stage_process_geopoints_basic_input"
    input_table_data = json.loads(resource.find("stage_process_geopoints_basic_input"))
    input_table_schema = json.loads(resource.find("stage_process_geopoints_basic_schema"))

    output_table_path = "//tmp/stage_process_geopoints_basic_output"
    output_table_data = json.loads(resource.find("stage_process_geopoints_basic_output"))

    yt.write_table(
        yt.TablePath(input_table_path, attributes={"schema": input_table_schema}),
        input_table_data,
    )

    stage_process_geopoints(yt, input_table_path, output_table_path, "", "")

    assert json.loads(json.dumps(list(yt.read_table(output_table_path)))) == output_table_data


def test_stage_recombine_by_userid_basic(yql_api, yt):
    yt = yt.yt_wrapper

    input_table_path = "//tmp/stage_recombine_by_userid_basic_input"
    input_table_data = json.loads(resource.find("stage_recombine_by_userid_basic_input"))
    input_table_schema = json.loads(resource.find("stage_recombine_by_userid_basic_schema"))

    output_table_path = "//tmp/stage_recombine_by_userid_basic_output"
    output_table_data = json.loads(resource.find("stage_recombine_by_userid_basic_output"))

    yt.write_table(
        yt.TablePath(input_table_path, attributes={"schema": input_table_schema}),
        input_table_data,
    )

    client = YqlClient(
        server="localhost",
        port=yql_api.port,
        db="plato"
    )

    stage_recombine_by_userid(client, input_table_path, output_table_path)

    assert convert(list(yt.read_table(output_table_path))) == convert(output_table_data)


def test_binary(yql_api, yt):
    yt = yt.yt_wrapper

    input_table_path = "//tmp/binary_cmd_input"
    input_table_data = json.loads(resource.find("stage_prepare_geopoints_basic_input"))
    input_table_schema = json.loads(resource.find("stage_prepare_geopoints_basic_schema"))

    output_table_path = "//tmp/binary_cmd_output"
    output_table_data = json.loads(resource.find("binary_basic_output"))

    yt.write_table(
        yt.TablePath(input_table_path, attributes={"schema": input_table_schema}),
        input_table_data,
    )

    with open("yt_token", "w") as f1, open("yql_token", "w") as f2:
        f1.write("blablabla")
        f2.write("blablabla")

    env = dict(os.environ, YQL_SERVER="localhost", YQL_PORT=str(yql_api.port), YQL_DB="plato")
    binpath = yatest.common.binary_path("taxi/antifraud/geo_markup/bin/geo_markup")

    # whole process test

    options = {
        "-t": "yt_token",
        "-y": "yql_token",
        "--input-tables": "//tmp/binary_cmd_input",
        "--output-table": "//tmp/binary_cmd_output",
        "--date": "2020-01-26",
        "--cluster": yt.config["proxy"]["url"],
    }
    options_list = [item for pair in options.iteritems() for item in pair]
    command = [binpath] + options_list

    process = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
    streamdata = process.communicate()
    rc = process.returncode

    assert rc == 0, streamdata
    assert list(yt.read_table(output_table_path, format="json")) == output_table_data

    # stage-by-stage test
    # prepare stage

    options = {
        "--stage": "prepare",
        "-t": "yt_token",
        "-y": "yql_token",
        "--input-tables": "//tmp/binary_cmd_input",
        "--output-table": "//tmp/binary_stage_1_output",
        "--date": "2020-01-26",
        "--cluster": yt.config["proxy"]["url"],
    }
    options_list = [item for pair in options.iteritems() for item in pair]
    command = [binpath] + options_list

    process = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
    streamdata = process.communicate()
    rc = process.returncode

    assert rc == 0, streamdata

    # process stage

    options = {
        "--stage": "process",
        "-t": "yt_token",
        "-y": "yql_token",
        "--input-tables": "//tmp/binary_stage_1_output",
        "--output-table": "//tmp/binary_stage_2_output",
        "--date": "2020-01-26",
        "--cluster": yt.config["proxy"]["url"],
    }
    options_list = [item for pair in options.iteritems() for item in pair]
    command = [binpath] + options_list

    process = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
    streamdata = process.communicate()
    rc = process.returncode

    assert rc == 0, streamdata

    # recombine stage

    options = {
        "--stage": "recombine",
        "-t": "yt_token",
        "-y": "yql_token",
        "--input-tables": "//tmp/binary_stage_2_output",
        "--output-table": "//tmp/binary_stage_3_output",
        "--date": "2020-01-26",
        "--cluster": yt.config["proxy"]["url"],
    }
    options_list = [item for pair in options.iteritems() for item in pair]
    command = [binpath] + options_list

    process = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
    streamdata = process.communicate()
    rc = process.returncode

    assert rc == 0, streamdata

    assert convert(list(yt.read_table("//tmp/binary_stage_3_output", format="json"))) == convert(output_table_data)

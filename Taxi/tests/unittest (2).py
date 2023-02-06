import json
import os
import subprocess
import tempfile

from library.python import resource
import pandas as pd
import yatest.common

from taxi.antifraud.tools.read_mr_table_to_file.lib import mr_table_to_file


def read_table_to_json(path, file_format, sep=None):
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return "{}"

    if path.endswith(".xlsx") or path.endswith(".xls") or file_format in ("xlsx", "xls"):
        return pd.read_excel(path).fillna("").to_json()
    if sep is None:
        if file_format == "tsv" or path.endswith(".tsv"):
            sep = "\t"
        elif file_format == "csv" or path.endswith(".csv"):
            sep = ","
    return pd.read_csv(path, sep=sep, encoding="utf-8", engine="python").fillna("").to_json()


def _test_lib_one_table(wrapper, path, data, schema, file_format):
    wrapper.write_table(wrapper.TablePath(path, attributes={"schema": schema}), data)
    with tempfile.NamedTemporaryFile() as f:
        mr_table_to_file(path, f.name, file_format=file_format)
        return read_table_to_json(f.name, file_format)


def _test_bin_one_table(bin, wrapper, path, data, schema, file_format, sort_by, yt_proxy):
    wrapper.write_table(wrapper.TablePath(path, attributes={"schema": schema}), data)
    with tempfile.NamedTemporaryFile() as f:
        options = {
            "-i": path,
            "-o": f.name
        }
        if file_format is not None:
            options["-f"] = file_format
        if sort_by is not None:
            options["-s"] = sort_by
        options_list = [item for pair in options.items() for item in pair]
        command = [bin] + options_list

        env = dict(os.environ, YT_PROXY=yt_proxy)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, env=env)
        process.communicate()

        rc = process.returncode
        assert rc == 0

        return read_table_to_json(f.name, file_format)


def test_lib(yt):
    result = []
    for test in json.loads(resource.find("test_config")):
        path = "//tmp/{}".format(test["table_name"])
        data = json.loads(resource.find(test["table_data"]))
        schema = json.loads(resource.find(test["table_schema"]))
        if "file_format" not in test:
            file_format = "tsv"
        else:
            file_format = test["file_format"]
        result.append(_test_lib_one_table(yt.yt_wrapper, path, data, schema, file_format))
    return result


def test_bin(yt):
    binpath = yatest.common.binary_path("taxi/antifraud/tools/read_mr_table_to_file/bin/read_mr_table_to_file")

    result = []
    for test in json.loads(resource.find("test_config")):
        path = "//tmp/{}".format(test["table_name"])
        data = json.loads(resource.find(test["table_data"]))
        schema = json.loads(resource.find(test["table_schema"]))
        if "file_format" not in test:
            file_format = "tsv"
        else:
            file_format = test["file_format"]
        if "sort_by" not in test:
            sort_by = None
        else:
            sort_by = test["sort_by"]
        result.append(_test_bin_one_table(binpath, yt.yt_wrapper, path, data, schema, file_format, sort_by, f"localhost:{yt.yt_proxy_port}"))

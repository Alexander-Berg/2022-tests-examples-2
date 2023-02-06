import json

from library.python import resource

from taxi.antifraud.stranger_things.lib import table2html


def test_html(yt):
    yt = yt.yt_wrapper

    input_table_path = "//tmp/abakan"
    s = resource.find("abakan_data").decode()
    s = s.strip()
    s = s.split("\n")
    input_table_data = [json.loads(line) for line in s]
    input_table_schema = json.loads(resource.find("abakan_schema"))

    yt.write_table(
        yt.TablePath(input_table_path, attributes={"schema": input_table_schema}),
        input_table_data,
    )

    return table2html(yt, input_table_path)

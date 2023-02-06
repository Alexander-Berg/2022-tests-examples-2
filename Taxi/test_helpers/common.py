import inspect
import os
from bson import json_util


def load_test_json(filename):
    caller_path = os.path.abspath(inspect.stack()[1][1])
    file_path = os.path.join(os.path.dirname(caller_path), 'metadata', filename)
    json_options = json_util.JSONOptions(tz_aware=False)
    with open(file_path, 'r') as fin:
        return json_util.loads(fin.read(), json_options=json_options)

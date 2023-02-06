import os
import json


def load_test_json(filename):
    with open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r') as fin:
        return json.load(fin)

import json
from dmp_suite.file_utils import from_same_directory
from pyspark.sql import Row


FILES = [
    "1.json",
    "2.json",
    "3.json",
    "4.json",
    "5.json",
]

def test_cases():
    for f_name in FILES:
        f = open(from_same_directory(__file__, f_name))
        yield json.load(f)
        f.close()

from dmp_suite.file_utils import from_same_directory


def get_json_file(json_package, json_file):
    return from_same_directory(json_package.__file__, json_file)


def evaluate_map_objs(record):
    for key, value in record.items():
        if isinstance(value, map):
            record[key] = list(value)
    return record

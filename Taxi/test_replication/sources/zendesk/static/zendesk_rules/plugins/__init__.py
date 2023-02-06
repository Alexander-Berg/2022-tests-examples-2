from replication.custom_models import testsuite_plugins

INPUT_TRANSFORM = testsuite_plugins.INPUT_TRANSFORM


def int_to_string(value):
    return str(value)


CAST = {'int_to_string': int_to_string}

from nile.api.v1 import clusters

from zoo.utils.nile_helpers import configure_environment


STATFACE_PATH_TEMPLATE = 'Adhoc/taxi_ml/nirvana_bucket_test/{}'


def prepare_environment(obj):
    return configure_environment(obj, parallel_operations_limit=5)


def get_project_cluster():
    return prepare_environment(clusters.yt.Hahn())

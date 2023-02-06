from replication import settings
from replication.common import yaml_cache


def test_existence_clusters_graphs_links():
    for connections in settings.QUEUE_MONGO_DB_CLUSTERS.values():
        queue_database = connections[1]
        try:
            yaml_cache.substitutions.get(f'graph_link_{queue_database}')
        except KeyError:
            assert (
                False
            ), f'Not found link to external graphs for {queue_database}'

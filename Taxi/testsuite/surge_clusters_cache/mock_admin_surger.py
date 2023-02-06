import pytest

FILENAME = 'surge_clusters_snapshot.json'


class AdminSurgerClustersContext:
    def __init__(self, clusters):
        self.clusters = clusters

    def get_clusters(self):
        return self.clusters


@pytest.fixture(autouse=True)
def admin_surger_clusters(mockserver, load_json):
    clusters_snapshot = {}
    try:
        clusters_snapshot = load_json(FILENAME)
    except FileNotFoundError:
        pass

    ctx = AdminSurgerClustersContext(clusters_snapshot)

    @mockserver.json_handler('/taxi-admin-surger/get_clusters/')
    def _get_clusters(request):
        return mockserver.make_response(json=ctx.get_clusters())

    return ctx

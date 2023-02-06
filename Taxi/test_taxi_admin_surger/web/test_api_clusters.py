import pytest

from taxi_admin_surger import clusters_common
from taxi_admin_surger.generated.service.swagger.models import api as models

ZONE_PROTOTYPE = {
    'id': 'a',
    'geometry': [],
    'tariff_class': 'econom',
    'production_experiment_id': 'a',
    'name': 'A',
    'forced': [
        {
            'is_active': True,
            'experiment_name': 'BETTER_NOT_TO',
            'experiment_id': 'c1e39cb193054aedab92235ed32914bf',
        },
    ],
    'square': 1,
    'updated': '2000-01-02T03:04:05.659616+03:00',
}

AREAS_SIMPLE = [models.Zone.deserialize(ZONE_PROTOTYPE) for i in range(0, 6)]
AREAS_SIMPLE[0].geometry = [
    [33.47481818382888, 59.615129096780855],
    [33.43773932640699, 59.65476715189861],
    [33.53386969750076, 59.69852301478061],
    [33.635493232657, 59.663800834039606],
    [33.66570563500075, 59.6109539373776],
    [33.54760260765702, 59.58728486495442],
    [33.47481818382888, 59.615129096780855],
]
AREAS_SIMPLE[1].geometry = [
    [33.73900200915166, 59.6350602612564],
    [33.79942681383914, 59.67293822037215],
    [33.905856867550085, 59.63853709176359],
    [33.73900200915166, 59.6350602612564],
]
AREAS_SIMPLE[2].geometry = [
    [33.820662923151424, 59.31565989283442],
    [33.83336586504597, 59.322504005481576],
    [33.840575642878, 59.31460682969207],
    [33.820662923151424, 59.31565989283442],
]
AREAS_SIMPLE[3].geometry = [
    [33.818881936365514, 59.31535275277235],
    [33.80798143892898, 59.319959560952725],
    [33.80454821138992, 59.31350985408681],
    [33.818881936365514, 59.31535275277235],
]
AREAS_SIMPLE[4].geometry = [
    [33.8163267125482, 59.30512944341381],
    [33.82164821523374, 59.30885993791356],
    [33.83091792958923, 59.304032161001615],
    [33.8163267125482, 59.30512944341381],
]

AREAS_SIMPLE[5].geometry = [
    [33.773319150838674, 59.37686052778456],
    [33.774520780477324, 59.382597534957846],
    [33.78567876997928, 59.37948828554173],
    [33.773319150838674, 59.37686052778456],
]

EXPECTED_CLUSTERS = [
    ['61caea4c8431aa4f518deb2f', '094637bf71bd4675bf9d1103d6598427'],
    ['094637bf71bd4675bf9d1103d6598428', '094637bf71bd4675bf9d1103d6598429'],
]

EXPECTED_BOXES = [
    [
        [33.43773932640699, 59.69852301478061],
        [33.905856867550085, 59.58728486495442],
    ],
    [
        [33.80454821138992, 59.322504005481576],
        [33.840575642878, 59.31350985408681],
    ],
]

EXPECTED_FIXED_POINTS_MODIFIED = [[], ['snapshot_hello']]


@pytest.mark.parametrize(
    'areas,area_clusterization_distance_meter,expected_size',
    [
        (AREAS_SIMPLE, 10, 6),
        (AREAS_SIMPLE, 500, 5),
        (AREAS_SIMPLE, 1000, 4),
        (AREAS_SIMPLE, 8000, 3),
    ],
)
async def test_clusterize(
        areas, area_clusterization_distance_meter, expected_size,
):
    clusters = clusters_common.clusterize_surge_areas(
        areas, area_clusterization_distance_meter,
    )
    assert len(clusters) == expected_size


@pytest.mark.filldb(surge_clusters_snapshot='empty')
async def test_calculate_clusters_first_time(web_app_client, mongodb):
    response = await web_app_client.get('/recalculate_clusters/')
    assert response.status == 200
    clusters_snapshot = mongodb.surge_clusters_snapshot.find_one({})

    assert clusters_snapshot['version'] == 1

    clusters = clusters_snapshot['clusters']

    assert len(clusters) == len(EXPECTED_CLUSTERS)

    for i, _ in enumerate(EXPECTED_CLUSTERS):
        cluster = clusters[i]
        assert sorted(cluster['zone_ids']) == sorted(EXPECTED_CLUSTERS[i])
        assert cluster['box'] == EXPECTED_BOXES[i]
        assert not cluster['fixed_points_modified']


async def test_recalculate_clusters(web_app_client, mongodb):
    response = await web_app_client.get('/recalculate_clusters/')
    assert response.status == 200

    clusters_snapshot = mongodb.surge_clusters_snapshot.find_one({})

    assert clusters_snapshot['version'] == 2

    assert 'clusters' in clusters_snapshot
    clusters = clusters_snapshot['clusters']

    assert len(clusters) == len(EXPECTED_CLUSTERS)

    for i, _ in enumerate(EXPECTED_CLUSTERS):
        cluster = clusters[i]
        assert sorted(cluster['zone_ids']) == sorted(EXPECTED_CLUSTERS[i])
        assert cluster['box'] == EXPECTED_BOXES[i]
        assert (
            cluster['fixed_points_modified']
            == EXPECTED_FIXED_POINTS_MODIFIED[i]
        )


async def test_get_clusters(web_app_client):
    response = await web_app_client.get('/get_clusters/')
    assert response.status == 200

    clusters_snapshot = await response.json()
    assert 'clusters' in clusters_snapshot
    assert 'version' not in clusters_snapshot

    clusters = clusters_snapshot['clusters']

    assert len(clusters) == 2

    for cluster in clusters:
        assert 'box' in cluster
        assert 'zone_ids' in cluster
        assert 'fixed_points_modified' not in cluster

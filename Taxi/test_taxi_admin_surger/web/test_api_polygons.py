import copy
import logging

from aiohttp import web
import pytest

from taxi_admin_surger import clusters_common
from . import common

logger = logging.getLogger(__name__)

API_PREFIX = common.API_PREFIX
SEARCH_API_PREFIX = common.SEARCH_API_PREFIX


def fix_point(point):
    point['id'] = str(point['_id'])
    del point['_id']
    if 'position_id' in point:
        fixed_position_id = str(point['position_id'])
        point['position_id'] = fixed_position_id
    point['location'] = point['loc']['coordinates']
    del point['loc']


STATIC_PATH = 'test_recalculate_polygons'
POINTS_PATH = 'db_surge_points.json'
CLUSTERS_SNAPSHOT_PATH = 'db_surge_clusters_snapshot.json'


@pytest.fixture(name='points_data')
def _points_data(load_json):
    points = load_json(POINTS_PATH)
    for point in points:
        fix_point(point)
    return points


@pytest.fixture(name='clusters_snapshot_data')
def _clusters_snapshot_data(load_json):
    clusters_snapshot = load_json(CLUSTERS_SNAPSHOT_PATH)[0]
    return clusters_snapshot


@pytest.fixture(name='mock_pin_storage_impl')
def _mock_pin_storage_impl(mock_pin_storage):
    @mock_pin_storage('/v1/calculate-polygons')
    async def _handler(request):
        return web.json_response(
            {
                'polygons': [
                    {'fixed_point': point, 'vertices': MOCK_POLYGON}
                    for point in request.json['points']
                ],
            },
        )


MOCK_POLYGON = [[100, 100], [101, 100], [101, 101]]


@pytest.mark.parametrize(
    'snapshot,code,num_updated_points',
    [
        ('new', 200, 3),
        ('default', 200, 3),
        ('idontexist', 200, 0),
        ('unchanged', 200, 0),
    ],
)
async def test_recalculate_polygons(
        web_app_client,
        db,
        snapshot,
        code,
        num_updated_points,
        mock_pin_storage_impl,
        clusters_snapshot_data,
        points_data,
):
    def get_request_url(snapshot):
        return (
            f'/admin/v1/polygons/recalculate?snapshot={snapshot}&radius=3000.0'
        )

    def get_expected_clusters(_snapshot):
        expected_clusters_ = copy.deepcopy(clusters_snapshot_data)
        is_modified = False
        for cluster in expected_clusters_['clusters']:
            if _snapshot in cluster['fixed_points_modified']:
                cluster['fixed_points_modified'].remove(_snapshot)
                is_modified = True
        if is_modified:
            expected_clusters_['version'] = expected_clusters_['version'] + 1
        return expected_clusters_

    def get_expected_points(_snapshot):
        def point_needs_modified(_point):
            if 'position_id' not in _point or _point['snapshot'] != _snapshot:
                return False
            for _, cluster in enumerate(clusters_snapshot_data['clusters']):
                if (
                        _snapshot in cluster['fixed_points_modified']
                        and clusters_common.is_in_box(
                            _point['location'], cluster['box'],
                        )
                ):
                    return True
            return False

        expected_points_ = copy.deepcopy(points_data)
        for point in expected_points_:
            if point_needs_modified(point):
                point['polygon'] = {'points': MOCK_POLYGON}
                point['version'] = point['version'] + 1
            if 'position_id' not in point:
                point['position_id'] = point['id']
        return expected_points_

    response = await web_app_client.patch(get_request_url(snapshot))
    assert response.status == code
    if code != 200:
        return

    # Check response ok
    response_data = await response.json()
    assert response_data['updated'] == num_updated_points

    # Check points ok
    def normalized(_response):
        response_sorted = list(sorted(_response, key=lambda x: x['id']))
        return response_sorted

    search_url = SEARCH_API_PREFIX
    actual_points = await common.make_request_checked(
        web_app_client.get, search_url,
    )

    expected_points = get_expected_points(snapshot)
    assert normalized(actual_points['items']) == normalized(expected_points)

    # Check clusters ok
    actual_clusters = clusters_common.for_json(
        await clusters_common.fetch_no_check(db),
    )

    expected_clusters = get_expected_clusters(snapshot)

    def normalized_clusters(cluster_response):
        response_sorted = list(
            sorted(cluster_response, key=lambda x: tuple(x['box'])),
        )
        return response_sorted

    assert actual_clusters['version'] == expected_clusters['version']
    assert normalized_clusters(
        actual_clusters['clusters'],
    ) == normalized_clusters(expected_clusters['clusters'])


@pytest.mark.parametrize(
    'point_id,code,num_updated_points',
    [
        ('6e922784c1ef4c92a8d05ce5', 200, 2),
        ('624dbd27a0d759f1631a222c', 404, 0),
        ('6e922784c1ef4c92a8d05ce2', 200, 3),
        ('6e922784c1ef4c92a8d05ce8', 200, 1),
        ('61e56db979b9c0cc8955288f', 200, 1),
    ],
)
# pylint: disable=W0621
async def test_force_recalculate_polygons(
        web_app_client,
        mock_pin_storage_impl,
        point_id,
        code,
        num_updated_points,
):
    def get_request_url():
        return (
            f'/admin/v1/polygons/force-recalculate?'
            f'point_id={point_id}&radius=3000.0'
        )

    response = await web_app_client.patch(get_request_url())
    assert response.status == code
    if code != 200:
        return

    # Check response ok
    response_data = await response.json()
    assert response_data['updated'] == num_updated_points

    # Don't test expected clusters and points
    # because already tested in previous test

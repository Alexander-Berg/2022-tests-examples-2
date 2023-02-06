import copy

import pytest

from taxi_admin_surger import clusters_common
from . import common

# Test data visualization can be found following the link below:
# https://yandex.ru/maps/?um=constructor%3A805e1721bd3b489a5a362a5b259876baf1db57f65aae68a7a22517c18cd996bb
# https://jing.yandex-team.ru/files/ivochkin/map_04-12-2020_16-03-23.geojson

API_PREFIX = common.API_PREFIX
POINT_API_PREFIX = common.POINT_API_PREFIX
TAG_API_PREFIX = f'{API_PREFIX}/tag'
SNAPSHOT_API_PREFIX = f'{API_PREFIX}/snapshot'
SEARCH_API_PREFIX = common.SEARCH_API_PREFIX

POLYGON = {'points': [[1, 2], [2, 3], [3, 4], [4, 5]]}

POINTS = [
    {
        'id': '6e922784c1ef4c92a8d05ce1',
        'position_id': '6e922784c1ef4c92a8d05ce1',
        'name': 'surge point #1 foo',
        'surge_zone_name': 'surge zone name',
        'location': [149.19371767012146, -35.30226135194424],
        'mode': 'apply',
        'tags': ['foo', 'bar'],
        'version': 1,
        'snapshot': 'default',
        'created': '2000-01-02T03:04:05.659616+03:00',
        'updated': '2000-01-02T03:04:05.659616+03:00',
        'employed': False,
    },
    {
        'id': '6e922784c1ef4c92a8d05ce2',
        'position_id': 'ffff2784c1ef4c92a8d05ce2',
        'name': 'surge point #2 bar',
        'surge_zone_name': '',
        'location': [149.12453813520932, -35.30803083852475],
        'mode': 'ignore',
        'tags': ['foo', 'qux'],
        'version': 1,
        'snapshot': 'default',
        'created': '2000-01-02T03:04:05.659616+03:00',
        'updated': '2000-01-02T03:04:05.659616+03:00',
        'employed': False,
    },
    {
        'id': '6e922784c1ef4c92a8d05ce3',
        'position_id': '6e922784c1ef4c92a8d05ce3',
        'name': 'surge point #3 quax',
        'surge_zone_name': 'surge zone name',
        'location': [149.18230218855405, -35.301276276165055],
        'mode': 'calculate',
        'tags': [],
        'version': 1,
        'snapshot': 'default',
        'created': '2000-01-02T03:04:05.659616+03:00',
        'updated': '2000-01-02T03:04:05.659616+03:00',
        'employed': False,
    },
    {
        'id': '6e922784c1ef4c92a8d05ce4',
        'position_id': '6e922784c1ef4c92a8d05ce4',
        'name': 'surge point #4 janfu',
        'surge_zone_name': '',
        'location': [149.202472400346, -35.31168932224323],
        'mode': 'calculate',
        'tags': ['qux'],
        'version': 1,
        'snapshot': 'default',
        'created': '2000-01-02T03:04:05.659616+03:00',
        'updated': '2000-01-02T03:04:05.659616+03:00',
        'employed': False,
    },
    {
        'id': '6e922784c1ef4c92a8d05ce5',
        'position_id': '6e922784c1ef4c92a8d05ce5',
        'name': 'surge point #5 gazebo',
        'surge_zone_name': '',
        'location': [149.2024724003461, -35.311689322243231],
        'mode': 'ignore',
        'tags': [],
        'version': 1,
        'snapshot': 'new',
        'created': '2000-01-02T03:04:05.659616+03:00',
        'updated': '2000-01-02T03:04:05.659616+03:00',
        'employed': True,
    },
    {
        'id': '6e922784c1ef4c92a8d05ce6',
        'position_id': 'ffff2784c1ef4c92a8d05ce6',
        'name': 'surge point #6 bazinga',
        'surge_zone_name': '',
        'location': [149.2024724003462, -35.311689322243232],
        'mode': 'calculate',
        'tags': ['qux'],
        'version': 1,
        'snapshot': 'new',
        'created': '2000-01-02T03:04:05.659616+03:00',
        'updated': '2000-01-02T03:04:05.659616+03:00',
        'employed': True,
    },
    {
        'id': '6e922784c1ef4c92a8d05ce7',
        'position_id': 'ffff2784c1ef4c92a8d05ce7',
        'name': 'surge point #7 poly',
        'surge_zone_name': '',
        'location': [149.2024724003463, -35.311689322243233],
        'mode': 'calculate',
        'tags': ['qux'],
        'version': 1,
        'snapshot': 'new',
        'created': '2000-01-02T03:04:05.659616+03:00',
        'updated': '2000-01-02T03:04:05.659616+03:00',
        'employed': True,
        'polygon': POLYGON,
    },
]

POINT_UPDATES = copy.deepcopy(POINTS)
for point_update in POINT_UPDATES:
    for pop_field in [
            'location',
            'updated',
            'created',
            'snapshot',
            'employed',
    ]:
        del point_update[pop_field]

VIEWPORTS = [
    {
        'tl': '149.1383568760537,-35.279988648386265',
        'br': '149.22496004072661,-35.341759951427846',
    },
    {
        'tl': '149.11569757429592,-35.29631553237549',
        'br': '149.18667955366593,-35.31489035880864',
    },
    {
        'tl': '149.13363618818752,-35.277102948484796',
        'br': '149.17843980757235,-35.34970655925299',
    },
]

SURGE_ZONES = [{'surge_zone_id': '094637bf71bd4675bf9d1103d6598426'}]

NEW_POINT_ID = '0e922784c1ef4c92a8d05ce1'
NEW_LOCATION = [149.187210, -35.303239]

POINT_CREATE_REQUEST = {
    'location': NEW_LOCATION,
    'mode': 'apply',
    'name': 'Точка зрения',
}


@pytest.mark.parametrize(
    'point,code',
    [
        (POINT_CREATE_REQUEST, 200),
        ({**POINT_CREATE_REQUEST, **{'mode': 'unknown'}}, 400),
        ({**POINT_CREATE_REQUEST, **{'id': NEW_POINT_ID}}, 400),
        ({**POINT_CREATE_REQUEST, **{'location': [181, 30]}}, 400),
        ({**POINT_CREATE_REQUEST, **{'location': [0, -91]}}, 400),
        (
            {
                **POINT_CREATE_REQUEST,
                **{'surge_zone_name': 'name', 'tags': ['foo', 'as diff']},
            },
            200,
        ),
        ({**POINT_CREATE_REQUEST, **{'tags': ['foo', 'as diff']}}, 200),
        ({**POINT_CREATE_REQUEST, **{'mode': 'unknown'}}, 400),
        ({**POINT_CREATE_REQUEST, **{'polygon': POLYGON}}, 200),
    ],
)
async def test_create(web_app_client, mongodb, point, code):
    new_point_url = f'{POINT_API_PREFIX}'
    params = {'snapshot': 'default'}
    response = await web_app_client.post(
        new_point_url, json=point, params=params,
    )
    assert response.status == code

    if code == 200:
        created_point = await response.json()
        # backend should generate and populate default values for
        # 'id', 'created', 'updated'
        generated_fields = ['id', 'created', 'updated', 'position_id']
        for field in generated_fields:
            assert field in created_point
            created_point.pop(field)
        assert created_point.pop('version') == 1
        assert not created_point.pop('employed')
        assert created_point.pop('snapshot') == 'default'
        point.setdefault('tags', [])
        point.setdefault('surge_zone_name', '')
        assert created_point == point

        clusters_snapshot = mongodb.surge_clusters_snapshot.find_one({})
        assert clusters_snapshot
        assert clusters_snapshot['version'] == 2

        assert 'clusters' in clusters_snapshot
        clusters = clusters_snapshot['clusters']

        assert any(cluster['fixed_points_modified'] for cluster in clusters)
        for cluster in clusters:
            assert len(cluster['fixed_points_modified']) < 2
            assert (
                ('default' in cluster['fixed_points_modified'])
                == clusters_common.is_in_box(
                    POINT_CREATE_REQUEST['location'], cluster['box'],
                )
            )


@pytest.mark.parametrize(
    'test_request,expected_response',
    [
        ({}, POINTS),
        (SURGE_ZONES[0], [POINTS[0], POINTS[2]]),
        ({'name': 'janfu'}, [POINTS[3]]),
        (
            VIEWPORTS[0],
            [POINTS[0], POINTS[2], POINTS[3], POINTS[4], POINTS[5], POINTS[6]],
        ),
        (VIEWPORTS[1], [POINTS[1], POINTS[2]]),
        (VIEWPORTS[2], []),
        ({'tags': 'foo'}, [POINTS[0], POINTS[1]]),
        ({'tags': 'foo,qux'}, [POINTS[1]]),
        ({**SURGE_ZONES[0], **VIEWPORTS[1]}, [POINTS[2]]),
        ({**SURGE_ZONES[0], **{'tags': 'foo', 'name': 'foo'}}, [POINTS[0]]),
        (
            {'snapshot': 'default'},
            [POINTS[0], POINTS[1], POINTS[2], POINTS[3]],
        ),
        ({'snapshot': 'new'}, [POINTS[4], POINTS[5], POINTS[6]]),
        ({'snapshot': 'foo'}, []),
        ({'text': '6e922784c1ef4c92a8d05ce1'}, [POINTS[0]]),
        ({'text': 'bar'}, [POINTS[0], POINTS[1]]),
        ({'text': 'janfu'}, [POINTS[3]]),
        ({'text': 'ffff2784c1ef4c92a8d05ce6'}, [POINTS[5]]),
        ({'sort': 'name'}, POINTS),
        ({'sort': 'name', 'order': 'asc'}, POINTS),
        ({'sort': 'name', 'order': 'desc'}, list(reversed(POINTS))),
        ({'has_polygon': 'true'}, [POINTS[6]]),
        ({'has_polygon': 'false'}, POINTS[:6]),
    ],
)
async def test_search(web_app_client, test_request, expected_response):
    search_url = SEARCH_API_PREFIX
    response = await common.make_request_checked(
        web_app_client.get, search_url, params=test_request,
    )

    def normalized(points):
        if 'sort' in test_request:
            return points
        return sorted(points, key=lambda x: x['id'])

    assert normalized(response['items']) == normalized(expected_response)


async def test_download(web_app_client):
    download_url = f'{POINT_API_PREFIX}/download'
    response = await web_app_client.get(
        download_url, params={'snapshot': 'default'},
    )
    assert response.status == 200

    expected_response = [POINTS[0], POINTS[1], POINTS[2], POINTS[3]]

    def normalized(points):
        return sorted(points, key=lambda x: x['id'])

    assert normalized((await response.json())['items']) == normalized(
        expected_response,
    )
    assert (
        response.headers['content-disposition']
        == 'attachment; filename="surge-points-default.json"'
    )


@pytest.mark.parametrize(
    'snapshot,code,expected_response,expected_points',
    [
        ('new', 200, [POINTS[4], POINTS[5], POINTS[6]], POINTS),
        (
            'default',
            200,
            [
                {**POINTS[i], **{'employed': True, 'version': 2}}
                for i in range(4)
            ],
            [
                {**POINTS[0], **{'employed': True, 'version': 2}},
                {**POINTS[1], **{'employed': True, 'version': 2}},
                {**POINTS[2], **{'employed': True, 'version': 2}},
                {**POINTS[3], **{'employed': True, 'version': 2}},
                POINTS[4],
                POINTS[5],
                POINTS[6],
            ],
        ),
        ('non_existing', 404, [], []),
    ],
)
async def test_employ(
        web_app_client, snapshot, code, expected_response, expected_points,
):
    employ_url = f'{POINT_API_PREFIX}/employ'
    search_url = SEARCH_API_PREFIX

    params = {'snapshot': snapshot}

    response = await web_app_client.post(employ_url, params=params)
    assert response.status == code

    if code != 200:
        return

    def normalized(points):
        return sorted(points, key=lambda x: x['id'])

    assert normalized((await response.json())['items']) == normalized(
        expected_response,
    )

    response = await common.make_request_checked(
        web_app_client.get, search_url,
    )
    assert normalized(response['items']) == normalized(expected_points)


@pytest.mark.parametrize(
    'point_id,expected_response,code',
    [(POINTS[0]['id'], POINTS[0], 200), (NEW_POINT_ID, None, 404)],
)
async def test_get(web_app_client, point_id, expected_response, code):
    point_url = f'{POINT_API_PREFIX}/{point_id}'

    response = await web_app_client.get(point_url)
    assert response.status == code

    if code == 200:
        assert await response.json() == expected_response


@pytest.mark.parametrize(
    'point,update,code',
    [
        (POINTS[0], {'version': 1, 'name': 'точка зрения'}, 200),
        (POINTS[0], {'version': 1, 'location': NEW_LOCATION}, 400),
        (
            POINTS[1],
            {'version': 1, 'surge_zone_name': 'yet another surge zone'},
            200,
        ),
        (POINTS[2], {'version': 1, 'mode': 'unknown_mode'}, 400),
        (POINTS[3], {'version': 1, 'mode': 'ignore'}, 200),
        (
            POINTS[0],
            {'version': 1, 'tags': ['tag1', 'tag 2', 'по-русски']},
            200,
        ),
        (POINTS[3], {'version': 2, 'mode': 'ignore'}, 409),
        (POINTS[3], {'version': 0, 'mode': 'ignore'}, 409),
        (POINTS[4], {'version': 1, 'mode': 'ignore'}, 409),
        (
            POINTS[3],
            {'version': 1, 'polygon': {'points': [[5, 6], [7, 8], [9, 10]]}},
            200,
        ),
    ],
)
async def test_update(web_app_client, point, update, code):
    point_url = f'{POINT_API_PREFIX}/{point["id"]}'
    params = {'version': update.pop('version')}
    response = await web_app_client.patch(
        point_url, json=update, params=params,
    )
    assert response.status == code

    def normalized(resp):
        resp.pop('updated', None)
        return resp

    if code == 200:
        assert normalized(await response.json()) == normalized(
            {**point, **update, **{'version': params['version'] + 1}},
        )


@pytest.mark.parametrize(
    'remove_point_id,code', [(POINTS[0]['id'], 200), (NEW_POINT_ID, 404)],
)
async def test_delete(web_app_client, mongodb, remove_point_id, code):
    point_url = f'{POINT_API_PREFIX}/{remove_point_id}'
    search_url = SEARCH_API_PREFIX

    params = {'version': 1}

    assert (
        await web_app_client.delete(point_url, params=params)
    ).status == code

    if code != 200:
        return

    response = await common.make_request_checked(
        web_app_client.get, search_url,
    )
    assert remove_point_id not in {i['id'] for i in response['items']}
    assert (
        await web_app_client.delete(point_url, params=params)
    ).status == 404

    clusters_snapshot = mongodb.surge_clusters_snapshot.find_one({})
    assert clusters_snapshot
    assert clusters_snapshot['version'] == 2

    assert 'clusters' in clusters_snapshot
    clusters = clusters_snapshot['clusters']

    assert any(cluster['fixed_points_modified'] for cluster in clusters)
    for cluster in clusters:
        assert len(cluster['fixed_points_modified']) < 2


@pytest.mark.parametrize(
    'test_request,expected_response,expected_points,code',
    [
        (
            {'create': [], 'update': [], 'delete': []},
            {'created': 0, 'updated': 0, 'deleted': 0},
            POINTS,
            200,
        ),
        (
            {
                'create': [
                    {
                        'name': 'surge point #5 yuppie',
                        'location': NEW_LOCATION,
                        'mode': 'ignore',
                    },
                ],
                'update': [
                    {'id': POINTS[1]['id'], 'mode': 'apply', 'version': 1},
                ],
                'delete': [POINTS[0]['id'], POINTS[3]['id'], POINTS[2]['id']],
            },
            {'created': 1, 'updated': 1, 'deleted': 3},
            [
                {
                    'name': 'surge point #5 yuppie',
                    'surge_zone_name': '',
                    'location': NEW_LOCATION,
                    'mode': 'ignore',
                    'snapshot': 'default',
                    'tags': [],
                    'version': 1,
                    'employed': False,
                },
                {**POINTS[1], **{'mode': 'apply'}},
                POINTS[4],
                POINTS[5],
                POINTS[6],
            ],
            200,
        ),
        (
            {
                'create': [],
                'update': [
                    {'id': NEW_POINT_ID, 'mode': 'apply', 'version': 1},
                ],
                'delete': [],
            },
            {'created': 0, 'updated': 0, 'deleted': 0},
            POINTS,
            404,
        ),
        (
            {'create': [], 'update': [], 'delete': [NEW_POINT_ID]},
            {'created': 0, 'updated': 0, 'deleted': 0},
            POINTS,
            404,
        ),
        (
            {
                'create': [],
                'update': [
                    {'id': POINTS[0]['id'], 'version': 1, 'mode': 'ignore'},
                    {'id': POINTS[0]['id'], 'version': 1, 'name': 'new name'},
                ],
                'delete': [],
            },
            {'created': 0, 'updated': 0, 'deleted': 0},
            POINTS,
            400,
        ),
        (
            {
                'create': [],
                'update': [
                    {'id': POINTS[0]['id'], 'version': 1, 'mode': 'ignore'},
                ],
                'delete': [POINTS[0]],
            },
            {'created': 0, 'updated': 0, 'deleted': 0},
            POINTS,
            400,
        ),
        (
            {
                'create': [
                    {
                        'name': 'surge point #5 yuppie',
                        'location': NEW_LOCATION,
                        'mode': 'ignore',
                    },
                ],
                'update': [
                    {'id': POINTS[1]['id'], 'mode': 'apply', 'version': 1},
                    {
                        'id': POINTS[3]['id'],
                        'name': 'hippie',
                        'version': 0,  # version conflict here
                    },
                    {'id': POINTS[2]['id'], 'mode': 'ignore', 'version': 1},
                ],
                'delete': [POINTS[0]['id']],
            },
            {
                'created': 0,
                'updated': 1,
                'deleted': 1,
                'errors': [
                    {'op_index': 2, 'op_type': 'update', 'message': ''},
                ],
            },
            [
                {**POINTS[1], **{'mode': 'apply', 'version': 2}},
                POINTS[2],
                POINTS[3],
                POINTS[4],
                POINTS[5],
                POINTS[6],
            ],
            200,
        ),
        (
            {
                'create': [],
                'update': [
                    {
                        'id': POINTS[0]['position_id'],
                        'version': 1,
                        'mode': 'ignore',
                    },
                    {'id': POINTS[1]['id'], 'version': 1, 'mode': 'calculate'},
                ],
                'delete': [POINTS[3]['id'], POINTS[2]['position_id']],
            },
            {'created': 0, 'updated': 2, 'deleted': 0},
            [
                {**POINTS[0], **{'version': 2, 'mode': 'ignore'}},
                {**POINTS[1], **{'version': 2, 'mode': 'calculate'}},
                POINTS[4],
                POINTS[5],
                POINTS[6],
            ],
            200,
        ),
        (
            {
                'create': [],
                'update': [
                    {
                        'id': POINTS[1]['position_id'],
                        'version': 1,
                        'mode': 'ignore',
                    },
                    {'id': POINTS[1]['id'], 'version': 1, 'mode': 'calculate'},
                ],
                'delete': [],
            },
            {'created': 0, 'updated': 0, 'deleted': 0},
            POINTS,
            400,
        ),
        (
            {
                'create': [],
                'update': [
                    {
                        'id': POINTS[1]['position_id'],
                        'version': 1,
                        'mode': 'ignore',
                    },
                ],
                'delete': [POINTS[1]['id']],
            },
            {'created': 0, 'updated': 0, 'deleted': 0},
            POINTS,
            400,
        ),
    ],
)
async def test_bulk_update(
        web_app_client, test_request, expected_response, expected_points, code,
):
    bulk_update_url = f'{POINT_API_PREFIX}/bulk'
    search_url = SEARCH_API_PREFIX

    params = {'snapshot': 'default'}

    response = await web_app_client.post(
        bulk_update_url, json=test_request, params=params,
    )
    assert response.status == code

    if code != 200:
        return

    def pop_message(resp):
        for err in resp.get('errors', []):
            err.pop('message')

    assert pop_message(await response.json()) == pop_message(expected_response)

    response = await common.make_request_checked(
        web_app_client.get, search_url,
    )

    def normalized(points):
        generated_fields = [
            'id',
            'version',
            'created',
            'updated',
            'position_id',
        ]
        points = copy.deepcopy(points)
        for point in points:
            for generated_field in generated_fields:
                point.pop(generated_field, None)
        return sorted(points, key=lambda x: x['name'])

    assert normalized(response['items']) == normalized(expected_points)


POINT_INSIDE_AIRPORT = [149.196118, -35.302931]
POINT_OUTSIDE_AIRPORT = [149.180671405473, -35.28565417183031]

POINT_INSIDE_AIRPORT_ID = '6e922784c1ef4c92a8d05ce1'
POINT_OUTSIDE_AIRPORT_ID = '6e922784c1ef4c92a8d05ce2'


@pytest.mark.filldb(surge_points='modification_test')
@pytest.mark.parametrize(
    'test_request',
    [
        (
            {
                'create': [
                    {
                        'name': 'surge point #3 inside airport',
                        'location': POINT_INSIDE_AIRPORT,
                        'mode': 'apply',
                    },
                    {
                        'name': 'surge point #4 outside airport',
                        'location': POINT_OUTSIDE_AIRPORT,
                        'mode': 'apply',
                    },
                ],
                'update': [],
                'delete': [],
            }
        ),
        (
            {
                'create': [
                    {
                        'name': 'surge point #4 outside airport',
                        'location': POINT_OUTSIDE_AIRPORT,
                        'mode': 'apply',
                    },
                ],
                'update': [],
                'delete': [POINT_INSIDE_AIRPORT_ID],
            }
        ),
        (
            {
                'create': [
                    {
                        'name': 'surge point #3 inside airport',
                        'location': POINT_INSIDE_AIRPORT,
                        'mode': 'apply',
                    },
                    {
                        'name': 'surge point #4 outside airport',
                        'location': POINT_OUTSIDE_AIRPORT,
                        'mode': 'apply',
                    },
                ],
                'update': [],
                'delete': [POINT_INSIDE_AIRPORT_ID, POINT_OUTSIDE_AIRPORT_ID],
            }
        ),
    ],
)
async def test_bulk_update_clusters_modified(
        web_app_client, mongodb, test_request,
):
    bulk_update_url = f'{POINT_API_PREFIX}/bulk'

    params = {'snapshot': 'default'}

    response = await web_app_client.post(
        bulk_update_url, json=test_request, params=params,
    )
    assert response.status == 200

    clusters_snapshot = mongodb.surge_clusters_snapshot.find_one({})
    assert clusters_snapshot
    assert clusters_snapshot['version'] == 2

    assert 'clusters' in clusters_snapshot
    clusters = clusters_snapshot['clusters']

    modified = 0
    for cluster in clusters:
        if cluster['fixed_points_modified']:
            assert cluster['fixed_points_modified'] == ['default']
            modified = modified + 1
    assert modified == 1


@pytest.mark.filldb(surge_clusters_snapshot='existing')
@pytest.mark.parametrize(
    'snapshot_from,snapshot_to,code,expected_points',
    [
        (
            'new',
            'new_default',
            200,
            POINTS
            + [
                {
                    **POINTS[4],
                    **{'snapshot': 'new_default', 'employed': False},
                },
                {
                    **POINTS[5],
                    **{'snapshot': 'new_default', 'employed': False},
                },
                {
                    **POINTS[6],
                    **{'snapshot': 'new_default', 'employed': False},
                },
            ],
        ),
        ('new', 'default', 409, []),
        ('non_existing', 'new_default', 404, []),
    ],
)
async def test_copy_snapshot(
        web_app_client,
        mongodb,
        snapshot_from,
        snapshot_to,
        code,
        expected_points,
):
    copy_snapshots_url = f'{SNAPSHOT_API_PREFIX}/copy'
    search_url = SEARCH_API_PREFIX

    params = {'from': snapshot_from, 'to': snapshot_to}

    response = await web_app_client.post(copy_snapshots_url, params=params)
    assert response.status == code

    if code != 200:
        return

    response = await common.make_request_checked(
        web_app_client.get, search_url,
    )

    def normalized(points):
        # Do not consider 'position_id' generated here. position_id should
        # persist through snapshot copy.
        generated_fields = ['id', 'version', 'created', 'updated']
        points = copy.deepcopy(points)
        for point in points:
            for generated_field in generated_fields:
                point.pop(generated_field, None)
        return sorted(points, key=lambda x: x['name'])

    assert normalized(response['items']) == normalized(expected_points)

    clusters_snapshot = mongodb.surge_clusters_snapshot.find_one({})
    assert clusters_snapshot
    assert clusters_snapshot['version'] == 2

    assert 'clusters' in clusters_snapshot
    clusters = clusters_snapshot['clusters']

    for cluster in clusters:
        if snapshot_from in cluster['fixed_points_modified']:
            assert snapshot_to in cluster['fixed_points_modified']
            assert len(cluster['fixed_points_modified']) == 3
        else:
            assert snapshot_to not in cluster['fixed_points_modified']
            assert len(cluster['fixed_points_modified']) == 1


@pytest.mark.parametrize(
    'points_to_remove,points_to_create,snapshot,expected_response',
    [
        ([], [], None, {'items': ['foo', 'bar', 'qux']}),
        ([POINTS[i]['id'] for i in range(4)], [], 'default', {'items': []}),
        (
            [POINTS[1]['id'], POINTS[3]['id']],
            [],
            'default',
            {'items': ['foo', 'bar']},
        ),
        (
            [],
            [
                {**POINT_CREATE_REQUEST, **{'tags': ['по-русски']}},
                {
                    **POINT_CREATE_REQUEST,
                    **{'tags': ['по-русски', 'with space']},
                },
            ],
            None,
            {'items': ['foo', 'bar', 'qux', 'по-русски', 'with space']},
        ),
        ([], [], 'new', {'items': ['qux']}),
    ],
)
async def test_search_tags(
        web_app_client,
        points_to_remove,
        points_to_create,
        snapshot,
        expected_response,
):
    search_tags_url = f'{TAG_API_PREFIX}/search'

    for point_id in points_to_remove:
        point_url = f'{POINT_API_PREFIX}/{point_id}'
        params = {'version': 1}
        await common.make_request_checked(
            web_app_client.delete, point_url, params=params,
        )

    for point in points_to_create:
        point_url = f'{POINT_API_PREFIX}'
        params = {'snapshot': 'default'}
        await common.make_request_checked(
            web_app_client.post, point_url, json=point, params=params,
        )

    params = {'snapshot': snapshot} if snapshot is not None else None
    response = await web_app_client.get(search_tags_url, params=params)
    assert response.status == 200

    def normalized(response):
        response['items'] = list(sorted(response['items']))
        return response

    assert normalized(await response.json()) == normalized(expected_response)


@pytest.mark.parametrize(
    'points_to_remove,points_to_create,expected_response',
    [
        ([], [], {'items': [{'name': 'default'}, {'name': 'new'}]}),
        (
            [POINTS[i]['id'] for i in range(4)],
            [],
            {'items': [{'name': 'new'}]},
        ),
        (
            [],
            [(POINT_CREATE_REQUEST, 'old')],
            {'items': [{'name': 'default'}, {'name': 'old'}, {'name': 'new'}]},
        ),
    ],
)
async def test_search_snapshots(
        web_app_client, points_to_remove, points_to_create, expected_response,
):
    search_tags_url = f'{SNAPSHOT_API_PREFIX}/search'

    for point_id in points_to_remove:
        point_url = f'{POINT_API_PREFIX}/{point_id}'
        params = {'version': 1}
        await common.make_request_checked(
            web_app_client.delete, point_url, params=params,
        )

    for point, snapshot in points_to_create:
        point_url = f'{POINT_API_PREFIX}'
        params = {'snapshot': snapshot}
        await common.make_request_checked(
            web_app_client.post, point_url, json=point, params=params,
        )

    response = await web_app_client.get(search_tags_url)
    assert response.status == 200

    def normalized(response):
        response['items'] = list(
            sorted(response['items'], key=lambda x: x['name']),
        )
        return response

    assert normalized(await response.json()) == normalized(expected_response)


async def test_error_reporting(web_app_client):
    bulk_update_url = f'{POINT_API_PREFIX}/bulk'
    params = {'snapshot': 'default'}
    body = {
        'update': [{'id': POINTS[0]['id'], 'mode': 'ignore', 'version': 1}],
        'delete': [POINTS[0]['id']],
    }
    response = await web_app_client.post(
        bulk_update_url, json=body, params=params,
    )
    assert response.status == 400
    assert await response.json() == {
        'code': 'surge_point_bad_request',
        'message': (
            'updates and deletes contain same ids='
            '{\'6e922784c1ef4c92a8d05ce1\'}'
        ),
    }

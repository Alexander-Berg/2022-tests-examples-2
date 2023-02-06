# pylint:disable=no-member
# type: ignore
import pytest

FIRST_POLYGON = {'name': 'zone1', 'enabled': False}
SECOND_POLYGON = {'name': 'zone2', 'enabled': True}


@pytest.mark.parametrize(
    'groups, expected_info',
    [
        ([], [FIRST_POLYGON, SECOND_POLYGON]),
        (['group1'], [FIRST_POLYGON]),
        (['group2'], [FIRST_POLYGON, SECOND_POLYGON]),
        (['group1', 'group2'], [FIRST_POLYGON, SECOND_POLYGON]),
    ],
)
async def test_base(web_app_client, groups, expected_info):
    response = await web_app_client.post(
        '/v1/service/polygons/list', json={'groups': groups},
    )
    assert response.status == 200
    body = await response.json()
    assert sorted(body['polygon_names']) == [
        row['name'] for row in expected_info
    ]
    assert (
        sorted(body['polygons_info'], key=lambda x: x['name']) == expected_info
    )

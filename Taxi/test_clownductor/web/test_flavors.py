import urllib.parse

import pytest

from clownductor.internal.db import db_types
from clownductor.internal.db import flavors


def _get_params_string(db_type):
    return (
        '?' + urllib.parse.urlencode({'db_type': db_type.value})
        if db_type
        else ''
    )


@pytest.mark.parametrize(
    'db_type, flavor_example, expected_count',
    [
        (None, flavors.FlavorNames.s2_nano, 2),
        (db_types.DbType.Postgres, flavors.FlavorNames.s2_nano, 2),
        (db_types.DbType.Mongo, flavors.FlavorNames.s2_nano, 2),
        (db_types.DbType.Redis, flavors.FlavorNames.m2_nano, 2),
    ],
)
@pytest.mark.pgsql('clownductor')
async def test_get_developer_flavors(
        web_app_client, db_type, flavor_example, expected_count,
):
    params = _get_params_string(db_type)
    response = await web_app_client.get(f'/v1/flavors/developer/{params}')
    assert response.status == 200
    content = await response.json()
    flavors_ = content['flavors']
    assert len(flavors_) == expected_count
    assert flavor_example.value in set(f['name'] for f in flavors_)


@pytest.mark.parametrize(
    'db_type, flavor_example, expected_count',
    [
        (None, flavors.FlavorNames.s2_nano, 9),
        (db_types.DbType.Postgres, flavors.FlavorNames.s2_large, 9),
        (db_types.DbType.Mongo, flavors.FlavorNames.s2_large, 9),
        (db_types.DbType.Redis, flavors.FlavorNames.m2_large, 12),
    ],
)
@pytest.mark.pgsql('clownductor')
async def test_get_admin_flavors(
        web_app_client, db_type, flavor_example, expected_count,
):
    params = {}
    if db_type:
        params.update({'db_type': db_type.value})
    response = await web_app_client.get(
        f'/v1/flavors/admin/?{urllib.parse.urlencode(params)}',
    )
    assert response.status == 200
    content = await response.json()
    flavors_ = content['flavors']
    assert len(flavors_) == expected_count
    assert flavor_example.value in set(f['name'] for f in flavors_)

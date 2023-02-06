import pytest

__DEFAULT_QUOTAS = (
    """
INSERT INTO quota.quotas (name, owner, value)
VALUES ('tags_count', 'efficiency', 10000),
       ('tags_count', 'taxi_effect', 20000),
       ('tags_count', 'cargo', 30000),
       ('passenger_tags_count', 'efficiency', 40000),
       ('passenger_tags_count', 'cargo', 50000)
""",
)


async def test_put_quota(taxi_segments_provider, pgsql):
    response = await taxi_segments_provider.put(
        '/admin/v1/quotas/quota?name=tags_count&owner=efficiency',
        json={'value': 100000},
    )
    assert response.status_code == 200

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute('SELECT name, owner, value FROM quota.quotas')
    assert [r for r in cursor] == [('tags_count', 'efficiency', 100000)]


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        """INSERT INTO quota.quotas (name, owner, value)
           VALUES ('tags_count', 'efficiency', 100000)""",
    ],
)
async def test_put_quota_already_exist(taxi_segments_provider, pgsql):
    response = await taxi_segments_provider.put(
        '/admin/v1/quotas/quota?name=tags_count&owner=efficiency',
        json={'value': 200000},
    )
    assert response.status_code == 200

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute('SELECT name, owner, value FROM quota.quotas')
    assert [r for r in cursor] == [('tags_count', 'efficiency', 200000)]


@pytest.mark.pgsql(
    'segments_provider',
    queries=[
        """INSERT INTO quota.quotas (name, owner, value)
           VALUES ('tags_count', 'efficiency', 100000)""",
    ],
)
async def test_delete_quota(taxi_segments_provider, pgsql):
    response = await taxi_segments_provider.delete(
        '/admin/v1/quotas/quota?name=tags_count&owner=efficiency',
    )
    assert response.status_code == 204

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute('SELECT name, owner, value FROM quota.quotas')
    assert [r for r in cursor] == []


async def test_delete_quota_non_existent(taxi_segments_provider, pgsql):
    response = await taxi_segments_provider.delete(
        '/admin/v1/quotas/quota?name=tags_count&owner=efficiency',
    )
    assert response.status_code == 200

    cursor = pgsql['segments_provider'].cursor()
    cursor.execute('SELECT name, owner, value FROM quota.quotas')
    assert [r for r in cursor] == []


@pytest.mark.pgsql('segments_provider', queries=[__DEFAULT_QUOTAS])
async def test_list_quotas_full(taxi_segments_provider, pgsql):
    response = await taxi_segments_provider.get(
        '/admin/v1/quotas/list?name=tags_count&owner=efficiency',
    )
    assert response.status_code == 200
    assert response.json() == {
        'quotas': [
            {'name': 'tags_count', 'owner': 'efficiency', 'value': 10000},
        ],
    }


@pytest.mark.pgsql('segments_provider', queries=[__DEFAULT_QUOTAS])
async def test_list_quotas_only_name(taxi_segments_provider, pgsql):
    response = await taxi_segments_provider.get(
        '/admin/v1/quotas/list?name=tags_count',
    )
    assert response.status_code == 200
    assert response.json() == {
        'quotas': [
            {'name': 'tags_count', 'owner': 'cargo', 'value': 30000},
            {'name': 'tags_count', 'owner': 'efficiency', 'value': 10000},
            {'name': 'tags_count', 'owner': 'taxi_effect', 'value': 20000},
        ],
    }


@pytest.mark.pgsql('segments_provider', queries=[__DEFAULT_QUOTAS])
async def test_list_quotas_only_owner(taxi_segments_provider, pgsql):
    response = await taxi_segments_provider.get(
        '/admin/v1/quotas/list?owner=eff',
    )
    assert response.status_code == 200
    assert response.json() == {
        'quotas': [
            {'name': 'tags_count', 'owner': 'efficiency', 'value': 10000},
            {'name': 'tags_count', 'owner': 'taxi_effect', 'value': 20000},
            {
                'name': 'passenger_tags_count',
                'owner': 'efficiency',
                'value': 40000,
            },
        ],
    }

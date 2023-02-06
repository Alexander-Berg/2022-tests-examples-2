import pytest


@pytest.mark.now('2017-11-01T01:10:00+0300')
async def test_yt_replications(monitoring_client):
    response = await monitoring_client.get('/yt/replications')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'test': {
            'updated_delay_from_now': 3600.0,
            'sync_delay': 477.0,
            'updated_delay_from_latest': {'hahn': 0.0, 'banach': 600.0},
        },
    }


class MockSession:
    async def close(self):
        pass


async def test_yt_resources(monkeypatch, monitoring_client, monitoring_app):
    class MockYtClient:
        session = MockSession()
        resources_info = {
            '//home/taxi/home/@recursive_resource_usage': {
                'disk_space_per_medium': {
                    'default': 10,
                    'ssd_blobs': 0,
                    'cloud': 0,
                    'ssd_journals': 0,
                },
                'tablet_count': 2,
                'tablet_static_memory': 1,
                'disk_space': 20,
                'chunk_count': 10,
                'node_count': 2,
            },
            '//home/taxi/production/@recursive_resource_usage': {
                'disk_space_per_medium': {
                    'default': 20,
                    'ssd_blobs': 1,
                    'cloud': 1,
                    'ssd_journals': 1,
                },
                'tablet_count': 5,
                'tablet_static_memory': 1,
                'disk_space': 50,
                'chunk_count': 50,
                'node_count': 5,
            },
            '//sys/accounts/taxi/@resource_limits': {
                'disk_space_per_medium': {
                    'default': 100,
                    'ssd_blobs': 1,
                    'cloud': 1,
                    'ssd_journals': 2,
                },
                'tablet_count': 10,
                'tablet_static_memory': 5,
                'disk_space': 100,
                'chunk_count': 100,
                'node_count': 10,
            },
            '//sys/accounts/taxi/@resource_usage': {
                'disk_space_per_medium': {
                    'default': 35,
                    'ssd_blobs': 1,
                    'cloud': 1,
                    'ssd_journals': 2,
                },
                'tablet_count': 8,
                'tablet_static_memory': 3,
                'disk_space': 80,
                'chunk_count': 70,
                'node_count': 8,
            },
        }

        async def get(self, path, *args, **kwargs):
            return self.resources_info[path]

    monkeypatch.setattr(
        monitoring_app, 'yt_clients', {'test_client': MockYtClient()},
    )
    response = await monitoring_client.get('/yt/resources')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'test_client': {
            'account': {
                'disk_space_per_medium.default': {
                    'limit': 100,
                    'used': 35,
                    'percentage': 35.0,
                },
                'disk_space_per_medium.ssd_blobs': {
                    'limit': 1,
                    'used': 1,
                    'percentage': 100.0,
                },
                'disk_space_per_medium.cloud': {
                    'limit': 1,
                    'used': 1,
                    'percentage': 100.0,
                },
                'disk_space_per_medium.ssd_journals': {
                    'limit': 2,
                    'used': 2,
                    'percentage': 100.0,
                },
                'tablet_count': {'limit': 10, 'used': 8, 'percentage': 80.0},
                'tablet_static_memory': {
                    'limit': 5,
                    'used': 3,
                    'percentage': 60.0,
                },
                'disk_space': {'limit': 100, 'used': 80, 'percentage': 80.0},
                'chunk_count': {'limit': 100, 'used': 70, 'percentage': 70.0},
                'node_count': {'limit': 10, 'used': 8, 'percentage': 80.0},
            },
            'home': {
                'disk_space_per_medium.default': {
                    'limit': 100,
                    'used': 10,
                    'percentage': 10.0,
                },
                'disk_space_per_medium.ssd_blobs': {
                    'limit': 1,
                    'used': 0,
                    'percentage': 0.0,
                },
                'disk_space_per_medium.cloud': {
                    'limit': 1,
                    'used': 0,
                    'percentage': 0.0,
                },
                'disk_space_per_medium.ssd_journals': {
                    'limit': 2,
                    'used': 0,
                    'percentage': 0.0,
                },
                'tablet_count': {'limit': 10, 'used': 2, 'percentage': 20.0},
                'tablet_static_memory': {
                    'limit': 5,
                    'used': 1,
                    'percentage': 20.0,
                },
                'disk_space': {'limit': 100, 'used': 20, 'percentage': 20.0},
                'chunk_count': {'limit': 100, 'used': 10, 'percentage': 10.0},
                'node_count': {'limit': 10, 'used': 2, 'percentage': 20.0},
            },
            'production': {
                'disk_space_per_medium.default': {
                    'limit': 100,
                    'used': 20,
                    'percentage': 20.0,
                },
                'disk_space_per_medium.ssd_blobs': {
                    'limit': 1,
                    'used': 1,
                    'percentage': 100.0,
                },
                'disk_space_per_medium.cloud': {
                    'limit': 1,
                    'used': 1,
                    'percentage': 100.0,
                },
                'disk_space_per_medium.ssd_journals': {
                    'limit': 2,
                    'used': 1,
                    'percentage': 50.0,
                },
                'tablet_count': {'limit': 10, 'used': 5, 'percentage': 50.0},
                'tablet_static_memory': {
                    'limit': 5,
                    'used': 1,
                    'percentage': 20.0,
                },
                'disk_space': {'limit': 100, 'used': 50, 'percentage': 50.0},
                'chunk_count': {'limit': 100, 'used': 50, 'percentage': 50.0},
                'node_count': {'limit': 10, 'used': 5, 'percentage': 50.0},
            },
        },
    }

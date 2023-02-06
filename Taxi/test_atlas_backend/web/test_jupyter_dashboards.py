import pytest

MARK_PG = pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_jupyter_dashboards.sql'],
)
MARK_CONFIG = pytest.mark.config(
    ATLAS_BACKEND_JUPYTERHUB_SERVER={
        'template-link': (
            'https://jupyter.yandex-team.ru/user/{login}/voila/render/{name}'
        ),
    },
)
MARKS = [MARK_PG, MARK_CONFIG]


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_jupyter_dashboards.sql'],
)
@pytest.mark.config(
    ATLAS_BACKEND_JUPYTERHUB_SERVER={
        'template-link': (
            'https://jupyter.yandex-team.ru/user/{login}/voila/render/{name}'
        ),
    },
)
@pytest.mark.parametrize('username', ['jupyter_viewer_1'])
async def test_get_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db, username,
):
    response = await web_app_client.get('/api/jupyter/dashboards')
    assert response.status == 200
    data = await response.json()
    assert len(data) == 1
    assert data[0] == {
        'id': 1,
        'name': '1.ipynb',
        'description': 'Это первый дашборд',
        'url': (
            'https://jupyter.yandex-team.ru/user/'
            'jupyter_viewer_1/voila/render/1.ipynb'
        ),
    }


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_jupyter_dashboards.sql'],
)
@pytest.mark.config(
    ATLAS_BACKEND_JUPYTERHUB_SERVER={
        'template-link': (
            'https://jupyter.yandex-team.ru/user/{login}/voila/render/{name}'
        ),
    },
)
@pytest.mark.parametrize(
    'username, count',
    [
        ('jupyter_viewer_1', 1),
        ('jupyter_viewer_2_3', 2),
        ('super_user', 3),
        ('jupyter_admin', 3),
        ('without_any_role', 0),
        ('jupyter_viewer_all', 3),
    ],
)
async def test_permissions_get_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db, username, count,
):
    response = await web_app_client.get('/api/jupyter/dashboards')
    assert response.status == 200
    data = await response.json()
    assert len(data) == count


@pytest.mark.parametrize('', [pytest.param(marks=MARKS)])
async def test_delete_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db,
):
    response = await web_app_client.delete('/api/jupyter/dashboards?id=1')
    assert response.status == 204
    response_get = await web_app_client.get('/api/jupyter/dashboards')
    assert response_get.status == 200
    data = await response_get.json()
    assert len(data) == 2


@pytest.mark.parametrize(
    'username, code',
    [
        pytest.param('jupyter_admin', 204, marks=MARKS),
        pytest.param('super_user', 204, marks=MARKS),
        pytest.param('without_any_role', 403, marks=MARKS),
        pytest.param('jupyter_viewer_1', 403, marks=MARKS),
        pytest.param('jupyter_viewer_all', 403, marks=MARKS),
    ],
)
async def test_permissions_delete_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db, username, code,
):
    response = await web_app_client.delete('/api/jupyter/dashboards?id=1')
    assert response.status == code


@pytest.mark.parametrize('', [pytest.param(marks=MARKS)])
async def test_update_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db,
):
    response = await web_app_client.put(
        '/api/jupyter/dashboards',
        json={
            'id': 1,
            'name': '1.ipynb',
            'description': 'Измененное описание',
        },
    )
    assert response.status == 200
    response_get = await web_app_client.get('/api/jupyter/dashboards')
    assert response_get.status == 200
    data = await response_get.json()
    assert len(data) == 3
    assert sorted(data, key=lambda x: x['id'])[0] == {
        'id': 1,
        'name': '1.ipynb',
        'description': 'Измененное описание',
        'url': (
            'https://jupyter.yandex-team.ru/user/'
            'omnipotent_user/voila/render/1.ipynb'
        ),
    }


@pytest.mark.parametrize('', [pytest.param(marks=MARKS)])
async def test_bad_update_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db,
):
    response = await web_app_client.put(
        '/api/jupyter/dashboards',
        json={
            'id': 4,
            'name': '1.ipynb',
            'description': 'Измененное описание',
        },
    )
    assert response.status == 404


@pytest.mark.parametrize(
    'username, code',
    [
        pytest.param('jupyter_admin', 200, marks=MARKS),
        pytest.param('super_user', 200, marks=MARKS),
        pytest.param('without_any_role', 403, marks=MARKS),
        pytest.param('jupyter_viewer_1', 403, marks=MARKS),
        pytest.param('jupyter_viewer_all', 403, marks=MARKS),
    ],
)
async def test_permissions_update_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db, username, code,
):
    response = await web_app_client.put(
        '/api/jupyter/dashboards',
        json={
            'id': 1,
            'name': '1.ipynb',
            'description': 'Измененное описание',
        },
    )
    assert response.status == code


@pytest.mark.parametrize('', [pytest.param(marks=MARKS)])
async def test_post_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db,
):
    response = await web_app_client.post(
        '/api/jupyter/dashboards',
        json={'name': '4.ipynb', 'description': 'Это четвертый дашборд'},
    )
    assert response.status == 200
    response_get = await web_app_client.get('/api/jupyter/dashboards')
    assert response_get.status == 200
    data = await response_get.json()
    assert len(data) == 4
    assert sorted(data, key=lambda x: x['id'])[3] == {
        'id': 4,
        'name': '4.ipynb',
        'description': 'Это четвертый дашборд',
        'url': (
            'https://jupyter.yandex-team.ru/user/'
            'omnipotent_user/voila/render/4.ipynb'
        ),
    }


@pytest.mark.parametrize(
    'username, code',
    [
        pytest.param('jupyter_admin', 200, marks=MARKS),
        pytest.param('super_user', 200, marks=MARKS),
        pytest.param('without_any_role', 403, marks=MARKS),
        pytest.param('jupyter_viewer_1', 403, marks=MARKS),
        pytest.param('jupyter_viewer_all', 403, marks=MARKS),
    ],
)
async def test_permissions_post_jupyter_dashboards(
        web_app_client, atlas_blackbox_mock, db, username, code,
):
    response = await web_app_client.post(
        '/api/jupyter/dashboards',
        json={'name': '4.ipynb', 'description': 'Это четвертый дашборд'},
    )
    assert response.status == code

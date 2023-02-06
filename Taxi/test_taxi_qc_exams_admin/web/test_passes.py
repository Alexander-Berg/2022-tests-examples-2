from aiohttp import web
import pytest

from taxi_qc_exams_admin.helpers import consts
HEADERS = {'Content-Type': 'application/json'}


@pytest.mark.config(
    QC_EXAMS_ADMIN_NIRVANA_ALLOWED_EXAMS=['thermobag', 'some_exam'],
)
async def test_pass_list_unavliable(web_app_client):

    response = await web_app_client.get(
        '/qc-admin/v1/pass/list',
        params={'source': 'test', 'limit': 100, 'exam': 'identity'},
        headers=HEADERS,
    )

    assert response.status == 400


@pytest.mark.config(
    QC_EXAMS_ADMIN_NIRVANA_ALLOWED_EXAMS=['thermobag', 'some_exam'],
)
async def test_pass_list(web_app_client, mock_quality_control_py3):
    @mock_quality_control_py3('/api/v1/pass/list')
    def _mock_pass_list(request):
        assert request.query == dict(
            limit='100', options='urls', exam='some_exam', direction='asc',
        )

        return web.json_response(
            dict(
                items=[
                    dict(
                        id='id_new',
                        status=consts.Status.NEW,
                        modified='2020-04-20T17:19:48.506531',
                        exam='some_exam',
                        entity_id='entity_id_new',
                        entity_type='driver',
                    ),
                    dict(
                        id='id_pending',
                        status=consts.Status.PENDING,
                        modified='2020-04-20T17:22:48.506531',
                        exam='some_exam',
                        entity_id='entity_id_pending',
                        entity_type='driver',
                    ),
                ],
                modified='2020-04-20T17:22:48.506531',
                cursor='test_cursor',
            ),
        )

    response = await web_app_client.get(
        '/qc-admin/v1/pass/list',
        params={'source': 'test', 'limit': 100, 'exam': 'some_exam'},
        headers=HEADERS,
    )

    assert response.status == 200
    data = await response.json()
    assert 'items' in data
    assert len(data['items']) == 1


@pytest.mark.config(
    QC_EXAMS_ADMIN_NIRVANA_ALLOWED_EXAMS=['thermobag', 'some_exam'],
)
async def test_pass_resolve(web_app_client, mock_quality_control_py3):
    @mock_quality_control_py3('/api/v1/pass/resolve')
    def _mock_pass_resolve(request):
        assert request.query == dict(pass_id='pass_id')
        assert request.json == {
            'identity': {'script': {'name': 'test'}},
            'status': 'SUCCESS',
        }
        return web.json_response(
            status=200, data={}, content_type='text/plain',
        )

    response = await web_app_client.post(
        '/qc-admin/v1/pass/resolve',
        params={'source': 'test', 'name': 'resolver', 'exam': 'some_exam'},
        json=[{'pass_id': 'pass_id', 'status': 'SUCCESS'}],
        headers=HEADERS,
    )

    assert response.status == 200


@pytest.mark.config(
    QC_EXAMS_ADMIN_NIRVANA_ALLOWED_EXAMS=['thermobag', 'some_exam'],
)
async def test_pass_multi_resolve(web_app_client, mock_quality_control_py3):
    @mock_quality_control_py3('/api/v1/pass/resolve')
    def _mock_pass_resolve(request):
        assert request.json == {
            'identity': {'script': {'name': 'test'}},
            'status': 'SUCCESS',
        }
        return web.json_response(
            status=200, data={}, content_type='text/plain',
        )

    response = await web_app_client.post(
        '/qc-admin/v1/pass/resolve',
        params={'source': 'test', 'name': 'resolver', 'exam': 'some_exam'},
        json=[
            {'pass_id': 'pass_1', 'status': 'SUCCESS'},
            {'pass_id': 'pass_2', 'status': 'SUCCESS'},
        ],
        headers=HEADERS,
    )
    assert _mock_pass_resolve.times_called == 2
    assert response.status == 200


@pytest.mark.config(
    QC_EXAMS_ADMIN_NIRVANA_ALLOWED_EXAMS=['thermobag', 'some_exam'],
    QC_EXAMS_ADMIN_NIRVANA_RESOLVE_LIMIT=1,
)
async def test_pass_multi_resolve_limit(
        web_app_client, mock_quality_control_py3,
):

    response = await web_app_client.post(
        '/qc-admin/v1/pass/resolve',
        params={'source': 'test', 'name': 'resolver', 'exam': 'some_exam'},
        json=[
            {'pass_id': 'pass_1', 'status': 'SUCCESS'},
            {'pass_id': 'pass_2', 'status': 'SUCCESS'},
        ],
        headers=HEADERS,
    )
    assert response.status == 400

import pytest

from test_clowny_alert_manager.helpers import builders


@pytest.mark.parametrize(
    'tmpl_id, status, expected_data',
    [
        (
            1,
            200,
            builders.template(
                'oom',
                builders.Event(id_=1, name='oom', template_id=1),
                repo_meta_=builders.repo_meta(
                    file_name='oom.yaml', file_path='templates/oom.yaml',
                ),
            ),
        ),
        (3, 404, None),
    ],
)
async def test_get(get_template, tmpl_id, status, expected_data):
    tmpl = await get_template(tmpl_id, status)
    if status != 200:
        return
    assert tmpl == expected_data


@pytest.mark.parametrize(
    'filters, max_id, templates_count',
    [({}, 2, 2), ({'limit': 1}, 1, 1), ({'cursor': {'newer_than': 1}}, 2, 1)],
)
async def test_list(
        taxi_clowny_alert_manager_web, filters, max_id, templates_count,
):
    response = await taxi_clowny_alert_manager_web.post(
        '/v1/templates/list/', json=filters,
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    assert len(data['templates']) == templates_count
    assert data['cursor']['newer_than'] == max_id

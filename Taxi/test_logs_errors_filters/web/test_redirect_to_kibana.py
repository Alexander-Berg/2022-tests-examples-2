import pytest


@pytest.mark.parametrize(
    'cgroup_id,expected_code,expected_link',
    [
        ('1', 302, 'https://kibana.taxi.yandex-team.ru/test1'),
        ('t1', 302, 'https://kibana.taxi.yandex-team.ru/test2'),
        (2, 404, None),
    ],
)
@pytest.mark.pgsql(
    'logs_errors_filters', files=['test_redirect_to_kibana.sql'],
)
async def test_update_cgroup(
        web_app_client, cgroup_id, expected_code, expected_link,
):
    response = await web_app_client.get(
        f'/k/{cgroup_id}', allow_redirects=False,
    )
    assert response.status == expected_code
    if expected_link:
        assert 'Location' in response.headers
        assert response.headers['Location'] == expected_link

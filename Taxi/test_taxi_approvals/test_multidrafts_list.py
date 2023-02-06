import pytest

from taxi_approvals.internal import headers as headers_module


@pytest.mark.parametrize(
    'filters,list_length',
    [
        ({}, 5),
        ({'tickets': ['TAXIRATE-35']}, 1),
        (
            {
                'created_before': '2017-11-01T04:10:00+0300',
                'created_after': '2017-11-01T04:10:00+0300',
            },
            5,
        ),
        ({'created_by': 'test_user'}, 3),
        ({'authors': ['test_user']}, 3),
        ({'authors': ['test_user', 'User Mult 10']}, 4),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_get_multidrafts_list(
        taxi_approvals_client, filters, list_length,
):
    response = await taxi_approvals_client.post(
        '/multidrafts/list/',
        json=filters,
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 200
    content = await response.json()
    assert len(content) == list_length


@pytest.mark.parametrize(
    'filters,list_length',
    [
        ({}, 1),
        ({'created_by': 'test_user'}, 1),
        ({'authors': ['test_user']}, 1),
    ],
)
@pytest.mark.pgsql('approvals', files=['data.sql'])
async def test_platform_multidrafts_list(
        taxi_approvals_client, filters, list_length,
):
    response = await taxi_approvals_client.post(
        '/multidrafts/list/',
        json=filters,
        headers={
            headers_module.X_YANDEX_LOGIN: 'test_login',
            headers_module.X_MULTISERVICES_PLATFORM: 'true',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert len(content) == list_length

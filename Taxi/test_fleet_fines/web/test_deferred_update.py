import datetime

import pytest

from fleet_fines.generated.web import web_context as context


@pytest.mark.config(
    FLEET_FINES_DEFERRED_UPDATE={
        'is_enabled': True,
        'retry_delays': ['5m', '10m', '15m'],
        'total_limit': 1000,
    },
)
@pytest.mark.now('2020-01-01T12:00:00+0')
async def test_success(web_app_client, web_context: context.Context):
    response = await web_app_client.post(
        '/v1/deferred-update', params={'uin': 'uin1'},
    )
    assert response.status == 200

    scheduled = await web_context.pg.main.fetch(
        'SELECT * FROM fleet_fines.deferred_updates',
    )
    scheduled_dicts = [dict(s) for s in scheduled]
    assert scheduled_dicts == [
        {'id': 1, 'uin': 'uin1', 'eta': datetime.datetime(2020, 1, 1, 12, 5)},
        {'id': 2, 'uin': 'uin1', 'eta': datetime.datetime(2020, 1, 1, 12, 10)},
        {'id': 3, 'uin': 'uin1', 'eta': datetime.datetime(2020, 1, 1, 12, 15)},
    ]


@pytest.mark.config(
    FLEET_FINES_DEFERRED_UPDATE={
        'is_enabled': True,
        'retry_delays': ['5m', '10m'],
        'total_limit': 1,
    },
)
async def test_limit(web_app_client, web_context: context.Context):
    response = await web_app_client.post(
        '/v1/deferred-update', params={'uin': 'uin1'},
    )
    assert response.status == 409

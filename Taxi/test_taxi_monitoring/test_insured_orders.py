import datetime

import pytest


@pytest.mark.parametrize(
    'utcnow,total_expected',
    [
        (datetime.datetime(2002, 1, 1), 0),
        (datetime.datetime(2002, 1, 1, 0, 1, 1), 8),
        (datetime.datetime(2002, 1, 1, 0, 3), 9),
        (datetime.datetime(2002, 1, 1, 0, 4, 1), 20),
        (datetime.datetime(2002, 1, 1, 0, 5), 20),
        (datetime.datetime(2002, 1, 1, 0, 5, 1), 16),
        (datetime.datetime(2002, 1, 1, 0, 8), 12),
        (datetime.datetime(2002, 1, 1, 0, 10, 1), 0),
    ],
)
async def test_by_various_nowtime(
        monkeypatch, monitoring_client, utcnow, total_expected,
):
    monkeypatch.setattr(datetime.datetime, 'utcnow', lambda: utcnow)
    response = await monitoring_client.get('/insured_orders')
    assert response.status == 200
    content = await response.json()
    assert content == {'total': total_expected}

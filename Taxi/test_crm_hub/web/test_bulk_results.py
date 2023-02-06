import datetime

import pytest

from crm_hub.logic import sending_stats


@pytest.mark.parametrize(
    'campaign_id, group_id, stat, result',
    [
        (
            1,
            1,
            {'planned': 0, 'sent': 0, 'failed': 0, 'skipped': 0, 'denied': 0},
            200,
        ),
        (
            1,
            2,
            {
                'planned': 1500,
                'sent': 700,
                'failed': 500,
                'skipped': 300,
                'denied': 200,
                'finished_at': '2021-02-06T01:00:00+03:00',
            },
            200,
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init.sql'])
async def test_bulk_result(
        web_app_client, campaign_id, group_id, stat, result,
):
    response = await web_app_client.get(
        '/v1/communication/bulk/results',
        params={
            'campaign_id': campaign_id,
            'group_id': group_id,
            'start_id': 0,
        },
    )
    assert response.status == result
    data = await response.json()
    assert data == stat


def test_sending_result_ex():

    _stat = sending_stats.SendingResultEx()

    _stat += sending_stats.SendingResultEx()
    assert _stat.planned == 0
    assert _stat.sent == 0
    assert _stat.failed == 0
    assert _stat.skipped == 0
    assert _stat.finished_at is None

    _stat += sending_stats.SendingResultEx(planned=10)
    assert _stat.planned == 10
    assert _stat.sent == 0
    assert _stat.failed == 0
    assert _stat.skipped == 0
    assert _stat.finished_at is None

    _stat += sending_stats.SendingResultEx(planned=10, sent=10)
    assert _stat.planned == 20
    assert _stat.sent == 10
    assert _stat.failed == 0
    assert _stat.skipped == 0
    assert _stat.finished_at is None

    _stat += sending_stats.SendingResultEx(sent=10, failed=10)
    assert _stat.planned == 20
    assert _stat.sent == 20
    assert _stat.failed == 10
    assert _stat.skipped == 0
    assert _stat.finished_at is None

    _stat += sending_stats.SendingResultEx(failed=10, skipped=10)
    assert _stat.planned == 20
    assert _stat.sent == 20
    assert _stat.failed == 20
    assert _stat.skipped == 10
    assert _stat.finished_at is None

    _stat += sending_stats.SendingResultEx(
        finished_at=datetime.datetime(2020, 2, 2, 2, 2, 2),
    )
    assert _stat.planned == 20
    assert _stat.sent == 20
    assert _stat.failed == 20
    assert _stat.skipped == 10
    assert _stat.finished_at == datetime.datetime(2020, 2, 2, 2, 2, 2)

    _stat += sending_stats.SendingResultEx(
        finished_at=datetime.datetime(2020, 1, 1, 2, 2, 2),
    )
    assert _stat.planned == 20
    assert _stat.sent == 20
    assert _stat.failed == 20
    assert _stat.skipped == 10
    assert _stat.finished_at == datetime.datetime(2020, 2, 2, 2, 2, 2)

    _stat += sending_stats.SendingResultEx(
        finished_at=datetime.datetime(2020, 3, 3, 2, 2, 2),
    )
    assert _stat.planned == 20
    assert _stat.sent == 20
    assert _stat.failed == 20
    assert _stat.skipped == 10
    assert _stat.finished_at == datetime.datetime(2020, 3, 3, 2, 2, 2)

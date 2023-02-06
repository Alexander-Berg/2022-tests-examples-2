import pytest

from eats_integration_shooter.stq import health_ping


@pytest.mark.pgsql(
    'eats_integration_shooter', files=['pg_eats_integration_shooter.sql'],
)
@pytest.mark.parametrize(
    'status_code, solomon_calls', [(200, 0), (500, 1), (404, 1)],
)
async def test_should_correct_run(
        mock_eats_partner_engine_yandex_eda,
        mockserver,
        stq_runner,
        stq3_context,
        task_info,
        status_code,
        solomon_calls,
        mock_solomon,
):
    solomon_mock = mock_solomon()

    @mock_eats_partner_engine_yandex_eda('/health/ping')
    async def ping_mock(request):
        return mockserver.make_response(status=status_code, json={})

    await health_ping.task(
        stq3_context, task_info, place_group_id='place_group_id_1',
    )
    assert ping_mock.has_calls
    assert solomon_mock.times_called == solomon_calls

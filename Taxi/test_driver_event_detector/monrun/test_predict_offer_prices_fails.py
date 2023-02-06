import pytest

from driver_event_detector.generated.cron import run_monrun

MODULE = 'driver_event_detector.monrun.predict_offer_prices_fails'


@pytest.mark.parametrize(
    'monitoring_status, expected_result',
    [
        (
            'crit',
            (
                '2; Following task is in status CRIT: '
                'driver_event_detector-crontasks-predict_offer_prices'
            ),
        ),
        ('ok', '0; OK'),
    ],
)
async def test_predict_offer_prices_fails(
        patch, response_mock, monitoring_status, expected_result,
) -> None:
    @patch('aiohttp.ClientSession.get')
    # pylint: disable=W0612
    async def json(*args, **kwargs):
        return response_mock(json={'monitoring_status': monitoring_status})

    result = await run_monrun.run([MODULE])
    assert result == expected_result

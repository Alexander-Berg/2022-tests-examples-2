import pytest

from eats_tips_withdrawal.generated.cron import run_cron


@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.now('1970-01-03 06:00:16')
@pytest.mark.config(
    EATS_TIPS_WITHDRAWALS_CRON_STATS={
        'withdrawal_thresholds': {
            'long_in_status': [
                {
                    'withdrawal_type': 'SBPb2p',
                    'status': 'sent to manual check',
                    'delay': 48 * 3600,
                },
            ],
        },
    },
)
async def test_send_stats(mock_stats, mysql):
    await run_cron.main(
        ['eats_tips_withdrawal.crontasks.send_statistics', '-t', '0'],
    )
    result = sorted(
        [sensor_to_dict(x) for senors in mock_stats for x in senors],
        key=sorting_dict_condition,
    )
    assert result == [
        {
            'labels': {
                'sensor': 'cron_withdrawal_stats',
                'status': 'sent_to_manual_check',
                'withdrawal_type': 'SBPb2p',
            },
            'value': 1.0,
        },
    ]


def sensor_to_dict(sensor):
    return {'value': sensor.value, 'labels': sensor.labels}


def sorting_dict_condition(item):
    return (
        item['labels']['sensor'],
        item['value'],
        item['labels'].get('payment_type', ''),
        item['labels'].get('transaction_status', ''),
    )
